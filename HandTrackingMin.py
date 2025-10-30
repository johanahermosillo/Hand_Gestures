import cv2 # import open CV
import mediapipe as mp # import media pipe
import time # import time to check frame rate

cap = cv2.VideoCapture(0); # use webcam from laptop. if you want external camera, use 1

mpHands = mp.solutions.hands
hands = mpHands.Hands() # has a tracking confidence of 0.5
mpDraw = mp.solutions.drawing_utils # method from media pipe that helps us visualize hands

pTime = 0 # previous time = 0 
cTime = 0 # current time = 0 


while True: # runs webcame
    success, img = cap.read()
    if not success or img is None:
        print("Frame not captured, skipping...")
        continue
    
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # covert image to RGB since mp only takes RGB
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks: # draws the dots on the hands using the bult in mpDraw
        for handLms in results.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                #print(id, lm) # each ID has a corresponding x,y landmark
                h, w, c = img.shape # height width and channel
                cx, cy = int(lm.x *w), int(lm.y*h)

                print(id,cx,cy)
                if id == 0:
                    cv2.circle(img, (cx,cy), 10, (255,0,255), cv2.FILLED) # helps detect the bottom of the palm
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS) # draws the line connection

    cTime = time.time()
    fps = 1 / (cTime-pTime)
    pTime = cTime

    cv2.putText(img, str(int(fps)),(10,70), cv2.FONT_HERSHEY_PLAIN, 1, (0,0,0), 3) #where you display, what you display, position, font, font size, color, thickness


    cv2.imshow("Image", img)
        # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- Cleanup ---
cap.release()           # releases webcam
cv2.destroyAllWindows()