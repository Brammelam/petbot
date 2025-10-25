#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import curses, time
from state import load_state, update_emotions
from behavior import update_behavior, update_wandering, update_ball, update_speech, say_hello
from render import draw_frame, update_animation
from game_actions import handle_input
from utils import DEFAULT_PEN_HEIGHT, DEFAULT_PEN_WIDTH, init_colors, save_state

FPS = 1.5

speed_map = {
    "playing": 0.3,
    "wandering": 0.3,
    "eating": 0.5,
    "sleeping": 0.8,
    "resting": 1 / FPS
}

def main(stdscr):
    curses.curs_set(0)
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    curses.mouseinterval(0)
    init_colors()
    stdscr.nodelay(True)
    state = load_state()
    state["frame_index"] = 0 # reset always
    state["ball_state"] = "gone" # reset always
    update_emotions(state)
    
    say_hello(state)

    try:
        while True:
            stdscr.clear()
            update_behavior(state)
            update_wandering(state, DEFAULT_PEN_WIDTH, DEFAULT_PEN_HEIGHT)
            update_ball(state, DEFAULT_PEN_WIDTH)
            update_speech(state)
            update_animation(state)
            draw_frame(stdscr, state)

            # --- Input handling ---
            key = stdscr.getch()
            if key != -1:
                keep_running = handle_input(stdscr, key, state)
                if not keep_running:
                    break

            # --- Timing ---
            time.sleep(speed_map.get(state["behavior"], 1 / FPS))

            if state.get("render_click_timer", 0) > 0:
               state["render_click_timer"] = max(0, state.get("render_click_timer", 0) - 1)

    finally:
        save_state(state)

if __name__ == "__main__":
    curses.wrapper(main)
