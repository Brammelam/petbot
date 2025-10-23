from utils import safe_addstr, DEFAULT_PEN_HEIGHT, DEFAULT_PEN_WIDTH

# ---------------------------
# Individual draw helpers
# ---------------------------

def draw_pen(stdscr, top, height, width):
    safe_addstr(stdscr, top, 0, "+" + "-" * width + "+")
    for y in range(top + 1, top + height):
        safe_addstr(stdscr, y, 0, "|" + " " * width + "|")
    safe_addstr(stdscr, top + height, 0, "+" + "-" * width + "+")


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

    safe_addstr(stdscr, y, 2, f"Hunger:    {bar(10 - state['hunger'])}")
    safe_addstr(stdscr, y + 1, 2, f"Happiness: {bar(state['happiness'])}")
    safe_addstr(stdscr, y + 2, 2, f"Energy:    {bar(state['energy'])}")


def draw_speech_bubble(stdscr, state, width):
    """Draw a speech bubble above the pet when there's a message."""
    msg = state.get("speech", "")
    if not msg or not msg.strip():
        return

    bubble_width = min(len(msg) + 2, width - 2)
    bubble_x = max(1, min(width - bubble_width - 2, int(state["pos_x"])))
    bubble_y = int(state["pos_y"])+1  # place slightly above pet

    safe_addstr(stdscr, bubble_y, bubble_x, f"{msg[:bubble_width]}")


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


# ---------------------------
# Master draw pipeline
# ---------------------------

def draw_frame(stdscr, state, frames, frame_index, width):
    """Render all visual elements for the current frame."""
    frame = frames[frame_index % len(frames)]
    pen_top = 1
    pen_height = DEFAULT_PEN_HEIGHT
    pen_width = DEFAULT_PEN_WIDTH  # ✅ use fixed width, not terminal width

    draw_pen(stdscr, pen_top, pen_height, pen_width)
    draw_pet(stdscr, state, pen_top, pen_height, pen_width, frame)
    draw_speech_bubble(stdscr, state, pen_width)
    draw_ball(stdscr, state, pen_top)
    draw_stats(stdscr, state, pen_top, pen_height)
    draw_instructions(stdscr, pen_top, pen_height)
    stdscr.refresh()
