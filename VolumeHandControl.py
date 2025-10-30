import cv2
import time
import numpy as np
import HandTrackingModule as htm # has to be in the same folder
import math
import pyautogui # to control volume, simulate key presses

wCam, hCam = 640, 480 # define width and height of camera

cap = cv2.VideoCapture(0) # turns on camera 0
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

# zoom configuration
last_zoom_time = 0
cooldown = 1  # seconds between zooms
zoom_threshold_in = 40   # distance threshold to start zooming in
zoom_threshold_out = 150 # distance threshold to zoom out

detector = htm.handDetector(detectionCon=0.7) # calls the handDetector class from HandTrackingModule with a confidence of 0.7

while True:
    success, img = cap.read()
    img = detector.findHands(img) # finds hands and draws landmarks from method in HandTrackingModule
    lmList = detector.findPosition(img, draw=False) # gets the landmark list from method in HandTrackingModule, does not draw circles on landmarks
    current_time = time.time() # current time used for cooldown timing

    if len(lmList) != 0: # if the list is not empty, it will skip the print
        print(lmList[4], lmList[8]) # prints the x,y coordinates of the thumb tip and index finger tip

        x1, y1 = lmList[4][1], lmList[4][2] # thumb tip
        x2, y2 = lmList[8][1], lmList[8][2] # index finger tip

        cx, cy = (x1 + x2)//2, (y1 + y2)//2 # center point between thumb and index finger

        cv2.circle(img, (x1, y1), 5, (0, 0, 0), cv2.FILLED) # draw circle on thumb tip
        cv2.circle(img, (x2, y2), 5, (0, 0, 0), cv2.FILLED) # draw circle on index tip
        cv2.line(img, (x1, y1), (x2, y2), (0, 0, 0), 2) # draw line between thumb and index finger
        cv2.circle(img, (cx, cy), 5, (0, 0, 0), cv2.FILLED) # draw circle on center point

        length = math.hypot(x2 - x1, y2 - y1) # calculate distance between thumb and index finger
        print(length)

        # if distance is less than zoom_threshold_in pixels, trigger zoom in
        if length < zoom_threshold_in and (current_time - last_zoom_time > cooldown):
            pyautogui.hotkey('ctrl', '+') # simulate ctrl + '+' to zoom in browser/app
            cv2.circle(img, (cx, cy), 10, (255, 0, 0), cv2.FILLED) # change center point circle to blue when zooming in
            print("Zoom In")
            last_zoom_time = current_time

        # if distance is greater than zoom_threshold_out pixels, trigger zoom out
        elif length > zoom_threshold_out and (current_time - last_zoom_time > cooldown):
            pyautogui.hotkey('ctrl', '-') # simulate ctrl + '-' to zoom out browser/app
            cv2.circle(img, (cx, cy), 10, (0, 0, 255), cv2.FILLED) # change center point circle to red when zooming out
            print("Zoom Out")
            last_zoom_time = current_time

    # calculate frames per second
    cTime = time.time()
    fps = 1 / (cTime - pTime) if pTime != 0 else 0
    pTime = cTime

    # display FPS counter
    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 2)

    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == 27: # press ESC to exit
        break

cap.release()
cv2.destroyAllWindows()
