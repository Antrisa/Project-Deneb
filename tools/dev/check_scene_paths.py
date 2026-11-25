"""Checks every cutscene in the given maps against those maps as they are now (no game run): each person's
start and each walk's end is on open floor (else says where the game will nudge them), and every walk has a way
round the furniture (the game walks a straight line, through things, when it finds none). Written 24 Nov for the
mess hall, common room and shops rebuilt in tools/public_rooms.py.
    python3 tools/dev/check_scene_paths.py [map ...]      (default: mess common bram weaver armoury)"""
import json, re, sys
from collections import deque
src = open('scripts/map_data.gd', encoding='utf-8').read()
ROOMS = sys.argv[1:] or ['mess', 'common', 'bram', 'weaver', 'armoury']
maps = {}
for key in ROOMS:
    i = src.index('"%s": {' % key, src.index('const AREAS'))
    def rows(tag):
        a = src.index('"%s": [' % tag, i); return json.loads(re.sub(r',\s*\]$', ']', src[a + len(tag) + 4:src.index(']', a) + 1]))
    maps[key] = (rows('floor'), rows('obj'))
WALK = set('.shafkoteuj')
def open_(key, x, y):
    F, O = maps[key]
    return 0 <= y < len(F) and 0 <= x < len(F[0]) and F[y][x] in WALK and O[y][x] != 'x'
def stand(key, t):
    if open_(key, *t): return t
    for r in range(1, 4):
        for ox, oy in ((0, -r), (-r, 0), (r, 0), (0, r), (-r, -r), (r, -r), (-r, r), (r, r)):
            if open_(key, t[0] + ox, t[1] + oy): return (t[0] + ox, t[1] + oy)
    return None
def path(key, a, b):
    if a == b: return [a]
    prev = {a: None}; q = deque([a])
    while q:
        c = q.popleft()
        if c == b:
            out = []
            while c: out.append(c); c = prev[c]
            return out[::-1]
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (c[0] + dx, c[1] + dy)
            if n not in prev and open_(key, *n): prev[n] = c; q.append(n)
    return None
s = open('scripts/heart_events.gd').read()
starts = [(m.start(), m.group(1)) for m in re.finditer(r'^\t"(\w+)": \{', s, re.M)]
tok = re.compile(r'"area": "(?P<area>\w+)"|\["go", "(?P<go>\w+)", (?P<gx>-?\d+), (?P<gy>-?\d+)'
                 r'|"player": \[(?P<px>-?\d+), (?P<py>-?\d+)'
                 r'|"cast": \[(?P<cast>(?:\[[^\[\]]*\],?\s*)+)\]'
                 r'|\["(?P<cmd>place|walk)", "(?P<cn>[^"]+)", (?P<cx>-?\d+), (?P<cy>-?\d+)'
                 r'|\["walks", \[(?P<walks>(?:\[[^\[\]]*\],?\s*)+)\]\]')
problems, checked = [], 0
for k, (st, name) in enumerate(starts):
    en = starts[k + 1][0] if k + 1 < len(starts) else len(s)
    blk = s[st:en]; cur = None; pos = {}
    for m in tok.finditer(blk):
        if m.group('area'):
            cur = m.group('area'); pos = {}; continue
        if m.group('go'):
            cur = m.group('go'); pos = {}
            if cur in maps: pos['player'] = stand(cur, (int(m.group('gx')), int(m.group('gy'))))
            continue
        if cur not in maps: continue
        def place(who, x, y, how):
            t = stand(cur, (x, y))
            if t is None: problems.append((name, cur, how, who, (x, y), 'nowhere to stand')); return
            if t != (x, y): problems.append((name, cur, how, who, (x, y), 'nudged to %s' % (t,)))
            pos[who] = t
        def walk(who, x, y):
            global checked
            t = stand(cur, (x, y))
            if t is None: problems.append((name, cur, 'walk', who, (x, y), 'nowhere to stand')); return
            if t != (x, y): problems.append((name, cur, 'walk', who, (x, y), 'nudged to %s' % (t,)))
            if who not in pos: problems.append((name, cur, 'walk', who, (x, y), 'starts unplaced (from their usual spot)'))
            if who in pos:
                checked += 1
                if path(cur, pos[who], t) is None: problems.append((name, cur, 'walk', who, (x, y), 'NO PATH from %s' % (pos[who],)))
            pos[who] = t
        if m.group('px') is not None: place('player', int(m.group('px')), int(m.group('py')), 'start')
        elif m.group('cast'):
            for c in re.findall(r'\["([^"]+)", (-?\d+), (-?\d+)', m.group('cast')): place(c[0], int(c[1]), int(c[2]), 'cast')
        elif m.group('cmd') == 'place': place(m.group('cn'), int(m.group('cx')), int(m.group('cy')), 'place')
        elif m.group('cmd') == 'walk': walk(m.group('cn'), int(m.group('cx')), int(m.group('cy')))
        elif m.group('walks'):
            for c in re.findall(r'\["([^"]+)", (-?\d+), (-?\d+)\]', m.group('walks')): walk(c[0], int(c[1]), int(c[2]))
print('walks checked:', checked)
for p in problems: print(p)
print('all clear' if not problems else '%d problem(s)' % len(problems))
