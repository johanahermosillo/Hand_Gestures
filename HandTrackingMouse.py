# AirMouse.py
import pyautogui
import numpy as np
import math
import time

# AirMouse Controller Class
class AirMouse:
    def __init__(self, screen_smooth=5, move_threshold=5):
        self.screen_w, self.screen_h = pyautogui.size()
        self.plocX, self.plocY = 0, 0  # previous cursor location
        self.smoothening = screen_smooth
        self.move_threshold = move_threshold
        self.last_click_time = 0
        self.click_cooldown = 0.5  # seconds

    def controlMouse(self, lmList, wCam, hCam):
        """
        Takes landmark list from hand detector, maps the index finger to the screen,
        and allows pinch-click gesture.
        """
        if len(lmList) == 0:
            return

        # Index (8) and Thumb (4)
        x1, y1 = lmList[8][1], lmList[8][2]
        x2, y2 = lmList[4][1], lmList[4][2]
        distance = math.hypot(x2 - x1, y2 - y1)

        # Map hand coordinates to screen coordinates (inverted horizontally)
        screenX = np.interp(wCam - x1, (100, wCam - 100), (0, self.screen_w))
        screenY = np.interp(y1, (100, hCam - 100), (0, self.screen_h))

        # --- Movement smoothing ---
        clocX = self.plocX + (screenX - self.plocX) / self.smoothening
        clocY = self.plocY + (screenY - self.plocY) / self.smoothening

        # --- Apply deadzone to prevent micro-movements ---
        if abs(clocX - self.plocX) > self.move_threshold or abs(clocY - self.plocY) > self.move_threshold:
            pyautogui.moveTo(clocX, clocY)
            self.plocX, self.plocY = clocX, clocY

        # --- Click gesture (pinch) ---
        current_time = time.time()
        if distance < 40 and (current_time - self.last_click_time) > self.click_cooldown:
            pyautogui.click()
            self.last_click_time = current_time
