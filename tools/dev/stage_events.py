"""Staging pass for the heart events (24 Nov 2026; Zachary: the cutscenes should be "animated like stardew cutscenes
npcs move and do actions as well as character using emotes and text boxes").

Where an event is short of them, it adds, from the lines' portrait tags and the map:
  - movement: at the main resident's first line standing, they come a step or two closer; if they're beside you
    already, at their first sad or shy line they step away and turn their back, then turn round; failing both, at the
    end they get up (if sitting) and come to stand beside you, or head off a couple of steps. Tiles are open floor
    you can reach, never one anyone else stands on or walks to in the event; backup places get their own tiles;
  - poses: a gift pose before a keepsake or perk, a jump for a surprised line, a laugh for a happy one with a "!",
    a sad pose for a sad one, else a talking pose (up to three in all), each put back after the line;
  - resident emotes from the first line's tag (love, surprise, frustrated, sad, cute), up to four in all;
  - the player's reactions (love after a confession at 8+ hearts, then surprise, sad or joy, from the last line's tag).
Edits scripts/heart_events.gd in place (text insertions; nothing else moves). Run it on new arcs, then read the
result and fix what reads oddly. tests/check_heart_events.py fails any event left unstaged.
Usage: python3 -I tools/dev/stage_events.py REPO [--dry]"""
import json, re, sys
from pathlib import Path
from collections import deque

REPO = Path(sys.argv[1]); DRY = '--dry' in sys.argv
src_path = REPO / 'scripts/heart_events.gd'
chk = (REPO / 'tests/check_heart_events.py').read_text()
d = {'__file__': str(REPO / 'tests/check_heart_events.py')}
exec(compile(chk[:chk.index('\ndef event_sheet')], 'chk', 'exec'), d)
EVENTS, A, seen, walkable = d['EVENTS'], d['A'], d['seen'], d['walkable']
def event_sheet(who):
    return (REPO / 'art' / ('npc_%s_event.png' % who.lower().replace("'", "").replace('.', ''))).exists()

TAG = re.compile(r'^\[(\w+)\]')
def tag_of(line):
    m = TAG.match(str(line)); return m.group(1) if m else ''
def lines_of(s):
    return s[2] if isinstance(s[2], list) else [s[2]]

EMOTE_FOR = {'love': 'love', 'surprised': 'surprise', 'shocked': 'surprise', 'angry': 'frustrated', 'sad': 'sad',
             'bashful': 'cute'}
EMOTE_PRI = {'love': 0, 'surprised': 1, 'shocked': 1, 'angry': 2, 'sad': 3, 'bashful': 4}

def is_resident(who):
    return who not in ('', 'player')

# ------------------------------------------------------------------ walking the steps
def walk_steps(steps, ctx, out, depth, top):
    """Visit steps in order. ctx: {'pose': {who: pose or None(unknown)}, 'pos': {who: (x,y)} for top-level known,
    'unknown': bool, 'gone': bool}. out collects visit records."""
    prev = None
    for idx, s in enumerate(steps):
        if isinstance(s, dict):
            continue
        op = s[0]
        rec = {'step': s, 'list': steps, 'idx': idx, 'depth': depth, 'top': top and not ctx['gone'] and not ctx['unknown'],
               'pose': dict(ctx['pose']), 'pos': dict(ctx['pos']), 'prev': prev}
        out.append(rec)
        if op == 'pose':
            ctx['pose'][s[1]] = s[2]
        elif op == 'place':
            ctx['pos'][s[1]] = (s[2], s[3])
        elif op == 'walk':
            ctx['pos'][s[1]] = (s[2], s[3])
        elif op == 'walks':
            for w in s[1]: ctx['pos'][w[0]] = (w[1], w[2])
        elif op == 'go':
            ctx['gone'] = True
        elif op == 'choose':
            for o in s[1]:
                sub = {'pose': dict(ctx['pose']), 'pos': dict(ctx['pos']), 'unknown': True, 'gone': ctx['gone']}
                walk_steps(o.get('steps', []), sub, out, depth + 1, False)
                # a choice that moves or poses someone leaves them unknown afterwards
                for who, p in sub['pose'].items():
                    if ctx['pose'].get(who, '') != p: ctx['pose'][who] = None
                if any(r['step'][0] in ('walk', 'walks', 'place', 'go') for r in out if r['step'] in o.get('steps', [])):
                    ctx['unknown'] = True
        elif op == 'if':
            for branch in s[2:]:
                sub = {'pose': dict(ctx['pose']), 'pos': dict(ctx['pos']), 'unknown': True, 'gone': ctx['gone']}
                walk_steps(branch, sub, out, depth + 1, False)
                for who, p in sub['pose'].items():
                    if ctx['pose'].get(who, '') != p: ctx['pose'][who] = None
                if any(isinstance(b, list) and b and b[0] in ('walk', 'walks', 'place', 'go') for b in branch):
                    ctx['unknown'] = True
        prev = s


def place_variants(ev):
    """[(flag or None, area, player (x,y), cast {who: (x,y,pose)})]: the event's place, and its backup."""
    out = []
    cast = {c[0]: (c[1], c[2], c[4] if len(c) > 4 else '') for c in ev.get('cast', [])}
    out.append((None, ev['area'], tuple(ev['player'][:2]) if 'player' in ev else None, cast))
    b = ev.get('backup')
    if b:
        bcast = {c[0]: (c[1], c[2], c[4] if len(c) > 4 else '') for c in b.get('cast', [])}
        out.append((b['unless'], b['area'], tuple(b['player'][:2]), bcast))
    return out


def free(area, x, y, taken):
    return (area, x, y) in seen and walkable(area, x, y) and (x, y) not in taken


def approach(area, r, p, taken):
    """A tile 1-2 steps from r toward p (straight), never onto p or next to nothing; None if no clean step."""
    rx, ry = r; px, py = p
    dist = abs(px - rx) + abs(py - ry)
    if dist < 2:
        return None
    dx, dy = px - rx, py - ry
    if abs(dx) >= abs(dy):
        step = (1 if dx > 0 else -1, 0)
    else:
        step = (0, 1 if dy > 0 else -1)
    n = 2 if dist >= 4 else 1
    path = [(rx + step[0] * k, ry + step[1] * k) for k in range(1, n + 1)]
    while path and not all(free(area, x, y, taken) for x, y in path):
        path = path[:-1]
    if not path or path[-1] == (px, py):
        return None
    return path[-1]


def step_away(area, r, p, taken):
    """1-2 tiles straight away from p (turning their back for a sad line), and the direction they then face."""
    rx, ry = r; px, py = p
    dx, dy = rx - px, ry - py
    options = []
    if abs(dx) >= abs(dy):
        options.append(((1 if dx >= 0 else -1, 0)))
        options += [(0, 1), (0, -1)]
    else:
        options.append((0, 1 if dy >= 0 else -1))
        options += [(1, 0), (-1, 0)]
    for st in options:
        for n in (2, 1):
            path = [(rx + st[0] * k, ry + st[1] * k) for k in range(1, n + 1)]
            if all(free(area, x, y, taken) for x, y in path):
                face = {(1, 0): 'r', (-1, 0): 'l', (0, 1): 'd', (0, -1): 'u'}[st]
                return path[-1], face
    return None


# ------------------------------------------------------------------ deciding
def plan(eid, ev):
    recs = []
    variants = place_variants(ev)
    pose0 = {}
    for who, (x, y, p) in variants[0][3].items():
        pose0[who] = p if all(v[3].get(who, (0, 0, p))[2] == p for v in variants) else None
    top_ctx = {'pose': dict(pose0), 'pos': {}, 'unknown': False, 'gone': False}
    walk_steps(ev['steps'], top_ctx, recs, 0, True)
    steps_flat = [r['step'] for r in recs]
    ins = []   # (record, 'before'|'after', [steps], why)
    R = ev['who']
    npc_walks = sum(1 for s in steps_flat if s[0] == 'walk' and s[1] != 'player') + \
        sum(sum(1 for w in s[1] if w[0] != 'player') for s in steps_flat if s[0] == 'walks')
    poses = sum(1 for s in steps_flat if s[0] == 'pose' and s[2] != '')
    emotes = sum(1 for s in steps_flat if s[0] == 'emote')
    p_emotes = sum(1 for s in steps_flat if s[0] == 'emote' and s[1] == 'player')
    says = [r for r in recs if r['step'][0] == 'say' and is_resident(r['step'][1])]
    # every tile anyone is placed on or walks to in this event: a new walk never ends on one
    later = set()
    for s in steps_flat:
        if s[0] in ('walk', 'place'): later.add((s[2], s[3]))
        elif s[0] == 'walks': later |= {(w[1], w[2]) for w in s[1]}
    used = set()   # ids of records that already got an insertion of the same kind

    # (a) movement: at the main resident's first line standing (pose ""), they come a step or two closer; or, if
    # they're already beside you, at their first sad or shy line they step away and turn their back, then turn round
    if npc_walks == 0 and R != 'Sara':
        for r in says:
            s = r['step']
            if s[1] != R or not r['top'] or r['depth'] != 0 or r['pose'].get(R, '') != '':
                continue
            t = tag_of(lines_of(s)[0])
            plans = []
            for (flag, area, pl, cast) in variants:
                if R not in cast:
                    plans = None; break
                rpos = tuple(r['pos'].get(R, cast[R][:2]))
                ppos = tuple(r['pos'].get('player', pl))
                taken = {tuple(v[:2]) for w, v in cast.items() if w != R} | {ppos} | later
                for w, v in r['pos'].items():
                    if w != R: taken.add(tuple(v))
                tgt = approach(area, rpos, ppos, taken)
                if tgt:
                    plans.append((flag, [["walk", R, tgt[0], tgt[1]], ["face", R, "player"], ["face", "player", R]], None))
                    continue
                aw = step_away(area, rpos, ppos, taken) if t in ('sad', 'bashful') else None
                if aw:
                    (tx, ty), face = aw
                    plans.append((flag, [["walk", R, tx, ty], ["face", R, face]], [["face", R, "player"]]))
                    continue
                plans = None; break
            if not plans:
                continue
            if len(plans) == 1:
                before, after = plans[0][1], plans[0][2]
            else:
                (fa, ba, aa), (fb, bb, ab) = plans[0], plans[1]
                before = [["if", {"flag": fb}, ba, bb]]
                after = [["if", {"flag": fb}, aa or [], ab or []]] if (aa or ab) else None
            ins.append((r, 'before', before, 'walk'))
            if after:
                ins.append((r, 'after', after, 'walk back'))
            npc_walks += 1
            break

    # (a2) no movement yet: at the end of the scene, the resident gets up (if sitting) and comes to stand beside you,
    # or, if they're beside you already, heads off a couple of steps
    if npc_walks == 0 and R != 'Sara' and not top_ctx['unknown'] and not top_ctx['gone']:
        plans = []
        for (flag, area, pl, cast) in variants:
            if R not in cast:
                plans = None; break
            rpos = tuple(top_ctx['pos'].get(R, cast[R][:2]))
            ppos = tuple(top_ctx['pos'].get('player', pl))
            taken = {tuple(v[:2]) for w, v in cast.items() if w != R} | {ppos} | later
            for w, v in top_ctx['pos'].items():
                if w != R: taken.add(tuple(v))
            pose_now = top_ctx['pose'].get(R, '')
            stand = [["pose", R, ""]] if pose_now not in ('', None) else []
            if pose_now is None:
                stand = [["pose", R, ""]]
            d0 = abs(rpos[0] - ppos[0]) + abs(rpos[1] - ppos[1])
            got = None
            if d0 >= 2:
                beside = [(ppos[0] + dx, ppos[1] + dy) for dx, dy in ((-1, 0), (1, 0), (0, 1), (0, -1))]
                beside = [b for b in beside if b != rpos and free(area, b[0], b[1], taken)]
                beside.sort(key=lambda b: abs(b[0] - rpos[0]) + abs(b[1] - rpos[1]))
                if beside:
                    b = beside[0]
                    got = stand + [["walk", R, b[0], b[1]], ["face", R, "player"], ["face", "player", R], ["wait", 0.6]]
            if got is None:
                aw = step_away(area, rpos, ppos, taken)
                if aw:
                    (tx, ty), face = aw
                    got = stand + [["walk", R, tx, ty], ["face", R, "player"], ["wait", 0.6]]
            if got is None:
                plans = None; break
            plans.append((flag, got))
        if plans:
            if len(plans) == 1:
                end = plans[0][1]
            else:
                end = [["if", {"flag": plans[1][0]}, plans[0][1], plans[1][1]]]
            ins.append(({'step': None, 'end': True}, 'end', end, 'walk at the end'))
            npc_walks += 1

    # (b) poses
    need = 3 - poses
    if need > 0:
        cands = []
        for k, r in enumerate(says):
            s = r['step']; X = s[1]
            if X == 'Sara' or not event_sheet(X) or r['pose'].get(X, '') != '':
                continue
            t = tag_of(lines_of(s)[0]); text = ' '.join(map(str, lines_of(s)))
            nxt = r['list'][r['idx'] + 1] if r['idx'] + 1 < len(r['list']) else None
            if nxt and isinstance(nxt, list) and nxt and nxt[0] in ('keepsake', 'give', 'perk') and X == R:
                cands.append((0, k, r, 'gift'))
            elif t in ('surprised', 'shocked'):
                cands.append((1, k, r, 'jump'))
            elif t == 'happy' and ('!' in text or 'Ha' in text):
                cands.append((2, k, r, 'laugh'))
            elif t == 'sad':
                cands.append((3, k, r, 'sad'))
            elif t in ('happy', 'love', 'bashful', ''):
                cands.append((5, k, r, 'talk'))
        cands.sort(key=lambda c: (c[0], c[1]))
        taken_idx = set()
        for pri, k, r, pose in cands:
            if need <= 0: break
            if k in taken_idx or k - 1 in taken_idx or k + 1 in taken_idx: continue
            X = r['step'][1]
            ins.append((r, 'before', [["pose", X, pose]], 'pose'))
            ins.append((r, 'after', [["pose", X, ""]], 'pose back'))
            taken_idx.add(k); need -= 1

    # (c) resident emotes
    want = max(0, 4 - emotes)
    if want:
        cands = []
        for k, r in enumerate(says):
            s = r['step']; X = s[1]; t = tag_of(lines_of(s)[0])
            if t not in EMOTE_FOR: continue
            prev = r['prev']
            if prev and prev[0] == 'emote' and prev[1] == X: continue
            cands.append((EMOTE_PRI[t], k, r, EMOTE_FOR[t]))
        cands.sort(key=lambda c: (c[0], c[1]))
        got = set()
        for pri, k, r, emo in cands:
            if want <= 0: break
            if k in got: continue
            ins.append((r, 'before', [["emote", r['step'][1], emo]], 'emote'))
            got.add(k); want -= 1

    # (d) the player's reactions
    if p_emotes == 0:
        picks = []
        love = [r for r in says if r['step'][1] == R and any(tag_of(l) == 'love' for l in lines_of(r['step']))]
        if love and ev.get('hearts', 0) >= 8:
            picks.append((love[0], 'love'))
        for t, emo in (('surprised', 'surprise'), ('shocked', 'surprise'), ('sad', 'sad'), ('happy', 'joy')):
            if len(picks) >= (2 if picks else 1): break
            hit = [r for r in says if tag_of(lines_of(r['step'])[-1]) == t and all(r is not p[0] for p in picks)]
            if hit:
                picks.append((hit[0], emo))
        if not picks and says:
            picks.append((says[-1], 'joy'))
        for r, emo in picks[:2]:
            ins.append((r, 'after', [["emote", "player", emo]], 'player emote'))
    return ins, recs


# ------------------------------------------------------------------ applying to the source
src = src_path.read_text()
norm = re.sub(r'\bnull\b', 'None', src).replace('true', 'True').replace('false', 'False')
assert len(norm) == len(src)
spans = {}
_ev0, _ev1 = src.index('\nconst EVENTS'), src.index('\nconst SCENES')
starts = [(m.group(1), m.start()) for m in re.finditer(r'^\t"([a-z0-9_]+)": \{', src, re.M) if _ev0 < m.start() < _ev1]
for i, (eid, st) in enumerate(starts):
    spans[eid] = (st, starts[i + 1][1] if i + 1 < len(starts) else src.index('\nconst SCENES'))


def gd(step):
    return json.dumps(step, ensure_ascii=False).replace('{"flag"', '{"flag"')


def step_end(text, i):
    depth, ins_, esc = 0, False, False
    while i < len(text):
        ch = text[i]
        if ins_:
            if esc: esc = False
            elif ch == '\\': esc = True
            elif ch == '"': ins_ = False
        elif ch == '"': ins_ = True
        elif ch == '[': depth += 1
        elif ch == ']':
            depth -= 1
            if depth == 0: return i + 1
        i += 1
    raise ValueError


edits = []   # (offset, text)
report = {}
for eid, ev in EVENTS.items():
    ins, recs = plan(eid, ev)
    if not ins: continue
    st, en = spans[eid]
    # every say step's source offset, in order
    occ = {}
    say_recs = [r for r in recs if r['step'][0] == 'say']
    offsets = {}
    for r in say_recs:
        s = r['step']
        first = json.dumps(str(lines_of(s)[0]), ensure_ascii=False)[:-1]
        needle_re = re.escape('["say", %s, [' % json.dumps(s[1], ensure_ascii=False)) + r'\s*' + re.escape(first[:40])
        key = (s[1], first[:40])
        k = occ.get(key, 0); occ[key] = k + 1
        found = [m.start() for m in re.finditer(needle_re, norm[st:en])]
        assert len(found) > k, (eid, key, len(found), k)
        offsets[id(s)] = st + found[k]
    for r, where, new, why in ins:
        if where == 'end':
            close = src.rindex('\n\t\t],\n', st, en)
            text = ', '.join(gd(x) for x in new)
            edits.append((close + 1, '\t\t\t' + text + ',\n', 2))
            report.setdefault(eid, []).append(why)
            continue
        off = offsets[id(r['step'])]
        line_start = src.rindex('\n', 0, off) + 1
        before_text = src[line_start:off]
        own_line = before_text.strip() == ''
        indent = re.match(r'[\t ]*', before_text).group(0)
        if not own_line:
            indent += ' '      # inside a branch list that opened on this line: line up with the step
        text = ', '.join(gd(x) for x in new)
        if where == 'before':
            edits.append((off, (text + ',\n' + indent) if own_line else (text + ', '), 0))
        else:
            e = step_end(src, off)
            if src[e:e + 2] == ',\n':
                nl_end = src.index('\n', e)
                edits.append((e + 1, '\n' + indent + text + ',', 1))
            else:
                edits.append((e, ', ' + text, 1))
        report.setdefault(eid, []).append(why)
edits.sort(key=lambda t: (t[0], t[2]))
out = src
for off, text, _ in reversed(edits):
    out = out[:off] + text + out[off:]
print('%d insertions in %d events' % (len(edits), len(report)))
from collections import Counter
print(Counter(w for v in report.values() for w in v))
if not DRY:
    src_path.write_text(out)
