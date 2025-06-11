import cv2
import mediapipe as mp
import pyautogui

# Initialize mediapipe hands module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Initialize webcam
cap = cv2.VideoCapture(0)

# Set up the screen width and height
screen_width, screen_height = pyautogui.size()

# To track the previous position of the cursor
prev_x, prev_y = 0, 0

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)  # Flip horizontally for mirror effect
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw hand landmarks
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            fingers_up = []
            landmarks = hand_landmarks.landmark

            # Thumb (adjusted logic for flipped cam)
            if landmarks[4].x > landmarks[3].x:
                fingers_up.append(1)
            else:
                fingers_up.append(0)

            # Fingers: index to pinky
            tips_ids = [8, 12, 16, 20]
            for tip_id in tips_ids:
                if landmarks[tip_id].y < landmarks[tip_id - 2].y:
                    fingers_up.append(1)
                else:
                    fingers_up.append(0)

            total_fingers = sum(fingers_up)

            # Get the index finger tip position for mouse movement
            index_finger_x = int(landmarks[8].x * screen_width)
            index_finger_y = int(landmarks[8].y * screen_height)

            # Mouse control logic:
            if total_fingers == 1:  # One finger: Move the cursor
                # Move the cursor based on index finger position
                pyautogui.moveTo(index_finger_x, index_finger_y)

            elif total_fingers == 2:  # Two fingers: Click
                # Click the mouse using pyautogui
                pyautogui.click()

            elif total_fingers == 3:  # Three fingers: Scroll
                # Scroll up or down based on the vertical movement of the index finger
                if prev_y - index_finger_y > 10:  # Scroll up
                    pyautogui.scroll(50)
                elif index_finger_y - prev_y > 10:  # Scroll down
                    pyautogui.scroll(-50)

            elif total_fingers == 4:  # Four fingers: No movement
                pass  # No action taken

            elif total_fingers == 5:  # Five fingers: Back (Alt + Left Arrow)
                # Perform 'Alt + Left Arrow' to go back (typically in browsers)
                pyautogui.hotkey('alt', 'left')

            # Update the previous position for scrolling
            prev_x, prev_y = index_finger_x, index_finger_y

    # Show the video feed with hand landmarks
    cv2.imshow("Hand Tracker - Mousepad Simulation", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
