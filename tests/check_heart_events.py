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
ITEMS = gd_consts(ROOT / 'scripts/item_data.gd').get('ITEMS', {})
LETTERS = gd_consts(ROOT / 'scripts/mail_data.gd').get('LETTERS', {})
he = gd_consts(ROOT / 'scripts/heart_events.gd')
A, SOLID, OPEN = md['AREAS'], md['SOLID_FLOOR'], md['OPEN_OBJ']
ACTION_ROWS = md['ACTION_ROWS']
RESIDENTS = set(md['SCHEDULES'])
EVENTS, ORDER = he['EVENTS'], he['ORDER']
SCENES = he.get('SCENES', {})   # story scenes that aren't heart events (your first morning): checked the same way
_story = gd_consts(ROOT / 'scripts/story_scenes.gd')
assert 'SCENES' in _story, "scripts/story_scenes.gd: SCENES didn't parse (write paths out in full, no consts in it)"
SCENES = dict(SCENES, **_story['SCENES'])   # the main story (24 Nov): the prologue, the Custodians
EVENT_ROWS = ["talk", "laugh", "sad", "jump", "gift", "bench", "wave"]
EMOTES = {"surprise", "question", "love", "joy", "sad", "frustrated", "hello", "ready", "no", "wait", "help", "follow", "cute"}
TAGS = {"neutral", "happy", "sad", "surprised", "love", "angry", "shocked", "bashful"}
STEPS = {"say", "place", "go", "met", "walk", "walks", "face", "pose", "emote", "wait", "fade", "shake", "sfx", "clock", "choose",
         "if", "flag", "friendship", "perk", "keepsake", "partner", "toast", "hide", "show", "ship", "sky", "energy", "fx", "sara",
         "give", "mail", "board", "bsprite", "bmove", "bmoves", "bfade", "flash"}
VOICES = {"Sensors", "Sara", "Ivan", "MotherDrone", "Chancellor", "Sovereign", "Forgemaster", "Harbinger", "Shepherd", "Warden"}   # who may speak without being a resident (portraits by name)
FX = {"bees", "fireflies", "steam", "heartbeats", "spray", "bubbles"}   # scripts/scene_fx.gd
SARA_CLIPS = set(re.findall(r'"name": "(\w+)"', (ROOT / 'sara/animations_data.gd').read_text()))
SPECIAL = {"Sara"}   # S.A.R.A.: a hologram on her pads (MapData.PEOPLE), not a walking resident
SEASONS = {"Spring", "Summer", "Autumn", "Winter"}
SKIES = {"clear", "eclipse", "gas_cloud", "meteors", "transit", "aurora", "comet", "storm"}   # scripts/lounge_sky.gd
# main.gd only loads the sounds it names (SOUND_NAMES, SHIP_SOUNDS) that have a file: audio/<name>.ogg or .wav, or
# takes audio/<name>_1.ogg, _2.ogg ... (_sound_stream). Anything else plays nothing.
_main_src = (ROOT / 'scripts' / 'main.gd').read_text()
def _const_names(name):
    m = re.search(r'^const %s := \[(.*?)\]' % name, _main_src, re.S | re.M)
    return re.findall(r'"([a-z_0-9]+)"', m.group(1)) if m else []
SOUNDS = {s for s in _const_names('SOUND_NAMES') + _const_names('SHIP_SOUNDS')
          if any((ROOT / 'audio' / f).exists() for f in (s + '.ogg', s + '.wav', s + '_1.ogg'))}
DIRS = {"d", "u", "l", "r"}


def walkable(a, x, y):
    f, o = A[a]['floor'], A[a]['obj']
    return 0 <= y < len(f) and 0 <= x < len(f[0]) and f[y][x] not in SOLID and (o[y][x] == ' ' or o[y][x] in OPEN)


start = tuple(md['START'])
seen = {start}
q = deque([start])
if 'TIDELIGHT' in md:                     # Tidelight is reached by shuttle, not a warp (tools/tidelight.py)
    tl = ('tidelight', md['TIDELIGHT']['landing'][0], md['TIDELIGHT']['landing'][1])
    seen.add(tl)
    q.append(tl)
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
board_ids = set()   # the sprites on a scene's picture board so far


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
        if op in ("place", "walk", "face", "pose", "emote", "hide", "show") and s[1] not in RESIDENTS and s[1] != "player" \
                and not (op == "emote" and s[1] in SPECIAL):
            bad(ev_id, "%s: %r is not a resident" % (op, s[1]))
        if op == "say":
            if s[1] and s[1] not in RESIDENTS and s[1] not in VOICES:
                bad(ev_id, "say: %r is not a resident" % s[1])
            for line in s[2]:
                count["lines"] += 1
                m = re.match(r'^\[(\w+)\] ', line)
                if m and m.group(1) not in TAGS:
                    bad(ev_id, "unknown portrait tag [%s]" % m.group(1))
                text = line[m.end():] if m else line
                if len(text) > 150:
                    bad(ev_id, "line over 150 characters: %r" % text[:60])
        elif op in ("board", "bsprite"):
            path = s[1] if op == "board" else s[2]
            if path and not (ROOT / path.replace("res://", "")).exists():
                bad(ev_id, "%s: no picture %s" % (op, path))
            if op == "bsprite":
                if path: board_ids.add(s[1])
                else: board_ids.discard(s[1])
        elif op in ("bmove", "bfade"):
            if s[1] not in board_ids: bad(ev_id, "%s: no sprite %r on the board" % (op, s[1]))
        elif op == "bmoves":
            for m in s[1]:
                if m[0] not in board_ids: bad(ev_id, "bmoves: no sprite %r on the board" % m[0])
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
        elif op == "ship":
            if s[1] not in ("lift", "land"): bad(ev_id, "ship: %r is neither lift nor land" % s[1])
            if area != "bay": bad(ev_id, "ship: your ship is only in the Shuttle Bay, not %r" % area)
        elif op == "sara":
            if s[1] == "place":
                check_spot(ev_id, area, s[2], s[3], "S.A.R.A.'s projection")
            elif s[1] not in SARA_CLIPS:
                bad(ev_id, "sara: no hologram clip %r" % s[1])
        elif op == "fx":
            if s[1] not in FX: bad(ev_id, "fx: no effect %r" % s[1])
            f = A[area]['floor']
            if s[2:] == ["off"]: pass   # stops it
            elif not (0 <= s[3] < len(f) and 0 <= s[2] < len(f[0])): bad(ev_id, "fx: (%d,%d) is off the map" % (s[2], s[3]))
        elif op == "give":
            if s[1] not in ITEMS: bad(ev_id, "give: no item %r in scripts/item_data.gd" % s[1])
            if not (isinstance(s[2], int) and s[2] > 0): bad(ev_id, "give: %r should be a count above 0" % s[2])
        elif op == "mail":
            if s[1] not in LETTERS: bad(ev_id, "mail: no letter %r in scripts/mail_data.gd" % s[1])
            if len(s) > 2 and not (isinstance(s[2], int) and s[2] >= 0): bad(ev_id, "mail: %r should be a number of mornings" % s[2])
        elif op == "energy":
            if not (isinstance(s[1], int) and s[1] < 0): bad(ev_id, "energy: %r should be a small cost, a negative number" % s[1])
        elif op == "sky":
            if s[1] not in SKIES: bad(ev_id, "sky: no sky event %r" % s[1])
            if area != "lounge": bad(ev_id, "sky: only the Observation Lounge has the window, not %r" % area)
        elif op == "choose":
            if not 2 <= len(s[1]) <= 4: bad(ev_id, "a choice needs 2 to 4 options")
            for o in s[1]:
                if len(o.get("text", "")) > 64: bad(ev_id, "choice text too long for the menu: %r" % o["text"])
                check_steps(ev_id, ev, o.get("steps", []), area, known)
        elif op == "if":
            if not set(s[1]) <= {"flag", "not_flag", "arrived", "partner", "dating_other", "has"}:
                bad(ev_id, "if: unknown condition %r" % s[1])
            if "has" in s[1] and s[1]["has"] not in ITEMS:
                bad(ev_id, "if: no item %r in scripts/item_data.gd" % s[1]["has"])
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
for ev_id in SCENES:
    if ev_id in EVENTS:
        bad(ev_id, "is both a heart event and a story scene")
def _all_steps(steps, out):
    for s in steps:
        if isinstance(s, dict):
            _all_steps(s.get('steps', []), out)
        elif isinstance(s, list) and s and isinstance(s[0], str):
            out.append(s)
            if s[0] == 'choose':
                for o in s[1]:
                    _all_steps(o.get('steps', []), out)
            elif s[0] == 'if':
                for branch in s[2:]:
                    _all_steps(branch, out)


for ev_id, ev in list(EVENTS.items()) + list(SCENES.items()):
    if ev_id not in ORDER and ev_id not in SCENES:
        bad(ev_id, "not in ORDER, so it never plays")
    if ev['area'] == 'here' and ev_id in SCENES:
        # a story scene that plays wherever you are (the Harbinger's random cavern floor): nobody is placed or
        # walked, so there is no map to check against
        st = []
        _all_steps(ev['steps'], st)
        for s_ in st:
            if s_[0] in ('place', 'walk', 'walks', 'go') or (s_[0] == 'face' and s_[2] not in DIRS):
                bad(ev_id, "an \"area\": \"here\" scene can't %s" % s_[0])
        board_ids.clear()
        head = ([["board", ev['board']]] + ev.get('board_setup', [])) if ev.get('board') else []
        check_steps(ev_id, dict(ev, area='mine'), head + [s_ for s_ in ev['steps'] if s_[0] not in ('place', 'walk', 'walks', 'go')], 'mine')
        continue
    if ev['area'] not in A:
        bad(ev_id, "no area %r" % ev['area'])
        continue
    if ev['who'] not in RESIDENTS and ev['who'] not in SPECIAL:
        bad(ev_id, "%r is not a resident" % ev['who'])
    for w in ev.get('with', []):
        if w not in RESIDENTS: bad(ev_id, "with: %r is not a resident" % w)
    for se in ev.get('seasons', []):
        if se not in SEASONS: bad(ev_id, "seasons: %r is not a season" % se)
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
        board_ids.clear()
        if pev.get('board'):
            check_steps(ev_id, pev, [["board", pev['board']]] + pev.get('board_setup', []), pev['area'], known)
        check_steps(ev_id, pev, pev['steps'], pev['area'], known)

# The Custodians (scripts/custodian_data.gd, 24 Nov): every bundle item is an item, every voice has a portrait,
# every fix is one main.gd knows, and the order lists them all.
CUST = gd_consts(ROOT / 'scripts' / 'custodian_data.gd')
assert 'CUSTODIANS' in CUST, "scripts/custodian_data.gd didn't parse"
FIXES = {"", "sprinklers", "storage", "orchard", "hotel_wing", "kiosks", "gates", "suite", "shipyard", "storm_plating",
         "braced", "primed", "blast", "storm_ends", "tl_market", "tl_beacon", "warden_home"}
if sorted(CUST['ORDER']) != sorted(CUST['CUSTODIANS']):
    bad("custodians", "ORDER and CUSTODIANS differ")
for cid, c in CUST['CUSTODIANS'].items():
    if not (ROOT / 'art' / ('portrait_%s.png' % c['voice'].lower())).exists():
        bad("custodians", "%s: no portrait art/portrait_%s.png" % (cid, c['voice'].lower()))
    if c['voice'] not in VOICES:
        bad("custodians", "%s: voice %r isn't in the checker's VOICES" % (cid, c['voice']))
    ids = set()
    for b in c['bundles']:
        if b['id'] in ids: bad("custodians", "%s: two bundles called %r" % (cid, b['id']))
        ids.add(b['id'])
        if b['fixes'] not in FIXES: bad("custodians", "%s/%s: unknown fix %r" % (cid, b['id'], b['fixes']))
        for item, n in b['items'].items():
            if item not in ITEMS: bad("custodians", "%s/%s: no item %r" % (cid, b['id'], item))
            if not (isinstance(n, int) and n > 0): bad("custodians", "%s/%s: %r count %r" % (cid, b['id'], item, n))
        if len(b['items']) > 4: bad("custodians", "%s/%s: more than 4 items won't fit the Relics page" % (cid, b['id']))
    for key in ('hello', 'thanks', 'done'):
        for line in c[key]:
            text = re.sub(r'^\[\w+\] ', '', line)
            if len(text) > 150: bad("custodians", "%s: %s line over 150 characters" % (cid, key))

# The datapad's Perks tab (scripts/perk_data.gd): every perk and keepsake an event gives has its entry and an icon
# in art/perks.png, and the icon numbers run 0 to ICON_COUNT - 1 with none shared.
PERK_DATA = gd_consts(ROOT / 'scripts' / 'perk_data.gd')
_given = {'perk': set(), 'keepsake': set()}


def _gives(steps):
    for s in steps:
        if isinstance(s, dict):
            _gives(s.get('steps', []))
            continue
        if isinstance(s, list) and s and isinstance(s[0], str) and s[0] in _given:
            _given[s[0]].add(s[1])
        for x in (s[1:] if isinstance(s, list) else []):
            if isinstance(x, list):
                _gives([x] if x and not isinstance(x[0], list) else x)
            elif isinstance(x, dict):
                for v in x.values():
                    if isinstance(v, list):
                        _gives(v)


for _ev in list(EVENTS.values()) + list(SCENES.values()):
    _gives(_ev['steps'])
for kind, table in (('perk', 'PERKS'), ('keepsake', 'KEEPSAKES')):
    for pid in sorted(_given[kind] - set(PERK_DATA[table])):
        problems.append("perk_data.gd: the %s %r has no %s entry (the datapad's Perks tab)" % (kind, pid, table))
_icons = [int(v['icon']) for tbl in ('PERKS', 'KEEPSAKES') for v in PERK_DATA[tbl].values()]
if sorted(_icons) != list(range(int(PERK_DATA['ICON_COUNT']))):
    problems.append("perk_data.gd: icon numbers must run 0 to ICON_COUNT - 1, each used once")
try:
    from PIL import Image
    if Image.open(ROOT / 'art' / 'perks.png').width < 24 * int(PERK_DATA['ICON_COUNT']):
        problems.append("art/perks.png has fewer icons than perk_data.gd needs (tools/dev/perk_icons.py)")
except ImportError:
    pass

# Staged like a Stardew cutscene (Zachary, 24 Nov: "npcs move and do actions as well as character using emotes and
# text boxes"): every heart event has someone moving (a resident walks, or S.A.R.A. plays her clips), the player
# reacting at least once, two resident emotes, and a pose (S.A.R.A. is a hologram and can't pose).
staged = 0
for ev_id, ev in EVENTS.items():
    st = []
    _all_steps(ev['steps'], st)
    moves = sum(1 for s in st if s[0] == 'walk' and s[1] != 'player') + \
        sum(1 for s in st if s[0] == 'walks' for w in s[1] if w[0] != 'player') + sum(1 for s in st if s[0] == 'sara')
    p_emotes = sum(1 for s in st if s[0] == 'emote' and s[1] == 'player')
    r_emotes = sum(1 for s in st if s[0] == 'emote' and s[1] != 'player')
    poses = sum(1 for s in st if s[0] == 'pose' and s[2] != '')
    short = []
    if moves < 1: short.append("nobody moves")
    if p_emotes < 1: short.append("the player never emotes")
    if r_emotes < 2: short.append("fewer than two resident emotes")
    if poses < 1 and ev['who'] != 'Sara': short.append("no poses")
    if short:
        bad(ev_id, "not staged: " + ", ".join(short))
    else:
        staged += 1

if problems:
    print("\n".join("FAIL: " + p for p in problems))
    raise SystemExit(1)
print("PASS: %d heart events and %d story scene(s), %d steps, %d lines: places reachable, poses drawn, steps and lines valid;"
      " all %d events staged (movement, emotes, poses)." % (len(EVENTS), len(SCENES), count["steps"], count["lines"], staged))
