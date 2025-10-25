import curses
from pet_frames import PET_FRAMES
from state import set_mode
from utils import STATE_FILE, safe_addstr, DEFAULT_PEN_HEIGHT, DEFAULT_PEN_WIDTH

# ---------------------------
# Individual draw helpers
# ---------------------------

def get_color_for_value(value):
    """Return a curses color pair index based on value level (0–10)."""
    if value < 4:
        return curses.color_pair(1)  # red
    elif value < 7:
        return curses.color_pair(2)  # yellow
    else:
        return curses.color_pair(3)  # green
    
def draw_name(stdscr, state):
    safe_addstr(stdscr, 0, 2, f'{state["name"]} the {state["species"]}')

def draw_pen(stdscr, top, height, width):
    stdscr.attron(curses.color_pair(4))
    safe_addstr(stdscr, top, 0, "+" + "-" * width + "+")
    for y in range(top + 1, top + height):
        safe_addstr(stdscr, y, 0, "|" + " " * width + "|")
    safe_addstr(stdscr, top + height, 0, "+" + "-" * width + "+")
    stdscr.attroff(curses.color_pair(4))


def draw_pet(stdscr, state, top, height, width, frame):
    pet_x = int(min(max(1, state["pos_x"]), width - len(frame)))
    pet_y = int(top + 1 + min(max(0, state["pos_y"]), height - 2))
    safe_addstr(stdscr, pet_y, pet_x + 1, frame)


def draw_ball(stdscr, state, top):
    if state["ball_state"] != "gone" and state["ball_x"] is not None:
        y = int(top + 1 + min(max(0, state["ball_y"]), DEFAULT_PEN_HEIGHT - 2))
        x = int(max(1, min(DEFAULT_PEN_WIDTH - 2, state["ball_x"])) + 1)
        safe_addstr(stdscr, y, x, "🎾")


def draw_stats(stdscr, state, top, height):
    y = top + height + 2

    def bar(val):
        v = max(0, min(10, int(val)))
        return "▓" * v + "░" * (10 - v)

    # Hunger bar: inverse logic (lower hunger = good)
    hunger_value = 10 - state["hunger"]
    hunger_color = get_color_for_value(hunger_value)
    happiness_color = get_color_for_value(state["happiness"])
    energy_color = get_color_for_value(state["energy"])

    stdscr.attron(hunger_color)
    safe_addstr(stdscr, y, 2, f"Hunger:    {bar(hunger_value)}")
    stdscr.attroff(hunger_color)

    stdscr.attron(happiness_color)
    safe_addstr(stdscr, y + 1, 2, f"Happiness: {bar(state['happiness'])}")
    stdscr.attroff(happiness_color)

    stdscr.attron(energy_color)
    safe_addstr(stdscr, y + 2, 2, f"Energy:    {bar(state['energy'])}")
    stdscr.attroff(energy_color)


def draw_speech_bubble(stdscr, state, width):
    """Draw a speech bubble above the pet when there's a message."""
    msg = state.get("speech", "")
    if not msg or not msg.strip():
        return

    bubble_width = min(len(msg) + 2, width - 2)
    bubble_x = max(1, min(width - bubble_width - 2, int(state["pos_x"])))
    bubble_y = int(state["pos_y"])+1  # place slightly above pet

    stdscr.attron(curses.color_pair(2))
    safe_addstr(stdscr, bubble_y, bubble_x, f"{msg[:bubble_width]}")
    stdscr.attroff(curses.color_pair(2))

def draw_instructions(stdscr, pen_top, pen_height):
    y = pen_top + pen_height + 6
    safe_addstr(stdscr, y, 2,
        "Controls\n"
        "  [f]  feed\n"
        "  [p]  play\n"
        "  [t]  pet\n"
        "  [n]  name\n"
        "  [s]  switch species\n"
        "  [q]  quit\n"
    )

def draw_click_target(stdscr, state, pen_top, render=False):
    if state.get("render_click_timer", 0) > 0:
        if state.get("target_x") is None or state.get("target_y") is None:
            return
        safe_addstr(stdscr, int(state["target_y"] + pen_top), int(state["target_x"]), "x")

def update_animation(state):
    """Advance animation frame for the current behavior."""
    behavior = state.get("behavior", "resting")
    species = state.get("species", "cat")
    frames = PET_FRAMES.get(species, PET_FRAMES["cat"])

    frame_list = []
    if behavior == "eating":
        frame_list = frames.get("eat", [])
    elif behavior == "playing":
        frame_list = frames.get("play", [])
    elif behavior == "sleeping":
        frame_list = frames.get("sleep", [])
    elif behavior == "wandering":
        direction = state.get("direction", "right")
        frame_list = frames.get("walk_right" if direction == "right" else "walk_left", [])
    else:
        frame_list = frames.get("resting", [])

    if not frame_list:
        return
    
    frame_index = state.get("frame_index", 0) + 1
    state["frame_index"] = frame_index

    if behavior == "eating" and frame_index >= len(frame_list):
        set_mode(state, "resting")
        return

    state["frame_index"] %= len(frame_list)

# ---------------------------
# Master draw pipeline
# ---------------------------

def draw_frame(stdscr, state):
    """Render all visual elements for the current frame."""
    pen_top = 1
    pen_height = DEFAULT_PEN_HEIGHT
    pen_width = DEFAULT_PEN_WIDTH

    species = state.get("species", "cat")
    frames = PET_FRAMES.get(species, PET_FRAMES["cat"])
    behavior = state.get("behavior", "resting")

    if behavior == "sleeping":
        frame_list = frames["sleep"]
    elif behavior == "playing":
        frame_list = frames["play"]
    elif behavior == "eating":
        frame_list = frames["eat"]
    elif behavior == "wandering":
        frame_list = frames["walk_right"] if state["direction"] == "right" else frames["walk_left"]
    else:
        frame_list = frames["resting"]

    local_index = state.get("frame_index", 0)
    frame = frame_list[local_index % len(frame_list)]

    draw_name(stdscr, state)
    draw_pen(stdscr, pen_top, pen_height, pen_width)
    draw_pet(stdscr, state, pen_top, pen_height, pen_width, frame)
    draw_speech_bubble(stdscr, state, pen_width)
    draw_ball(stdscr, state, pen_top)
    draw_stats(stdscr, state, pen_top, pen_height)
    draw_instructions(stdscr, pen_top, pen_height)
    draw_click_target(stdscr, state, pen_top)

    if state.get("debug_mode", False):
        safe_addstr(stdscr, 25, 2, f"statefile:   {str(STATE_FILE)}")
        safe_addstr(stdscr, 26, 2, f"behavior:    {state.get('behavior', '')}")
        safe_addstr(stdscr, 27, 2, f"frame_index: {state.get('frame_index', 0)}")

    stdscr.refresh()
