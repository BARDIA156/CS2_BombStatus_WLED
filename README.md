# CS2 WLED Sync

Sync your WLED RGB LEDs with Counter-Strike 2 bomb timer using **real WLED Fade effects**.

## ✨ Features
- Real WLED Fade (no simulation)
- Accurate 40s bomb timer
- Green → Yellow → Red phases
- Bomb exploded → Android effect (orange)
- Bomb defused → Solid gray
- Round end → Solid black
- Test mode (no CS2 needed)
- IP configurable via ip.json
- EXE build support

## 🧪 Test Mode
```bash
python cs2_wled.py --test
```

## 🎮 CS2 Config
Create `gamestate_integration_wled.cfg`:
```
"uri" "http://127.0.0.1:3000"
```

## 🛠 Build EXE
Double-click:
```
Python_to_EXE.bat
```

## 📡 Requirements
- Python 3.10+
- WLED device
- CS2
