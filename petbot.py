#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PetBot – Terminal Virtual Pet 🐾
Animated ASCII pet that walks around, reacts to you,
and remembers its mood between runs.

Controls
--------
[f]  feed
[p]  play
[t]  pet
[n]  name
[q]  quit

Requirements
------------
None – uses only Python standard library.
"""

import curses
import json
import random
import time
from pathlib import Path
from datetime import datetime

# --------------------------------------------------------------------------- #
#  Configuration
# --------------------------------------------------------------------------- #

STATE_FILE = Path.home() / "./petbot/petbot_state.json"
FPS = 1  # frames per second
DEFAULT_PEN_WIDTH = 20
DEFAULT_PEN_HEIGHT = 10

# --------------------------------------------------------------------------- #
#  Pet frames (using ^•ﻌ•^ style)
# --------------------------------------------------------------------------- #

PET_FRAMES = {
    "idle": [
    "^•ﻌ•^",      # default
    "^-ﻌ-^",      # blink
    "^•ﻌ•^",      # open eyes
    "^•ﻌ•^ฅ",     # small paw raise
    "^•ﻌ•^",      # reset
    "^•ﻌ•^",      # hold still
    "^-ﻌ-^",      # blink again
    "^•ﻌ•^",      # reset
],
    "walk_right": [
    " ^•ﻌ•^",     # lean right
    " ^-ﻌ-^",     # step
    "  ^•ﻌ•^",    # lean further right
    " ^•ﻌ•^",     # center
],

"walk_left": [
    "^•ﻌ•^ ",     # lean left
    "^-ﻌ-^ ",     # step
    "^•ﻌ•^  ",    # lean further left
    "^•ﻌ•^ ",     # center
],
    "sleep": [
        "/ᐠ-˕-マ💤",
        "/ᐠ-˕-マzZ",
        "/\_˕_マ💤",
        "/ᐠ-˕-マzZ",
    ],
    "eat": [
    "^•ﻌ•^🍣",   # notice food
    "^-ﻌ-^🍣",   # first bite
    "^>ﻌ<^🍱",   # munching
    "^•ﻌ•^🍱",   # swallow
    "^-ﻌ-^",     # satisfied
],
    "play": [
    "^•ﻌ•^",      # neutral
    "^>ﻌ<^",      # excited / pounce
    "^>ﻌ<ฅ",      # paw out
    "^-ﻌ-^ฅ",     # lower paw
    "^•ﻌ•^",      # reset
],
    "slap": [
    "^•ﻌ•^",      # neutral
    "^•ﻌ•^ฅ",     # paw ready
    "ฅ^-ﻌ-^",     # paw swing back
    " ^>ﻌ<^ ฅ",   # slap!
    " ^•ﻌ•^ฅ",    # follow-through
    "^•ﻌ•^",      # reset
],
}

# --------------------------------------------------------------------------- #
#  Persistence helpers
# --------------------------------------------------------------------------- #

def load_state():
    """Load pet state or initialize defaults."""
    state = None
    if STATE_FILE.exists():
        try:
            data = STATE_FILE.read_text().strip()
            if data:
                state = json.loads(data)
        except Exception:
            pass

    if not isinstance(state, dict):
        state = {}

    defaults = {
        "name": "Mochi",
        "species": "cat",
        "hunger": 3,
        "happiness": 7,
        "energy": 8,
        "behavior": "resting",
        "behavior_timer": 0,
        "action_timer": 0,
        "direction": "right",
        "pos_x": random.randint(5, DEFAULT_PEN_WIDTH - 10),
        "pos_y": random.randint(2, 8),
        "ball_x": None,
        "ball_y": None,
        "ball_dir": None,
        "ball_state": "gone",
        "target_x": None,
        "target_y": None,
        "pause_timer": 0,
        "play_delay_timer": 0,
        "message_timer": 0,
        "last_seen": datetime.now().isoformat(),
    }
    for k, v in defaults.items():
        state.setdefault(k, v)
    return state


def save_state(state):
    state["last_seen"] = datetime.now().isoformat()
    STATE_FILE.write_text(json.dumps(state, indent=2))


# --------------------------------------------------------------------------- #
#  Pet logic
# --------------------------------------------------------------------------- #
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
    if abs(state["pos_x"] - state["target_x"]) <= 0 and abs(state["pos_y"] - state["target_y"]) <= 0:
        state["behavior"] = "resting"
        state["behavior_timer"] = random.randint(8, 20)
        state["target_x"] = None
        state["target_y"] = None


def update_emotions(state):
    """Update hunger, happiness, and energy based on time away."""
    try:
        last = datetime.fromisoformat(state["last_seen"])
        hours = (datetime.now() - last).total_seconds() / 3600

        # Hunger increases gradually (gets hungrier)
        state["hunger"] = min(10, state["hunger"] + hours * 0.3)

        # Happiness decays slowly
        state["happiness"] = max(0, state["happiness"] - hours * 0.2)

        # Energy depends on time away:
        # - If energy was low, it recharges up to a cap
        # - If you left it for a long time, it fills up completely
        recharge_rate = 2  # per hour (so ~5h = full recovery)
        state["energy"] = min(10, state["energy"] + hours * recharge_rate)

        # Save this update timestamp
        state["last_seen"] = datetime.now().isoformat()

    except Exception:
        pass



def act(state, action):
    if action == "play":
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

# --------------------------------------------------------------------------- #
#  Rendering helpers
# --------------------------------------------------------------------------- #

def safe_addstr(stdscr, y, x, text):
    try:
        stdscr.addstr(y, x, text)
    except curses.error:
        pass


def draw_pen(stdscr, top, height, width):
    safe_addstr(stdscr, top, 0, "+" + "-" * width + "+")
    for y in range(top + 1, top + height):
        safe_addstr(stdscr, y, 0, "|" + " " * width + "|")
    safe_addstr(stdscr, top + height, 0, "+" + "-" * width + "+")


def draw_pet(stdscr, state, top, height, width, frame):
    pet_x = int(min(max(1, state["pos_x"]), width - len(frame)))
    pet_y = int(top + 1 + min(max(0, state["pos_y"]), height - 2))
    safe_addstr(stdscr, pet_y, pet_x + 1, frame)


def draw_stats(stdscr, state, top, height):
    y = top + height + 2
    def bar(val):
        v = max(0, min(10, int(val)))
        return "▓" * v + "░" * (10 - v)
    safe_addstr(stdscr, y, 2, f"Hunger:    {bar(10 - state['hunger'])}")
    safe_addstr(stdscr, y + 1, 2, f"Happiness: {bar(state['happiness'])}")
    safe_addstr(stdscr, y + 2, 2, f"Energy:    {bar(state['energy'])}")


def draw_message(stdscr, msg, top, height):
    y = top + height + 6
    safe_addstr(stdscr, y, 2, " " * 60)
    safe_addstr(stdscr, y, 2, msg[:60])

def draw_debug(stdscr, state, action_mode, pen_top, pen_height):
    """Show current behavior and animation state for debugging."""
    y = pen_top + pen_height + 10
    safe_addstr(stdscr, y, 2, " " * 80)
    debug_text = (
        f"[DEBUG] behavior={state['behavior']:>10} | "
        f"action={action_mode:>6} | timer={state.get('behavior_timer', 0):>3} | "
        f"target=({state.get('target_x')},{state.get('target_y')}) | "
        f"pause={state.get('pause_timer')}"
        
    )
    safe_addstr(stdscr, y, 2, debug_text)


def update_ball(state, pen_width):
    """Simplified play logic: approach ball, slap it away, then rest."""
    if state["ball_state"] == "gone":
        return
    
    if state["energy"] < 2:
        state["ball_state"] = "gone"
        state["behavior"] = "sleeping"
        state["message"] = f'💤 {state["name"]} got too sleepy to keep playing...'
        state["speech"] = "Zzz..."
        state["message_timer"] = 3
        return

    # Wait before moving toward the ball
    if state.get("play_delay_timer", 0) > 0:
        state["play_delay_timer"] -= 1
        if state["ball_x"] is not None:
            state["direction"] = "right" if state["ball_x"] > state["pos_x"] else "left"
        return

    # --- Approach the ball ---
    if state["behavior"] == "playing" and state["ball_state"] == "idle":
        dx = state["ball_x"] - state["pos_x"]
        dy = state["ball_y"] - state["pos_y"]

        # Move horizontally toward ball
        if abs(dx) > 0:
            step = 2 if abs(dx) > 3 else 1  # faster when far
            state["pos_x"] += step if dx > 0 else -step
            state["direction"] = "right" if dx > 0 else "left"

        # Reached ball?
        if abs(dx) <= 5 and abs(dy) <= 1:
            # Trigger slap animation and send the ball flying
            state["ball_state"] = "flying"
            state["ball_dir"] = 1 if state["direction"] == "right" else -1
            state["message"] = f'🎾 {state["name"]} bats the ball!'
            state["speech"] = 'Mow!'
            state["message_timer"] = 3
            state["action_mode"] = "slap"
            state["action_timer"] = len(PET_FRAMES["slap"])  # show all slap frames
            return

    # --- Ball flying away ---
    if state["ball_state"] == "flying":
        state["ball_x"] += state["ball_dir"] * 2

        # When ball leaves the pen, finish play
        if state["ball_x"] < 0 or state["ball_x"] > pen_width:
            state["ball_state"] = "gone"
            state["behavior"] = "resting"
            state["target_x"] = None
            state["target_y"] = None
            state["message"] = f'😸 {state["name"]} looks pleased!'
            state["message"] = 'Miauw!'
            state["message_timer"] = 3

def spawn_ball_opposite_side(state, pen_width, margin=3):
    """Spawn ball on the opposite side of cat, within pen bounds."""
    cat_x = state["pos_x"]
    is_left_side = cat_x < pen_width / 2

    if is_left_side:
        ball_x = random.randint(int(pen_width * 0.6), pen_width - (margin + 3))
        state["direction"] = "right"
    else:
        ball_x = random.randint(margin + 3, int(pen_width * 0.4))
        state["direction"] = "left"

    state["ball_x"] = ball_x
    state["ball_y"] = state["pos_y"]
    state["ball_state"] = "idle"
    state["ball_dir"] = random.choice([-1, 1])
    state["play_delay_timer"] = random.randint(3, 6)

def draw_ball(stdscr, state, top):
    if state["ball_state"] != "gone" and state["ball_x"] is not None:
        y = int(top + 1 + min(max(0, state["ball_y"]), DEFAULT_PEN_HEIGHT - 2))
        x = int(max(1, min(DEFAULT_PEN_WIDTH - 2, state["ball_x"]) + 1))
        safe_addstr(stdscr, y, x, "🎾")

def draw_speech_bubble(stdscr, state, width):
    """Draw a speech bubble above cat when there's a message."""
    msg = state.get("speech", "")
    if not msg or not msg.strip():
        return  # nothing to show

    bubble_width = min(len(msg) + 4, width - 4)
    bubble_x = int(state["pos_x"])
    bubble_y = int(state["pos_y"]+1)

    # Draw bubble outline
    safe_addstr(stdscr, bubble_y, bubble_x, f"{msg[:bubble_width]}")

def prompt_for_name(stdscr, prompt="Enter new name: "):
    """Prompt user for a new name."""
    curses.echo()
    stdscr.nodelay(False)  # Wait for user input
    stdscr.addstr(0, 0, " " * 60)
    stdscr.addstr(0, 0, prompt)
    stdscr.refresh()

    name = stdscr.getstr(0, len(prompt), 20).decode("utf-8").strip()
    curses.noecho()
    stdscr.nodelay(True)
    return name if name else None

# --------------------------------------------------------------------------- #
#  Animation loop
# --------------------------------------------------------------------------- #

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    state = load_state()
    if state.get("ball_state") != "gone":
        state["ball_state"] = "gone"
        state["ball_x"] = None
        state["ball_y"] = None
        state["ball_dir"] = None
    state["action_timer"] = 0
    state["play_delay_timer"] = 0
    state["message"] = ""
    state["speech"] = ""

    update_emotions(state)

    frame_index = 0
    action_mode = "idle"
    state["speech"] = "Purr~ 💕"
    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        pen_width = min(width - 4, DEFAULT_PEN_WIDTH)
        pen_height = DEFAULT_PEN_HEIGHT
        pen_top = 1

        # Random motion
        update_wandering(state, pen_width, pen_height)
        update_ball(state, pen_width)

        if state["behavior"] == "sleeping" and action_mode in ("play", "slap"):
            action_mode = "idle"

        # Choose frame set
        if state["behavior"] == "sleeping":
            frames = PET_FRAMES["sleep"]
        elif action_mode == "feed":
            frames = PET_FRAMES["eat"]
        elif action_mode == "slap":
            frames = PET_FRAMES["slap"]
        elif action_mode == "play":
            frames = PET_FRAMES["play"]
        elif state["behavior"] == "wandering":
            frames = PET_FRAMES["walk_right"] if state["direction"] == "right" else PET_FRAMES["walk_left"]
        else:
            frames = PET_FRAMES["idle"]

        frame = frames[frame_index % len(frames)]

        # Draw
        draw_pen(stdscr, pen_top, pen_height, pen_width)
        draw_pet(stdscr, state, pen_top, pen_height, pen_width, frame)
        draw_speech_bubble(stdscr, state, pen_width)
        draw_stats(stdscr, state, pen_top, pen_height)
        # draw_message(stdscr, state.get("message", message), pen_top, pen_height)
        # draw_debug(stdscr, state, action_mode, pen_top, pen_height)
        draw_ball(stdscr, state, pen_top)
        stdscr.refresh()
        frame_index += 1

        if frame_index % FPS == 0:
            update_behavior(state)

        # Autosave and idle emotion decay
        if frame_index % (FPS * 10) == 0:
            save_state(state)
            if state["behavior"] == "wandering":
                state["energy"] = max(0, state["energy"] - 0.1)
                state["hunger"] = min(10, state["hunger"] + 0.05)
            elif state["behavior"] == "resting":
                state["energy"] = min(10, state["energy"] + 0.05)
            elif state["behavior"] == "sleeping":
                state["energy"] = min(10, state["energy"] + 0.2)


        # Input
        key = stdscr.getch()
        if key != -1:
            if key in (ord("q"), ord("Q")):
                save_state(state)
                break
            elif key in (ord("f"), ord("F")):
                act(state, "feed")
                action_mode = "feed"
                state["action_timer"] = len(PET_FRAMES["eat"])
                state["speech"] = "Nom"
                state["message_timer"] = 3
            elif key in (ord("p"), ord("P")):
                act(state, "play")
                action_mode = "play"
                state["speech"] = "!"
                state["message_timer"] = 3
                state["behavior"] = "playing"
                spawn_ball_opposite_side(state, pen_width)
                state["ball_dir"] = random.choice([-1, 1])
                state["ball_state"] = "idle"
                state["play_delay_timer"] = random.randint(3, 6)
            elif key in (ord("t"), ord("T")):
                act(state, "pet")
                action_mode = "idle"
                state["speech"] = "🫶"
                state["message_timer"] = 3
            elif key in (ord("n"), ord("N")):
                new_name = prompt_for_name(stdscr)
                if new_name:
                    state["name"] = new_name
                    save_state(state)
                    message = f"🐾 Nice! Your cat is now named {new_name}!"
                    state["speech"] = f'Me {state["name"]}!'
                    state["message_timer"] = 3



        # Reset action animation after a short delay
        # Decrease action timer, and return to idle when done
        if state["action_timer"] > 0:
            state["action_timer"] -= 1
            if state["action_timer"] <= 0:
                action_mode = "idle"

        if state["ball_state"] == "gone" and state["behavior"] == "playing":
            state["behavior"] = "resting"
            state["speech"] = "Meow!"
            state["message_timer"] = 3

        if action_mode in ("play", "feed"):
            time.sleep(0.5)
        else:
            time.sleep(1 / FPS)
        
        if state["message_timer"] > 0:
            state["message_timer"] -= 1
        elif random.random() < 0.2:
            state["message"] = ""
            state["speech"] = ""



# --------------------------------------------------------------------------- #
#  Entry point
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    curses.wrapper(main)
