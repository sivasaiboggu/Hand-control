# Hand Control

Hand Control is a webcam-based gesture control project built with MediaPipe, OpenCV, and PyAutoGUI. It lets you control the mouse and common system actions using right-hand and left-hand gestures. 

## Features

- Move the cursor with your right index finger
- Left click with a right-hand pinch
- Right click with a right-hand middle-finger pinch
- Double click by holding an open right hand
- Scroll up and down with right-hand gestures
- Toggle mute by holding a fist
- Increase and decrease volume with left-hand gestures
- On-screen overlay for current gesture, action, and FPS

## Requirements

- Python 3.10+ recommended
- Webcam
- Packages:
  - `opencv-python`
  - `mediapipe`
  - `pyautogui`
  - `numpy`

## Installation

If you are using the project virtual environment:

```powershell
cd C:\vscodefolder\hand_control
.\venv\Scripts\Activate.ps1
```

Install dependencies if needed:

```powershell
pip install opencv-python mediapipe pyautogui numpy
```

## Run

```powershell
python main.py
```

## Controls

### Right Hand

- Index finger only: move cursor
- Pinch index finger and thumb: left click
- Open all five fingers and hold: double click
- Pinch middle finger and thumb: right click
- Thumb + index: scroll up
- Thumb only: scroll down
- Fist and hold: mute toggle

### Left Hand

- Open palm: volume up
- Fist: volume down

## How It Works

- `main.py` reads webcam frames and sends them through MediaPipe Hands
- `utils.py` classifies the hand pose into a gesture string
- `controller.py` performs the corresponding mouse or system action
- Cursor movement is smoothed before it is sent to PyAutoGUI

## Notes

- Press `Q` to quit the app
- Cursor movement and click timing include cooldowns to reduce accidental actions
- If a gesture feels too sensitive or too slow, tune the thresholds in `utils.py` or `controller.py`

## Project Files

- `main.py` - application loop and video display
- `controller.py` - cursor, click, scroll, mute, and volume actions
- `utils.py` - hand landmark feature and gesture detection helpers
- `.gitignore` - ignored files and folders for Git
