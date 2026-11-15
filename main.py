import cv2
import mediapipe as mp
import time
from utils import (get_right_hand_gesture, get_left_hand_gesture,
                   get_index_tip_position, get_distance, get_wrist_position)
from controller import Controller

mp_hands   = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def main():
    controller = Controller()

    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.6,  # slightly lower = better left hand detection
        min_tracking_confidence=0.6
    )

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    fps_counter = 0
    fps_start   = time.time()
    fps         = 0

    print("✅ Hand Control Active!")
    print("")
    print("RIGHT HAND:")
    print("  ☝️  Index only          → Move cursor")
    print("  🤏 Pinch index         → Left click")
    print("  🖐️  All 5 fingers hold  → Double click")
    print("  🤏 Pinch middle        → Right click")
    print("  👍 Thumb + Index       → Scroll up")
    print("  👍 Thumb only          → Scroll down")
    print("  ✊ Hold fist           → Mute toggle")
    print("")
    print("LEFT HAND:")
    print("  🖐️  Full palm open      → Volume up")
    print("  ✊ Hold fist           → Volume down")
    print("")
    print("Press Q to quit\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame  = cv2.flip(frame, 1)
        h, w   = frame.shape[:2]
        rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        right_gesture = "NONE"
        left_gesture  = "NONE"
        right_action  = "NONE"
        left_action   = "NONE"

        if result.multi_hand_landmarks and result.multi_handedness:
            for hand_landmarks, handedness in zip(
                result.multi_hand_landmarks,
                result.multi_handedness
            ):
                landmarks = hand_landmarks.landmark
                label     = handedness.classification[0].label

                # Draw skeleton
                mp_drawing.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
                )

                if label == "Right":
                    right_gesture = get_right_hand_gesture(landmarks, w, h)
                    tip_x, tip_y  = get_index_tip_position(landmarks, w, h)
                    right_action  = controller.execute_right(
                        right_gesture, tip_x, tip_y
                    )

                    # Draw index tip
                    cv2.circle(frame, (tip_x, tip_y), 10, (0, 255, 0), -1)

                    # Draw pinch line
                    thumb_x     = int(landmarks[4].x * w)
                    thumb_y     = int(landmarks[4].y * h)
                    index_x     = int(landmarks[8].x * w)
                    index_y     = int(landmarks[8].y * h)
                    index_pinch = get_distance(landmarks, 4, 8, w, h)
                    color = (0, 0, 255) if index_pinch < 30 else (255, 255, 0)
                    cv2.line(frame, (thumb_x, thumb_y),
                             (index_x, index_y), color, 2)

                    # Double click progress bar
                    if right_gesture == "DOUBLE_CLICK" and \
                       controller.double_click_start:
                        held     = time.time() - controller.double_click_start
                        progress = min(int(held / 1.0 * 200), 200)
                        cv2.rectangle(frame, (10, h-40),
                                      (210, h-20), (50, 50, 50), -1)
                        cv2.rectangle(frame, (10, h-40),
                                      (10+progress, h-20), (0, 255, 0), -1)
                        cv2.putText(frame, "Hold for double click",
                                    (10, h-45),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.5, (0, 255, 0), 1)

                    # Mute progress bar
                    if right_gesture == "MUTE" and \
                       controller.mute_hold_start:
                        held     = time.time() - controller.mute_hold_start
                        progress = min(int(held / 1.0 * 200), 200)
                        cv2.rectangle(frame, (10, h-70),
                                      (210, h-55), (50, 50, 50), -1)
                        cv2.rectangle(frame, (10, h-70),
                                      (10+progress, h-55), (0, 0, 255), -1)
                        cv2.putText(frame, "Hold to mute",
                                    (10, h-75),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.5, (0, 0, 255), 1)

                elif label == "Left":
                    left_gesture = get_left_hand_gesture(landmarks, w, h)
                    left_action  = controller.execute_left(left_gesture)

                    # Label left hand
                    wrist_x = int(landmarks[0].x * w)
                    wrist_y = int(landmarks[0].y * h)
                    cv2.putText(frame, "LEFT HAND",
                                (wrist_x - 40, wrist_y + 20),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.6, (255, 100, 100), 2)

        # Display info
        cv2.rectangle(frame, (0, 0), (340, 145), (0, 0, 0), -1)
        cv2.putText(frame, f"R Gesture: {right_gesture}",
                    (10, 25), cv2.FONT_HERSHEY_SIMPLEX,
                    0.55, (0, 255, 0), 2)
        cv2.putText(frame, f"R Action : {right_action}",
                    (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    0.55, (0, 255, 255), 2)
        cv2.putText(frame, f"L Gesture: {left_gesture}",
                    (10, 80), cv2.FONT_HERSHEY_SIMPLEX,
                    0.55, (255, 100, 100), 2)
        cv2.putText(frame, f"L Action : {left_action}",
                    (10, 105), cv2.FONT_HERSHEY_SIMPLEX,
                    0.55, (100, 255, 255), 2)
        cv2.putText(frame, f"FPS: {fps:.1f}",
                    (10, 128), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (255, 255, 0), 1)

        # FPS
        fps_counter += 1
        if time.time() - fps_start >= 1.0:
            fps         = fps_counter
            fps_counter = 0
            fps_start   = time.time()

        cv2.imshow("Hand Control", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("\n👋 Hand control stopped.")

if __name__ == "__main__":
    main()