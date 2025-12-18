from flask import Flask, request
import requests, threading, time, sys, json, os, logging

# ===================== LOGGING =====================
logging.getLogger('werkzeug').setLevel(logging.ERROR)

def log(tag, msg):
    print(f"[{tag}] {msg}")

# ===================== LOAD IP =====================
def load_ip():
    if not os.path.exists("ip.json"):
        log("ERROR", "ip.json not found")
        sys.exit(1)
    try:
        with open("ip.json", "r") as f:
            return json.load(f)["wled_ip"]
    except:
        log("ERROR", "Invalid ip.json")
        sys.exit(1)

WLED_IP = load_ip()
CS2_PORT = 3000
BOMB_TIME = 40

# ===================== COLORS / SPEED =====================
COLORS = {
    "green": [0,255,0],
    "yellow": [255,180,0],
    "red": [255,0,0],
    "orange": [255,80,0],
    "gray": [80,80,80],
    "black": [0,0,0]
}

SPEED = {"green":80, "yellow":165, "red":255}

# ===================== GLOBAL =====================
app = Flask(__name__)
effects = {}
bomb_active = False
bomb_start = 0

# ===================== WLED =====================
def wled(data):
    try:
        requests.post(f"http://{WLED_IP}/json/state", json=data, timeout=0.4)
    except:
        log("WARN", "WLED not reachable")

def detect_effects():
    try:
        r = requests.get(f"http://{WLED_IP}/json/effects").json()
        for i, e in enumerate(r): effects[e.lower()] = i
        log("INFO", "WLED effects detected")
    except:
        log("ERROR", "Cannot get WLED effects")
        sys.exit(1)

def solid(color):
    wled({"on":True,"ps":-1,"pl":-1,"seg":[{"fx":effects.get("solid",0),"col":[color]}]})


def effect(name, color, speed):
    wled({"on":True,"ps":-1,"pl":-1,"seg":[{"fx":effects.get(name,0),"sx":speed,"ix":128,"col":[color]}]})

# ===================== STATES =====================
def reset_black():
    solid(COLORS["black"])

# ===================== BOMB =====================
def bomb_sequence():
    global bomb_active
    log("GAME", "Bomb planted")

    phases = [("green",0,10),("yellow",10,20),("red",20,40)]
    for name,start,end in phases:
        if not bomb_active: return
        effect("fade", COLORS[name], SPEED[name])
        while time.time() - bomb_start < end:
            if not bomb_active: return
            time.sleep(0.05)


def bomb_exploded():
    log("GAME", "Bomb exploded")
    effect("android", COLORS["orange"], 180)


def bomb_defused():
    log("GAME", "Bomb defused")
    solid(COLORS["gray"])

# ===================== CS2 =====================
@app.route('/', methods=['POST'])
def cs2():
    global bomb_active, bomb_start
    data = request.json
    if not data: return "OK"

    rnd = data.get("round", {})

    if rnd.get("bomb") == "planted" and not bomb_active:
        bomb_active = True
        bomb_start = time.time()
        threading.Thread(target=bomb_sequence, daemon=True).start()

    if rnd.get("bomb") == "exploded":
        bomb_active = False
        bomb_exploded()

    if rnd.get("bomb") == "defused":
        bomb_active = False
        bomb_defused()

    if rnd.get("phase") == "over":
        bomb_active = False
        reset_black()
        log("GAME", "Round ended")

    return "OK"

# ===================== TEST =====================
def test_mode():
    log("TEST", "Running test mode")
    for c in ["green","yellow","red"]:
        effect("fade", COLORS[c], SPEED[c])
        time.sleep(10)
    effect("android", COLORS["orange"], 180)
    time.sleep(5)
    solid(COLORS["gray"])
    time.sleep(3)
    reset_black()

# ===================== MAIN =====================
if __name__ == '__main__':
    log("INFO", f"WLED IP: {WLED_IP}")
    detect_effects()
    reset_black()

    if '--test' in sys.argv:
        test_mode()
        sys.exit(0)

    log("INFO", "Waiting for CS2...")
    app.run(host='0.0.0.0', port=CS2_PORT)