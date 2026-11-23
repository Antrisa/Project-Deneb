"""Check the heart events (scripts/heart_events.gd) against the built map data, without Godot.

Every event: its area exists; the player's start, the cast's spots and every walk target are open floor that can
be reached from the station; every pose is drawn (a row of the resident's heart-event sheet, or of their action
sheet); every step is one the cutscene knows; emotes and portrait tags exist; lines fit the dialogue box.
An event with a backup place is checked at both places; a "go" step moves the check to its map.
Run from the repo: python3 tests/check_heart_events.py
"""
import ast
import re
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def gd_consts(path):
    """The const values of a GDScript file whose consts are plain data (JSON-like literals)."""
    out = {}
    src = path.read_text()
    for m in re.finditer(r'^const (\w+)(?:\s*:=|\s*=)\s*', src, flags=re.M):
        start = m.end()
        depth, i, in_str, esc = 0, start, False, False
        while i < len(src):
            ch = src[i]
            if in_str:
                if esc: esc = False
                elif ch == '\\': esc = True
                elif ch == '"': in_str = False
            elif ch == '"': in_str = True
            elif ch == '#':
                i = src.index('\n', i)
                continue
            elif ch in '[{(': depth += 1
            elif ch in ']})': depth -= 1
            elif ch == '\n' and depth == 0: break
            i += 1
        text = src[start:i]
        text = re.sub(r'#[^\n"]*$', '', text, flags=re.M)          # comments (not inside strings on these lines)
        text = re.sub(r'\bnull\b', 'None', text).replace('true', 'True').replace('false', 'False')
        try:
            out[m.group(1)] = ast.literal_eval(text)
        except (ValueError, SyntaxError):
            pass
    return out


md = gd_consts(ROOT / 'scripts/map_data.gd')
he = gd_consts(ROOT / 'scripts/heart_events.gd')
A, SOLID, OPEN = md['AREAS'], md['SOLID_FLOOR'], md['OPEN_OBJ']
ACTION_ROWS = md['ACTION_ROWS']
RESIDENTS = set(md['SCHEDULES'])
EVENTS, ORDER = he['EVENTS'], he['ORDER']
EVENT_ROWS = ["talk", "laugh", "sad", "jump", "gift", "bench", "wave"]
EMOTES = {"surprise", "question", "love", "joy", "sad", "frustrated", "hello", "ready", "no", "wait", "help", "follow", "cute"}
TAGS = {"neutral", "happy", "sad", "surprised", "love", "angry", "shocked", "bashful"}
STEPS = {"say", "place", "go", "walk", "walks", "face", "pose", "emote", "wait", "fade", "shake", "sfx", "clock", "choose",
         "if", "flag", "friendship", "perk", "keepsake", "partner", "toast"}
SOUNDS = {p.stem for p in (ROOT / 'audio').glob('*.wav')}
DIRS = {"d", "u", "l", "r"}


def walkable(a, x, y):
    f, o = A[a]['floor'], A[a]['obj']
    return 0 <= y < len(f) and 0 <= x < len(f[0]) and f[y][x] not in SOLID and (o[y][x] == ' ' or o[y][x] in OPEN)


start = tuple(md['START'])
seen = {start}
q = deque([start])
while q:
    a, x, y = q.popleft()
    nxt = [(a, x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
    for (wx, wy, dest, tx, ty) in A[a]['warps']:
        if (wx, wy) == (x, y):
            nxt = [(dest, tx, ty)]
    for nb in nxt:
        if nb not in seen and walkable(*nb):
            seen.add(nb)
            q.append(nb)


def event_sheet(who):
    return (ROOT / 'art' / ('npc_%s_event.png' % who.lower().replace("'", "").replace('.', ''))).exists()


problems = []
count = {"steps": 0, "lines": 0}


def bad(ev_id, msg):
    problems.append("%s: %s" % (ev_id, msg))


def check_spot(ev_id, area, x, y, what):
    if (area, x, y) not in seen:
        bad(ev_id, "%s at %s (%d,%d) is not open floor you can reach" % (what, area, x, y))


def check_pose(ev_id, who, pose):
    if pose == "" or who == "player":
        return
    name = pose.split(" ")[0]
    if name in EVENT_ROWS and event_sheet(who):
        return
    if pose not in ACTION_ROWS.get(who, []):
        bad(ev_id, "%s has no pose %r (no heart-event sheet row or action row)" % (who, pose))


def check_steps(ev_id, ev, steps, area=None, known=None):
    """known: story flags taken as set (True) or not (False) when an "if" tests them, e.g. the flag a backup place
    stands in for; the other branch is then not checked here. Returns the area the steps end in ("go")."""
    area = area or ev['area']
    known = known or {}
    for s in steps:
        count["steps"] += 1
        op = s[0]
        if op not in STEPS:
            bad(ev_id, "unknown step %r" % op)
            continue
        if op in ("place", "walk", "face", "pose", "emote") and s[1] not in RESIDENTS and s[1] != "player":
            bad(ev_id, "%s: %r is not a resident" % (op, s[1]))
        if op == "say":
            if s[1] and s[1] not in RESIDENTS and s[1] != "Sensors":
                bad(ev_id, "say: %r is not a resident" % s[1])
            for line in s[2]:
                count["lines"] += 1
                m = re.match(r'^\[(\w+)\] ', line)
                if m and m.group(1) not in TAGS:
                    bad(ev_id, "unknown portrait tag [%s]" % m.group(1))
                text = line[m.end():] if m else line
                if len(text) > 150:
                    bad(ev_id, "line over 150 characters: %r" % text[:60])
        elif op == "go":
            if s[1] not in A:
                bad(ev_id, "go: no area %r" % s[1])
                continue
            area = s[1]
            check_spot(ev_id, area, s[2], s[3], "the player's place after go")
            if s[4] not in DIRS: bad(ev_id, "go: facing %r" % s[4])
        elif op == "place":
            check_spot(ev_id, area, s[2], s[3], "%s's place" % s[1])
            if s[4] not in DIRS: bad(ev_id, "place: facing %r" % s[4])
        elif op == "walk":
            check_spot(ev_id, area, s[2], s[3], "%s's walk" % s[1])
        elif op == "walks":
            for w in s[1]:
                check_spot(ev_id, area, w[1], w[2], "%s's walk" % w[0])
        elif op == "face":
            if s[2] not in DIRS and s[2] not in RESIDENTS and s[2] != "player":
                bad(ev_id, "face: %r is neither a direction nor a person" % s[2])
        elif op == "pose":
            check_pose(ev_id, s[1], s[2])
        elif op == "emote":
            if s[2] not in EMOTES: bad(ev_id, "unknown emote %r" % s[2])
        elif op == "sfx":
            if s[1] not in SOUNDS: bad(ev_id, "no sound %r in audio/" % s[1])
        elif op == "choose":
            if not 2 <= len(s[1]) <= 4: bad(ev_id, "a choice needs 2 to 4 options")
            for o in s[1]:
                if len(o.get("text", "")) > 64: bad(ev_id, "choice text too long for the menu: %r" % o["text"])
                check_steps(ev_id, ev, o.get("steps", []), area, known)
        elif op == "if":
            if not set(s[1]) <= {"flag", "not_flag", "arrived", "partner", "dating_other"}:
                bad(ev_id, "if: unknown condition %r" % s[1])
            f = s[1].get("flag", s[1].get("not_flag"))
            if f in known:
                taken = known[f] if "flag" in s[1] else not known[f]
                if taken: check_steps(ev_id, ev, s[2], area, known)
                elif len(s) > 3: check_steps(ev_id, ev, s[3], area, known)
                continue
            check_steps(ev_id, ev, s[2], area, known)
            if len(s) > 3: check_steps(ev_id, ev, s[3], area, known)
    return area


for ev_id in ORDER:
    if ev_id not in EVENTS:
        bad(ev_id, "in ORDER but not in EVENTS")
for ev_id, ev in EVENTS.items():
    if ev_id not in ORDER:
        bad(ev_id, "not in ORDER, so it never plays")
    if ev['area'] not in A:
        bad(ev_id, "no area %r" % ev['area'])
        continue
    if ev['who'] not in RESIDENTS:
        bad(ev_id, "%r is not a resident" % ev['who'])
    for need in ev.get('seen', []):
        if need not in EVENTS: bad(ev_id, "seen: no event %r" % need)
    for w in ev.get('windows', []):
        if not (re.match(r'^\d\d:\d\d$', w[1]) and re.match(r'^\d\d:\d\d$', w[2]) and w[1] < w[2]):
            bad(ev_id, "window %r" % (w,))
    # an event with a backup place is checked twice: at its own place with the backup's flag set, and at the
    # backup place without it
    places = [(ev, {})]
    if 'backup' in ev:
        b = ev['backup']
        if b.get('area') not in A:
            bad(ev_id, "backup: no area %r" % b.get('area'))
            continue
        merged = dict(ev)
        merged.update({k: v for k, v in b.items() if k != 'unless'})
        places = [(ev, {b['unless']: True}), (merged, {b['unless']: False})]
    for pev, known in places:
        p = pev.get('player')
        if p: check_spot(ev_id, pev['area'], p[0], p[1], "the player's start")
        taken = {}
        for c in pev.get('cast', []):
            check_spot(ev_id, pev['area'], c[1], c[2], "%s's start" % c[0])
            if (c[1], c[2]) in taken or (p and (c[1], c[2]) == (p[0], p[1])):
                bad(ev_id, "%s starts on a tile someone else has" % c[0])
            taken[(c[1], c[2])] = c[0]
            if len(c) > 4: check_pose(ev_id, c[0], c[4])
        check_steps(ev_id, pev, pev['steps'], pev['area'], known)

if problems:
    print("\n".join("FAIL: " + p for p in problems))
    raise SystemExit(1)
print("PASS: %d heart events, %d steps, %d lines: places reachable, poses drawn, steps and lines valid."
      % (len(EVENTS), count["steps"], count["lines"]))
