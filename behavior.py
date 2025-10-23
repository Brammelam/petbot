import random
from pet_frames import PET_FRAMES
from state import save_state
from utils import DEFAULT_PEN_HEIGHT, DEFAULT_PEN_WIDTH

def say_hello(state):
    if state["hunger"] > 6:
        speak(state, "Snacktime?")
    else:
        speak(state, "Meow❤️" if state["species"] == "cat" else "Oink❤️")

def speak(state, text, duration = 3):
    state["speech"] = text
    state["message_timer"] = duration

def update_behavior(state):
    """Handle switching between resting, wandering, and sleeping."""
    state["behavior_timer"] -= 1

    if state["behavior_timer"] <= 0:
        # Decide next behavior based on energy
        if state["energy"] < 3:
            state["behavior"] = "sleeping"
            state["behavior_timer"] = random.randint(30, 80)
        else:
            # 70% chance to rest, 30% chance to wander
            state["behavior"] = random.choices(
                ["resting", "wandering"],
                weights=[0.7, 0.3],
                k=1
            )[0]
            state["behavior_timer"] = random.randint(8, 25)

        # Reset wandering target when switching behaviors
        if state["behavior"] != "wandering":
            state["target_x"] = None
            state["target_y"] = None

    # Clamp position inside pen
    state["pos_x"] = max(1, min(DEFAULT_PEN_WIDTH - 8, state["pos_x"]))
    state["pos_y"] = max(1, min(DEFAULT_PEN_HEIGHT - 2, state["pos_y"]))

def update_wandering(state, pen_width, pen_height):
    """Move Cat toward a random target, or stay still if resting."""
    if state["behavior"] != "wandering":
        return  # Do nothing when resting, sleeping, or playing

    # If we don't yet have a destination, choose one
    if state["target_x"] is None or state["target_y"] is None:
        margin = 2
        state["target_x"] = random.randint(margin, pen_width - 8)
        state["target_y"] = random.randint(margin, pen_height - 2)
        return

    # Move one step toward target
    if state["pos_x"] < state["target_x"]:
        state["pos_x"] += 1
        state["pos_x"] = int(state["pos_x"])
        state["direction"] = "right"
    elif state["pos_x"] > state["target_x"]:
        state["pos_x"] -= 1
        state["pos_x"] = int(state["pos_x"])
        state["direction"] = "left"

    if state["pos_y"] < state["target_y"]:
        state["pos_y"] += 1
        state["pos_y"] = int(state["pos_y"])
    elif state["pos_y"] > state["target_y"]:
        state["pos_y"] -= 1
        state["pos_y"] = int(state["pos_y"])

    # Reached target? Rest for a while
    if abs(state["pos_x"] - state["target_x"]) <= 1 and abs(state["pos_y"] - state["target_y"]) <= 1:
        state["behavior"] = "resting"
        state["behavior_timer"] = random.randint(8, 20)
        state["target_x"] = None
        state["target_y"] = None


def update_ball(state, pen_width):
    """Simplified play logic: approach ball, slap it away, then rest."""
    if state["ball_state"] == "gone":
        return

    # Sleepy?
    if state["energy"] < 2:
        state["ball_state"] = "gone"
        state["behavior"] = "sleeping"
        speak(state, "So sleepy..")
        return

    # Wait briefly before approaching
    if state.get("play_delay_timer", 0) > 0:
        state["play_delay_timer"] -= 1
        if state["ball_x"] is not None:
            state["direction"] = "right" if state["ball_x"] > state["pos_x"] else "left"
        return

    # --- Approach the ball (horizontal only) ---
    if state["behavior"] == "playing" and state["ball_state"] == "idle":
        dx = state["ball_x"] - state["pos_x"]

        # Move horizontally toward the ball
        if abs(dx) > 1:
            step = 2 if abs(dx) > 4 else 1
            state["pos_x"] += step if dx > 0 else -step
            state["direction"] = "right" if dx > 0 else "left"

        # Slap when close enough
        if abs(dx) <= 4:
            species_frames = PET_FRAMES.get(state["species"], PET_FRAMES["cat"])
            state["action_mode"] = "slap"
            state["action_timer"] = len(species_frames.get("slap", []))
            state["ball_state"] = "flying"
            state["ball_dir"] = 1 if state["direction"] == "right" else -1
            state["message"] = f'🎾 {state["name"]} bats the ball!'
            speak(state, "Mow!" if state["species"] == "cat" else "Ree!")
            return

    # --- Ball flying away ---
    if state["ball_state"] == "flying":
        state["ball_x"] += state["ball_dir"] * 2
        if state["ball_x"] < 0 or state["ball_x"] > pen_width:
            state["ball_state"] = "gone"
            state["behavior"] = "resting"
            state["target_x"] = None
            state["target_y"] = None
            state["message"] = f'😸 {state["name"]} looks pleased!'
            speak(state, "Miauw!" if state["species"] == "cat" else "Oink!")

def act(state, action):
    if action == "play":
        state["behavior"] = "playing" 
        state["energy"] = max(0, state["energy"] - 0.5)
        state["happiness"] = min(10, state["happiness"] + 2)
    elif action == "feed":
        state["hunger"] = max(0, state["hunger"] - 3)
        state["energy"] = min(10, state["energy"] + 0.2)
        state["happiness"] = min(10, state["happiness"] + 1)
    elif action == "pet":
        state["happiness"] = min(10, state["happiness"] + 1)
        state["energy"] = min(10, state["energy"] + 0.05)
    save_state(state)

def update_speech(state):
    """Reduce message timer and clear speech when expired."""
    if state.get("message_timer", 0) > 0:
        state["message_timer"] -= 1
        if state["message_timer"] <= 0:
            state["speech"] = ""

