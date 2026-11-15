import pyautogui
import time
from collections import deque
import numpy as np

SCREEN_W, SCREEN_H = pyautogui.size()
pyautogui.FAILSAFE = False
pyautogui.PAUSE    = 0.01

class Controller:
    def __init__(self):
        self.smooth_buffer       = deque(maxlen=6)

        # Click
        self.last_click_time     = 0
        self.click_cooldown      = 0.8

        # Double click
        self.double_click_start  = None
        self.double_click_hold   = 1.0
        self.double_click_done   = False

        # Scroll — faster now
        self.scroll_cooldown     = 0.08  # faster than before
        self.last_scroll_time    = 0
        self.scroll_amount       = 6     # doubled from 3

        # Mute — hold fist
        self.is_muted            = False
        self.mute_hold_start     = None
        self.mute_hold_time      = 1.0   # hold 1 second to mute
        self.mute_done           = False
        self.last_mute_time      = 0
        self.mute_cooldown       = 1.5

        # Volume — hold based
        self.last_volume_time    = 0
        self.volume_cooldown     = 0.15  # faster volume change

        self.last_gesture        = "NONE"

    def smooth_cursor(self, x, y):
        screen_x = int(np.interp(x, [100, 540], [0, SCREEN_W]))
        screen_y = int(np.interp(y, [50,  430], [0, SCREEN_H]))
        screen_x = max(0, min(screen_x, SCREEN_W - 1))
        screen_y = max(0, min(screen_y, SCREEN_H - 1))
        self.smooth_buffer.append((screen_x, screen_y))
        avg_x = int(np.mean([p[0] for p in self.smooth_buffer]))
        avg_y = int(np.mean([p[1] for p in self.smooth_buffer]))
        return avg_x, avg_y

    def move_cursor(self, x, y):
        smooth_x, smooth_y = self.smooth_cursor(x, y)
        pyautogui.moveTo(smooth_x, smooth_y, duration=0.03)
        return smooth_x, smooth_y

    def left_click(self):
        now = time.time()
        if now - self.last_click_time < self.click_cooldown:
            return "COOLDOWN"
        pyautogui.click()
        self.last_click_time = now
        print("🖱️  Left Click!")
        return "LEFT_CLICK"

    def double_click(self, gesture_start_time):
        now  = time.time()
        held = now - gesture_start_time
        progress = min(int(held / self.double_click_hold * 10), 10)
        bar      = "█" * progress + "░" * (10 - progress)
        print(f"\r⏳ Hold: [{bar}]", end="")
        if held >= self.double_click_hold and not self.double_click_done:
            pyautogui.doubleClick()
            self.double_click_done = True
            print("\n🖱️  Double Click!")
            return "DOUBLE_CLICK"
        return f"HOLDING {held:.1f}s"

    def right_click(self):
        now = time.time()
        if now - self.last_click_time < self.click_cooldown:
            return "COOLDOWN"
        pyautogui.rightClick()
        self.last_click_time = now
        print("🖱️  Right Click!")
        return "RIGHT_CLICK"

    def scroll_up(self):
        now = time.time()
        if now - self.last_scroll_time < self.scroll_cooldown:
            return "COOLDOWN"
        pyautogui.scroll(self.scroll_amount)
        self.last_scroll_time = now
        return "SCROLL_UP ⬆️"

    def scroll_down(self):
        now = time.time()
        if now - self.last_scroll_time < self.scroll_cooldown:
            return "COOLDOWN"
        pyautogui.scroll(-self.scroll_amount)
        self.last_scroll_time = now
        return "SCROLL_DOWN ⬇️"

    def mute(self):
        """Hold fist for 1 second to toggle mute"""
        now = time.time()

        if self.mute_hold_start is None:
            self.mute_hold_start = now
            self.mute_done       = False

        held     = now - self.mute_hold_start
        progress = min(int(held / self.mute_hold_time * 10), 10)
        bar      = "█" * progress + "░" * (10 - progress)
        print(f"\r✊ Hold to mute: [{bar}]", end="")

        if held >= self.mute_hold_time and not self.mute_done:
            if now - self.last_mute_time > self.mute_cooldown:
                pyautogui.press('volumemute')
                self.is_muted    = not self.is_muted
                self.mute_done   = True
                self.last_mute_time = now
                status = "MUTED 🔇" if self.is_muted else "UNMUTED 🔊"
                print(f"\n{status}")
                return status

        return f"MUTE HOLD {held:.1f}s"

    def reset_mute(self):
        self.mute_hold_start = None
        self.mute_done       = False

    def volume_up(self):
        now = time.time()
        if now - self.last_volume_time < self.volume_cooldown:
            return "VOL_COOLDOWN"
        pyautogui.press('volumeup')
        self.last_volume_time = now
        print("🔊 Volume Up")
        return "VOLUME_UP"

    def volume_down(self):
        now = time.time()
        if now - self.last_volume_time < self.volume_cooldown:
            return "VOL_COOLDOWN"
        pyautogui.press('volumedown')
        self.last_volume_time = now
        print("🔉 Volume Down")
        return "VOLUME_DOWN"

    def execute_right(self, gesture, landmark_x, landmark_y):
        action = "NONE"

        # Reset double click
        if gesture != "DOUBLE_CLICK":
            self.double_click_start = None
            self.double_click_done  = False

        if gesture == "DOUBLE_CLICK" and self.double_click_start is None:
            self.double_click_start = time.time()

        # Reset mute hold
        if gesture != "MUTE":
            self.reset_mute()

        if gesture == "MOVE":
            cx, cy = self.move_cursor(landmark_x, landmark_y)
            action = f"MOVE ({cx},{cy})"

        elif gesture == "LEFT_CLICK":
            action = self.left_click()

        elif gesture == "RIGHT_CLICK":
            action = self.right_click()

        elif gesture == "DOUBLE_CLICK":
            action = self.double_click(self.double_click_start)

        elif gesture == "SCROLL_UP":
            action = self.scroll_up()

        elif gesture == "SCROLL_DOWN":
            action = self.scroll_down()

        elif gesture == "SCROLL_READY":
            action = "SCROLL_READY"

        elif gesture == "MUTE":
            action = self.mute()

        self.last_gesture = gesture
        return action

    def execute_left(self, gesture):
        """Left hand — volume only"""
        if gesture == "VOLUME_UP":
            return self.volume_up()
        elif gesture == "VOLUME_DOWN":
            return self.volume_down()
        return "NONE"