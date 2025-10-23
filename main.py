#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import curses, time, random
from state import load_state, save_state, update_emotions
from behavior import update_behavior, update_wandering, update_ball, update_speech, say_hello
from render import draw_frame
from game_actions import handle_input
from pet_frames import get_frames
from utils import DEFAULT_PEN_HEIGHT, DEFAULT_PEN_WIDTH

FPS = 1

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    state = load_state()
    update_emotions(state)
    frame_index = 0
    action_mode = "idle"
    say_hello(state)

    try:
        while True:
            stdscr.clear()

            update_wandering(state, DEFAULT_PEN_WIDTH, DEFAULT_PEN_HEIGHT)
            update_ball(state, DEFAULT_PEN_WIDTH)
            update_speech(state)
            if frame_index % 3 == 0:  # every 3 frames regardless of FPS
                update_behavior(state)

            frames = get_frames(state, action_mode)
            frame_to_draw = frames[state.get("action_frame", 0) % len(frames)]
            draw_frame(stdscr, state, [frame_to_draw], frame_index, DEFAULT_PEN_WIDTH)

            key = stdscr.getch()
            if key != -1:
                keep_running, action_mode = handle_input(stdscr, key, state, action_mode)
                if not keep_running:
                    break
            if state["behavior"] == "playing":
                time.sleep(0.5)
            else:
                time.sleep(1 / FPS)
            
            if state.get("action_timer", 0) > 0:
                state["action_timer"] -= 1
                state["action_frame"] += 1
                if state["action_frame"] >= len(frames):
                    action_mode = "idle"
                    state["action_timer"] = 0
                    state["action_frame"] = 0
            else:
                state["action_frame"] = 0
            frame_index += 1
    finally:
        save_state(state)

if __name__ == "__main__":
    curses.wrapper(main)
