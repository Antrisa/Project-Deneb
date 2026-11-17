"""Check final serialized map data, including post-build corner processing."""
import ast
from pathlib import Path
from collections import deque
p=Path(__file__).resolve().parents[1]
d={}
import re, json
source=(p/'scripts/map_data.gd').read_text()
parts=re.split(r'^const (\w+) = ',source,flags=re.M)
for i in range(1,len(parts),2):
    try:d[parts[i]]=ast.literal_eval(parts[i+1].strip())
    except (ValueError,SyntaxError):pass
a=d['AREAS']['main'];f=a['floor'];o=a['obj']
def walk(x,y):return 0<=y<len(f) and 0<=x<len(f[0]) and f[y][x] not in d['SOLID_FLOOR'] and (o[y][x]==' ' or o[y][x] in d['OPEN_OBJ'])
q=deque([(115,108)]);seen=set(q)
while q:
    x,y=q.popleft()
    for n in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
        if n not in seen and walk(*n):seen.add(n);q.append(n)
for x,y,to,tx,ty in a['warps']:
    assert (x,y) in seen, ('unreachable door',to,x,y)
    ar=d['AREAS'][to]
    assert ar['floor'][ty][tx] not in d['SOLID_FLOOR'],('blocked destination',to)
for ar in d['AREAS'].values():
    for x,y,to,tx,ty in ar['warps']:
        if to=='main':assert (tx,ty) in seen,('blocked return',tx,ty)
for who,stops in d['SCHEDULES'].items():
    for e in stops:
        if e[1]=='main':assert (e[2],e[3]) in seen,('unreachable resident',who,e)
print('PASS: final map doorways, return landings and resident stops are connected;',len(seen),'reachable concourse tiles.')
# Buildings must never stamp rectangular solids across the residential ring.
import math
for y in range(len(f)):
    for x in range(len(f[0])):
        if 40 <= math.hypot(x-115,y-95) <= 49:
            assert f[y][x] not in d['SOLID_FLOOR'], ('ring obstruction',x,y)
for angle in range(0,360,45):
    for radius in range(29,50):
        x=round(115+radius*math.cos(math.radians(angle)))
        y=round(95+radius*math.sin(math.radians(angle)))
        assert f[y][x] not in d['SOLID_FLOOR'], ('blocked spoke',angle,radius)
print('PASS: continuous outer-ring floor and all eight radial connectors clear of structural protrusions.')
