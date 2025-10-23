import random
from state import save_state
from behavior import act, speak
from utils import prompt_for_name, AVAILABLE_SPECIES, DEFAULT_PEN_WIDTH

from pet_frames import PET_FRAMES

def handle_input(stdscr, key, state, action_mode):
    """Handle player input and return (keep_running, new_action_mode)."""
    species = state.get("species", "cat")
    species_frames = PET_FRAMES.get(species, PET_FRAMES["cat"])

    if key in (ord("q"), ord("Q")):
        save_state(state)
        return False, action_mode

    elif key in (ord("f"), ord("F")):
        act(state, "feed")
        speak(state, "Nom")
        # ✅ animation lasts as long as the number of feed frames
        state["action_timer"] = len(species_frames.get("eat", []))
        return True, "feed"

    elif key in (ord("p"), ord("P")):
        act(state, "play")
        spawn_ball_opposite_side(state, DEFAULT_PEN_WIDTH)
        speak(state, "!")
        state["action_timer"] = len(species_frames.get("play", []))
        return True, "play"

    elif key in (ord("t"), ord("T")):
        act(state, "pet")
        speak(state, "Purr 💕" if state["species"] == "cat" else "Snort 💕")
        state["action_timer"] = len(species_frames.get("idle", []))  # short neutral loop
        return True, "pet"

    elif key in (ord("s"), ord("S")):
        switch_species(state)
        return True, "idle"

    elif key in (ord("n"), ord("N")):
        new_name = prompt_for_name(stdscr, state)
        if new_name:
            state["name"] = new_name
            speak(state, f"Me {new_name}!")
            save_state(state)
        return True, "idle"

    # No recognized input
    return True, action_mode

def spawn_ball_opposite_side(state, pen_width, margin=3):
    """Spawn the ball on the opposite side of the animal, within pen bounds."""
    cat_x = state["pos_x"]
    safe_left = margin + 3
    safe_right = pen_width - (margin + 3)
    middle = pen_width / 2

    if cat_x > middle:
        # Animal is on the right → spawn ball on left
        ball_x = random.randint(safe_left, int(pen_width * 0.3))
        state["direction"] = "left"
    else:
        # Animal is on the left → spawn ball on right
        ball_x = random.randint(int(pen_width * 0.7), safe_right)
        state["direction"] = "right"

    # Same row as the animal
    state["ball_x"] = ball_x
    state["ball_y"] = state["pos_y"]
    state["ball_state"] = "idle"
    state["play_delay_timer"] = random.randint(3, 6)


def switch_species(state):
    """Cycle between available pet species (cat, pig, etc.)."""
    current = state.get("species", "cat")
    idx = AVAILABLE_SPECIES.index(current) if current in AVAILABLE_SPECIES else 0
    next_species = AVAILABLE_SPECIES[(idx + 1) % len(AVAILABLE_SPECIES)]
    state["species"] = next_species

    # Feedback message
    if next_species == "cat":
        speak(state, "Meow!")
    elif next_species == "pig":
        speak(state, "Oink!")
    else:
        speak(state, f"✨ Turned into a {next_species}!")

    state["message_timer"] = 5
    save_state(state)
