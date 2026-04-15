import cv2

try:
    import mediapipe as mp
except ImportError:
    mp = None


class HandGestureController:
    """Camera-based hand controller for platformer input."""

    def __init__(self, camera_index=0):
        self.available = True
        self.status_message = "Hand controls enabled"
        self.cap = None
        self.hands = None
        self.mp_hands = None
        self.mp_draw = None
        self.frame_width = 1
        self.frame_height = 1
        self.camera_index = camera_index

        if mp is None:
            self.available = False
            self.status_message = "MediaPipe not installed, using keyboard controls"
            return

        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.5,
        )
        self.cap = cv2.VideoCapture(self.camera_index)
        if self.cap.isOpened():
            self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 640)
            self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 480)
        else:
            self.available = False
            self.status_message = "Cannot open camera, using keyboard controls"
            self.cap.release()
            self.cap = None

    def _finger_curled(self, hand_landmarks, tip_id, pip_id):
        return hand_landmarks.landmark[tip_id].y > hand_landmarks.landmark[pip_id].y

    def _is_fist(self, hand_landmarks):
        # Require all four fingers to be curled to count as a fist.
        # This avoids treating "one finger pointing" as a jump gesture.
        curled = [
            self._finger_curled(hand_landmarks, 8, 6),   # index
            self._finger_curled(hand_landmarks, 12, 10), # middle
            self._finger_curled(hand_landmarks, 16, 14), # ring
            self._finger_curled(hand_landmarks, 20, 18), # pinky
        ]
        return sum(curled) == 4

    def _is_one_finger_pointing(self, hand_landmarks):
        # "1 finger" gesture: index up, other three fingers curled.
        index_up = hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y
        middle_curled = self._finger_curled(hand_landmarks, 12, 10)
        ring_curled = self._finger_curled(hand_landmarks, 16, 14)
        pinky_curled = self._finger_curled(hand_landmarks, 20, 18)
        return index_up and middle_curled and ring_curled and pinky_curled

    def get_controls(self):
        """
        Return dict with booleans: left, right, jump, power.
        Gesture mode:
        - Fist (closed hand) => jump
        - One finger (index up) => shoot power
        - Otherwise => stand still (no gesture movement)
        """
        default_controls = {"left": False, "right": False, "jump": False, "power": False}
        if not self.available or self.cap is None:
            return default_controls

        ok, frame = self.cap.read()
        if not ok:
            return default_controls

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb)

        if not result.multi_hand_landmarks:
            cv2.imshow("Hand Camera", frame)
            cv2.waitKey(1)
            return default_controls

        hand_landmarks = result.multi_hand_landmarks[0]
        self.mp_draw.draw_landmarks(
            frame,
            hand_landmarks,
            self.mp_hands.HAND_CONNECTIONS,
        )
        fist = self._is_fist(hand_landmarks)
        one_finger = self._is_one_finger_pointing(hand_landmarks)
        default_controls["jump"] = fist
        default_controls["power"] = one_finger

        cv2.imshow("Hand Camera", frame)
        cv2.waitKey(1)
        return default_controls

    def close(self):
        if self.hands is not None:
            self.hands.close()
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()
