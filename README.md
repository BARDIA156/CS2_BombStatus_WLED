# CS2 WLED Sync

Sync your WLED RGB LEDs with Counter-Strike 2 bomb timer using **real WLED Fade effects**.

## ✨ Features
- Real WLED Fade (no simulation)
- Accurate bomb timer
- Green → Yellow → Red phases
- Bomb exploded → Colortwinkles Effect
- Bomb defused → Solid gray
- Round end → Solid black
- Test mode (no CS2 needed)
- configurable via config.json
- EXE build support
- 3 Options : Player Health with real Bar Simulation , Player Status with Flashbang Simulation and Damage , Bomb Status with Better Explotion Effect.

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

## 📝 Configuration `config.json`:
```
For Setting The Mode :
0 = Off , 1 = On
⚠️ Only One Option Can Be Choose , If You Use More Than One Option , The App Simply NOT Gonna Work ⚠️

For "wled_ip" Put Your Real Ip. Mine is just Example
```

## 🛠 Build EXE
Double-click:
```
Python_to_EXE.bat
```
After That You Need to put out the app from "dist" Folder. if you don't , the app dosen't gonna work

## 🛡️ Firewall Settings For EXE ⚠️ Importent . If YOU Don't Do It The App Dosen't Work ⚠️
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

[Youtube Video Test](google.com)







