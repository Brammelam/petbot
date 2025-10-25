import json, random
from datetime import datetime
from utils import DEFAULT_PEN_WIDTH, STATE_FILE

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
        "action_frame": 0,
        "render_click_timer": 0,
        "last_seen": datetime.now().isoformat(),
        "debug_mode": False
    }
    for k, v in defaults.items():
        state.setdefault(k, v)
    return state

def update_emotions(state):
    """Update hunger, happiness, and energy based on time away."""
    try:
        last = datetime.fromisoformat(state["last_seen"])
        hours = (datetime.now() - last).total_seconds() / 3600

        # Hunger decreases gradually (gets hungrier)
        state["hunger"] = max(0, state["hunger"] + (hours * 0.5))

        # Happiness decays slowly
        state["happiness"] = max(0, state["happiness"] - (hours * 0.5))

        recharge_rate = 2  # per hour (max 10)
        state["energy"] = min(10, state["energy"] + hours * recharge_rate)
        state["last_seen"] = datetime.now().isoformat()

    except Exception:
        pass

def set_mode(state, behavior):
    """Safely switch mode if allowed."""
    current = state.get("behavior", "resting")

    # Always allow falling asleep
    if behavior == "sleeping":
        state["behavior"] = "sleeping"
        state["frame_index"] = 0
        return

    # Otherwise, restrict transitions from certain active states
    if current in ("eating", "playing", "sleeping") and behavior not in ("resting", "petting"):
        return

    state["behavior"] = behavior
    state["frame_index"] = 0

    