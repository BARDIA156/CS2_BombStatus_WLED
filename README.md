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
{
  "uri" "http://127.0.0.1:3000"
  "timeout" "5.0"
  "buffer"  "0.1"
  "throttle" "0.1"
  "heartbeat" "30.0"

  "data"
  {
    "provider"            "1"
    "map"                 "1"
    "round"               "1"
    "player_id"           "1"
    "player_state"        "1"
    "player_match_stats"  "1"
    "bomb"                "1"
    "allplayers_id"       "1"
    "allplayers_state"    "1"
    "allplayers_match_stats" "1"
  }
}

```
on `YourDrive:\SteamLibrary\steamapps\common\Counter-Strike Global Offensive\game\csgo\cfg`

## 🛠 Build EXE
Double-click:
```
Python_to_EXE.bat
```
## 🛡️ Firewall Settings For EXE !!Importent . If YOU Don't Do It The App Dosen't Work!!
```
Press the Windows Key and type "Windows Defender Firewall", then open Windows Defender Firewall with Advanced Security.
In the left pane, click on Outbound Rules.
In the right pane, click on New Rule....
Select Port and click Next.
Select TCP.
Select Specific remote ports and enter 3000. Click Next.
Select Allow the connection and click Next.
Keep all profiles (Domain, Private, Public) checked and click Next.
Give the rule a name (e.g., "WLED_CS2") and click Finish.
```

## 📡 Requirements
- Python 3.10+
- WLED device
- CS2
- flask
- requests




