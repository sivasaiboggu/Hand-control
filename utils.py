import mediapipe as mp
import numpy as np

mp_hands   = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

FINGER_TIPS  = [4, 8, 12, 16, 20]
FINGER_BASES = [2, 5,  9, 13, 17]

def get_finger_states(landmarks):
    fingers = []

    if landmarks[4].x < landmarks[3].x:
        fingers.append(True)
    else:
        fingers.append(False)

    for tip, base in zip(FINGER_TIPS[1:], FINGER_BASES[1:]):
        if landmarks[tip].y < landmarks[base].y - 0.02:
            fingers.append(True)
        else:
            fingers.append(False)

    return fingers

def get_left_finger_states(landmarks):
    fingers = []

    if landmarks[4].x > landmarks[3].x:
        fingers.append(True)
    else:
        fingers.append(False)

    for tip, base in zip(FINGER_TIPS[1:], FINGER_BASES[1:]):
        if landmarks[tip].y < landmarks[base].y - 0.02:
            fingers.append(True)
        else:
            fingers.append(False)

    return fingers

def get_distance(landmarks, p1, p2, frame_w, frame_h):
    x1 = landmarks[p1].x * frame_w
    y1 = landmarks[p1].y * frame_h
    x2 = landmarks[p2].x * frame_w
    y2 = landmarks[p2].y * frame_h
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def get_right_hand_gesture(landmarks, frame_w, frame_h):
    fingers = get_finger_states(landmarks)
    # [thumb, index, middle, ring, pinky]

    index_pinch  = get_distance(landmarks, 4, 8,  frame_w, frame_h)
    middle_pinch = get_distance(landmarks, 4, 12, frame_w, frame_h)
    PINCH_THRESHOLD = 30

    # Pinch — highest priority
    if index_pinch < PINCH_THRESHOLD:
        return "LEFT_CLICK"

    if middle_pinch < PINCH_THRESHOLD and fingers[2]:
        return "RIGHT_CLICK"

    # All 5 open — double click
    if all(fingers):
        return "DOUBLE_CLICK"

    # Scroll up — ✌️ index + middle up
    if (not fingers[0] and fingers[1] and fingers[2]
            and not fingers[3] and not fingers[4]):
        return "SCROLL_UP"

    # Scroll down — 👍 thumb only
    # Make sure thumb is clearly out
    if (fingers[0] and not fingers[1] and not fingers[2]
            and not fingers[3] and not fingers[4]):
        thumb_dist = get_distance(landmarks, 4, 5, frame_w, frame_h)
        if thumb_dist > 50:      # thumb clearly extended
            return "SCROLL_DOWN"

    # Index only — move cursor
    if (not fingers[0] and fingers[1] and not fingers[2]
            and not fingers[3] and not fingers[4]):
        return "MOVE"

    # Fist — mute hold
    if not any(fingers):
        return "MUTE"

    return "NONE"

def get_left_hand_gesture(landmarks, frame_w, frame_h):
    fingers = get_left_finger_states(landmarks)

    if all(fingers):
        return "VOLUME_UP"

    if not any(fingers):
        return "VOLUME_DOWN"

    return "NONE"

def get_index_tip_position(landmarks, frame_w, frame_h):
    x = int(landmarks[8].x * frame_w)
    y = int(landmarks[8].y * frame_h)
    return x, y

def get_wrist_position(landmarks, frame_h):
    return int(landmarks[0].y * frame_h)