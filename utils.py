import curses
from pathlib import Path

DEFAULT_PEN_WIDTH = 25
DEFAULT_PEN_HEIGHT = 10
STATE_FILE = Path.home() / "petbot_state.json"
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
