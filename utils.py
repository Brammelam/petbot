import curses
from datetime import datetime
import json
from pathlib import Path

DEFAULT_PEN_WIDTH = 25
DEFAULT_PEN_HEIGHT = 10
STATE_FILE = Path.cwd() / "petbot_state.json"
AVAILABLE_SPECIES = ["cat", "pig"]

def safe_addstr(stdscr, y, x, text):
    try:
        stdscr.addstr(y, x, text)
    except curses.error:
        pass

def prompt_for_name(stdscr, state, prompt="Enter new name: "):
    """Prompt user for a new pet name using curses input."""
    curses.echo()
    stdscr.nodelay(False)  # allow blocking input
    stdscr.addstr(0, 0, " " * 60)
    stdscr.addstr(0, 0, prompt)
    stdscr.refresh()

    new_name = stdscr.getstr(0, len(prompt), 20).decode("utf-8").strip()

    curses.noecho()
    stdscr.nodelay(True)

    if new_name:
        state["name"] = new_name
        return new_name
    return None

def init_colors():
    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(1, curses.COLOR_RED, -1)
    curses.init_pair(2, curses.COLOR_YELLOW, -1)
    curses.init_pair(3, curses.COLOR_GREEN, -1)

    if curses.can_change_color():
        curses.init_color(4, 400, 400, 400)  
        curses.init_pair(4, 4, -1)
        pass


def save_state(state):
    state["last_seen"] = datetime.now().isoformat()
    STATE_FILE.write_text(json.dumps(state, indent=2))

def toggle_debug_mode(state):
    debug = state["debug_mode"]
    state["debug_mode"] = True if debug is False else False 