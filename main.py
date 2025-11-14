# main.py
"""
Main application file for hand gesture control
"""
import cv2
import mediapipe as mp
import time
import pyautogui

from gestures import (
    fingers_up, is_fist, is_open_palm, 
    is_hang_loose, is_rock_roll, detect_pinch
)
from actions import open_myutep, open_spotify, change_volume
from mouse_smoother import MouseController
import config


# Disable PyAutoGUI failsafe
pyautogui.FAILSAFE = False


def main():
    """Main application loop"""
    
    # Initialize camera
    cap = cv2.VideoCapture(config.CAMERA_INDEX)

    # Initialize MediaPipe
    mpHands = mp.solutions.hands
    hands = mpHands.Hands(
        max_num_hands=config.MAX_HANDS,
        model_complexity=config.MODEL_COMPLEXITY,
        min_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
        min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE
    )
    mpDraw = mp.solutions.drawing_utils

    # Initialize mouse controller
    screen_w, screen_h = pyautogui.size()
    mouse_controller = MouseController(screen_w, screen_h, config.EDGE_DAMPENING_MARGIN)

    # Timing variables
    pTime = 0
    last_hang_time = 0
    last_rock_time = 0
    last_vol_time = 0
    last_pinch_time = 0

    # Drag state
    dragging = False

    print("Starting hand gesture control...")
    print("Press ESC to exit")

    while True:
        success, img = cap.read()
        if not success:
            continue

        img = cv2.flip(img, 1)
        h, w, c = img.shape

        # Process with MediaPipe
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)

        lmList = []
        gesture_label = "NONE"
        now = time.time()

        # Extract hand landmarks
        if results.multi_hand_landmarks:
            handLms = results.multi_hand_landmarks[0]
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

            for id, lm in enumerate(handLms.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])

        # Process gestures if hand detected
        if len(lmList) != 0:
            fingers = fingers_up(lmList)

            # Gesture: Hang Loose → Open myUTEP
            if is_hang_loose(fingers):
                gesture_label = "PICKS UP!"
                if now - last_hang_time > config.HANG_COOLDOWN:
                    open_myutep()
                    last_hang_time = now

            # Gesture: Rock On → Open Spotify
            elif is_rock_roll(fingers):
                gesture_label = "ROCK ON"
                if now - last_rock_time > config.ROCK_COOLDOWN:
                    open_spotify()
                    last_rock_time = now

            # Gesture: Open Palm → Volume Up
            elif is_open_palm(fingers):
                gesture_label = "VOLUME UP"
                if now - last_vol_time > config.VOLUME_COOLDOWN:
                    change_volume("UP")
                    last_vol_time = now

            # Gesture: Fist → Volume Down
            elif is_fist(fingers):
                gesture_label = "VOLUME DOWN"
                if now - last_vol_time > config.VOLUME_COOLDOWN:
                    change_volume("DOWN")
                    last_vol_time = now

            # Mouse control with index finger
            ix, iy = lmList[8][1], lmList[8][2]
            mouse_controller.process_movement(ix, iy, w, h)

            # Pinch detection for clicking
            pinch_distance, (x1, y1), (x2, y2) = detect_pinch(lmList)

            # Draw pinch indicator
            if pinch_distance < config.RELEASE_THRESHOLD:
                color = (0, 255, 0) if pinch_distance < config.PINCH_THRESHOLD else (0, 255, 255)
                cv2.line(img, (x1, y1), (x2, y2), color, 3)
                cv2.circle(img, (x1, y1), 10, color, cv2.FILLED)
                cv2.circle(img, (x2, y2), 10, color, cv2.FILLED)

            # Start drag/click
            if (pinch_distance < config.PINCH_THRESHOLD and 
                not dragging and 
                now - last_pinch_time > config.PINCH_COOLDOWN):
                pyautogui.mouseDown()
                dragging = True
                last_pinch_time = now
                gesture_label = "PINCH (DRAG)"

            # Release drag
            elif pinch_distance > config.RELEASE_THRESHOLD and dragging:
                pyautogui.mouseUp()
                dragging = False
                gesture_label = "RELEASE"

        # Display info
        if config.DISPLAY_FPS:
            cTime = time.time()
            fps = 1 / (cTime - pTime) if pTime else 0
            pTime = cTime
            cv2.putText(img, f'FPS: {int(fps)}', (10, 40), 
                       cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)

        if config.DISPLAY_GESTURE:
            cv2.putText(img, f'Gesture: {gesture_label}', (10, 80), 
                       cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)

        cv2.imshow("Hand Gesture Control", img)

        # Exit on ESC
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Exiting...")


if __name__ == "__main__":
    main()