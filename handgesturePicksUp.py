import cv2
import mediapipe as mp
import time
import subprocess
import platform

class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        """
        Initialize the hand detector with MediaPipe
        
        Args:
            mode: Static image mode (False for video stream)
            maxHands: Maximum number of hands to detect
            detectionCon: Minimum detection confidence threshold
            trackCon: Minimum tracking confidence threshold
        """
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        
        # Initialize MediaPipe Hands solution
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            model_complexity=1,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
        self.mpDraw = mp.solutions.drawing_utils
        self.results = None
        
        # Variables to control cooldown between gesture detections
        self.last_gesture_time = 0
        self.cooldown = 3  # 3 seconds between detections
        
    def findHands(self, img, draw=True):
        """
        Detect hands in the image and optionally draw landmarks
        
        Args:
            img: Input image (BGR format)
            draw: Whether to draw hand landmarks on the image
            
        Returns:
            Image with drawn landmarks (if draw=True)
        """
        # Convert BGR to RGB for MediaPipe processing
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        
        # Draw landmarks if hands are detected
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(
                        img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img
    
    def findPosition(self, img, handNo=0, draw=True):
        """
        Find the position of hand landmarks
        
        Args:
            img: Input image
            handNo: Which hand to track (0 for first detected hand)
            draw: Whether to draw circles on landmark positions
            
        Returns:
            List of landmarks [id, x, y]
        """
        lmList = []
        
        # Check if hands were detected
        if self.results and self.results.multi_hand_landmarks:
            if handNo < len(self.results.multi_hand_landmarks):
                myHand = self.results.multi_hand_landmarks[handNo]
                
                # Get pixel coordinates for each landmark
                for id, lm in enumerate(myHand.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])
                    
                    # Draw circle on landmark if requested
                    if draw:
                        cv2.circle(img, (cx, cy), 7, (255, 0, 255), cv2.FILLED)
        return lmList
    
    def fingersUp(self, lmList):
        """
        Detect which fingers are up
        
        Args:
            lmList: List of hand landmarks
            
        Returns:
            List of 5 elements [thumb, index, middle, ring, pinky]
            1 = up, 0 = down
        """
        fingers = []
        
        # Return empty list if no landmarks detected
        if len(lmList) == 0:
            return fingers
        
        # Landmark IDs for fingertips
        tipIds = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
        
        # Check thumb (horizontal comparison)
        # Thumb is up if tip is to the right of the joint below it
        if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)
        
        # Check other 4 fingers (vertical comparison)
        for id in range(1, 5):
            # Finger is up if tip is above the joint two positions below
            if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        
        return fingers
    
    def isHangLooseSign(self, fingers):
        """
        Detect the hand gesture
        (thumb and pinky up, other fingers down)
        
        Args:
            fingers: List of finger states [thumb, index, middle, ring, pinky]
            
        Returns:
            True if hang loose gesture is detected, False otherwise
        """
        # Hand pattern: [1, 0, 0, 0, 1]
        # [thumb, index, middle, ring, pinky]
        if len(fingers) == 5:
            return fingers[0] == 1 and fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 1
        return False
    
    def openMyUTEP(self):
        """
        Open the myUTEP application based on the operating system
        Implements cooldown to prevent multiple openings
        
        Returns:
            True if successfully opened, False otherwise
        """
        current_time = time.time()
        
        # Check cooldown to avoid multiple openings
        if current_time - self.last_gesture_time < self.cooldown:
            return False
        
        self.last_gesture_time = current_time
        
        try:
            system = platform.system()
            
            if system == "Windows":
                # On Windows, try to open from Microsoft Store or open browser
                subprocess.Popen(['start', 'https://my.utep.edu'], shell=True)
                print("✓ Opening myUTEP on Windows")
                
            elif system == "Darwin":  # macOS
                # On macOS, open browser with URL
                subprocess.Popen(['open', 'https://my.utep.edu'])
                print("✓ Opening myUTEP on macOS")
                
            else:  # Linux
                # On Linux, use xdg-open
                subprocess.Popen(['xdg-open', 'https://my.utep.edu'])
                print("✓ Opening myUTEP on Linux")
            
            return True
            
        except Exception as e:
            print(f"✗ Error opening myUTEP: {e}")
            return False

def main():
    """
    Main function to run the hand gesture detector
    Continuously captures video and detects the hang gesture
    """
    pTime = 0  # Previous time for FPS calculation
    cap = cv2.VideoCapture(0)  # Initialize webcam
    detector = handDetector()  # Create detector instance
    
    # Print instructions
    print("=" * 50)
    print("'🤙 Picks Up' GESTURE DETECTOR FOR myUTEP")
    print("=" * 50)
    print("Instructions:")
    print("1. Show your hand to the camera")
    print("2. Raise ONLY your thumb and pinky")
    print("3. Keep middle fingers down (index, middle, ring)")
    print("4. myUTEP will open automatically!")
    print("\nPress ESC to exit")
    print("=" * 50)
    
    gesture_detected = False  # Flag to track gesture state
    
    while True:
        # Read frame from webcam
        success, img = cap.read()
        if not success:
            break
        
        # Flip image horizontally for mirror effect
        img = cv2.flip(img, 1)
        
        # Detect hands in the frame
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=False)
        
        # If a hand is detected
        if len(lmList) != 0:
            # Get finger states
            fingers = detector.fingersUp(lmList)
            
            # Check for hang loose gesture
            if detector.isHangLooseSign(fingers):
                if not gesture_detected:
                    # Display detection message
                    cv2.putText(img, "HAND DETECTED! 🤙", (50, 100),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                    # Open myUTEP
                    detector.openMyUTEP()
                    gesture_detected = True
            else:
                gesture_detected = False
            
            # Display finger status on screen
            finger_names = ["Thumb", "Index", "Middle", "Ring", "Pinky"]
            for i, (name, status) in enumerate(zip(finger_names, fingers)):
                # Green for up, red for down
                color = (0, 255, 0) if status == 1 else (0, 0, 255)
                cv2.putText(img, f"{name}: {'UP' if status == 1 else 'DOWN'}", 
                           (10, 150 + i*30), cv2.FONT_HERSHEY_PLAIN, 1.5, color, 2)
        
        # Calculate and display FPS
        cTime = time.time()
        fps = 1 / (cTime - pTime) if (cTime - pTime) > 0 else 0
        pTime = cTime
        
        cv2.putText(img, f'FPS: {int(fps)}', (10, 50),
                   cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
        
        # Display instruction at bottom of screen
        cv2.putText(img, "Make the 'hang loose' gesture (thumb and pinky up)", 
                   (10, img.shape[0] - 20), cv2.FONT_HERSHEY_PLAIN, 1.2, (255, 255, 0), 2)
        
        # Show the image in window
        cv2.imshow("Gesture Detector - myUTEP", img)
        
        # Exit on ESC key press
        if cv2.waitKey(1) & 0xFF == 27:
            break
    
    # Clean up
    cap.release()
    cv2.destroyAllWindows()
    print("\nProgram finished!")

# Run the main function if script is executed directly
if __name__ == "__main__":
    main()