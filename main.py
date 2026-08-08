import cv2
import time
from vision_tracker import VisionSystem, open_camera
from emotion_engine import EmotionEngine
from personality_engine import PersonalityEngine
from behavior_engine import BehaviorEngine
from voice_engine import VoiceEngine

class MasterSystemController:
    def __init__(self, initial_personality: str = "dog"):
        print("\n=======================================================")
        print("     ROVER ROBOT COMPANION - MASTER SYSTEM STARTING    ")
        print("=======================================================")
        
        # Initialize Subsystems
        self.vision = VisionSystem()
        self.emotion = EmotionEngine()
        self.personality = PersonalityEngine(initial_profile=initial_personality)
        self.behavior = BehaviorEngine()
        self.voice = VoiceEngine()
        
        self.running = False

    def run(self):
        """Main system loop connecting all input sensors to outputs."""
        cap = open_camera()
        if cap is None or not cap.isOpened():
            print("[ERROR] Failed to start camera feed. Exiting master engine.")
            return

        self.running = True
        last_reaction_time = 0.0
        last_decay_time = time.time()

        print(f"\n[SYSTEM READY] Active Profile: [{self.personality.active_profile_key.upper()}]")
        print("Controls:")
        print(" - Press 'd' for DOG profile")
        print(" - Press 'c' for CAT profile")
        print(" - Press 'r' for ROBOT profile")
        print(" - Press 'q' to QUIT\n")

        while self.running:
            ret, frame = cap.read()
            if not ret or frame is None or frame.size == 0:
                continue

            # 1. Vision Processing
            vision_event, annotated_frame = self.vision.process_frame(frame)

            # 2. Emotion Idle Decay (Ticks every 5 seconds)
            if time.time() - last_decay_time > 5.0:
                self.emotion.decay_tick()
                last_decay_time = time.time()

            # 3. Vision Trigger Reaction (Limit to once every 4 seconds)
            if vision_event != "NO_FACE" and (time.time() - last_reaction_time > 4.0):
                last_reaction_time = time.time()

                # Update Emotion State based on Vision Input
                if vision_event == "USER_SMILING":
                    current_mood = self.emotion.update_sensors("TOUCH_HEAD")
                    raw_text = "I saw you smiling at me!"
                else:
                    current_mood = self.emotion.update_sensors("FACE_DETECTED")
                    raw_text = "Hello human!"

                # Transform Text with Active Personality
                speech_payload = self.personality.transform_text(raw_text, current_emotion=current_mood)

                # Trigger Motor Behavior Sequence
                anim_trigger = speech_payload["hardware_signals"]["animation_trigger"]
                self.behavior.trigger_animation(anim_trigger, priority=1)
                motor_result = self.behavior.process_next_action()

                # Print Telemetry & Speak Output
                print(f"[EVENT] : {vision_event}")
                print(f"[MOOD ] : {current_mood} | Metrics: {self.emotion.get_status()['metrics']}")
                print(f"[ACTION]: Running animation '{motor_result['active_animation']}' ({motor_result['motor_steps_count']} steps)")
                
                # Speak out response
                self.voice.speak(speech_payload["speakable_text"], emotion=current_mood, blocking=False)
                print("-" * 60)

            # 4. Render Video Feed Window
            if annotated_frame is not None:
                # Overlay system telemetry on camera view
                status_text = f"Profile: {self.personality.active_profile_key.upper()} | Mood: {self.emotion.primary_emotion}"
                cv2.putText(annotated_frame, status_text, (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                cv2.imshow("ROVER Master View", annotated_frame)

            # 5. Handle Keyboard Hotkeys
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\n[SYSTEM] Shutting down ROVER Companion...")
                self.running = False
            elif key == ord('d'):
                self.personality.set_personality("dog")
                print("\n>>> Switched Personality to [DOG] <<<")
            elif key == ord('c'):
                self.personality.set_personality("cat")
                print("\n>>> Switched Personality to [CAT] <<<")
            elif key == ord('r'):
                self.personality.set_personality("robot")
                print("\n>>> Switched Personality to [ROBOT] <<<")

        cap.release()
        cv2.destroyAllWindows()


# --- START MASTER SYSTEM ---
if __name__ == "__main__":
    controller = MasterSystemController(initial_personality="dog")
    controller.run()