"""Lunar promenade: two rings, eight spokes, inset rooms and interactive props."""
import math
from collections import deque

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
    for y in range(cy-62,cy+63):
        for x in range(cx-62,cx+63):
            r=math.hypot(x-cx,y-cy)
            if r<=61:floor(x,y,'#')
            if r<=30:floor(x,y,'i')
            if 8.5<=r<=10.5:floor(x,y,'.')
            if 39<=r<=50:floor(x,y,'a')
            for angle in range(0,360,45):
                u,v=math.cos(math.radians(angle)),math.sin(math.radians(angle))
                along=(x-cx)*u+(y-cy)*v;across=abs((y-cy)*u-(x-cx)*v)
                if 0<=along<=50 and across<=(2.5 if angle%90 else 2.5):floor(x,y,'.')
    exits=[('west',49,95,163,110),('east',185,95,4,55),('top',115,20,20,14),('eng',115,170,34,8)]
    for dest,x,y,tx,ty in exits:
        if x!=cx:rect(min(x,cx),cy-2,max(x,cx),cy+2,'a')
        else:rect(cx-2,min(y,cy),cx+2,max(y,cy),'a')
        # Enclosed access corridors continue through the lunar perimeter shell.
        if x==cx:
            for yy in range(min(y,cy),max(y,cy)+1):
                if abs(yy-cy)>60:
                    for xx in (cx-4,cx-3,cx+3,cx+4):floor(xx,yy,'#')
        else:
            for xx in range(min(x,cx),max(x,cx)+1):
                if abs(xx-cx)>60:
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
    shops=[('common','Community room',80,60,'S',17,10,'major'),('mess','Mess hall',150,60,'S',17,10,'major'),
           ('fab','Manufacturing hub',80,130,'N',17,10,'major'),('medbay','Medbay',150,130,'N',17,10,'major'),
           ('library','Library',102,68,'S',9,7,'shop'),('weaver',"Sesska's textiles",128,68,'S',9,7,'shop'),
           ('bram',"Bram's supplies",144,95,'W',7,9,'shop'),('bar',"Rusk's bar",86,95,'E',7,9,'shop'),
           ('furn',"Tobbin's workshop",102,122,'N',9,7,'shop'),('armoury','Armoury',128,122,'N',9,7,'shop')]
    homes=[('aptB','Residences B',97,48,'S',9,7,'home'),('aptA','Residences A',133,48,'S',9,7,'home'),
           ('aptDoc','Family residences',164,83,'W',7,9,'home'),('aptSec','Security residences',66,107,'E',7,9,'home'),
           ('aptEmpty','Empty flats',133,142,'N',9,7,'home'),('aptMoog','Moogli residences',97,142,'N',9,7,'home')]
    offsets={'S':(0,1),'N':(0,-1),'W':(-1,0),'E':(1,0)}
    for key,title,x,y,facing,w,h,kind in shops+homes:
        ix,iy=offsets[facing]
        # Soft-edged forecourt meets the diagonal spoke, with no raised perimeter curb.
        if kind=='major':
            px,py=x+ix*6,y+iy*6
            for yy in range(py-7,py+8):
                for xx in range(px-10,px+11):
                    if ((xx-px)/10)**2+((yy-py)/7)**2<=1:floor(xx,yy,'p')
        if facing in ('S','N'):
            x0,x1=x-w//2,x+w//2;y0,y1=(y-h+1,y) if facing=='S' else (y,y+h-1)
        else:
            x0,x1=(x,x+w-1) if facing=='W' else (x-w+1,x);y0,y1=y-h//2,y+h//2
        # Rooms occupy the existing curved structural band. Never stamp a
        # rectangular solid footprint across the public annulus or its spokes.
        # The annuli above already contain the roof/collision cells.
        # Recessed, NPC-sized door and a short link to the public ring.
        for step in range(0,5):
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
    def prop(name,x,y,w,h,title,kind='inspect',hint='Inspect',solid=True):
        props.append([name,x,y,w,h,title])
        if solid:
            for yy in range(y+h-1,y+h):
                for xx in range(x,x+w):m.obj[yy][xx]='x'
        if kind:thing(kind,title,hint,x+(w-1)/2,y+h-1,30)
    # The fountain basin is centered at 115.5,95.5. Its south plinth holds BOTH panels.
    # Fountain is a multipart scene; reserve its complete basin footprint.
    for yy in range(cy-2,cy+3):
        for xx in range(cx-3,cx+4):
            if ((xx-cx)/3.6)**2+((yy-cy)/2.6)**2<=1:m.obj[yy][xx]='x'
    thing('board','Community board','Read requests',cx-1,cy+3,21)
    thing('calendar','Community calendar','Open calendar',cx+1,cy+3,21)
    thing('inspect','Water-recycling fountain','Inspect',cx,cy-3,30)
    for x,y,d in [(104,91,'e'),(124,91,'w'),(104,103,'e'),(124,103,'w')]:prop('bench_'+d,x,y,1,3,'Fountain seating ['+d.upper()+']','seat','Sit')
    # Tables and benches flank broad passageways, rather than forming a blocking fence.
    for key,x,y,facing in [('mess',150,60,'S'),('common',80,60,'S'),('fab',80,130,'N'),('medbay',150,130,'N')]:
        sign=1 if facing=='S' else -1
        for ox in (-6,4):
            if key in ('mess','common'):
                px,py=x+ox,y+sign*5
                prop('table',px,py,3,2,'Dining table','inspect')
                thing('seat','Dining chair left','Sit',px,py+1,22);thing('seat','Dining chair right','Sit',px+2,py+1,22)
            else:prop('bench',x+ox,y+sign*5,3,2,'Waiting bench','seat','Sit')
        prop('plants',x-6,y+sign*9,3,2,'Hydroponic garden')
        prop('terminal',x+3,y+sign*2-1,1,2,{'mess':'Mess hall menu','common':'Community activities','fab':'Manufacturing work orders','medbay':'Medbay reception'}[key])
    prop('clothes',124,70,3,2,'Textile display')
    prop('seed_rack',136,88,2,2,'Seed and plant display')
    prop('plants',92,50,3,2,'Resident garden')
    prop('plants',137,138,3,2,'Resident garden')
    for key,title,x,y,facing,w,h,kind in homes:
        ix,iy=offsets[facing]
        px,py=x+ix*4+(3 if iy else 0),y+iy*4+(3 if ix else 0)
        prop('plants',px,py,3,2,'Resident garden')
    # Library garden and south-east games court are chamfered terraces with open approaches.
    def in_poly(px,py,pts):
        inside=False;j=len(pts)-1
        for i,(ax,ay) in enumerate(pts):
            bx,by=pts[j]
            if (ay>py)!=(by>py) and px<(bx-ax)*(py-ay)/(by-ay)+ax:inside=not inside
            j=i
        return inside
    garden=[(99,72),(101,70),(110,70),(110,81),(108,83),(105,80),(99,74)]
    games=[(118,112),(120,110),(125,110),(130,115),(130,119),(120,119),(118,117)]
    for pts,ch in [(garden,'h'),(games,'u')]:
        for yy in range(min(p[1] for p in pts),max(p[1] for p in pts)+1):
            for xx in range(min(p[0] for p in pts),max(p[0] for p in pts)+1):
                if in_poly(xx+.5,yy+.5,pts) and m.floor[yy][xx]=='i':floor(xx,yy,ch)
    prop('flowers',104,71,4,2,'Library flower border','garden','Water flowers')
    prop('flowers',105,76,4,2,'Community planting bed','garden','Water flowers')
    prop('water_tank',109,73,2,3,'Garden watering station','garden','Water flowers')
    prop('bench_e',100,72,1,3,'Reading garden bench [E]','seat','Sit')
    prop('bench_w',109,78,1,3,'Planting-view bench [W]','seat','Sit')
    prop('bench_n',104,78,3,2,'Flower garden bench [N]','seat','Sit')
    prop('books',100,71,2,2,'Garden book exchange','read','Read a community story')
    prop('chess',121,112,2,2,'Community chess table','game','Play a short game')
    prop('hologame',126,116,2,2,'Holographic strategy table','game','Play a short game')
    for x,y,d in [(120,112,'e'),(123,112,'w'),(126,114,'s'),(126,117,'n')]:
        prop('chair_'+d,x,y,1,2,'Game chair ['+d.upper()+']','seat','Sit',False)
    prop('bench_s',124,112,3,2,'Games spectator bench [S]','seat','Sit')
    prop('plants',128,113,2,2,'Games court planter')
    # Market stall is recessed against Bram's wall, with a clear approach from plaza.
    prop('market_canopy',138,85,4,4,"Bram's canopy",None,solid=False)
    for xx in (138,141):m.obj[88][xx]='x'
    prop('market_counter',139,88,3,2,"Bram's supply counter",'market','Browse supplies')
    prop('cargo',142,89,2,2,'Sealed supply crates')
    prop('trolley',140,91,2,2,'Delivery trolley')
    prop('workbench',74,125,3,2,'Public repair bench','repair','Inspect tools')
    prop('medical',155,123,2,3,'First aid supplies','inspect')
    for key,title,x,y,facing,w,h,kind in homes:
        ix,iy=offsets[facing]
        prop('mailbox',x+ix*2+(2 if iy else 0),y+iy*2+(2 if ix else 0),1,2,'Residential mail terminal')
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
    prop('telescope',49,76,2,3,'Lunar telescope','observe','Look through telescope')
    prop('bench_n',50,85,3,2,'Observation bench [N]','seat','Sit')
    thing('observe','Panoramic lunar window','Look outside',54,76,38)
    m.zones.insert(0,['Observation bay',44,72,62,90])
    m.zones.insert(0,['Flower garden',100,72,112,85])
    m.zones.insert(0,['Community games',118,108,131,120])
    m.zones.insert(0,["Bram's market",136,84,143,93])
    # Utilities sit only on solid roof tiles, never on public floor or door approaches.
    roof=[]
    for key,title,x,y,w,h in buildings:
        for name,ox,oy,ww,hh in [('roof_fan',1,1,2,2),('roof_pipe',w-4,h-4,2,2),('roof_duct',w//2,2,3,2)]:
            px,py=x+ox,y+oy
            if all(m.floor[yy][xx]=='#' for yy in range(py,py+hh) for xx in range(px,px+ww)):
                roof.append([name,px,py,ww,hh])
    g['ROOF_PROPS']=roof
    g['SOCIAL_SPOTS']=[['garden',105,73],['garden',106,78],['chess',120,113],['chess',123,113],['hologame',126,115],['hologame',126,118],['observe',51,79],['read',54,85],['browse',138,90],['restock',140,87]]
    m.obj[89][122]='E'
    invisible=[[x,y] for y in range(m.h) for x in range(m.w) if m.obj[y][x]=='x']
    g.update(CONCOURSE_PROPS=props,CONCOURSE_FRONTS=fronts,CONCOURSE_LABELS=[],CONCOURSE_HIDDEN=invisible,ENTRANCES=entries,
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
    visits=[('Evarra',840,900,105,73,'u','garden'),('Merrow',930,990,106,78,'u','garden'),
            ('Owen',840,930,120,113,'r','chess'),("Tar'Besh",840,930,123,113,'l','chess'),
            ('Kit',930,1020,126,115,'d','hologame'),('Pip',930,1020,126,118,'u','hologame'),
            ('Zaas',840,930,51,79,'l','observe'),('Quill',930,990,54,85,'l','read'),
            ('Saffi',780,840,138,90,'r','browse')]
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
