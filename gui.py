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
import customtkinter as ctk
import subprocess
import json
import os
import sys
import shutil

# ======================
# App setup
# ======================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

APP_WIDTH = 900
APP_HEIGHT = 494

app = ctk.CTk()
app.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
app.title("CS2 WLED GUI")
app.resizable(True, True)

# ======================
# Paths (FIXED)
# ======================
BASE_DIR = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) \
    else os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
EXE_FILE = os.path.join(BASE_DIR, "cs2_wled.exe")
PY_FILE = os.path.join(BASE_DIR, "cs2_wled.py")
ICON_FILE = os.path.join(BASE_DIR, "icon.ico")

if os.path.exists(ICON_FILE):
    app.iconbitmap(ICON_FILE)

# ======================
# Config
# ======================
DEFAULT_CONFIG = {
    "wled_ip": "",
    "bomb_status": 1,
    "player_status": 0,
    "player_health": 0
}

def ensure_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)

def load_config():
    ensure_config()
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

config = load_config()

# ======================
# Python finder
# ======================
def find_python():
    for cmd in ("python", "python3"):
        if shutil.which(cmd):
            return cmd
    return None

# ======================
# Logger (CLEAN)
# ======================
def log(text):
    log_box.configure(state="normal")
    log_box.insert("end", f"{text}\n")
    log_box.see("end")
    log_box.configure(state="disabled")

# ======================
# Runtime state
# ======================
running = False
process = None

def update_status():
    status_label.configure(
        text="Running" if running else "Stopped",
        text_color="#00ff88" if running else "#ff4444"
    )

def update_mode_buttons():
    state = "disabled" if running else "normal"
    for btn in mode_buttons.values():
        btn.configure(state=state)

# ======================
# Save config (SAFE)
# ======================
def save_config():
    data = {
        "wled_ip": ip_entry.get().strip(),
        "bomb_status": 1 if selected_mode.get() == "bomb" else 0,
        "player_status": 1 if selected_mode.get() == "player" else 0,
        "player_health": 1 if selected_mode.get() == "health" else 0
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# ======================
# Start / Stop (FIXED)
# ======================
def start_app(test=False):
    global process, running

    if running:
        return

    save_config()

    if os.path.exists(EXE_FILE):
        cmd = [EXE_FILE]
    elif os.path.exists(PY_FILE):
        python = find_python()
        if not python:
            log("Python not found")
            return
        cmd = [python, PY_FILE]
    else:
        log("cs2_wled not found")
        return

    if test:
        cmd.append("--test")

    try:
        process = subprocess.Popen(
            cmd,
            cwd=BASE_DIR,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        )
        running = not test
        log("Test mode started" if test else "CS2 WLED started")
    except:
        log("Failed to start")
        return

    update_status()
    update_mode_buttons()
    toggle_btn.configure(text="Stop")

def stop_app():
    global running, process

    if process:
        try:
            process.terminate()
        except:
            pass

    process = None
    running = False

    log("Stopped")
    update_status()
    update_mode_buttons()
    toggle_btn.configure(text="Start")

def toggle_app():
    if running:
        stop_app()
    else:
        start_app()

def test_wled():
    start_app(test=True)

# ======================
# Process monitor (CRITICAL FIX)
# ======================
def monitor_process():
    global running, process

    if process and process.poll() is not None:
        process = None
        running = False
        update_status()
        update_mode_buttons()
        toggle_btn.configure(text="Start")

    app.after(500, monitor_process)

# ======================
# Mode
# ======================
selected_mode = ctk.StringVar()

if config.get("bomb_status"):
    selected_mode.set("bomb")
elif config.get("player_status"):
    selected_mode.set("player")
else:
    selected_mode.set("health")

def select_mode(mode):
    if running:
        return
    selected_mode.set(mode)
    for m, btn in mode_buttons.items():
        btn.configure(fg_color="#7b3fe4" if m == mode else "#2b2b2b")
    save_config()

# ======================
# Layout
# ======================
main = ctk.CTkFrame(app, corner_radius=20)
main.pack(expand=True, fill="both", padx=15, pady=15)
main.grid_columnconfigure(0, weight=3)
main.grid_columnconfigure(1, weight=2)

# LEFT
left = ctk.CTkFrame(main, corner_radius=18)
left.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)

ctk.CTkLabel(left, text="MODE SELECT",
             font=ctk.CTkFont(size=22, weight="bold")).pack(pady=20)

mode_buttons = {}

def add_mode(text, mode):
    btn = ctk.CTkButton(
        left, text=text,
        width=220, height=85,
        corner_radius=20,
        fg_color="#2b2b2b",
        hover_color="#5b2bbf",
        command=lambda: select_mode(mode)
    )
    btn.pack(pady=12)
    mode_buttons[mode] = btn

add_mode("Bomb Status", "bomb")
add_mode("Player Status", "player")
add_mode("Player Health", "health")

# RIGHT
right = ctk.CTkFrame(main, corner_radius=18)
right.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)

status_label = ctk.CTkLabel(right, font=ctk.CTkFont(size=18, weight="bold"))
status_label.pack(pady=(15, 5))
update_status()

toggle_btn = ctk.CTkButton(
    right, text="Start",
    width=260, height=45,
    corner_radius=18,
    fg_color="#7b3fe4",
    hover_color="#9a63ff",
    command=toggle_app
)
toggle_btn.pack(pady=10)

ctk.CTkButton(
    right, text="Test WLED",
    width=260, height=40,
    corner_radius=16,
    fg_color="#444",
    hover_color="#666",
    command=test_wled
).pack(pady=(0, 15))

ctk.CTkLabel(right, text="WLED IP").pack(anchor="w", padx=30)

ip_entry = ctk.CTkEntry(right, width=235, height=32, corner_radius=10)
ip_entry.insert(0, config.get("wled_ip", ""))
ip_entry.pack(pady=(5, 10))

log_box = ctk.CTkTextbox(right, height=140, corner_radius=12)
log_box.pack(fill="x", padx=20, pady=10)
log_box.configure(state="disabled")

log("GUI ready")

monitor_process()
app.mainloop()
