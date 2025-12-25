# ============================================================
#  Project: CS2 WLED Controller
#  Author (Online): BARDIA156
#  Author (Personal): Bardia Dehbozorgi
#
#  License:
#  This project is open-source and free to use.
#  You are allowed to study, modify, and redistribute the source code
#  for non-commercial purposes.
#
#  Commercial use, selling, or monetizing this software or any derived
#  work is strictly prohibited without explicit permission from the author.
#
#  © 2025 Bardia Dehbozorgi. All rights reserved.
# ============================================================

from flask import Flask, request
import requests
import threading
import time
import json
import sys
import os

# =======================
# Arguments
# =======================
TEST_MODE = "--test" in sys.argv
TOTAL_LEDS = 105

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

# =======================
# Load config
# =======================
try:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)
except Exception:
    print("[ERROR] Cannot load config.json")
    sys.exit(1)

WLED_IP = config.get("wled_ip", "")

ENABLE_BOMB   = int(config.get("bomb_status", 0))
ENABLE_PLAYER = int(config.get("player_status", 0))
ENABLE_HEALTH = int(config.get("player_health", 0))

# =======================
# Validate mode
# =======================
modes = [ENABLE_BOMB, ENABLE_PLAYER, ENABLE_HEALTH]
if modes.count(1) != 1:
    print("[ERROR] Exactly ONE mode must be enabled")
    sys.exit(1)

if ENABLE_BOMB:
    MODE = "bomb"
elif ENABLE_PLAYER:
    MODE = "player_status"
else:
    MODE = "player_health"

# =======================
# Flask
# =======================
app = Flask(__name__)

def log(msg):
    print(f"[STATUS] {msg}")

# =======================
# Runtime state
# =======================
last_health = 100
bomb_active = False
current_state = "idle"
lock = threading.Lock()

# =======================
# WLED helpers
# =======================
def send_wled(data):
    try:
        requests.post(
            f"http://{WLED_IP}/json/state",
            json=data,
            timeout=0.25
        )
    except:
        pass

def solid(r, g, b, transition=5):
    send_wled({
        "on": True,
        "transition": transition,
        "seg": [{
            "id": 0,
            "start": 0,
            "stop": TOTAL_LEDS,
            "fx": 0,
            "col": [[r, g, b]]
        }]
    })

def fade(r, g, b, speed):
    send_wled({
        "on": True,
        "seg": [{
            "id": 0,
            "fx": 2,
            "sx": speed,
            "ix": speed,
            "col": [[r, g, b]]
        }]
    })

def android(r, g, b):
    send_wled({
        "on": True,
        "seg": [{
            "id": 0,
            "fx": 74,
            "col": [[r, g, b]]
        }]
    })

def off():
    send_wled({
        "on": False,
        "transition": 8
    })

def reset_state():
    global bomb_active, current_state
    with lock:
        bomb_active = False
        current_state = "idle"
    off()

# =======================
# Bomb sequence (safe)
# =======================
def bomb_sequence():
    global bomb_active

    stages = [
        ((0, 255, 0), 80, 10),
        ((255, 180, 0), 165, 10),
        ((255, 0, 0), 255, 20),
    ]

    for color, speed, delay in stages:
        with lock:
            if not bomb_active:
                return
        fade(*color, speed)
        time.sleep(delay)

# =======================
# Health bar
# =======================
def health_bar(health):
    if health <= 0:
        off()
        return

    leds = max(1, int((health / 100) * TOTAL_LEDS))
    color = [0, 255, 0] if health > 20 else [255, 0, 0]

    send_wled({
        "on": True,
        "seg": [{
            "id": 0,
            "start": 0,
            "stop": leds,
            "fx": 0,
            "col": [color]
        }]
    })

# =======================
# Test mode
# =======================
def test_mode():
    if MODE == "bomb":
        solid(255, 0, 0, 0)
        time.sleep(1)
        off()

    elif MODE == "player_status":
        solid(200, 200, 200, 0)
        time.sleep(0.6)
        off()

        fade(150, 150, 150, 120)
        time.sleep(2)
        off()

        solid(255, 0, 0, 0)
        time.sleep(0.3)
        off()

    elif MODE == "player_health":
        for hp in [100, 75, 50, 25, 10]:
            health_bar(hp)
            time.sleep(0.5)
        off()

# =======================
# CS2 handler
# =======================
@app.route("/", methods=["POST"])
def cs2_event():
    global last_health, bomb_active, current_state

    data = request.json
    if not data:
        reset_state()
        return "OK"

    round_data = data.get("round", {})
    player = data.get("player", {})
    state = player.get("state", {})
    previously = data.get("previously", {})

    # ---- Round / Match end ----
    if round_data.get("phase") == "over":
        reset_state()
        return "OK"

    # ---- Bomb mode ----
    if MODE == "bomb":
        bomb_state = round_data.get("bomb")

        if bomb_state == "planted" and not bomb_active:
            bomb_active = True
            threading.Thread(
                target=bomb_sequence, daemon=True
            ).start()

        if bomb_active and bomb_state is None:
            bomb_active = False
            prev = previously.get("round", {}).get("bomb")

            if prev == "planted":
                android(255, 120, 0)
            else:
                solid(120, 120, 120)

    # ---- Player status ----
    elif MODE == "player_status":
        flashed = state.get("flashed", 0)
        smoked = state.get("smoked", 0)
        health = state.get("health", last_health)

        if smoked > 0:
            if current_state != "smoke":
                current_state = "smoke"
                fade(150, 150, 150, 120)
            return "OK"

        if current_state == "smoke" and smoked == 0:
            off()
            current_state = "idle"

        if flashed > 0:
            if current_state != "flash":
                current_state = "flash"
                solid(190, 190, 190, 0)
            return "OK"

        if current_state == "flash" and flashed == 0:
            off()
            current_state = "idle"

        if health < last_health:
            solid(255, 0, 0, 0)
            time.sleep(0.12)
            off()

        last_health = health

    # ---- Health mode ----
    elif MODE == "player_health":
        health = state.get("health", last_health)
        if health != last_health:
            health_bar(health)
        last_health = health

    return "OK"

# =======================
# Start
# =======================
if __name__ == "__main__":
    log("CS2 WLED Controller Started")

    if TEST_MODE:
        test_mode()
        sys.exit(0)

    app.run(host="0.0.0.0", port=3000, debug=False)
