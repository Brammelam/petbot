import curses
import random
from behavior import act, speak
from state import set_mode
from utils import prompt_for_name, AVAILABLE_SPECIES, DEFAULT_PEN_WIDTH, DEFAULT_PEN_HEIGHT, save_state, toggle_debug_mode

def handle_input(stdscr, key, state):
    """Handle player input and return (keep_running, new_action_mode)."""    

    if key in (ord("q"), ord("Q")):
        save_state(state)
        return False
    
    elif key in (ord("n"), ord("N")):
            new_name = prompt_for_name(stdscr, state)
            if new_name:
                state["name"] = new_name
                speak(state, f"Me {new_name}!")
                save_state(state)
    elif key in (ord("d"), ord("D")):
        toggle_debug_mode(state)
    
    elif key in (ord("f"), ord("F")):
        act(state, "feed")

    elif key in (ord("p"), ord("P")):
        if state.get("behavior") in ("eating", "sleeping", "playing"):
            speak(state, "Busy...")
            return True

        act(state, "play")
        spawn_ball_opposite_side(state, DEFAULT_PEN_WIDTH)

    elif key in (ord("t"), ord("T")):
        act(state, "pet")

    elif key in (ord("s"), ord("S")):
        switch_species(state)
    
    elif key == curses.KEY_MOUSE:
        try:
            _, mx, my, _, _ = curses.getmouse()
            handle_mouse_click(mx, my, state)
        except curses.error:
            pass

    return True

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
    state["ball_state"] = "resting"
    state["play_delay_timer"] = random.randint(3, 6)

def handle_mouse_click(mx, my, state):    
    """Handle mouse click — move pet if inside pen."""
    pen_top = 1
    pen_bottom = pen_top + DEFAULT_PEN_HEIGHT
    pen_left = 1
    pen_right = DEFAULT_PEN_WIDTH

    # If click is near the pet, treat it as petting
    pet_x = int(state["pos_x"]) + 1
    pet_y = int(pen_top + 1 + state["pos_y"]) 
    if abs(mx - pet_x) < 5 and abs(my - pet_y) < 3:
        speak(state, "pet")
        state["happiness"] = min(10, state["happiness"] + 1)
        return

    # Check if click is inside the pen area
    if pen_top < my < pen_bottom and pen_left < mx < pen_right:
        if state.get("behavior") == "sleeping":
            speak(state, "sleepy")
            return
        state["target_x"] = mx
        state["target_y"] = my - pen_top  # adjust for pen offset
        set_mode(state, "wandering")
        state["behavior_timer"] = 10  # let it walk for a bit
        speak(state, "..")
        state["render_click_timer"] = 2
        return

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
