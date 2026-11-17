"""Lunar promenade: two rings, eight spokes, inset rooms and interactive props."""
import math
from collections import deque

R_OUT=57            # outer edge of the station shell (was 61: four tiles less plain roof)
# The garden and games courts are wedges of the plaza: two arcs round the fountain and two sides
# parallel to the spokes. scripts/lunar_paving.gd uses the same numbers to draw them.
COURT_R1,COURT_R2,COURT_MARGIN=14.0,24.5,3.25
# The four big facilities sit in round pods that bulge out of the shell on the diagonals, so their
# buildings have room. In front of each is a square forecourt 13 tiles across, centred on the diagonal
# walk, which runs straight into its inner corner. tools/bake_floor.py paves them with the same numbers.
POD_DIST,POD_R=56.0,14.0
POD_R_I=14
FORECOURT_OFF,FORECOURT_HALF=35,6
# The outer corner of each forecourt (the one furthest from the fountain) is rounded, except the mess
# hall's, which Zachary wanted to keep square. tools/bake_floor.py and lunar_paving.gd use the same numbers.
FORECOURT_ROUND=5.5
def forecourt_inset(px,py,fx,fy,rounded):
    """How far inside a forecourt a point is, in tiles. fx,fy is the square's centre."""
    qx,qy=(px-fx)*(1 if fx>115.5 else -1),(py-fy)*(1 if fy>95.5 else -1)   # positive: away from the fountain
    h=FORECOURT_HALF+0.5
    inset=min(h-abs(px-fx),h-abs(py-fy))
    c=h-FORECOURT_ROUND
    if rounded and qx>c and qy>c:inset=min(inset,FORECOURT_ROUND-math.hypot(qx-c,qy-c))
    return inset
def in_pod(x,y):
    return any(math.hypot(x-(115+sx*POD_DIST/math.sqrt(2)),y-(95+sy*POD_DIST/math.sqrt(2)))<=POD_R for sx in (-1,1) for sy in (-1,1))
def court_inset(px,py,sign):
    """How far inside a court a point is, in tiles (negative: outside). sign 1 is the garden
    (north-north-west of the fountain), -1 the games court (south-south-east)."""
    dx,dy=(px-115.5)*sign,(py-95.5)*sign
    r=math.hypot(dx,dy)
    return min(r-COURT_R1,COURT_R2-r,-dx-COURT_MARGIN,(dx-dy)/math.sqrt(2)-COURT_MARGIN)

def rebuild(g):
    A,Area=g['A'],g['Area'];old=A['main'];cx,cy=115,95
    m=A['main']=Area('main','Community Concourse',231,191,'~');g['m']=m
    walk=g['WALK'];props=[];fronts=[];doors={};buildings=[];entries=[];things=[t for t in g['THINGS'] if t[3]!='main']
    def floor(x,y,ch='i'):
        if 0<=x<m.w and 0<=y<m.h:m.floor[y][x]=ch
    def rect(x0,y0,x1,y1,ch):
        for y in range(y0,y1+1):
            for x in range(x0,x1+1):floor(x,y,ch)
    def thing(kind,name,hint,x,y,r=28):things.append([kind,name,hint,'main',[x*16+8,y*16+8],r])
    # Solid annuli are actual room/roof footprints, not placed facade pictures.
    for y in range(cy-68,cy+69):
        for x in range(cx-68,cx+69):
            r=math.hypot(x-cx,y-cy)
            if r<=R_OUT or in_pod(x,y):floor(x,y,'#')
            if r<=30:floor(x,y,'i')
            if 8.5<=r<=10.5:floor(x,y,'.')
            if 39<=r<=50:floor(x,y,'a')
            for angle in range(0,360,45):
                u,v=math.cos(math.radians(angle)),math.sin(math.radians(angle))
                along=(x-cx)*u+(y-cy)*v;across=abs((y-cy)*u-(x-cx)*v)
                if 0<=along<=50 and across<=(2.9 if angle%90 else 2.5):floor(x,y,'.')
    exits=[('west',49,95,163,110),('east',185,95,4,55),('top',115,20,23,44),('eng',115,170,34,8)]
    for dest,x,y,tx,ty in exits:
        if x!=cx:rect(min(x,cx),cy-2,max(x,cx),cy+2,'a')
        else:rect(cx-2,min(y,cy),cx+2,max(y,cy),'a')
        # Enclosed access corridors continue through the lunar perimeter shell.
        if x==cx:
            for yy in range(min(y,cy),max(y,cy)+1):
                if abs(yy-cy)>R_OUT-1:
                    for xx in (cx-4,cx-3,cx+3,cx+4):floor(xx,yy,'#')
        else:
            for xx in range(min(x,cx),max(x,cx)+1):
                if abs(xx-cx)>R_OUT-1:
                    for yy in (cy-4,cy-3,cy+3,cy+4):floor(xx,yy,'#')
        floor(x,y,'a');m.warps.append((x,y,dest,tx,ty))
        for ar in A.values():
            if ar.key==dest:ar.warps=[(wx,wy,to,x+(1 if x<cx else -1 if x>cx else 0),y+(1 if y<cy else -1 if y>cy else 0)) if to=='main' else (wx,wy,to,dx,dy) for wx,wy,to,dx,dy in ar.warps]
        if dest in ('top','eng'):
            # Cabin sits beyond the public landing; south cabin faces inward/north.
            facing='S' if dest=='top' else 'N';dy=1 if facing=='S' else -1
            rect(x-3,y-4 if facing=='S' else y,x+3,y if facing=='S' else y+4,'#')
            floor(x,y,'a');fronts.append(['lift_'+dest,x,y,facing,7,5,'lift'])
            entries.append(['main',x,y,dest,tx,ty,facing,'Survey lift' if dest=='top' else 'Engineering lift',False])
            for wx,wy,to,dx,ddy in A[dest].warps:
                if to=='main':
                    A[dest].floor[wy][wx]='i'
                    entries.append([dest,wx,wy,'main',x,y+dy,'N' if dest=='top' else 'S','Concourse lift',False])
    # Major structures terminate the diagonal routes at the OUTER wall. Forecourts cut
    # into the shop band, maintaining a continuous public path behind each terrace.
    F,Hf=FORECOURT_OFF,FORECOURT_HALF
    shops=[('common','Community room',cx-F,cy-F-Hf,'S',13,10,'major'),('mess','Mess hall',cx+F,cy-F-Hf,'S',13,10,'major'),
           ('fab','Manufacturing hub',cx-F,cy+F+Hf,'N',13,10,'major'),('medbay','Medbay',cx+F,cy+F+Hf,'N',13,10,'major'),
           ('library','Library',102,68,'S',9,7,'shop'),('weaver',"Sesska's textiles",128,68,'S',9,7,'shop'),
           ('bram',"Bram's supplies",143,83,'W',7,9,'shop'),('bar',"Rusk's bar",87,107,'E',7,9,'shop'),
           ('furn',"Tobbin's workshop",102,122,'N',9,7,'shop'),('armoury','Armoury',128,122,'N',9,7,'shop')]
    homes=[('aptB','Residences B',97,48,'S',9,7,'home'),('aptA','Residences A',133,48,'S',9,7,'home'),
           ('aptDoc','Family residences',164,83,'W',7,9,'home'),('aptSec','Security residences',66,107,'E',7,9,'home'),
           ('aptEmpty','Empty flats',133,142,'N',9,7,'home'),('aptMoog','Moogli residences',97,142,'N',9,7,'home')]
    offsets={'S':(0,1),'N':(0,-1),'W':(-1,0),'E':(1,0)}
    for key,title,x,y,facing,w,h,kind in shops+homes:
        ix,iy=offsets[facing]
        # Soft-edged forecourt meets the diagonal spoke, with no raised perimeter curb.
        if kind=='major':
            # Square forecourt: the door is in the middle of its outer side.
            fy=y+iy*Hf
            for yy in range(fy-Hf,fy+Hf+1):
                for xx in range(x-Hf,x+Hf+1):
                    if m.floor[yy][xx]!='.' and forecourt_inset(xx+.5,yy+.5,x+.5,fy+.5,key!='mess')>0:floor(xx,yy,'a')
        if facing in ('S','N'):
            x0,x1=x-w//2,x+w//2;y0,y1=(y-h+1,y) if facing=='S' else (y,y+h-1)
        else:
            x0,x1=(x,x+w-1) if facing=='W' else (x-w+1,x);y0,y1=y-h//2,y+h//2
        # Rooms occupy the existing curved structural band. Never stamp a
        # rectangular solid footprint across the public annulus or its spokes.
        # The annuli above already contain the roof/collision cells.
        # Recessed, NPC-sized door and a short link to the public ring.
        for step in range(0,5 if kind!='major' else 0):
            px,py=x+ix*step,y+iy*step
            for cross in (-1,0,1):floor(px+(cross if iy else 0),py+(cross if ix else 0),'p')
        src=next(w for w in old.warps if w[2]==key)
        m.warps.append((x,y,key,src[3],src[4]))
        A[key].warps=[(wx,wy,to,x+ix*2,y+iy*2) if to=='main' else (wx,wy,to,tx,ty) for wx,wy,to,tx,ty in A[key].warps]
        doors[key]=(x,y,'1',x+ix*2,y+iy*2);g['MAP_PARENT'][key]=['main',x+ix*2,y+iy*2]
        buildings.append([key,title,x0,y0,w,h]);fronts.append([key,x,y,facing,w,h,kind])
        entries.append(['main',x,y,key,src[3],src[4],facing,title,False])
        m.zones.append([title,x0-3,y0-3,x1+3,y1+3])
        # Room exits also require opening a door, so locking works consistently.
        for wx,wy,to,tx,ty in A[key].warps:
            if to=='main':entries.append([key,wx,wy,to,tx,ty,'N','Exit to promenade',False])
    # ------------------------------------------------------------------ props, placed by rule
    # Every kind of prop has one size and one solid depth: (width, height, solid rows from the bottom).
    # x,y is the top-left tile of that footprint; the picture stands on its bottom edge, centred.
    SIZES={'bench':(3,2,1),'bench_s':(3,2,1),'bench_n':(3,2,1),'bench_e':(1,3,2),'bench_w':(1,3,2),
           'waiting_seat':(3,2,1),'table':(3,2,1),'cafe_table':(2,2,1),'chess':(2,2,1),'hologame':(2,2,1),
           'chair_e':(1,2,0),'chair_w':(1,2,0),'chair_s':(1,2,0),'chair_n':(1,2,0),
           'flowers':(4,2,2),'plants':(3,2,1),'hydroponics':(3,2,1),'water_tank':(2,2,1),'books':(2,2,1),
           'clothes':(3,2,1),'textiles':(3,2,1),'seed_rack':(2,2,1),'market_counter':(3,2,1),'cargo':(2,2,1),
           'trolley':(2,2,1),'workbench':(3,2,1),'medical':(2,3,1),'terminal':(1,2,1),'mailbox':(1,2,1),
           'telescope':(2,3,1),'market_canopy':(4,4,0),
           # Promenade Art Pack 5: back views, shop pieces, street furniture, garden and games extras
           'terminal_n':(1,2,1),'mailbox_n':(1,2,1),'books_n':(2,2,1),'medical_n':(2,3,1),'workbench_n':(3,2,1),
           'market_counter_n':(3,2,1),'waiting_seat_n':(3,2,1),'waiting_seat_e':(1,3,2),'waiting_seat_w':(1,3,2),
           'lamp_post':(1,2,1),'tree_tub':(2,2,1),'bollard_light':(1,1,1),'bin':(1,1,1),'drinking_fountain':(1,2,1),
           'signpost':(1,2,1),'banner_pole':(1,2,1),'kiosk':(3,3,2),'planter_long':(4,2,1),'play_piece':(3,2,1),
           'garden_tools':(2,2,1),'bird_bath':(1,2,1),'scoreboard':(2,3,1),'arcade':(1,3,1),'bar_table':(3,2,1),
           'garden_arch':(3,3,1)}
    for shop_ in ('bar','bram','library','weaver','furn','armoury','mess','common','medbay','fab'):
        SIZES['front_%s_1'%shop_]=SIZES['front_%s_2'%shop_]=(3,3,1)
    FRONT_TITLES={'bar':("Rusk's kegs","Rusk's mug sign"),'bram':('Salvage bins','Hanging scale'),
                  'library':('Outdoor bookcase','Globe and map stand'),'weaver':("Sesska's loom",'Dyed cloth on a frame'),
                  'furn':("Tobbin's chair and table",'Half-built cabinet'),'armoury':('Weapon rack','Training dummy'),
                  'mess':('Menu board and stock pot','Serving cart'),'common':('Notice pillar','Tea and coffee stand'),
                  'medbay':('Medbay banner','Stretcher trolley'),'fab':('Fabricator','Welding cart')}
    # Nothing may stand on a spoke, on a door's approach or on a way out.
    clear={(w[0],w[1]) for w in m.warps}
    for key,title,x,y,facing,w,h,kind in shops+homes:
        ix,iy=offsets[facing]
        for step in range(0,8):
            for cross in (-1,0,1):clear.add((x+ix*step+(cross if iy else 0),y+iy*step+(cross if ix else 0)))
    def free(x,y):
        return 0<=x<m.w and 0<=y<m.h and m.floor[y][x] in 'ihupa' and m.obj[y][x]==' ' and (x,y) not in clear
    def fits(name,x,y):
        w,h,solid=SIZES[name]
        return all(free(xx,yy) for yy in range(y+h-max(solid,1),y+h) for xx in range(x,x+w))
    def prop(name,x,y,title,kind='inspect',hint='Inspect'):
        w,h,solid=SIZES[name]
        assert fits(name,x,y),('prop does not fit',name,x,y,title)
        props.append([name,x,y,w,h,title])
        for yy in range(y+h-solid,y+h):
            for xx in range(x,x+w):m.obj[yy][xx]='x'
        if solid==0:clear.update((xx,y+h-1) for xx in range(x,x+w))      # a chair keeps its own tile
        if kind:thing(kind,title,hint,x+(w-1)/2,y+h-1,30)
    def soft(name,x,y,title,kind='inspect',hint='Inspect'):
        """Places a prop if it fits; otherwise leaves it out quietly."""
        if name in SIZES and fits(name,x,y):
            prop(name,x,y,title,kind,hint);return True
        return False
    def near_spot(name,fx,fy,title,kind='inspect',hint='Inspect',reach=3,ok=None):
        """Places a prop as close as it fits to fx,fy (its base centre, in tiles), or leaves it out."""
        w,h,solid=SIZES[name];best=None
        for yy in range(int(fy)-reach-h,int(fy)+reach+1):
            for xx in range(int(fx)-reach-w,int(fx)+reach+1):
                if fits(name,xx,yy) and (ok is None or ok(xx,yy,w,h)):
                    d=math.hypot(xx+w/2-fx,yy+h-.5-fy)
                    if d<=reach+1 and (best is None or d<best[0]):best=(d,xx,yy)
        if best:prop(name,best[1],best[2],title,kind,hint);return best[1],best[2]
        return None
    def facing_letter(x,y,focus):
        dx,dy=focus[0]-x,focus[1]-y
        return ('e' if dx>0 else 'w') if abs(dx)>=abs(dy) else ('s' if dy>0 else 'n')
    def bench_at(x,y,focus,title):
        """A bench whose sitter is on tile x,y and looks at the focus tile."""
        d=facing_letter(x,y,focus)
        if d in 'ew':prop('bench_'+d,x,y-2,'%s [%s]'%(title,d.upper()),'seat','Sit')
        else:prop('bench_'+d,x-1,y-1,'%s [%s]'%(title,d.upper()),'seat','Sit')
    def chair_at(x,y,focus,title):
        d=facing_letter(x,y,focus)
        prop('chair_'+d,x,y-1,'%s [%s]'%(title,d.upper()),'seat','Sit')
    def beside(door,side,name,title,kind='inspect',hint='Inspect',first_step=1,first_off=2):
        """Stands a prop next to a door's approach: side -1 or 1, as near the door as it fits."""
        x,y,facing=door;ix,iy=offsets[facing];w,h,solid=SIZES.get(name,(1,1,1))
        for step in range(first_step,8):
            for off in range(first_off,7):
                if iy:x0=x+off if side>0 else x-off-w+1;y0=y+iy*step-h+1
                else:x0=x+ix*step if ix>0 else x+ix*step-w+1;y0=y+off if side>0 else y-off-h+1
                if name in SIZES:
                    if fits(name,x0,y0):prop(name,x0,y0,title,kind,hint);return x0,y0
                elif free(x0,y0):return x0,y0
        raise AssertionError(('no room beside door',door,name))
    # Fountain: four benches in the gaps between the spokes, each looking at the water.
    for bx,by in [(104,91),(126,91),(104,101),(126,101)]:bench_at(bx,by,(cx,cy),'Fountain seating')
    thing('board','Community board','Read requests',cx-1,cy+3,21)
    thing('calendar','Community calendar','Open calendar',cx+1,cy+3,21)
    thing('inspect','Water-recycling fountain','Inspect',cx,cy-3,30)
    for yy in range(cy-2,cy+3):
        for xx in range(cx-3,cx+4):
            if ((xx-cx)/3.6)**2+((yy-cy)/2.6)**2<=1:m.obj[yy][xx]='x'
    # Garden and games courts: clean wedges of the plaza (see court_inset above).
    for yy in range(cy-30,cy+31):
        for xx in range(cx-30,cx+31):
            if m.floor[yy][xx]=='i':
                if court_inset(xx+.5,yy+.5,1)>0:floor(xx,yy,'h')
                elif court_inset(xx+.5,yy+.5,-1)>0:floor(xx,yy,'u')
    # Garden: two flower beds, benches that look at them, the watering station and the book exchange.
    prop('flowers',107,72,'Library flower border','garden','Water flowers')
    prop('flowers',106,76,'Community planting bed','garden','Water flowers')
    prop('water_tank',110,79,'Garden watering station','garden','Water flowers')
    prop('books',105,73,'Garden book exchange','read','Read a community story')
    bench_at(104,76,(106,76),'Reading garden bench')
    bench_at(111,76,(109,76),'Planting-view bench')
    bench_at(107,80,(107,77),'Flower garden bench')
    # Games court: two tables with a chair on each side that faces the board, and a bench to watch from.
    prop('chess',122,111,'Community chess table','game','Play a short game')
    chair_at(121,112,(122,112),'Game chair');chair_at(124,112,(123,112),'Game chair')
    prop('hologame',124,115,'Holographic strategy table','game','Play a short game')
    chair_at(124,114,(124,115),'Game chair');chair_at(124,117,(124,116),'Game chair')
    bench_at(120,114,(124,114),'Games spectator bench')
    prop('plants',120,117,'Games court planter')
    # The four big facilities: furniture in the forecourt, set out the same way on both sides of the way in.
    def local(name,door,u,v,title,kind='inspect',hint='Inspect'):
        """Places a prop in a corner forecourt by local position: u across (positive is toward the
        plaza side, mirrored for the eastern pods), v out from the door wall. Falls back to the nearest
        spot that fits inside the same forecourt."""
        X,Y,facing=door;w,h,solid=SIZES[name];east=X>cx;sv=1 if facing=='S' else -1
        def at(uu,vv):
            x0=X-uu-(w-1) if east else X+uu
            base=Y+sv*vv
            return x0,base-h+1
        def inside(x0,y0):
            return all(abs(xx-X)<=Hf and abs(yy-(Y+sv*Hf))<=Hf for xx in (x0,x0+w-1) for yy in (y0+h-max(solid,1),y0+h-1))
        for r in range(0,4):
            for du in range(-r,r+1):
                for dv in range(-r,r+1):
                    if max(abs(du),abs(dv))!=r:continue
                    x0,y0=at(u+du,v+dv)
                    if inside(x0,y0) and fits(name,x0,y0):
                        prop(name,x0,y0,title,kind,hint);return x0,y0
        raise AssertionError(('no room in forecourt',name,door,u,v))
    for key,title,x,y,facing,w,h,kind in shops[:4]:
        door=(x,y,facing)
        _local=local
        def local(name,door,u,v,*rest):      # beside a north-facing door everything sits one row further in
            return _local(name,door,u,v+(0 if door[2]=='S' else 1),*rest)
        if key=='mess':
            for u,v in [(-5,3),(3,3),(-5,8),(-2,12)]:
                tx,ty=local('table',door,u,v,'Dining table')
                thing('seat','Dining chair left','Sit',tx,ty+1,22);thing('seat','Dining chair right','Sit',tx+2,ty+1,22)
        elif key=='common':
            local('waiting_seat',door,-5,3,'Community sofa','seat','Sit');local('waiting_seat',door,3,3,'Community sofa','seat','Sit')
            local('cafe_table',door,-5,8,'Coffee table');local('cafe_table',door,-2,12,'Coffee table')
        elif key=='medbay':
            local('waiting_seat',door,-5,3,'Waiting seats','seat','Sit');local('waiting_seat',door,3,3,'Waiting seats','seat','Sit')
            local('medical',door,-5,8,'First aid supplies');local('hydroponics',door,-2,12,'Healing herb planter')
        elif key=='fab':
            local('workbench',door,-5,3,'Public repair bench','repair','Inspect tools');local('cargo',door,3,3,'Parts crates')
            local('cargo',door,-5,8,'Parts crates');local('trolley',door,-2,12,'Delivery trolley')
        local=_local
        s=1 if facing=='S' else -1
        # Along the back wall, either side of the door: sign, store-front pieces and the terminal, in a line.
        # (Beside a north-facing door the first row is under the roof's edge, so they stand one row in.)
        v0=0 if facing=='S' else 1;east=x>cx;sv=1 if facing=='S' else -1
        def cell(u,v):return (x-u if east else x+u, y+sv*v)
        _local('terminal_n' if facing=='N' else 'terminal',door,3,v0+1,{'mess':'Mess hall menu','common':'Community activities','fab':'Manufacturing work orders','medbay':'Medbay reception'}[key])
        spots=[(-3,0),(-6,0),(-5,0),(5,0),(6,0)] if key=='mess' else [(-2,0),(-3,1),(-4,2),(5,0),(6,0)]
        sx,sy=cell(spots[0][0],v0+spots[0][1]);assert free(sx,sy),('sign',key);m.obj[sy][sx]=str([sh[2] for sh in g['SHOPS']].index(key));thing('sign',title,'Read the sign',sx,sy,22)
        for ch_,(u,dv) in zip(g['PORCH_OBJS'][key],spots[1:]):
            ox,oy=cell(u,v0+dv);assert free(ox,oy),('store front',key,u);m.obj[oy][ox]=ch_
        for i_,choices in enumerate((((-3,6),(-4,9)),((3,8),(4,5),(5,10),(-5,11)))):
            for (u,v) in choices:
                try:_local('front_%s_%d'%(key,i_+1),door,u,v+v0,FRONT_TITLES[key][i_]);break
                except AssertionError:pass
            else:print('note: no room in the %s forecourt for its shop piece %d'%(key,i_+1))
        if key=='common':
            try:_local('play_piece',door,-3,10+v0,'Play corner')
            except AssertionError:print('note: no room for the play corner')
        try:_local('bin',door,5,11+v0,'Recycling bin')
        except AssertionError:pass
    # Bram's market: canopy, counter, crates and trolley, just below his door.
    prop('market_canopy',138,85,"Bram's canopy",None)
    for xx in (138,141):m.obj[88][xx]='x'
    prop('market_counter',139,88,"Bram's supply counter",'market','Browse supplies')
    prop('seed_rack',135,88,'Seed and plant display')
    prop('cargo',142,89,'Sealed supply crates')
    prop('trolley',136,90,'Delivery trolley')
    # Sesska's racks either side of her door; two small tables outside the bar.
    wd=[(xx,yy,f) for k,t,xx,yy,f,w,h,kd in shops if k=='weaver'][0]
    beside(wd,-1,'clothes','Textile display',first_off=4)
    # the garment rack: right of the door if there is room, otherwise further along on the left
    w_,h_,_=SIZES['textiles'];placed_=False
    for side_,off_ in ((1,4),(1,5),(-1,7),(-1,8)):
        x0_=wd[0]+off_ if side_>0 else wd[0]-off_-w_+1
        for step_ in (1,2):
            y0_=wd[1]+step_-h_+1
            if not placed_ and fits('textiles',x0_,y0_) and all(free(xx,y0_+h_) for xx in range(x0_,x0_+w_)):
                prop('textiles',x0_,y0_,'Finished garments');placed_=True
    if not placed_:print('note: no room for the garment rack')
    bd=[(xx,yy,f) for k,t,xx,yy,f,w,h,kd in shops if k=='bar'][0]
    beside(bd,-1,'bar_table','Tall bar table',first_step=2,first_off=4);beside(bd,1,'bar_table','Tall bar table',first_step=2,first_off=4)
    # Each shop's two big pieces (Art Pack 5) stand either side of its way in.
    for key,title,x,y,facing,w,h,kind in shops[4:]:
        for i_,side_ in enumerate((-1,1)):
            try:beside((x,y,facing),side_,'front_%s_%d'%(key,i_+1),FRONT_TITLES[key][i_],first_step=2 if facing=='N' else 1,first_off=2)
            except AssertionError:print('note: no room beside the %s door for its shop piece %d'%(key,i_+1))
    # Every shop: its sign board and its four store-front objects (Shop Art v4) either side of the way in.
    shop_order=[sh[2] for sh in g['SHOPS']]
    for key,title,x,y,facing,w,h,kind in shops[4:]:
        door=(x,y,facing);s_north=facing=='N'
        sx,sy=beside(door,-1,'',title,first_step=2 if s_north else 1,first_off=2)
        m.obj[sy][sx]=str(shop_order.index(key));thing('sign',title,'Read the sign',sx,sy,22)
        chars=g['PORCH_OBJS'][key]
        for n,(side,step) in enumerate([(-1,3),(1,2),(-1,5),(1,4)]):
            ox,oy=beside(door,side,'',title,first_step=step,first_off=2)
            m.obj[oy][ox]=chars[n]
    # Homes: a mail terminal on one side of the door and a planter on the other.
    for key,title,x,y,facing,w,h,kind in homes:
        door=(x,y,facing)
        # beside a north-facing door the mail terminal stands against the wall, seen from behind
        beside(door,1,'mailbox_n' if facing=='N' else 'mailbox','Residential mail terminal',first_step=2 if facing=='N' else 1)
        beside(door,-1,'plants','Resident garden')
    # ---------------------------------------------------------------- street furniture (Art Pack 5)
    def at_angle(r,a,off=0.0):
        a=math.radians(a);return cx+.5+r*math.cos(a)-off*math.sin(a),cy+.5+r*math.sin(a)+off*math.cos(a)
    for k in range(8):                       # a direction post at every spoke's crossing with the ring
        near_spot('signpost',*at_angle(40.5,45*k,3.2),'Direction post',reach=1)
    for k in range(8):                       # low lights along each spoke where it crosses the shop band
        for r_ in (32.0,36.5):
            for off_ in (-3.4,3.4):near_spot('bollard_light',*at_angle(r_,45*k,off_),'Path light',None,reach=1)
    for k in range(16):                      # tall lamps on the outer edge of the ring, between homes
        near_spot('lamp_post',*at_angle(49.2,11.25+22.5*k),'Ring lamp',None,reach=1)
    for k in range(8):                       # a tree half way between each pair of spokes, on the ring
        near_spot('tree_tub',*at_angle(44.5,22.5+45*k),'Ring tree','inspect','Inspect',reach=2)
    for k in range(8):                       # banner poles where each spoke leaves the plaza
        near_spot('banner_pole',*at_angle(27.0,45*k,-3.2),'Promenade banner',None,reach=1)
    for k in range(8):                       # long planters round the plaza, between the spokes
        near_spot('planter_long',*at_angle(20.5,22.5+45*k),'Plaza planter','inspect','Inspect',reach=2)
    for fx_,fy_ in ((109.5,104.5),(121.5,86.5)):
        near_spot('drinking_fountain',fx_,fy_,'Drinking fountain','inspect','Inspect',reach=2)
    for fx_,fy_ in ((101.5,89.5),(129.5,89.5),(101.5,102.5),(129.5,102.5)):
        near_spot('bin',fx_,fy_,'Recycling bin',None,reach=2)
    near_spot('kiosk',133.5,93.0,"Ooma's kiosk (closed today)",'inspect','Inspect',reach=3)
    # Garden: an arch over the way in from the fountain, a tool rack and a bird bath.
    gx_,gy_=at_angle(14.2,247.5)
    for yy in range(int(gy_)-3,int(gy_)+3):
        placed_=False
        for xx in range(int(gx_)-3,int(gx_)+2):
            if all(free(xx+dx_,yy+2) for dx_ in (0,2)) and m.floor[yy+2][xx+1] in 'ihupa':
                props.append(['garden_arch',xx,yy,3,3,'Garden arch'])
                m.obj[yy+2][xx]='x';m.obj[yy+2][xx+2]='x'          # the two posts; you walk under the middle
                thing('inspect','Garden arch','Inspect',xx+1,yy+2,26);placed_=True;break
        if placed_:break
    garden_ok=lambda xx,yy,w,h:all(m.floor[yy+h-1][x2]=='h' for x2 in range(xx,xx+w))
    games_ok=lambda xx,yy,w,h:all(m.floor[yy+h-1][x2]=='u' for x2 in range(xx,xx+w))
    near_spot('garden_tools',110.0,77.0,'Garden tool rack','inspect','Inspect',reach=3,ok=garden_ok)
    near_spot('bird_bath',104.0,79.0,'Bird bath','inspect','Inspect',reach=3,ok=garden_ok)
    near_spot('scoreboard',128.0,111.0,'Games scoreboard','inspect','Inspect',reach=3,ok=games_ok)
    near_spot('arcade',127.5,118.5,'Arcade cabinet','inspect','Inspect',reach=3,ok=games_ok)
    # Observation bay projects OUTWARD through the perimeter; no route to vacuum.
    outline=[(44,76),(48,72),(56,72),(61,77),(61,86),(56,90),(48,90),(44,86)]
    def inside(px,py):
        c=False;j=len(outline)-1
        for i,(ax,ay) in enumerate(outline):
            bx,by=outline[j]
            if (ay>py)!=(by>py) and px<(bx-ax)*(py-ay)/(by-ay)+ax:c=not c
            j=i
        return c
    for yy in range(71,92):
        for xx in range(43,63):
            if inside(xx+.5,yy+.5):floor(xx,yy,'#')
    for yy in range(74,89):
        for xx in range(46,60):
            if all(inside(xx+dx,yy+dy) for dx,dy in [(-1,-1),(2,-1),(-1,2),(2,2)]):floor(xx,yy,'u')
    rect(58,78,70,83,'a')
    prop('telescope',49,76,'Lunar telescope','observe','Look through telescope')
    bench_at(53,82,(53,75),'Observation bench')
    thing('observe','Panoramic lunar window','Look outside',54,76,38)
    m.zones.insert(0,['Observation bay',44,72,62,90])
    m.zones.insert(0,['Flower garden',101,70,112,82])
    m.zones.insert(0,['Community games',119,109,130,121])
    m.zones.insert(0,["Bram's market",135,84,143,92])
    # Roofs. Machinery and skylights sit in two orderly rings, one along the middle of the shop band and one
    # along the middle of the outer shell, and only where the roof is clear all round them.
    used=set();roof=[];lights=[]
    def roof_clear(x,y,w,h,below=2):
        cells=[(xx,yy) for yy in range(y-1,y+h+below) for xx in range(x-1,x+w+1)]
        return all(0<=xx<m.w and 0<=yy<m.h and m.floor[yy][xx]=='#' and (xx,yy) not in used for xx,yy in cells)
    kinds=[('roof_fan',2,2),('roof_solar',4,2),('roof_duct',3,2),('roof_tank',2,3),('roof_hatch',2,2),
           ('roof_garden',4,3),('roof_pipe',2,2),('roof_dish',2,3),('roof_lights',3,1),('roof_box',2,2)]
    for radius,step,first in [(34.5,45.0,11.0),(34.5,45.0,34.0),((50+R_OUT)/2+1,22.5,11.25)]:
        n=0;a=first
        while a<360:
            name,ww,hh=kinds[n%len(kinds)];n+=1
            px,py=int(round(cx+.5+radius*math.cos(math.radians(a))-ww/2)),int(round(cy+.5+radius*math.sin(math.radians(a))-hh/2))
            if roof_clear(px,py,ww,hh):
                roof.append([name,px,py,ww,hh]);used.update((xx,yy) for yy in range(py-1,py+hh+1) for xx in range(px-1,px+ww+1))
            a+=step
    for radius,step in [(34.5,6.0),((50+R_OUT)/2+1,4.0)]:
        a=0.0
        while a<360:
            px,py=int(round(cx+.5+radius*math.cos(math.radians(a))-1)),int(round(cy+.5+radius*math.sin(math.radians(a))-1))
            if all(m.floor[yy][xx]=='#' and (xx,yy) not in used for yy in range(py-1,py+4) for xx in range(px,px+2)):
                lights.append([px,py]);used.update((xx,yy) for yy in range(py-1,py+3) for xx in range(px-1,px+3))
            a+=step
    # The four corner pods: a fan, a duct and skylights on each, from the outer side inward.
    for sx_ in (-1,1):
        for sy_ in (-1,1):
            pcx,pcy=cx+sx_*POD_DIST/math.sqrt(2),cy+sy_*POD_DIST/math.sqrt(2)
            ax,ay=pcx+sx_*3,pcy+sy_*3
            spots=sorted([(xx,yy) for yy in range(int(pcy)-POD_R_I,int(pcy)+POD_R_I) for xx in range(int(pcx)-POD_R_I,int(pcx)+POD_R_I)],key=lambda c:(c[0]-ax)**2+(c[1]-ay)**2)
            plan=[('roof_fan',2,2),('light',2,2),('roof_duct',3,2),('light',2,2),('light',2,2),('roof_box',2,2)]
            for name,ww,hh in plan:
                for xx,yy in spots:
                    if math.hypot(xx+ww/2-pcx,yy+hh/2-pcy)<POD_R-2.5 and roof_clear(xx,yy,ww,hh):
                        if name=='light':lights.append([xx,yy])
                        else:roof.append([name,xx,yy,ww,hh])
                        used.update((x2,y2) for y2 in range(yy-1,yy+hh+1) for x2 in range(xx-1,xx+ww+1));break
    g['ROOF_PROPS']=roof
    g['SOCIAL_SPOTS']=[['garden',108,74],['garden',107,78],['chess',121,112],['chess',124,112],['hologame',124,114],['hologame',124,117],['observe',51,79],['read',54,85],['browse',140,90],['restock',140,87]]
    m.obj[89][122]='E'
    invisible=[[x,y] for y in range(m.h) for x in range(m.w) if m.obj[y][x]=='x']
    g.update(ROOF_LIGHTS=lights,CONCOURSE_PROPS=props,CONCOURSE_FRONTS=fronts,CONCOURSE_LABELS=[],CONCOURSE_HIDDEN=invisible,ENTRANCES=entries,
             MESS_OBJECTS=[],DOORS=doors,BUILDINGS=buildings,FRONTS=[],SIGNS=[],PORCH_MOUTHS=[(v[3],v[4]) for v in doors.values()])
    reserved={(w[0],w[1]) for w in m.warps}|{(v[3],v[4]) for v in doors.values()};owners={}
    def nearest(x,y,owner):
        q=deque([(x,y)]);seen={(x,y)}
        while q:
            px,py=q.popleft()
            if 1<=px<m.w-1 and 1<=py<m.h-1 and m.floor[py][px] in walk and (m.obj[py][px]==' ' or m.obj[py][px] in g['OPEN_OBJ']) and (px,py) not in reserved and owners.get((px,py),owner)==owner:
                owners[(px,py)]=owner;return px,py
            for ax,ay in [(1,0),(-1,0),(0,1),(0,-1)]:
                n=(px+ax,py+ay)
                if n not in seen and 0<=n[0]<m.w and 0<=n[1]<m.h:seen.add(n);q.append(n)
        raise AssertionError('No activity tile')
    for p in g['PEOPLE']:
        if p[1]=='main':p[2],p[3]=122,89;reserved.add((122,89))
    outdoor={'Bram':(140,87),'Sesska':(128,71),'Tobbin':(102,119),'Tikka':(80,127),'Ooma':(120,108)}
    visits=[('Evarra',840,900,108,74,'u','garden'),('Merrow',930,990,107,78,'u','garden'),
            ('Owen',840,930,121,112,'r','chess'),("Tar'Besh",840,930,124,112,'l','chess'),
            ('Kit',930,1020,124,114,'d','hologame'),('Pip',930,1020,124,117,'u','hologame'),
            ('Zaas',840,930,51,79,'l','observe'),('Quill',930,990,54,85,'l','read'),
            ('Saffi',780,840,140,90,'u','browse')]
    for who,start,end,x,y,facing,act in visits:
        rows=g['SCHEDULES'][who]
        resume=list([e for e in rows if e[0]<=end][-1]);resume[0]=end
        rows[:]=[e for e in rows if not start<=e[0]<=end]
        rows.extend([[start,'main',x,y,26,facing,act,-1],resume]);rows.sort(key=lambda e:e[0])
    for who,rows in g['SCHEDULES'].items():
        for e in rows:
            if who in outdoor and e[6]=='work' and (e[1] in {'bram','weaver','furn','fab'} or who=='Ooma'):e[1]='main';e[2],e[3]=outdoor[who];e[4]=26
            if who=='Bram' and e[1]=='main' and e[6]=='work':e[6]='restock';e[7]=-1
            if e[1]=='main':e[2],e[3]=nearest(e[2],e[3],who)
    g['THINGS']=things;m.zones.append(['Fountain plaza',103,84,127,108])
    assert len(doors)==16
    print('Lunar promenade: two rings, eight spokes, 16 inset rooms, attached board/calendar, two lifts.')
