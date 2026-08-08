import pyttsx3
import time
from typing import Dict, Any

class VoiceEngine:
    def __init__(self):
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        
        # Configure default baseline voice settings
        self.base_rate = 160   # Words per minute
        self.base_volume = 0.9 # 0.0 to 1.0

        # Emotional modulation map
        self.emotion_voice_profiles = {
            "HAPPY": {"rate_mult": 1.15, "volume": 1.0},
            "EXCITED": {"rate_mult": 1.35, "volume": 1.0},
            "SAD": {"rate_mult": 0.75, "volume": 0.6},
            "SLEEPY": {"rate_mult": 0.65, "volume": 0.5},
            "ANGRY": {"rate_mult": 1.20, "volume": 1.0},
            "BORED": {"rate_mult": 0.85, "volume": 0.7},
            "NEUTRAL": {"rate_mult": 1.00, "volume": 0.9}
        }

    def speak(self, text: str, emotion: str = "NEUTRAL", blocking: bool = True) -> Dict[str, Any]:
        """
        Modulates voice parameters according to emotion and synthesizes audio.
        """
        profile = self.emotion_voice_profiles.get(emotion.upper(), self.emotion_voice_profiles["NEUTRAL"])
        
        target_rate = int(self.base_rate * profile["rate_mult"])
        target_volume = profile["volume"]

        self.engine.setProperty('rate', target_rate)
        self.engine.setProperty('volume', target_volume)

        print(f"[VOICE SYNTH] Speaking: \"{text}\" | Mood: {emotion} (Rate: {target_rate} wpm, Vol: {int(target_volume * 100)}%)")

        self.engine.say(text)
        if blocking:
            self.engine.runAndWait()

        return {
            "text": text,
            "emotion": emotion,
            "speech_rate": target_rate,
            "volume": target_volume
        }


# --- TEST EXECUTION BLOCK ---
if __name__ == "__main__":
    from emotion_engine import EmotionEngine
    from personality_engine import PersonalityEngine

    voice = VoiceEngine()
    emotion_engine = EmotionEngine()
    personality = PersonalityEngine(initial_profile="dog")

    print("\n=======================================================")
    print("      TESTING VOICE STYLE & AUDIO SYNTHESIS PIPELINE    ")
    print("=======================================================\n")

    # Demo 1: Excited Reaction
    emotion_engine.update_sensors("TOUCH_HEAD") # Boosts to EXCITED
    mood = emotion_engine.primary_emotion
    speech_data = personality.transform_text("I see you smiling!", current_emotion=mood)
    
    voice.speak(speech_data["speakable_text"], emotion=mood)

    # Demo 2: Sleepy Reaction (Drain energy below 20.0)
    emotion_engine.state.energy = 10.0
    mood = emotion_engine._recalculate_primary_emotion()
    speech_data = personality.transform_text("Goodnight human.", current_emotion=mood)
    
    voice.speak(speech_data["speakable_text"], emotion=mood)