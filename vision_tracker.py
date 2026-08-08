import cv2
import time
from emotion_engine import EmotionEngine
from personality_engine import PersonalityEngine

class VisionSystem:
    def __init__(self):
        # Load Haar Cascade XML files safely
        face_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        smile_path = cv2.data.haarcascades + 'haarcascade_smile.xml'
        
        self.face_cascade = cv2.CascadeClassifier(face_path)
        self.smile_cascade = cv2.CascadeClassifier(smile_path)

        if self.face_cascade.empty():
            print("[WARNING] Could not load face cascade XML.")

    def process_frame(self, frame):
        """
        Scans a single camera frame for human faces and smiles.
        Returns detected vision events ('FACE_DETECTED', 'USER_SMILING', or 'NO_FACE').
        """
        if frame is None or frame.size == 0:
            return "NO_FACE", None

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        if len(faces) == 0:
            return "NO_FACE", frame

        event = "FACE_DETECTED"

        for (x, y, w, h) in faces:
            # Draw green box around detected face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            roi_gray = gray[y:y + h, x:x + w]
            smiles = self.smile_cascade.detectMultiScale(roi_gray, scaleFactor=1.8, minNeighbors=20)
            
            if len(smiles) > 0:
                event = "USER_SMILING"
                cv2.putText(frame, "SMILING!", (x, y - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        return event, frame


def open_camera():
    """Tries opening camera with explicit resolution and backend configuration."""
    # Attempt 1: DirectShow with standard 640x480 resolution
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if cap.isOpened():
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        ret, test_frame = cap.read()
        if ret and test_frame is not None and test_frame.size > 0:
            print("[INFO] Camera initialized successfully using DirectShow (640x480).")
            return cap
        cap.release()

    # Attempt 2: Fallback to standard capture index
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        print("[INFO] Camera initialized using default backend (640x480).")
        return cap

    return None


# --- LIVE CAMERA DEMO BLOCK ---
if __name__ == "__main__":
    vision = VisionSystem()
    emotion_engine = EmotionEngine()
    personality_engine = PersonalityEngine(initial_profile="dog")

    cap = open_camera()

    if cap is None or not cap.isOpened():
        print("[ERROR] Could not initialize webcam stream.")
        exit()

    print("\n=======================================================")
    print("      LIVE CAMERA VISION & PERSONALITY DEMO            ")
    print("=======================================================")
    print("Press 'q' in the video window to quit.")

    last_trigger_time = 0

    while True:
        ret, frame = cap.read()
        if not ret or frame is None or frame.size == 0:
            continue

        event, annotated_frame = vision.process_frame(frame)

        # Trigger reaction every 3 seconds
        if event != "NO_FACE" and (time.time() - last_trigger_time > 3.0):
            last_trigger_time = time.time()
            
            if event == "USER_SMILING":
                emotion_engine.update_sensors("TOUCH_HEAD") 
                raw_text = "I saw you smile at me!"
            else:
                emotion_engine.update_sensors("FACE_DETECTED")
                raw_text = "Hello there!"

            current_mood = emotion_engine.primary_emotion
            output = personality_engine.transform_text(raw_text, current_emotion=current_mood)

            print(f"\n[VISION EVENT] : {event}")
            print(f"[ROBOT MOOD ]  : {current_mood}")
            print(f"[REACTION   ]  : \"{output['speakable_text']}\"")
            print(f"[HEAD MOTION]  : {output['hardware_signals']['animation_trigger']}")

        if annotated_frame is not None:
            cv2.imshow("Robot Eye View", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()