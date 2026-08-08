import random
import re
import time
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class PersonalityProfile:
    name: str
    pitch_modifier: float
    speed_modifier: float
    default_led: str
    default_animation: str
    prefix_phrases: list
    suffix_phrases: list
    word_replacements: Dict[str, str]

class PersonalityEngine:
    def __init__(self, initial_profile: str = "dog"):
        self.profiles: Dict[str, PersonalityProfile] = {
            "dog": PersonalityProfile(
                name="Dog",
                pitch_modifier=1.25,
                speed_modifier=1.15,
                default_led="HAPPY_EYES",
                default_animation="TAIL_WAG",
                prefix_phrases=["Arf! ", "Hey friend! ", "Oh boy! ", "Woof! "],
                suffix_phrases=["!", "!! Let's play!", " *pant pant*", " *tail wags fast*"],
                word_replacements={
                    r"\bhello\b": "Hey best friend!",
                    r"\bhi\b": "Woof! Hi!",
                    r"\byes\b": "Yeah yeah yeah!",
                    r"\bno\b": "Aww, really?",
                    r"\bhelp\b": "fetch that for you",
                }
            ),
            "cat": PersonalityProfile(
                name="Cat",
                pitch_modifier=0.88,
                speed_modifier=0.80,
                default_led="HALF_CLOSED_EYES",
                default_animation="SLOW_BLINK",
                prefix_phrases=["*purr* ", "Hmm... ", "Meow. ", "*sigh* "],
                suffix_phrases=["...", " I guess.", " Now feed me.", " Don't bother me."],
                word_replacements={
                    r"\bhello\b": "Oh... you came back.",
                    r"\bhi\b": "Meow.",
                    r"\byes\b": "If I feel like it.",
                    r"\bno\b": "Absolutely not.",
                    r"\bhelp\b": "watch you do it yourself",
                }
            ),
            "robot": PersonalityProfile(
                name="Robot",
                pitch_modifier=1.00,
                speed_modifier=1.00,
                default_led="NEUTRAL_GRID",
                default_animation="PRECISION_NOD",
                prefix_phrases=["[SYS_ACK] ", "PROCESSING: ", "STATUS: ACTIVE -> "],
                suffix_phrases=[". Query complete.", ". Awaiting next command.", ". Executing."],
                word_replacements={
                    r"\bhello\b": "Greetings user.",
                    r"\bhi\b": "Initiating communication channel.",
                    r"\byes\b": "Affirmative.",
                    r"\bno\b": "Negative.",
                    r"\bhelp\b": "execute operational assistance",
                }
            )
        }
        
        self.active_profile_key = initial_profile.lower()

    def set_personality(self, profile_name: str) -> bool:
        """Switch active personality profile on the fly (dog, cat, or robot)."""
        key = profile_name.lower()
        if key in self.profiles:
            self.active_profile_key = key
            return True
        return False

    def transform_text(self, raw_llm_text: str, current_emotion: str = "NEUTRAL") -> Dict[str, Any]:
        """
        Transforms raw LLM text based on active personality selection 
        and extracts control tags for Audio, Motor, and LED modules.
        """
        profile = self.profiles[self.active_profile_key]
        transformed = raw_llm_text
        
        delay_seconds = 0.0
        led_expression = profile.default_led
        animation = profile.default_animation
        behavior_note = "Normal Response"

        # Roll a virtual die (1 to 100) for personality behaviors
        roll = random.randint(1, 100)

        # ---------------------------------------------------------------------
        # 1. DOG BEHAVIOR LOGIC
        # ---------------------------------------------------------------------
        if profile.name == "Dog":
            if roll <= 40:
                # High Energy / Excited
                animation = "FAST_HEAD_TILT_AND_WAG"
                led_expression = "SPARKLE_HAPPY_EYES"
                behavior_note = "Dog got excited and tilted head!"
            elif roll <= 80:
                # Playful
                transformed = "*barks happily* " + transformed
                animation = "HAPPY_BOB"
                led_expression = "HEART_EYES"
                behavior_note = "Dog barked with joy"
            else:
                # Curiously Attentive
                animation = "HEAD_TILT_LEFT"
                led_expression = "WIDE_EYES"
                behavior_note = "Dog is listening attentively"

        # ---------------------------------------------------------------------
        # 2. CAT BEHAVIOR LOGIC
        # ---------------------------------------------------------------------
        elif profile.name == "Cat":
            if roll <= 20:
                # Ignores user completely
                transformed = "... *stares blankly and licks paw*"
                animation = "TURN_HEAD_AWAY"
                led_expression = "UNINTERESTED_EYES"
                behavior_note = "Cat ignored you completely!"
            elif roll <= 50:
                # Lazy delayed response
                delay_seconds = 1.5
                animation = "SLOW_STRETCH"
                led_expression = "SLOW_BLINK"
                behavior_note = "Cat took a lazy pause before responding"
            elif roll <= 80:
                # Affectionate / Purring
                transformed = "*purrrr* " + transformed
                animation = "HEAD_RUB_MOTION"
                led_expression = "HAPPY_PURR_EYES"
                behavior_note = "Cat is feeling affectionate"
            else:
                # Annoyed / Flicking tail
                animation = "TAIL_FLICK"
                led_expression = "ANN_EYES"
                behavior_note = "Cat responded with mild annoyance"

        # ---------------------------------------------------------------------
        # 3. ROBOT BEHAVIOR LOGIC
        # ---------------------------------------------------------------------
        elif profile.name == "Robot":
            if roll <= 50:
                # Precise & Efficient Execution
                animation = "SERVO_STEP_SCAN"
                led_expression = "PROCESSING_MATRIX"
                behavior_note = "Robot executed precise diagnostic scan"
            else:
                # Data Processing Latency
                delay_seconds = 0.3
                animation = "SINGLE_AXIS_NOD"
                led_expression = "GRID_PULSE"
                behavior_note = "Robot computed latency check before speaking"

        # Apply basic text formatting if cat didn't ignore
        if behavior_note != "Cat ignored you completely!":
            # Apply regex replacements
            for pattern, replacement in profile.word_replacements.items():
                transformed = re.sub(pattern, replacement, transformed, flags=re.IGNORECASE)

            # Apply prefixes and suffixes
            if profile.name == "Dog":
                transformed = random.choice(profile.prefix_phrases) + transformed + random.choice(profile.suffix_phrases)
            elif profile.name == "Cat" and not transformed.startswith("*purrrr*"):
                transformed = random.choice(profile.prefix_phrases) + transformed + random.choice(profile.suffix_phrases)
            elif profile.name == "Robot":
                transformed = transformed.upper()
                transformed = f"{random.choice(profile.prefix_phrases)}{transformed}{random.choice(profile.suffix_phrases)}"

        # Construct Final Payload
        return {
            "active_personality": profile.name,
            "original_text": raw_llm_text,
            "speakable_text": transformed,
            "response_delay": delay_seconds,
            "behavior_description": behavior_note,
            "audio_config": {
                "pitch_modifier": profile.pitch_modifier,
                "speed_modifier": profile.speed_modifier,
            },
            "hardware_signals": {
                "led_expression": led_expression,
                "animation_trigger": animation
            }
        }


# --- EXECUTION TEST BLOCK ---
if __name__ == "__main__":
    engine = PersonalityEngine()
    test_input = "Hello! How can I help you today?"

    print("\n=======================================================")
    print("      TESTING MULTI-PERSONALITY ROBOT ENGINE           ")
    print("=======================================================")

    # Test all 3 personalities consecutively
    for personality in ["dog", "cat", "robot"]:
        engine.set_personality(personality)
        print(f"\n >>> SELECTING PERSONALITY: [{personality.upper()}] <<<")
        
        # Simulate 2 interactions per personality profile
        for i in range(1, 3):
            output = engine.transform_text(test_input)
            
            print(f"  [Run #{i}] Behavior Trigger: {output['behavior_description']}")
            if output['response_delay'] > 0:
                print(f"            Delay Simulation: Pause for {output['response_delay']}s...")
            print(f"            Spoken Text     : \"{output['speakable_text']}\"")
            print(f"            OLED Face       : {output['hardware_signals']['led_expression']}")
            print(f"            Motor Action    : {output['hardware_signals']['animation_trigger']}")
            print("  " + "-" * 50)