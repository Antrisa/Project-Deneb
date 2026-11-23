#!/usr/bin/env python3
"""Offline check of the residents' letters (scripts/mail_data.gd), without running Godot.

  python3 tests/check_mail.py

Checks that:
  - every letter has its from, title, body and sign, and every gift is a real item (scripts/item_data.gd) with a
    count above 0;
  - every letter fits on its paper in the mail reader (scripts/mail_reader.gd) at the smallest page, 768 x 432,
    measured with the datapad font's own advances (datapad/art.gd), the way ui/ship_screen.gd wraps text, with
    room left at the foot of the page for its gift;
  - letters use only the characters the datapad font has (plain ASCII: no curly quotes, dashes or accents);
  - every letter is sent by something: a fixed day (DATED), a heart event's ["mail", id, days] step
    (scripts/heart_events.gd), or a send_mail("id") in scripts/main.gd; and everything sent is a letter.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Borrow the heart event checker's GDScript reader (gd_consts): just its definitions, not its checks.
_src = (ROOT / 'tests/check_heart_events.py').read_text()
_defs = {'__file__': str(ROOT / 'tests/check_heart_events.py')}
exec(compile(_src[:_src.index('\nmd = gd_consts(')], 'check_heart_events.py', 'exec'), _defs)
gd_consts = _defs['gd_consts']

mail = gd_consts(ROOT / 'scripts/mail_data.gd')
LETTERS, DATED = mail.get('LETTERS', {}), mail.get('DATED', {})
ITEMS = gd_consts(ROOT / 'scripts/item_data.gd').get('ITEMS', {})
FONTS = gd_consts(ROOT / 'datapad/art.gd')['FONTS']
heart = gd_consts(ROOT / 'scripts/heart_events.gd')

# The mail reader's layout (scripts/mail_reader.gd _paint and _paint_letter) on the smallest page.
PAGE = (768, 432)
TOP, BOTTOM = 34, PAGE[1] - 44
LIST_W = 214
PAPER_X = 12 + LIST_W + 10
PAPER_W = PAGE[0] - (12 + LIST_W) - 22
TEXT_W = PAPER_W - 48
BODY_Y = TOP + 16 + 27 + 18 + 12          # title, "From ...", the rule
LINE, PARA = 17, 7                        # wrap_text's gap, and the space after a paragraph
SIGN_H = 4 + 22                           # the sign-off ("strong"), from the y below the last paragraph
GIFT_H = 42                               # the foot of the page that shows a gift
MARGIN = 10                               # paper left under the sign-off

errors = []


def bad(msg):
    errors.append(msg)


def width(s, font):
    adv = FONTS[font]['advance']
    return sum(adv[min(max(ord(c) - 32, 0), 94)] for c in s)


def wrap(s, w, font='body'):
    lines = []
    for para in s.split('\n'):
        ln = ''
        for word in para.split():
            if ln and width(ln + ' ' + word, font) > w:
                lines.append(ln)
                ln = word
            else:
                ln = word if not ln else ln + ' ' + word
        lines.append(ln)
    return lines


def steps_of(node):
    """Every step in an event, however deep: inside choices, ifs and their branches."""
    if isinstance(node, dict):
        for v in node.values():
            yield from steps_of(v)
    elif isinstance(node, list):
        if node and isinstance(node[0], str):
            yield node
        for part in node:
            if isinstance(part, (list, dict)):
                yield from steps_of(part)


# what sends each letter
sent = {}
for lid in DATED:
    sent.setdefault(lid, []).append('day %s' % DATED[lid])
for ev_id, ev in heart['EVENTS'].items():
    for s in steps_of(ev.get('steps', [])):
        if s[0] == 'mail':
            sent.setdefault(s[1], []).append(ev_id)
for m in re.finditer(r'send_mail\("([^"]+)"', (ROOT / 'scripts/main.gd').read_text()):
    sent.setdefault(m.group(1), []).append('main.gd')

for lid, by in sent.items():
    if lid not in LETTERS:
        bad('%s sends %r, which isn\'t in scripts/mail_data.gd' % (', '.join(by), lid))

gifts = 0
for lid, letter in LETTERS.items():
    where = 'letter %r' % lid
    for key in ('from', 'title', 'body', 'sign'):
        if key not in letter:
            bad('%s has no %r' % (where, key))
    if lid not in sent:
        bad('%s is never sent: give it a day in DATED, or a ["mail", %r, 1] step in a heart event' % (where, lid))
    texts = [letter.get('title', ''), letter.get('from', ''), letter.get('sign', '')] + list(letter.get('body', []))
    for t in texts:
        odd = sorted(set(c for c in str(t) if not (32 <= ord(c) <= 126)))
        if odd:
            bad('%s: the datapad font has no %s (in %r)' % (where, ' '.join(repr(c) for c in odd), str(t)[:50]))
    if width(str(letter.get('title', '')), 'mid') > TEXT_W - 90:
        bad('%s: the title is too wide for the page' % where)
    gift = letter.get('gift', {})
    for item, n in gift.items():
        if item not in ITEMS:
            bad('%s: the gift %r isn\'t an item in scripts/item_data.gd' % (where, item))
        elif not (isinstance(n, int) and n > 0):
            bad('%s: the gift %r needs a count above 0' % (where, item))
    if gift:
        gifts += 1
        row = width('ENCLOSED', 'micro') + 12 + width('IN YOUR PACK', 'micro') + 8
        row += sum(24 + 4 + width('%s x%d' % (ITEMS.get(i, {}).get('name', i), n), 'label') + 16 for i, n in gift.items())
        if row > TEXT_W:
            bad('%s: the gift row is too wide for the page' % where)
    y = BODY_Y
    for para in letter.get('body', []):
        y += LINE * len(wrap(str(para), TEXT_W)) + PARA
    floor = BOTTOM - (GIFT_H if gift else 0) - MARGIN
    if '-v' in sys.argv:
        print('%-22s %3d px to spare' % (lid, floor - y - SIGN_H))
    if y + SIGN_H > floor:
        bad('%s runs %d px off the page%s: shorten it' % (where, y + SIGN_H - floor, ' (it has a gift)' if gift else ''))

for e in errors:
    print('FAIL:', e)
if errors:
    sys.exit(1)
print('PASS: %d letters (%d with gifts): every one fits its page, every gift is an item, every letter is sent.'
      % (len(LETTERS), gifts))
