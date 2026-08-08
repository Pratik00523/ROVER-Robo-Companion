import time
import queue
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class MotorCommand:
    action: str        # e.g., "SERVO_HEAD_PITCH", "SERVO_HEAD_YAW", "WHEEL_MOTOR"
    target_value: int  # Angle (0-180) or Speed (-100 to 100)
    duration_ms: int   # Execution duration in milliseconds

class BehaviorEngine:
    def __init__(self):
        # Priority Queue: Lower number = higher priority
        # Format: (priority_level, creation_time, animation_name, sequence)
        self.action_queue = queue.PriorityQueue()
        self.current_animation = None
        
        # Predefined animation sequences (Motor script lookup matrix)
        self.animation_matrix: Dict[str, List[MotorCommand]] = {
            "FAST_HEAD_TILT_AND_WAG": [
                MotorCommand("SERVO_HEAD_PITCH", 110, 200),
                MotorCommand("SERVO_HEAD_YAW", 45, 150),
                MotorCommand("SERVO_HEAD_YAW", 135, 150),
                MotorCommand("SERVO_HEAD_YAW", 90, 100),
                MotorCommand("SERVO_HEAD_PITCH", 90, 150),
            ],
            "SLOW_HEAD_TURN": [
                MotorCommand("SERVO_HEAD_YAW", 120, 800),
                MotorCommand("SERVO_HEAD_PITCH", 70, 500),
                MotorCommand("SERVO_HEAD_YAW", 90, 800),
            ],
            "PRECISION_NOD": [
                MotorCommand("SERVO_HEAD_PITCH", 105, 150),
                MotorCommand("SERVO_HEAD_PITCH", 90, 150),
                MotorCommand("SERVO_HEAD_PITCH", 105, 150),
                MotorCommand("SERVO_HEAD_PITCH", 90, 150),
            ],
            "IDLE_SWAY": [
                MotorCommand("SERVO_HEAD_YAW", 85, 1000),
                MotorCommand("SERVO_HEAD_YAW", 95, 1000),
            ],
            "EMERGENCY_STOP": [
                MotorCommand("WHEEL_MOTOR", 0, 0),
                MotorCommand("SERVO_HEAD_PITCH", 90, 100),
            ]
        }

    def trigger_animation(self, animation_name: str, priority: int = 2) -> bool:
        """
        Adds an animation sequence to the priority queue.
        Priority Levels:
          1 = High Priority (Collision, User Command, Expression Reaction)
          2 = Normal Priority (Dialogue Speech Sync)
          3 = Low Priority (Idle background movements)
        """
        if animation_name in self.animation_matrix:
            sequence = self.animation_matrix[animation_name]
            # Priority Queue tuple: (priority, timestamp, name, sequence)
            self.action_queue.put((priority, time.time(), animation_name, sequence))
            return True
        else:
            print(f"[BEHAVIOR WARNING] Unknown animation trigger: {animation_name}")
            return False

    def process_next_action(self) -> Dict[str, Any]:
        """
        Pulls the highest priority animation sequence and executes/simulates 
        the step-by-step motor hardware pulses.
        """
        if self.action_queue.empty():
            # Trigger idle movement if queue is empty
            self.trigger_animation("IDLE_SWAY", priority=3)

        priority, created_at, anim_name, sequence = self.action_queue.get()
        self.current_animation = anim_name

        executed_steps = []
        for step in sequence:
            # Here is where you would send actual PWM/Serial commands to physical servos/motors
            executed_steps.append({
                "hardware_target": step.action,
                "value": step.target_value,
                "delay_ms": step.duration_ms
            })

        return {
            "active_animation": anim_name,
            "priority_level": priority,
            "motor_steps_count": len(executed_steps),
            "execution_sequence": executed_steps
        }


# --- TEST EXECUTION BLOCK ---
if __name__ == "__main__":
    behavior_system = BehaviorEngine()

    print("\n=======================================================")
    print("      TESTING BEHAVIOR & ANIMATION SELECTION ENGINE    ")
    print("=======================================================")

    # 1. Queue a low-priority idle motion
    behavior_system.trigger_animation("IDLE_SWAY", priority=3)
    
    # 2. Queue a high-priority face detection reaction (Dog fast tilt)
    behavior_system.trigger_animation("FAST_HEAD_TILT_AND_WAG", priority=1)

    # 3. Queue a normal-priority speech nod
    behavior_system.trigger_animation("PRECISION_NOD", priority=2)

    # Process queue items (Priority 1 will execute before Priority 2 and 3)
    print("\n[SYSTEM] Executing queued hardware animations in priority order:\n")
    
    step_num = 1
    while not behavior_system.action_queue.empty():
        result = behavior_system.process_next_action()
        print(f"--- Action #{step_num} ---")
        print(f"Animation Name : {result['active_animation']} (Priority {result['priority_level']})")
        print(f"Motor Steps    : {result['motor_steps_count']} steps")
        for idx, cmd in enumerate(result['execution_sequence'], 1):
            print(f"   Step {idx}: Set {cmd['hardware_target']} -> {cmd['value']} (hold {cmd['delay_ms']}ms)")
        print()
        step_num += 1