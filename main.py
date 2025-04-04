import cv2
import mediapipe as mp
import asyncio
import websockets
import json
from typing import Dict, Optional


class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=2)
        self.mp_draw = mp.solutions.drawing_utils

    def calculate_depth(self, hand_landmarks):
        wrist = hand_landmarks.landmark[0]
        mcp = hand_landmarks.landmark[9]
        return abs(wrist.z - mcp.z)

    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return self.hands.process(rgb_frame)

    def normalize_coordinates(self, x, y, frame_width, frame_height):
        norm_x = (x - frame_width / 2) / (frame_width / 2)
        norm_y = (y - frame_height / 2) / (frame_height / 2)
        return norm_x, norm_y

    def get_hand_data(self, frame, results) -> Dict[str, Optional[dict]]:
        height, width, _ = frame.shape
        hand_data = {"HandLeft": None, "HandRight": None}

        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                is_left = handedness.classification[0].label == "Left"
                hand_key = "HandLeft" if is_left else "HandRight"

                landmarks_data = []
                depth = self.calculate_depth(hand_landmarks)

                for id, landmark in enumerate(hand_landmarks.landmark):
                    norm_x, norm_y = self.normalize_coordinates(
                        landmark.x * width,
                        landmark.y * height,
                        width,
                        height
                    )
                    rel_z = landmark.z - hand_landmarks.landmark[0].z
                    landmarks_data.append({
                        "id": id,
                        "x": norm_x,
                        "y": norm_y,
                        "z": rel_z,
                    })

                hand_data[hand_key] = {
                    "landmarks": landmarks_data,
                    "depth": depth,
                    "rest": False
                }

        if hand_data["HandLeft"] is None:
            hand_data["HandLeft"] = {"rest": True}
        if hand_data["HandRight"] is None:
            hand_data["HandRight"] = {"rest": True}

        return hand_data


async def websocket_handler(websocket, path):
    cap = cv2.VideoCapture(0)
    tracker = HandTracker()

    try:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                continue

            results = tracker.process_frame(frame)
            hand_data = tracker.get_hand_data(frame, results)

            await websocket.send(json.dumps(hand_data))

            cv2.imshow('Hand Tracking', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()


async def main():
    server = await websockets.serve(websocket_handler, "localhost", 8765)
    print("WebSocket server started on ws://localhost:8765")
    await server.wait_closed()


if __name__ == '__main__':
    asyncio.run(main())