# pose_analyzer.py
import mediapipe as mp
import cv2

class PoseAnalyzer:
    def __init__(self):
        self.mp_pose  = mp.solutions.pose
        self.mp_hands = mp.solutions.hands

        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=0,
            min_detection_confidence=0.4,
            min_tracking_confidence=0.4
        )

        self.hands_detector = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.4,
            min_tracking_confidence=0.4
        )

    def _get_posture(self, lm, PL):
        VT = 0.4
        shoulders_visible = (lm[PL.LEFT_SHOULDER].visibility  > VT or
                             lm[PL.RIGHT_SHOULDER].visibility > VT)
        lower_visible     = (lm[PL.LEFT_KNEE].visibility   > VT or
                             lm[PL.RIGHT_KNEE].visibility  > VT or
                             lm[PL.LEFT_ANKLE].visibility  > VT or
                             lm[PL.RIGHT_ANKLE].visibility > VT)

        if not shoulders_visible:
            return "unknown"
        if shoulders_visible and not lower_visible:
            return "sitting"
        return "standing"

    def analyze(self, frame, x1, y1, x2, y2):
        result_data = {
            "posture":            "unknown",
            "head_y":             None,
            "left_wrist_y":       None,
            "right_wrist_y":      None,
            "upper_body_active":  False,
            "eye_direction":      "unknown",
            "hands_active":       False
        }

        H = frame.shape[0]
        W = frame.shape[1]

        # ── Run pose on FULL frame (more reliable) ─────────────
        rgb         = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pose_result = self.pose.process(rgb)

        if pose_result.pose_landmarks:
            lm = pose_result.pose_landmarks.landmark
            PL = self.mp_pose.PoseLandmark

            result_data["posture"] = self._get_posture(lm, PL)

            # Head Y (nose)
            if lm[PL.NOSE].visibility > 0.4:
                result_data["head_y"] = lm[PL.NOSE].y * H

            # Wrist Y positions
            if lm[PL.LEFT_WRIST].visibility > 0.4:
                result_data["left_wrist_y"] = lm[PL.LEFT_WRIST].y * H

            if lm[PL.RIGHT_WRIST].visibility > 0.4:
                result_data["right_wrist_y"] = lm[PL.RIGHT_WRIST].y * H

            # Upper body active: wrists above hips
            left_hip_y = lm[PL.LEFT_HIP].y * H if lm[PL.LEFT_HIP].visibility > 0.4 else None
            lw = result_data["left_wrist_y"]
            rw = result_data["right_wrist_y"]

            if left_hip_y:
                if (lw and lw < left_hip_y) or (rw and rw < left_hip_y):
                    result_data["upper_body_active"] = True

        # ── Run hands on full frame ────────────────────────────
        hands_result = self.hands_detector.process(rgb)
        if hands_result.multi_hand_landmarks:
            result_data["hands_active"] = True

            for idx, hand_lm in enumerate(hands_result.multi_hand_landmarks):
                wrist_y = hand_lm.landmark[0].y * H
                label   = hands_result.multi_handedness[idx].classification[0].label
                if label == "Left":
                    result_data["left_wrist_y"] = wrist_y
                else:
                    result_data["right_wrist_y"] = wrist_y

        return result_data