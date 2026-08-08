import time
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class EmotionalState:
    happiness: float = 50.0   # Range: 0.0 to 100.0
    energy: float = 100.0     # Range: 0.0 to 100.0
    boredom: float = 0.0      # Range: 0.0 to 100.0

class EmotionEngine:
    def __init__(self):
        self.state = EmotionalState()
        self.last_interaction_time = time.time()
        self.primary_emotion = "NEUTRAL"

    def update_sensors(self, event_type: str) -> str:
        """
        Processes incoming sensor events (touch, face detected, sound, voice)
        and updates numerical emotion parameters.
        """
        self.last_interaction_time = time.time()
        
        if event_type == "TOUCH_HEAD":
            self.state.happiness = min(100.0, self.state.happiness + 25.0)
            self.state.boredom = max(0.0, self.state.boredom - 40.0)
            
        elif event_type == "FACE_DETECTED":
            self.state.happiness = min(100.0, self.state.happiness + 10.0)
            self.state.boredom = max(0.0, self.state.boredom - 20.0)
            
        elif event_type == "LOUD_NOISE":
            self.state.happiness = max(0.0, self.state.happiness - 20.0)
            
        elif event_type == "USER_SPOKE":
            self.state.boredom = max(0.0, self.state.boredom - 15.0)
            self.state.energy = max(0.0, self.state.energy - 2.0)

        elif event_type == "BATTERY_LOW":
            self.state.energy = 10.0

        return self._recalculate_primary_emotion()

    def decay_tick(self) -> str:
        """
        Call this on a periodic loop (e.g., every 5 seconds) 
        to simulate energy drain and rising boredom over idle time.
        """
        idle_time = time.time() - self.last_interaction_time
        
        # Increase boredom if idle for more than 10 seconds
        if idle_time > 10.0:
            self.state.boredom = min(100.0, self.state.boredom + 10.0)
            self.state.happiness = max(0.0, self.state.happiness - 3.0)
        
        # Slowly decrease energy over time
        self.state.energy = max(0.0, self.state.energy - 1.5)
        
        return self._recalculate_primary_emotion()

    def _recalculate_primary_emotion(self) -> str:
        """Translates numerical state values into high-level emotion categories."""
        if self.state.energy < 20.0:
            self.primary_emotion = "SLEEPY"
        elif self.state.boredom > 70.0:
            self.primary_emotion = "BORED"
        elif self.state.happiness > 75.0:
            self.primary_emotion = "EXCITED"
        elif self.state.happiness < 30.0:
            self.primary_emotion = "ANNOYED"
        else:
            self.primary_emotion = "NEUTRAL"
            
        return self.primary_emotion

    def get_status(self) -> Dict[str, Any]:
        """Returns active emotion and state metrics dictionary."""
        return {
            "primary_emotion": self.primary_emotion,
            "metrics": {
                "happiness": round(self.state.happiness, 1),
                "energy": round(self.state.energy, 1),
                "boredom": round(self.state.boredom, 1)
            }
        }


# --- TEST EXECUTION BLOCK ---
if __name__ == "__main__":
    emotion_system = EmotionEngine()

    print("\n=======================================================")
    print("      TESTING EMOTION & INTERNAL STATE MACHINE          ")
    print("=======================================================")

    print(f"\nInitial State: {emotion_system.get_status()}")

    # Simulate physical interactions
    events = ["FACE_DETECTED", "TOUCH_HEAD", "TOUCH_HEAD", "USER_SPOKE"]
    
    for event in events:
        active_emotion = emotion_system.update_sensors(event)
        print(f"\n[EVENT TRIGGERED]: {event}")
        print(f" -> Active Emotion : {active_emotion}")
        print(f" -> Internal State : {emotion_system.get_status()['metrics']}")

    # Simulate idle decay
    print("\n[SYSTEM] Simulating 15 seconds of idle decay...")
    emotion_system.last_interaction_time -= 15.0  # Artificially jump time
    active_emotion = emotion_system.decay_tick()
    print(f" -> Active Emotion : {active_emotion}")
    print(f" -> Internal State : {emotion_system.get_status()['metrics']}")