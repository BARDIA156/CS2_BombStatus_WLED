from flask import Flask, request
import requests
import threading
import time
import json
import sys

# =======================
# Arguments
# =======================
TEST_MODE = "--test" in sys.argv
TOTAL_LEDS = 105   # 🔴 Put your real LED Length

# =======================
# Load config
# =======================
try:
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
except:
    print("[ERROR] Cannot load config.json")
    sys.exit(1)

WLED_IP = config.get("wled_ip")

ENABLE_BOMB = config.get("bomb_status", 0)
ENABLE_PLAYER = config.get("player_status", 0)
ENABLE_HEALTH = config.get("player_health", 0)

# =======================
# Validate mode (ONLY ONE)
# =======================
modes = [ENABLE_BOMB, ENABLE_PLAYER, ENABLE_HEALTH]

if modes.count(1) != 1:
    print("[ERROR] Exactly ONE mode must be enabled in config.json")
    print("bomb_status OR player_status OR player_health")
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
def log(msg): print(f"[STATUS] {msg}")

# =======================
# State
# =======================
last_health = 100
bomb_active = False
current_state = "idle"

# =======================
# WLED helpers
# =======================
def send_wled(data):
    try:
        requests.post(
            f"http://{WLED_IP}/json/state",
            json=data,
            timeout=0.3
        )
    except:
        pass

def solid(r, g, b, transition=7):
    send_wled({
        "on": True,
        "transition": transition,
        "seg": [{
            "fx": 0,
            "col": [[r, g, b]]
        }]
    })

def fade(r, g, b, speed):
    send_wled({
        "on": True,
        "seg": [{
            "fx": 2,      # Native WLED fade
            "sx": speed,
            "ix": speed,
            "col": [[r, g, b]]
        }]
    })

def android(r, g, b):
    send_wled({
        "on": True,
        "seg": [{
            "fx": 74,
            "col": [[r, g, b]]
        }]
    })

def off():
    send_wled({
        "on": False,
        "transition": 10
    })

# =======================
# Bomb timing
# =======================
def bomb_sequence():
    global bomb_active

    log("Bomb planted")
    fade(0, 255, 0, 80)        # Green – slow
    time.sleep(10)

    if not bomb_active:
        return

    fade(255, 180, 0, 165)    # Yellow – medium
    time.sleep(10)

    if not bomb_active:
        return

    fade(255, 0, 0, 255)      # Red – fast
    time.sleep(20)

# =======================
# Health Bar
# =======================
def health_bar(health):
    if health <= 0:
        off()
        return

    active_leds = int((health / 100) * TOTAL_LEDS)
    active_leds = max(1, active_leds)

    # Color selection
    if health > 20:
        color = [0, 255, 0]      # Green
    else:
        color = [255, 0, 0]      # Red

    send_wled({
        "on": True,
        "seg": [{
            "id": 0,
            "start": 0,
            "stop": active_leds,
            "fx": 0,
            "col": [color]
        }]
    })


# =======================
# Test mode
# =======================
def run_test():
    log("Running test mode")

    if MODE == "bomb":
        bomb_sequence()
        time.sleep(1)
        log("Bomb exploded (test)")
        android(255, 120, 0)

    elif MODE == "player_status":
        log("Flashbang test")
        solid(190, 190, 190, 0)
        time.sleep(2)
        solid(0, 0, 0, 15)

        log("Damage test")
        solid(255, 0, 0, 0)
        time.sleep(0.2)
        solid(0, 0, 0, 15)

    elif MODE == "player_health":
        log("Health test")
        solid(0, 255, 0)
        time.sleep(2)
        solid(255, 0, 0)
        time.sleep(2)
        off()

    log("Test finished")
    sys.exit(0)

# =======================
# CS2 handler
# =======================
@app.route("/", methods=["POST"])
def cs2_event():
    global last_health, bomb_active, current_state

    data = request.json
    if not data:
        return "OK"

    round_data = data.get("round", {})
    player = data.get("player", {})
    state = player.get("state", {})

    # ---- Bomb mode ----
    if MODE == "bomb":
        bomb_state = round_data.get("bomb")

        if bomb_state == "planted" and not bomb_active:
            bomb_active = True
            threading.Thread(
                target=bomb_sequence,
                daemon=True
            ).start()

        if bomb_active and round_data.get("phase") == "over":
            bomb_active = False

            if bomb_state == "exploded":
                log("Bomb exploded")
                android(255, 120, 0)
            else:
                log("Bomb defused")
                solid(120, 120, 120)

    # ---- Player status ----
    elif MODE == "player_status":
        flashed = state.get("flashed", 0)
        health = state.get("health", last_health)

        if flashed > 0:
            if current_state != "flash":
                log("Player flashed")
                current_state = "flash"
                solid(190, 190, 190, 0)
            return "OK"

        if current_state == "flash" and flashed == 0:
            solid(0, 0, 0, 20)
            current_state = "idle"

        if health < last_health:
            log("Player damaged")
            solid(255, 0, 0, 0)
            time.sleep(0.15)
            solid(0, 0, 0, 15)

        last_health = health

    # ---- Player health ----
    elif MODE == "player_health":
        health = state.get("health", 0)
        health_bar(health)

    # ---- Round end ----
    if round_data.get("phase") == "over":
        log("Round ended")
        off()

    return "OK"

# =======================
# Start
# =======================
if __name__ == "__main__":
    log("CS2 → WLED controller started")
    log(f"Active mode: {MODE}")
    log(f"WLED IP: {WLED_IP}")

    if TEST_MODE:
        run_test()

    app.run(host="0.0.0.0", port=3000, debug=False)

