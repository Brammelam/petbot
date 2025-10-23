import json, random
from datetime import datetime
from utils import DEFAULT_PEN_WIDTH, STATE_FILE

def load_state():
    """Load pet state or initialize defaults."""
    state = None
    print(STATE_FILE)
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
        "last_seen": datetime.now().isoformat(),
    }
    for k, v in defaults.items():
        state.setdefault(k, v)
    return state

def save_state(state):
    state["last_seen"] = datetime.now().isoformat()
    STATE_FILE.write_text(json.dumps(state, indent=2))

def update_emotions(state):
    """Update hunger, happiness, and energy based on time away."""
    try:
        last = datetime.fromisoformat(state["last_seen"])
        hours = (datetime.now() - last).total_seconds() / 3600

        # Hunger decreases gradually (gets hungrier)
        state["hunger"] = max(0, state["hunger"] + hours * 0.3)

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
