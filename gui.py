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
import json
import subprocess
import os
import sys

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
# Paths (EXE safe)
# ======================
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
    EXEC_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    EXEC_DIR = BASE_DIR

CONFIG_FILE = os.path.join(EXEC_DIR, "config.json")
CS2_FILE = os.path.join(EXEC_DIR, "cs2_wled.py")
ICON_FILE = os.path.join(EXEC_DIR, "icon.ico")

if os.path.exists(ICON_FILE):
    app.iconbitmap(ICON_FILE)

# ======================
# Globals
# ======================
running = False
cs2_process = None
ip_entry = None

# ======================
# Load config
# ======================
def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {
            "wled_ip": "192.168.1.100",
            "bomb_status": 1,
            "player_status": 0,
            "player_health": 0
        }
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

config = load_config()

# ======================
# Save config
# ======================
def save_config():
    if ip_entry is None:
        return

    mode = selected_mode.get()

    data = {
        "wled_ip": ip_entry.get().strip(),
        "bomb_status": 1 if mode == "bomb" else 0,
        "player_status": 1 if mode == "player" else 0,
        "player_health": 1 if mode == "health" else 0
    }

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    log("Config saved")

# ======================
# Logger
# ======================
def log(text):
    log_box.configure(state="normal")
    log_box.insert("end", text + "\n")
    log_box.see("end")
    log_box.configure(state="disabled")

# ======================
# Status label
# ======================
def update_status():
    if running:
        status_label.configure(text="App is Running", text_color="#00ff88")
    else:
        status_label.configure(text="App is Stopped", text_color="#ff4444")

# ======================
# Start / Stop
# ======================
def toggle_app():
    global running, cs2_process
    save_config()

    if not running:
        try:
            cs2_process = subprocess.Popen(
                [sys.executable, CS2_FILE],
                cwd=EXEC_DIR,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            running = True
            toggle_btn.configure(text="Stop")
            log("CS2 WLED started")
        except Exception as e:
            log(f"Start failed: {e}")
    else:
        if cs2_process:
            cs2_process.terminate()
            cs2_process = None

        running = False
        toggle_btn.configure(text="Start")
        log("CS2 WLED stopped")

    update_status()

# ======================
# Test WLED
# ======================
def test_wled():
    save_config()
    try:
        subprocess.Popen(
            [sys.executable, CS2_FILE, "--test"],
            cwd=EXEC_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        log("Test mode started")
    except Exception as e:
        log(f"Test failed: {e}")

# ======================
# Mode selection
# ======================
selected_mode = ctk.StringVar()

if config.get("bomb_status") == 1:
    selected_mode.set("bomb")
elif config.get("player_status") == 1:
    selected_mode.set("player")
else:
    selected_mode.set("health")

def select_mode(mode):
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

# ======================
# LEFT
# ======================
left = ctk.CTkFrame(main, corner_radius=18)
left.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)

ctk.CTkLabel(
    left, text="MODE SELECT",
    font=ctk.CTkFont(size=22, weight="bold")
).pack(pady=(20, 10))

mode_buttons = {}

def create_mode(text, mode):
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

create_mode("Bomb Status", "bomb")
create_mode("Player Status", "player")
create_mode("Player Health", "health")

select_mode(selected_mode.get())

# ======================
# RIGHT
# ======================
right = ctk.CTkFrame(main, corner_radius=18)
right.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)

status_label = ctk.CTkLabel(
    right, font=ctk.CTkFont(size=18, weight="bold")
)
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
ip_entry.insert(0, config.get("wled_ip", "192.168.1.100"))
ip_entry.pack(pady=(5, 10))

log_box = ctk.CTkTextbox(right, height=140, corner_radius=12)
log_box.pack(fill="x", padx=20, pady=10)
log_box.configure(state="disabled")

log("GUI ready")
app.mainloop()