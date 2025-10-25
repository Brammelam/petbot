PET_FRAMES = {
    "cat": {
        "resting": [
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
            "/ᐠ-˕-マ",
            "/ᐠ-˕-マz",
            "/\_˕_マzZ",
            "/ᐠ-˕-マz",
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
        ]
    },
    "pig":{
        "resting": [
            "(՞• Ꙫ•՞)",      # default
            "(՞- Ꙫ-՞)",      # blink
            "(՞• Ꙫ•՞)",      # open eyes
            "(՞•Ꙫ •՞)",      # look other way
            "(՞• Ꙫ•՞)",      # reset
            "(՞• Ꙫ•՞)",      # hold still
            "(՞^ Ꙫ^՞)",      # blink again
            "(՞• Ꙫ•՞)",      # reset
        ],
        "walk_right": [
            " (՞• Ꙫ•՞)",     # lean right
            "  (՞• Ꙫ•՞)",     # step
            "   (՞- Ꙫ-՞)",    # lean further right
            " (՞• Ꙫ•՞)",     # center
        ],
        "walk_left": [
            "(՞•Ꙫ •՞) ",     # lean left
            "(՞•Ꙫ •՞) ",     # step
            "(՞-Ꙫ -՞)  ",    # lean further left
            "(՞•Ꙫ •՞) ",     # center
        ],
        "sleep": [
            "(՞¯ Ꙫ¯՞)",
            "(՞– Ꙫ–՞)z",
            "(՞– Ꙫ–՞)zZ",
            "(՞– Ꙫ-՞)z",
        ],
        "eat": [
            "(՞• Ꙫ•՞)🍣",   # notice food
            "(՞◔ Ꙫ◔՞)🍣",   # first bite
            "(՞◕ Ꙫ◕՞)🍱",   # munching
            "(՞◔ Ꙫ◔՞)🍱",   # swallow
            "(՞• Ꙫ•՞)",     # satisfied
        ],
        "play": [
            "(՞• Ꙫ•՞)",      # neutral
            "(՞•Ꙫ •՞) ",      # excited / pounce
            "(՞• Ꙫ•՞)",      # paw out
            " (՞^ Ꙫ^՞)",    # lower paw
            "(՞• Ꙫ•՞)",      # reset
        ],
        "slap": [
            "(՞• Ꙫ•՞)",      # neutral
            "(՞◔ Ꙫ◔՞) ɞ",   # slap!
            "(՞◕ Ꙫ◕՞)ɞ",    # follow-through
            "(՞• Ꙫ•՞)",      # reset
        ],
    }
}

def get_frames(state, action_mode):
    
    """Return the correct frame set based on species, behavior, and action."""
    species = state.get("species", "cat")
    species_frames = PET_FRAMES.get(species, PET_FRAMES["cat"])

    # 1️⃣ Sleeping always overrides everything
    if state["behavior"] == "sleeping":
        return species_frames["sleep"]

    # 2️⃣ Action-specific overrides (feed, slap, play)
    if action_mode == "feed":
        return species_frames.get("eat", species_frames["resting"])
    elif action_mode == "slap":
        return species_frames.get("slap", species_frames["play"])
    elif action_mode == "play":
        return species_frames.get("play", species_frames["resting"])

    # 3️⃣ Movement (wandering)
    if state["behavior"] == "wandering":
        direction = state.get("direction", "right")
        if direction == "right":
            return species_frames.get("walk_right", species_frames["resting"])
        else:
            return species_frames.get("walk_left", species_frames["resting"])

    # 4️⃣ Default: idle
    return species_frames["resting"]
