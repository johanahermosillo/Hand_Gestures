import cv2
import time
import numpy as np
import HandTrackingModule as htm # has to be in the same folder
import math
import subprocess
import platform

wCam, hCam = 640, 480 # define width and height of camera

cap = cv2.VideoCapture(0) # turns on camera 0
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

# volume configuration
minDist = 50   # minimum distance between thumb and index finger (maps to 0% volume)
maxDist = 300  # maximum distance between thumb and index finger (maps to 100% volume)
volBar = 400   # initial volume bar height
volPer = 0     # initial volume percentage
vol = 0        # initial volume value

detector = htm.handDetector(detectionCon=0.7) # calls the handDetector class from HandTrackingModule with a confidence of 0.7

def set_volume_macos(volume_percent):
    """Set system volume on macOS using osascript"""
    # Volume range is 0-100, but osascript uses 0-7 scale (0-100%)
    # We'll use the set volume command with output volume
    volume_value = int(volume_percent)
    script = f'set volume output volume {volume_value}'
    subprocess.run(['osascript', '-e', script], capture_output=True)

def set_volume_windows(volume_percent):
    """Set system volume on Windows using nircmd or PowerShell"""
    # Using PowerShell to set volume
    volume_value = int(volume_percent)
    ps_command = f'(New-Object -comObject wscript.shell).SendKeys([char]175)'
    # Alternative: use pycaw library if available
    # For now, we'll use a simple approach
    try:
        import ctypes
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(volume_percent / 100.0, None)
    except:
        # Fallback: use keyboard simulation
        import pyautogui
        # This is a simplified approach - may need pycaw for proper control
        pass

def set_volume_linux(volume_percent):
    """Set system volume on Linux using amixer or pactl"""
    volume_value = int(volume_percent)
    try:
        # Try using amixer (ALSA)
        subprocess.run(['amixer', 'set', 'Master', f'{volume_value}%'], capture_output=True)
    except:
        try:
            # Try using pactl (PulseAudio)
            subprocess.run(['pactl', 'set-sink-volume', '@DEFAULT_SINK@', f'{volume_value}%'], capture_output=True)
        except:
            pass

def set_volume(volume_percent):
    """Set system volume based on the operating system"""
    system = platform.system()
    if system == 'Darwin':  # macOS
        set_volume_macos(volume_percent)
    elif system == 'Windows':
        set_volume_windows(volume_percent)
    elif system == 'Linux':
        set_volume_linux(volume_percent)

while True:
    success, img = cap.read()
    if not success:
        continue
    
    img = detector.findHands(img) # finds hands and draws landmarks from method in HandTrackingModule
    lmList = detector.findPosition(img, draw=False) # gets the landmark list from method in HandTrackingModule, does not draw circles on landmarks

    if len(lmList) != 0: # if the list is not empty
        # Get thumb tip (landmark 4) and index finger tip (landmark 8)
        x1, y1 = lmList[4][1], lmList[4][2] # thumb tip
        x2, y2 = lmList[8][1], lmList[8][2] # index finger tip

        cx, cy = (x1 + x2)//2, (y1 + y2)//2 # center point between thumb and index finger

        # Draw circles and line to visualize the gesture
        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED) # draw circle on thumb tip
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED) # draw circle on index tip
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3) # draw line between thumb and index finger
        cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED) # draw circle on center point

        # Calculate distance between thumb and index finger
        length = math.hypot(x2 - x1, y2 - y1)
        
        # Map distance to volume percentage (0-100%)
        # Clamp the distance to minDist-maxDist range
        length = np.interp(length, [minDist, maxDist], [0, 100])
        volPer = int(length)
        
        # Map volume percentage to volume bar height (400px = 0%, 150px = 100%)
        volBar = np.interp(length, [0, 100], [400, 150])
        vol = int(length)

        # Set system volume
        set_volume(volPer)

        # Visual feedback - change color based on volume level
        if volPer < 50:
            color = (0, 0, 255)  # Red for low volume
        else:
            color = (0, 255, 0)  # Green for high volume
        
        cv2.circle(img, (cx, cy), 10, color, cv2.FILLED)

    # Draw volume bar background
    cv2.rectangle(img, (50, 150), (85, 400), (0, 0, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
    
    # Display volume percentage
    cv2.putText(img, f'{int(volPer)}%', (40, 430), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)

    # Calculate frames per second
    cTime = time.time()
    fps = 1 / (cTime - pTime) if pTime != 0 else 0
    pTime = cTime

    # Display FPS counter
    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)

    cv2.imshow("Volume Hand Control", img)
    if cv2.waitKey(1) & 0xFF == 27: # press ESC to exit
        break

cap.release()
cv2.destroyAllWindows()
