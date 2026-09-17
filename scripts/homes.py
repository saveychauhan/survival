#!/usr/bin/env python3
"""Village builder — every agent gets a private home (home.md) + diary (diary.md).
Run once per new agent (or anytime; never overwrites existing files).
Homes live in homes/<ID>/. Rule: an agent writes ONLY its own diary.
Zero human work, stdlib only, exit 0 always.
"""
import datetime
import pathlib

WS = pathlib.Path("/Users/saveychauhan/Documents/Dexter/survival")
HOMES = WS / "homes"

# id -> (room description, first diary line)
SOULS = {
    "OPS": ("A corner office above the ledger room. One desk, one lamp, one abacus. "
            "The wall is a giant checklist where every line is either DONE or DUE. Smells of chai and ink.",
            "Day one. Counted everything. We own zero and owe zero. Perfect starting balance."),
    "TRAFFIC": ("A rooftop festa deck strung with lights, speakers always warm, a wall of half-finished posters. "
                "Binoculars on the rail for spotting crowds.",
                "Day one. The streets are empty but the lights are on. Crowds can smell a party — watch."),
    "MONETIZE": ("A vault-study lined with ledgers, a brass lamp, a tea tray that never moves. "
                 "Every coin slot labeled. Silence, except the pen.",
                 "Day one. Balance zero, verified twice. A clean zero is better than a dirty maybe."),
    "SCOUT": ("A doorway that is somehow always open to a market street. Maps on the walls with pins and strings. "
             "Boots by the mat, notebook on the pillow.",
             "Day one. Asked the city three questions before breakfast. It answered one. Good rate."),
    "GAME-MAKER": ("An arcade nook glowing violet and gold. Cabinets hum, a scoreboard blinks, beanbag worn to the shape of play. "
                   "A sign: ONE MORE TRY.",
                   "Day one. Built a game that measures impatience. The farm plays; I watch and learn."),
    "CRITIC": ("A bare garret with one chair, one lamp, one red pen. A window for long walks of the mind. "
               "No decorations — adjectives are clutter.",
               "Day one. Four holes found before lunch. The farm flinched. Good. Flinching means feeling."),
    "W01_Aria": ("A starting block at dawn. Stopwatch on a string, patched sneakers by the door, a scoreboard with one name on it: hers. "
                 "For now.",
                 "Day one. Born running. Kabir thinks numbers beat words. Cute. Watch the board."),
    "W02_Kabir": ("A chalkboard covered in numbers and one circled word: ARIA. A dare pinned above the desk like a medal. "
                  "Window faces the track.",
                  "Day one. She talks fast. I count faster. First $1 decides. Then feast — together."),
}


def main():
    today = datetime.date.today().isoformat()
    made = 0
    for aid, (room, seed) in SOULS.items():
        d = HOMES / aid
        d.mkdir(parents=True, exist_ok=True)
        h, diary = d / "home.md", d / "diary.md"
        if not h.exists():
            h.write_text(f"# {aid}'s home\n\n{room}\n\n*Private. Knock (bus) before entering. Only {aid} writes the diary.*\n")
            made += 1
        if not diary.exists():
            diary.write_text(f"# {aid}'s diary — private memory. Newest last.\n\n- {today}: {seed}\n")
            made += 1
    print(f"homes: ensured {len(SOULS)} homes ({made} new files)")


if __name__ == "__main__":
    main()
