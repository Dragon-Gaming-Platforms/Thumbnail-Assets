#!/usr/bin/env python3
"""Reproduce the owner's original-vector queue collection in a NEW directory.

These are hand-authored SVG concept illustrations, never gameplay captures.
No source images, fonts, scripts, logos, or third-party sprite paths are embedded.
The output directory is required; existing files are NEVER overwritten.
"""
import argparse
import hashlib
import html
import math
from pathlib import Path
import random

# id, display lines, mechanic caption, illustration, visual variant
ART = [
 ('zedinvaders','ZED INVADERS|3D','ISOMETRIC INVADER DEFENSE','invaders',2),
 ('wordle','WORDLE','FIVE LETTERS. SIX CHANCES.','word',0),
 ('vectoid-td-3d-v1.4','VECTOID TD|3D v1.4','BUILD • UPGRADE • DEFEND','tower',1),
 ('tic-tac-toe-3d','3D|TIC-TAC-TOE','THREE LAYERS. ONE WINNING LINE.','cubegrid',0),
 ('survivor','SURVIVOR','RETRO SPACE COMBAT','space',3),
 ('submersible','SUBMERSIBLE','EXPLORE BELOW THE SURFACE','submarine',0),
 ('spashal','SPASHAL','RIDE THE GRAVITY WELL','orbit',0),
 ('spades','SPADES','BID TOGETHER. WIN THE TRICK.','cards',3),
 ('spacecompany','SPACE|COMPANY','RESOURCES TO THE STARS','industry',0),
 ('space-invaders-13k','SPACE INVADERS|13k','FORMATION • FIRE • DEFEND','invaders',0),
 ('space-huggers','SPACE|HUGGERS','PROCEDURAL RUN-AND-GUN','run',2),
 ('solitaire','SOLITAIRE','BUILD THE FOUNDATIONS','cards',0),
 ('sokoban','SOKOBAN','PUSH. PLAN. SOLVE.','boxes',0),
 ('snowrider','SNOWRIDER','CARVE A PATH THROUGH THE SNOW','snow',1),
 ('snake','SNAKE','GROW WITHOUT CROSSING YOUR PATH','snake',0),
 ('slitherlink','SLITHERLINK','ONE UNBROKEN LOOP','loop',0),
 ('skifree','SKIFREE','FIND YOUR LINE DOWNHILL','snow',0),
]

PALETTES = [('#0d2335','#45e0c1','#ffca72'),('#201834','#b6a0ff','#ff927a'),
            ('#152b29','#b6df8b','#f5c97a'),('#2c1b28','#ff9bb7','#a6ddff'),
            ('#142846','#7cbaff','#f8d27f'),('#2c2420','#f0b47d','#a6d9b9')]

def blend(background, foreground, alpha):
    return '#' + ''.join(f'{round(int(background[i:i+2],16)*(1-alpha)+int(foreground[i:i+2],16)*alpha):02x}' for i in (1,3,5))

class Drawing:
    def __init__(self, background='#142846'): self.parts=[];self.background=background
    def add(self,tag,**kw):
        # Preblend translucent decoration for identical output in SVG backends
        # that do not implement element-level opacity (notably svglib).
        opacity=kw.pop('opacity',None)
        if opacity is not None:
            for channel in ['fill','stroke']:
                value=kw.get(channel,'')
                if isinstance(value,str) and len(value)==7 and value.startswith('#'):
                    kw[channel]=blend(self.background,value,float(opacity))
        attrs=' '.join(f'{k.replace("_","-")}="{html.escape(str(v),quote=True)}"' for k,v in kw.items())
        self.parts.append(f'<{tag} {attrs}/>')
    def rect(self,x,y,w,h,fill,rx=0,**kw): self.add('rect',x=x,y=y,width=w,height=h,fill=fill,rx=rx,**kw)
    def circle(self,x,y,r,fill,**kw): self.add('circle',cx=x,cy=y,r=r,fill=fill,**kw)
    def path(self,p,fill='none',**kw): self.add('path',d=p,fill=fill,**kw)
    def line(self,x,y,X,Y,color,width=2,**kw):self.add('line',x1=x,y1=y,x2=X,y2=Y,stroke=color,stroke_width=width,stroke_linecap='round',**kw)
    def poly(self,pts,fill,**kw):self.add('polygon',points=' '.join(f'{x:.1f},{y:.1f}' for x,y in pts),fill=fill,**kw)
    def text(self,x,y,t,size=16,color='#edf5f5',**kw):
        family=kw.pop('font_family','DejaVu Sans, sans-serif')
        a=' '.join(f'{k.replace("_","-")}="{html.escape(str(v),quote=True)}"' for k,v in kw.items())
        self.parts.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-family="{family}" {a}>{html.escape(str(t))}</text>')

def cube(d,x,y,s,h,c):
    d.poly([(x,y),(x+s,y-s/2),(x+2*s,y),(x+s,y+s/2)],c)
    d.poly([(x,y),(x+s,y+s/2),(x+s,y+s/2+h),(x,y+h)],'#335069')
    d.poly([(x+s,y+s/2),(x+2*s,y),(x+2*s,y+h),(x+s,y+s/2+h)],'#20394d')

def diamond(d,x,y,r,c):d.poly([(x,y-r),(x+r,y),(x,y+r),(x-r,y)],c)
def star(d,x,y,r,c):
    d.poly([(x+math.sin(i*math.pi/5)*(r if i%2==0 else r*.42),y-math.cos(i*math.pi/5)*(r if i%2==0 else r*.42)) for i in range(10)],c)
def ship(d,x,y,c):
    d.poly([(x,y-26),(x+23,y+22),(x,y+12),(x-23,y+22)],c)
    d.poly([(x,y-11),(x+6,y+7),(x-6,y+7)],'#14334c')
    d.path(f'M{x-7} {y+22} L{x} {y+43} L{x+7} {y+22}', '#ffc978')
def person(d,x,y,c):
    d.circle(x,y-15,6,c);d.line(x,y-7,x,y+10,c,5);d.path(f'M{x-11} {y+1} L{x} {y-4} L{x+12} {y+3} M{x-9} {y+23} L{x} {y+10} L{x+10} {y+24}',stroke=c,stroke_width=4,stroke_linecap='round')
def tree(d,x,y,s=1):
    d.line(x,y,x,y-25*s,'#7c9b96',4*s);d.poly([(x-16*s,y-16*s),(x,y-53*s),(x+16*s,y-16*s)],'#62a79d')
def card(d,x,y,label,c,angle=0):
    d.parts.append(f'<g transform="rotate({angle} {x+32} {y+43})">');d.rect(x,y,63,87,'#f6eedf',7);d.text(x+9,y+24,label,20,c,font_weight='bold');diamond(d,x+32,y+52,12,c);d.parts.append('</g>')
def grid(d,cols,rows,cell=31,x=35,y=25):
    for j in range(rows):
        for i in range(cols):d.rect(x+i*cell,y+j*cell,cell-3,cell-3,'#24404c',4)

def scene(d,kind,v,a,b,rng):
    # All coordinates are local to the 400×220 illustration region.
    if kind in ('space','invaders'):
        for _ in range(24):d.circle(rng.randint(0,385),rng.randint(0,205),rng.choice([1,1,2]),'#69818e')
        if kind=='invaders':
            for j in range(3):
                for i in range(5):
                    x=50+i*65+(j*8 if v else 0);y=25+j*42
                    if v: cube(d,x,y,11,10,a if j%2 else b)
                    else: d.poly([(x-13,y),(x,y-12),(x+13,y),(x+7,y+9),(x-7,y+9)],a if j%2 else b)
            ship(d,190,168,a);d.line(190,106,190,135,b,4)
        else:
            ship(d,170,108,a)
            for x,y,s in [(50,35,20),(325,55,26),(282,164,18),(70,180,14)]:
                d.poly([(x+math.cos(t)*s,y+math.sin(t)*s) for t in [0,1,1.8,2.8,3.8,5]],'#536b7f',stroke='#91a1a7',stroke_width=2)
            if v==3:
                for x in [16,355]:d.rect(x,62,12,96,b,2)
                d.path('M80 20 L310 20 L310 200 L80 200',stroke=a,stroke_width=2,stroke_dasharray='8 10')
            elif v==1:
                d.path('M10 195 L90 145 L125 163 L250 35 L350 105 L398 81',stroke=b,stroke_width=2)
            else:d.path('M130 196 Q140 155 170 142',stroke=b,stroke_width=3,stroke_dasharray='5 7')
    elif kind=='word':
        words=['TRAIL','CRANE','BRAVE','BRINE'];colors=['#405468','#8264ae','#48a49b']
        for j,word in enumerate(words):
            for i,ch in enumerate(word):
                x=80+i*43;y=8+j*43;d.rect(x,y,37,37,colors[2 if ch=='BRINE'[i] else (1 if ch in 'BRINE' else 0)],5);d.text(x+18,y+26,ch,23,'#fff',text_anchor='middle',font_weight='bold')
    elif kind in ('tower','balloons'):
        d.path('M10 160 L80 160 L80 65 L245 65 L245 175 L380 175',stroke='#46616a',stroke_width=25,stroke_linejoin='round')
        for x,y in [(131,117),(208,25),(300,121)]:
            d.circle(x,y,27,'none',stroke=a,stroke_width=1,stroke_dasharray='4 5');cube(d,x-13,y,13,24,a);d.line(x,y+5,x+13,y-12,b,5)
        for i in range(6):
            x=22+i*29;y=160 if i<2 else 65
            if kind=='balloons':d.add('ellipse',cx=x+35,cy=y,rx=10,ry=14,fill=[a,b,'#ee91aa'][i%3]);d.path(f'M{x+35} {y+14} q-6 8 0 18',stroke=b)
            else:diamond(d,x+35,y,7,b)
    elif kind=='cubegrid':
        for layer in range(3):
            x=30+layer*70;y=55+layer*36
            for j in range(3):
                for i in range(3):d.poly([(x+i*34+j*14,y+j*21),(x+i*34+j*14+29,y+j*21),(x+i*34+j*14+43,y+j*21+17),(x+i*34+j*14+14,y+j*21+17)],'#304959',stroke='#82939b',stroke_width=1)
            d.circle(x+48+layer*34,y+29,7,a,stroke=a)
        d.line(78,84,286,198,b,4)
    elif kind=='submarine':
        for y in [35,90,145]:d.path(f'M0 {y} Q80 {y-20} 160 {y} T400 {y}',stroke='#3d7281',stroke_width=2)
        d.add('ellipse',cx=200,cy=112,rx=75,ry=31,fill=a);d.rect(181,67,25,22,a,5);d.path('M194 72 V56 H213',stroke=a,stroke_width=8)
        d.poly([(132,101),(109,86),(109,138),(132,122)],b)
        for x in [174,205,236]:d.circle(x,110,10,'#163d57',stroke=b,stroke_width=3)
        for x,y in [(283,81),(311,46),(338,20)]:d.circle(x,y,6,'none',stroke='#8cc5d4',stroke_width=2)
        d.path('M20 215 Q40 140 55 210 M350 210 Q332 146 370 193',stroke='#63b5a4',stroke_width=6)
    elif kind=='orbit':
        d.add('ellipse',cx=215,cy=110,rx=145,ry=72,fill='none',stroke=a,stroke_width=2,transform='rotate(-22 215 110)',stroke_dasharray='8 7');d.circle(220,105,49,b);d.circle(204,90,12,'#fce2a5');d.circle(241,121,17,'#d09661');ship(d,85,139,a);d.circle(358,64,12,a)
    elif kind=='cards':
        d.add('ellipse',cx=210,cy=124,rx=172,ry=90,fill='#244847')
        labels= [['A','2','3','4'],['Q','A','7','K'],['A','K','Q','J'],['A','K','8','4']][v]
        for i,t in enumerate(labels):card(d,50+i*64,60-abs(i-1.5)*10,t,'#b05262' if (i+v)%2 else '#25374d',(i-1.5)*9)
        if v==2:star(d,341,67,24,b);d.text(339,113,'JOKER',11,b,text_anchor='middle',font_weight='bold')
        elif v==3:d.path('M190 17 Q169 41 167 49 Q169 64 183 61 L179 73 H202 L197 61 Q214 64 216 49 Q213 38 190 17',a)
        elif v==0:
            for x in [85,155,225,295]:d.rect(x,158,49,34,'none',4,stroke=a,stroke_width=2)
    elif kind=='industry':
        for x,h in [(35,58),(87,97),(144,73)]:d.rect(x,180-h,38,h,'#426276',4);d.rect(x+8,192-h,8,14,b,1)
        d.path('M10 194 H215 M110 60 V32 H160',stroke=a,stroke_width=3);d.circle(166,31,12,b);d.circle(284,62,44,'none',stroke='#607d91',stroke_width=2);d.path('M240 62 H328 M284 18 V106',stroke=a,stroke_width=2);ship(d,302,152,a);d.line(180,160,237,160,b,3,stroke_dasharray='6 7')
    elif kind in ('boxes','regions','islands','loop'):
        if kind=='boxes':
            grid(d,7,5,33,60,20)
            for i,j in [(1,1),(3,2),(4,3)]:
                d.rect(60+i*33,20+j*33,29,29,b,4);d.path(f'M{65+i*33} {25+j*33} l19 19 m0 -19 l-19 19',stroke='#8a694d',stroke_width=2)
            for i,j in [(5,1),(5,2),(5,3)]:d.circle(74+i*33,34+j*33,6,a)
            d.circle(105,134,9,a)
        elif kind=='regions':
            cells=[[1,2,2,3,3,3],[4,4,5,5,5,9],[4,4,5,5,9,9],[9,9,9,9,9,9]]
            cols={1:'#dcbe82',2:'#8ebac8',3:'#ad9cce',4:'#72a79d',5:'#c591a2',9:'#597786'}
            for j,row in enumerate(cells):
                for i,n in enumerate(row):d.rect(50+i*42,25+j*42,39,39,cols[n],3);d.text(69+i*42,52+j*42,n,19,'#152835',text_anchor='middle')
        elif kind=='loop':
            X=68;Y=30;s=42;edges=set();path=[(0,0),(1,0),(2,0),(3,0),(4,0),(4,1),(5,1),(5,2),(4,2),(4,3),(3,3),(2,3),(2,2),(1,2),(1,3),(0,3),(0,2),(0,1),(0,0)]
            for p,q in zip(path,path[1:]):edges.add(tuple(sorted([p,q])));d.line(X+p[0]*s,Y+p[1]*s,X+q[0]*s,Y+q[1]*s,a,5)
            for j in range(4):
                for i in range(6):d.circle(X+i*s,Y+j*s,3,'#c4d7dc')
            for j in range(3):
                for i in range(5):
                    ps=[(i,j),(i+1,j),(i+1,j+1),(i,j+1),(i,j)];n=sum(tuple(sorted([p,q])) in edges for p,q in zip(ps,ps[1:]));d.text(X+20+i*s,Y+28+j*s,n,17,b,text_anchor='middle')
        else:
            # Connected sea and disconnected land groups, no black 2x2 blocks.
            cells=[[1,0,1,1,0,1,1],[0,0,0,1,0,0,1],[1,0,1,0,0,1,1],[1,0,1,1,0,1,1],[1,0,0,0,0,0,1]]
            seen=set()
            for j,row in enumerate(cells):
                for i,n in enumerate(row):d.rect(60+i*30,22+j*30,28,28,'#e7e4cc' if n else '#35566b',2)
            for j,row in enumerate(cells):
                for i,n in enumerate(row):
                    if not n or (i,j) in seen:continue
                    todo=[(i,j)];group=set()
                    while todo:
                        x,y=todo.pop()
                        if (x,y) in group or not(0<=x<7 and 0<=y<5) or not cells[y][x]:continue
                        group.add((x,y));todo.extend([(x-1,y),(x+1,y),(x,y-1),(x,y+1)])
                    seen.update(group);d.text(74+i*30,42+j*30,len(group),17,'#243a43',text_anchor='middle')
    elif kind=='snow':
        d.path('M0 80 L70 20 L130 75 L200 10 L280 76 L350 35 L400 90 V220 H0 Z','#d6e3e4');d.path('M0 150 Q140 93 245 166 T400 190 V220 H0 Z','#a6c9d3');d.path('M220 50 Q145 95 208 130 T173 210',stroke='#729aaa',stroke_width=3,stroke_dasharray='7 6')
        for x,y in [(53,145),(310,118),(348,200)]:tree(d,x,y,.85)
        if v==0:person(d,203,119,'#45667d');d.line(188,150,220,140,b,4);d.line(194,156,226,146,b,4)
        else:d.path('M171 144 L211 144 L219 152 L230 151 M174 152 H216',stroke='#8b645b',stroke_width=5);d.line(182,130,182,144,a,4);d.line(210,130,210,144,a,4)
    elif kind=='snake':
        grid(d,9,5,27,35,32);p= 'M65 139 H146 V86 H254 V166 H308' if v==0 else 'M64 57 H225 V111 H118 V165 H307';d.path(p,stroke=a,stroke_width=19,stroke_linejoin='round',stroke_linecap='round');d.circle(310,165 if v else 166,10,a);d.circle(315,161,2,'#183746');diamond(d,280 if v else 199,57 if v else 139,10,b)
    elif kind=='sequence':
        for i,(x,y) in enumerate([(125,62),(220,62),(220,149),(125,149)]):
            d.rect(x,y,77,70,[a,'#d68caa',b,'#90a4d8'][i],18);d.text(x+38,y+45,i+1,25,'#193544',text_anchor='middle',font_weight='bold')
        d.circle(210,22,4,b);d.circle(230,22,4,a);d.circle(250,22,4,b)
    elif kind=='beacon':
        d.path('M20 210 L85 132 L140 174 L205 105 L276 170 L340 134 L400 212','#304757');d.rect(198,69,52,140,'#50677d',4);d.poly([(187,73),(224,37),(262,73)],b);d.circle(224,92,15,a);d.path('M224 83 L334 12 L376 55 L230 101',a,opacity='.2');d.path('M75 70 Q92 34 111 75 Q130 34 147 70 Q117 103 111 75 Q104 103 75 70',b);d.path('M130 210 Q160 176 223 170',stroke=b,stroke_width=3)
    elif kind=='rays':
        d.poly([(45,160),(92,18),(290,30),(336,185)],a,opacity='.23')
        for x,y in [(92,18),(150,30),(290,30),(300,145),(336,185),(165,195)]:d.line(45,160,x,y,a,1)
        d.poly([(151,55),(229,55),(250,127),(171,132)],'#426177',stroke=b,stroke_width=2);d.poly([(250,127),(336,185),(382,220),(295,210)],'#101c2b');d.circle(45,160,9,b)
    elif kind=='dungeon':
        for j in range(4):
            for i in range(7):d.rect(40+i*43,20+j*43,39,39,'#2d384e' if (i+j)%3 else '#4b5064',3)
        d.path('M65 168 H151 V83 H281',stroke=a,stroke_width=4,stroke_dasharray='7 8');d.text(150,127,'@' if v==0 else '+',35,b,text_anchor='middle');d.rect(263,48,30,46,'#171c30',13,stroke=b,stroke_width=3)
        for x,y in [(106,40),(280,170)]:diamond(d,x,y,10,b)
        if v: d.path('M55 155 L95 116 M74 115 L96 136',stroke='#f1e6ca',stroke_width=6)
    elif kind=='recoil':
        for x,y,w in [(24,175,91),(148,125,73),(269,68,96)]:d.rect(x,y,w,13,'#4e657b',3)
        d.rect(162,92,34,19,a,4);d.rect(188,97,30,8,b,2);d.path('M177 111 Q105 80 84 39',stroke=a,stroke_width=3,stroke_dasharray='7 7');d.poly([(81,26),(75,48),(96,40)],a);d.path('M223 102 h27 m-20 -10 l15 -9 m-15 27 l15 9',stroke=b,stroke_width=3)
    elif kind=='terminal':
        d.rect(39,22,305,173,'#4a6578',9);d.rect(51,44,281,137,'#102c32',4);d.circle(56,32,3,a);d.circle(67,32,3,b)
        if v==0:d.text(67,78,'$ boot rv32ima',18,a,font_family='DejaVu Sans Mono, monospace');d.text(67,111,'[ ok ] kernel 6.1.14',15,'#c6ded6');d.text(67,143,'$ cat readme.txt',16,b)
        else:d.text(68,78,'C:> cd windows',18,a);d.text(68,111,'C:> win',18,b);d.rect(235,94,75,58,'#7794ab',3);d.rect(238,97,69,9,'#334963');d.rect(241,113,29,32,'#d3decb',2)
        d.rect(150,197,80,7,'#667e89',3)
    elif kind=='pulley':
        d.line(105,17,298,17,'#8b9ba1',7);d.circle(176,62,32,'#4e697c',stroke=a,stroke_width=4);d.circle(176,62,8,b);d.circle(226,132,30,'#4e697c',stroke=a,stroke_width=4);d.circle(226,132,7,b);d.path('M145 196 V62 A31 31 0 0 1 207 62 V132 A19 19 0 0 0 245 132 V21',stroke=b,stroke_width=4);d.line(226,164,226,179,a,4);d.rect(198,179,56,35,a,4);d.path('M140 165 l-12 13 m12 -13 l12 13',stroke=b,stroke_width=3)
    elif kind=='pong':
        d.rect(27,20,330,177,'#132e42',8,stroke='#4e7281',stroke_width=2);d.line(192,28,192,190,'#54747e',2,stroke_dasharray='7 10');d.rect(49,57,11,63,a,4);d.rect(322,123,11,57,b,4);d.circle(238,91,9,'#f4eacc');d.path('M122 134 L190 108 L229 93',stroke=a,stroke_width=2,stroke_dasharray='4 7')
    elif kind in ('city','voxel'):
        heights= ([35,70,20,50,25,85,36,20,48] if kind=='city' else [[35,15,65,20,50,15,30,20,25],[20,65,30,60,20,40,30,45,15],[65,25,35,20,80,15,30,60,25],[25,30,60,60,15,30,45,20,75]][v])
        for j in range(3):
            for i in range(3):
                x=35+i*67+j*31;y=90+j*32-i*10;h=heights[j*3+i];cube(d,x,y,29,h,a if (i+j)%3 else b)
                if kind=='city':
                    for n in range(int(h/15)):d.rect(x+7,y+8+n*12,7,5,'#c9e2dc',1)
        if kind=='city' and v==1:tree(d,326,170,.8);d.path('M25 209 L198 209 L351 157',stroke=b,stroke_width=3)
        if kind=='voxel':d.circle(330,35,22,b)
    elif kind=='gem':
        d.poly([(95,180),(139,53),(211,17),(291,83),(316,180),(203,204)],'#48516d',stroke=a,stroke_width=2);d.poly([(95,180),(211,17),(190,153)],'#242d48');d.poly([(211,17),(291,83),(190,153)],'#8d83b3');d.poly([(190,153),(291,83),(316,180),(203,204)],'#3a4361');star(d,319,34,10,b)
    elif kind=='stones':
        for i in range(9):d.line(53+i*33,25,53+i*33,190,'#a49d82',1)
        for j in range(6):d.line(53,25+j*33,317,25+j*33,'#a49d82',1)
        for i in range(5):d.circle(86+i*33,58+i*33,12,a,stroke='#e6e8db',stroke_width=1)
        for x,y in [(86,157),(152,25),(251,58),(284,157),(185,25)]:d.circle(x,y,12,'#ece1c7')
    elif kind=='particles':
        for k,c in enumerate([a,b,'#d19adb','#8dbddd']):
            for n in range(40):
                t=n*.25+k;rad=20+n*1.5;d.circle(195+math.cos(t)*rad+k*7,105+math.sin(t)*rad*.78,2.5,c)
        for i in range(4):
            for j in range(4):d.rect(306+i*15,137+j*15,11,11,[a,b,'#5e778e'][(i+j)%3],2)
    elif kind=='maze':
        grid(d,10,6,29,25,18)
        paths=['M39 61 H155 V119 H271 V177 H184','M39 177 H126 V90 H242 V32 H300','M39 32 H97 V148 H213 V61 H300']
        d.path(paths[v],stroke=a,stroke_width=9,stroke_linecap='round',stroke_linejoin='round')
        for x,y in [(67,32),(271,90),(155,177),(300,148)]:diamond(d,x,y,5,b)
        d.circle(39,[61,177,32][v],8,b);d.path('M333 93 l17 17 -17 17',stroke=b,stroke_width=3)
    elif kind=='hexmap':
        coords=[]
        for j in range(4):
            for i in range(6):
                x=46+i*46+j*23;y=35+j*39;coords.append((x,y));d.poly([(x+25*math.cos(t*math.pi/3),y+25*math.sin(t*math.pi/3)) for t in range(6)],'#335267',stroke='#758a93',stroke_width=1)
        if v==1:
            for i in [0,7,8,14,15,21]:d.circle(*coords[i],15,a)
            for i in [3,9,10,16,17]:d.circle(*coords[i],15,b)
        else:
            for n in [7,10,15]:
                x,y=coords[n];d.rect(x-14,y-7,28,15,a,4);d.circle(x,y,8,b);d.line(x,y,x+22,y-14,b,5)
            d.path('M70 153 L155 153 L203 114',stroke=b,stroke_width=3,stroke_dasharray='6 7')
    elif kind in ('run','jump','moon'):
        if kind=='moon':d.circle(310,42,31,'#d3e6ce');d.circle(322,30,31,'#203e51')
        platforms=[(20,175,94),(137,130,82),(255,79,103)] if kind!='jump' else [(32,179,73),(136,122,76),(252,62,70)]
        for x,y,w in platforms:d.rect(x,y,w,12,'#526b81',3);d.line(x,y,x+w,y,a,2)
        d.path('M80 155 Q115 44 170 111 Q215 15 277 58',stroke=b,stroke_width=2,stroke_dasharray='7 7')
        if kind!='jump' or v!=2:person(d,170,100,a)
        else:star(d,172,90,15,a)  # No GitHub Octocat mascot.
        if kind=='run':
            for x in [112,228,240]:d.poly([(x,200),(x+10,177),(x+20,200)],'#d88ea0')
            if v==2:d.path('M197 97 h37 m-10 -7 l10 7 -10 7',stroke=b,stroke_width=3)
        elif kind=='jump' and v==0:d.path('M39 170 l7 -7 -7 -7 7 -7 -7 -7',stroke=b,stroke_width=3)
    elif kind=='bike':
        d.path('M5 191 L90 180 L210 106 L260 147 L398 110',stroke='#74878f',stroke_width=9)
        d.circle(169,111,24,'#172b40',stroke=a,stroke_width=5);d.circle(239,91,24,'#172b40',stroke=a,stroke_width=5);d.path('M169 111 L198 73 L216 102 Z M198 73 L225 67 L239 91 M191 67 L207 64',stroke=b,stroke_width=5,stroke_linejoin='round');d.circle(204,36,9,a);d.path('M203 46 L190 63 L216 67 L224 56 M190 63 L207 87',stroke=a,stroke_width=5)
    elif kind=='garden':
        d.path('M22 207 V34 Q200 -10 370 34 V207 M22 65 H370 M105 16 V205 M286 16 V205',stroke='#607b70',stroke_width=4)
        for i in range(9):
            x=40+i*37;d.path(f'M{x} 205 Q{x-23} 150 {x+6} 128 Q{x+21} 165 {x} 205','#6aa18e')
        d.circle(200,114,39,a,opacity='.15');d.rect(187,98,26,37,b,6);d.path('M191 96 V87 Q200 77 209 87 V96',stroke=b,stroke_width=3)
        for x,y in [(65,99),(319,137)]:diamond(d,x,y,7,b)
    elif kind=='candy':
        for x,y,angle in [(66,58,25),(178,35,-15),(301,70,10)]:
            d.parts.append(f'<g transform="rotate({angle} {x} {y})">');d.poly([(x-35,y-15),(x-15,y),(x-35,y+15)],a);d.poly([(x+35,y-15),(x+15,y),(x+35,y+15)],a);d.rect(x-19,y-16,38,32,b,8);d.line(x-8,y-12,x+8,y+12,'#f7e6ca',5);d.parts.append('</g>')
        d.path('M100 148 Q200 205 302 148 L289 190 Q202 232 113 190 Z',a);d.path('M192 81 Q205 113 203 142',stroke=b,stroke_width=3,stroke_dasharray='5 6')
    elif kind=='marbles':
        d.poly([(40,159),(188,60),(365,124),(214,218)],'#58736d',stroke=a,stroke_width=2)
        for x,y in [(204,154),(261,134)]:d.poly([(x-13,y),(x,y-9),(x+16,y-3),(x+1,y+8)],'#da8790')
        for x,y,r,c in [(112,151,17,a),(225,113,22,b)]:d.add('ellipse',cx=x+3,cy=y+15,rx=r,ry=6,fill='#294548');d.circle(x,y,r,c);d.circle(x-6,y-7,5,'#e9edcd')
        d.path('M140 149 L186 138',stroke=b,stroke_width=3)
    elif kind=='road':
        if v==0:
            d.path('M0 99 Q75 52 126 91 Q200 16 285 91 Q353 43 400 94 V220 H0 Z','#385c6d');d.path('M30 220 Q200 140 202 75 H222 Q245 154 380 220 Z','#253b50');d.path('M203 215 Q216 148 213 82',stroke=b,stroke_width=4,stroke_dasharray='14 10');d.rect(215,159,55,30,a,6);d.rect(224,165,36,8,'#32536a',2)
        else:
            for x,y,w,h in [(25,24,95,58),(260,29,85,66),(47,140,100,57),(274,151,90,45)]:d.rect(x,y,w,h,'#486276',3)
            d.path('M175 215 V116 Q175 110 184 110 H378',stroke='#7c8b93',stroke_width=45);d.path('M175 215 V116 H378',stroke=b,stroke_width=2,stroke_dasharray='8 10');d.rect(159,136,30,47,a,6);d.rect(165,141,18,11,'#30465a',2)
    elif kind=='island':
        d.add('ellipse',cx=200,cy=158,rx=171,ry=46,fill='#295c77');d.poly([(61,139),(103,99),(165,117),(219,70),(287,103),(345,142),(267,181),(124,174)],'#80aaa1');d.poly([(103,99),(122,143),(165,117)],'#b1c5a6');d.poly([(219,70),(202,126),(287,103)],'#c6d0b2');d.poly([(202,126),(267,181),(287,103)],'#527e7a');tree(d,194,118,.8);d.rect(119,121,30,24,'#6d6b75',2);d.poly([(114,121),(134,104),(154,121)],b);d.circle(320,37,21,b)
    elif kind=='ink':
        for i,c in enumerate([a,b,'#ad89e0','#e393b1']):
            d.path(f'M{25+i*12} {180-i*30} C90 {10+i*15} 155 {215-i*20} 204 {100+i*10} S345 {30+i*20} 372 {110+i*25}',stroke=c,stroke_width=13-i*2,opacity='.8',stroke_linecap='round')
        for i in range(18):d.circle(rng.randint(45,365),rng.randint(40,193),rng.randint(2,6),a if i%2 else b,opacity='.7')
    elif kind=='timer':
        d.circle(193,117,81,'none',stroke='#4e6579',stroke_width=14);d.path('M193 36 A81 81 0 1 1 117 145',stroke=a,stroke_width=14,stroke_linecap='round');d.rect(169,11,48,12,b,4);d.line(193,34,193,22,b,6);d.text(193,137,'10',63,b,text_anchor='middle',font_weight='bold');d.path('M287 66 l25 -15 m-18 51 h31',stroke=b,stroke_width=4)
    elif kind=='bridges':
        pts=[(66,43),(191,43),(316,43),(66,162),(191,162),(316,162)];edges=[(0,1,2),(1,2,1),(0,3,1),(1,4,1),(2,5,2),(3,4,2),(4,5,1)];counts=[0]*6
        for i,j,n in edges:
            x,y=pts[i];X,Y=pts[j];counts[i]+=n;counts[j]+=n
            for offset in ([-4,4] if n==2 else [0]):d.line(x+(offset if x==X else 0),y+(offset if y==Y else 0),X+(offset if x==X else 0),Y+(offset if y==Y else 0),a,3)
        for (x,y),n in zip(pts,counts):d.circle(x,y,20,'#e3e8d4');d.text(x,y+7,n,20,'#253a4d',text_anchor='middle',font_weight='bold')
    elif kind=='hollow':
        d.path('M15 215 Q-8 94 62 24 L95 22 Q36 105 70 215 Z M312 215 Q360 118 308 15 L345 15 Q405 104 370 215 Z','#456879');d.path('M87 204 Q192 155 313 204',stroke=a,stroke_width=3);person(d,134,143,b);d.circle(264,139,12,a)
        for s in [-1,1]:
            for k in range(4):d.path(f'M264 139 L{264+s*(23+k*3)} {129+k*7} l{s*7} 14',stroke=a,stroke_width=2)
        d.circle(207,44,22,'#8fabc2',opacity='.3')
    elif kind=='tactics':
        for j in range(4):
            for i in range(6):d.poly([(38+i*46+j*10,35+j*36),(78+i*46+j*10,35+j*36),(88+i*46+j*10,64+j*36),(48+i*46+j*10,64+j*36)],'#334e65',stroke='#6b8290',stroke_width=1)
        for x,y in [(82,105),(145,150),(218,75)]:d.circle(x,y,13,a);d.line(x,y-6,x,y+6,'#243949',3)
        for x,y in [(300,75),(305,153)]:diamond(d,x,y,13,b)
        d.rect(187,95,14,33,b,3);d.circle(194,91,9,'#e7e7c3');d.circle(194,91,28,'none',stroke=b,stroke_width=1)
    elif kind=='bird':
        for x,y in [(75,74),(205,142),(330,80)]:d.rect(x,0,23,y-30,'#42617a',5);d.rect(x,y+37,23,200-y,'#42617a',5);d.line(x-4,y-30,x+27,y-30,a,3);d.line(x-4,y+37,x+27,y+37,a,3)
        y=102-v*12;d.path(f'M33 {y+5} Q127 {y-60} 280 90',stroke=b,stroke_width=2,stroke_dasharray='5 8');d.poly([(123,y),(145,y-26),(146,y-6),(166,y-10),(153,y+3),(140,y+12)],b);d.poly([(137,y+1),(126,y-18),(150,y-6)],a)
    elif kind=='sand':
        for j in range(8):
            for i in range(30):
                y=194-j*11;x=25+i*11
                if j<3 or (5<i<17 and j<7-abs(i-11)//3):d.rect(x,y,10,10,b if i<20 else '#72b5cc',1)
        for i in range(15):d.rect(110+rng.randrange(70),25+rng.randrange(90),6,6,b,1)
        d.path('M280 170 Q250 125 277 96 Q305 138 280 170','#a5c28c');d.path('M283 181 V140',stroke=a,stroke_width=3)
    elif kind=='lantern':
        d.path('M5 165 L52 139 L93 165 L139 132 L173 164 L216 127 L256 165 L298 141 L350 163 V220 H5 Z','#334d63');d.circle(205,102,69,b,opacity='.12');d.rect(177,66,58,84,'#d7bd85',8);d.rect(187,78,38,60,'#ffe4a0',3);d.path('M185 65 V53 Q205 32 227 53 V65 M181 151 H232 M205 73 V140',stroke=a,stroke_width=4)
        for y in [40,92,172]:d.path(f'M8 {y} Q60 {y-16} 112 {y} M280 {y} Q330 {y+18} 390 {y}',stroke='#85adb4',stroke_width=2)
    elif kind=='duck':
        d.path('M4 206 Q70 178 140 206 T390 201',stroke='#92b9a4',stroke_width=12)
        for x,y in [(117,70),(264,111)]:d.path(f'M{x-42} {y+11} Q{x-12} {y-11} {x-7} {y-31} Q{x+1} {y-9} {x+27} {y} Q{x+42} {y+4} {x+30} {y+10} L{x+11} {y+15} L{x-9} {y+22} Z',a);d.line(x-16,y+9,x+7,y+8,b,3)
        d.circle(307,48,26,'none',stroke=b,stroke_width=2);d.line(307,13,307,31,b,2);d.line(272,48,290,48,b,2)
    elif kind=='dig':
        for j in range(5):
            for i in range(9):d.rect(22+i*36,18+j*36,33,33,'#5b5557',3)
        d.path('M35 33 H179 V105 H287 V177 H106',stroke='#172e40',stroke_width=25,stroke_linejoin='round')
        for x,y in [(107,33),(287,104),(143,177)]:diamond(d,x,y,12,b)
        d.path('M66 119 Q84 94 105 111 M88 106 L66 143',stroke=a,stroke_width=6)
    elif kind=='crystals':
        for x,y,s in [(80,105,1.3),(181,143,.8),(285,87,1.7)]:
            d.poly([(x-20*s,y),(x,y-48*s),(x+22*s,y),(x,y+42*s)],a,stroke='#b1e7df',stroke_width=2);d.poly([(x,y-48*s),(x+22*s,y),(x,y+42*s)],'#527895');d.line(x,y-43*s,x,y+35*s,b,1)
        for x,y in [(32,40),(201,31),(346,172)]:star(d,x,y,7,b)
    elif kind=='chocolate':
        for j in range(4):
            for i in range(6-j):
                x=46+i*44;y=27+j*43;d.rect(x,y,39,38,'#a47660',4);d.rect(x+5,y+5,29,26,'#70514c',3)
        d.circle(65,45,12,b);d.path('M60 40 l10 10 m0 -10 l-10 10',stroke='#4c404b',stroke_width=3);d.path('M226 187 L309 128',stroke=a,stroke_width=3,stroke_dasharray='5 7')
    elif kind=='chess':
        for j in range(4):
            for i in range(7):d.poly([(35+i*40+j*13,92+j*25),(75+i*40+j*13,92+j*25),(88+i*40+j*13,117+j*25),(48+i*40+j*13,117+j*25)],'#b3c1ad' if (i+j)%2 else '#486777')
        d.path('M139 162 L147 139 L145 107 L131 96 L148 73 L171 64 L184 100 L169 120 L174 142 L186 162 Z',b);d.circle(158,88,3,'#304354');d.path('M238 125 L243 94 H264 L269 125 M245 92 V80 M260 92 V80 M235 128 H273',stroke=a,stroke_width=7,stroke_linejoin='round')
    elif kind=='cells':
        for x in [40,236]:
            d.rect(x,27,111,153,'#2f4a60',7,stroke='#758b94',stroke_width=2)
            for i in range(4):d.line(x+18+i*24,31,x+18+i*24,176,'#8eaaa9',4)
        person(d,94,125,a);person(d,290,125,b);d.path('M122 200 H195 V75 H223',stroke=b,stroke_width=3,stroke_dasharray='5 7');d.circle(191,53,11,b);d.line(200,62,219,81,b,5);d.line(211,74,218,68,b,4)
    elif kind=='flock':
        for n in range(39):
            t=n*.48;r=20+n*3;x=190+math.cos(t)*r;y=106+math.sin(t)*r*.5;angle=t+.9
            pts=[(x+math.cos(angle)*10,y+math.sin(angle)*10),(x+math.cos(angle+2.6)*7,y+math.sin(angle+2.6)*7),(x,y),(x+math.cos(angle-2.6)*7,y+math.sin(angle-2.6)*7)];d.poly(pts,a if n%3 else b)
        d.circle(204,112,64,'none',stroke='#7593a1',stroke_width=1,stroke_dasharray='4 8')
    elif kind=='banana':
        grid(d,7,5,30,62,20)
        for x,y in [(93,49),(183,109),(243,139)]:d.path(f'M{x-12} {y-16} Q{x-2} {y+16} {x+24} {y-6} Q{x+4} {y+34} {x-14} {y+2} Z',b)
        d.path('M78 158 H138 V98 H258',stroke=a,stroke_width=3,stroke_dasharray='6 7')
    elif kind=='tank':
        d.rect(108,86,136,76,'#263c4c',22,stroke='#83988f',stroke_width=3);d.rect(129,76,95,86,a,12);d.circle(177,111,26,b);d.path('M185 102 L254 52',stroke=b,stroke_width=17);d.path('M270 42 l19 -13 m-10 26 h27',stroke=a,stroke_width=3)
        for i in range(5):d.rect(115+i*24,154,13,12,'#152e40',2)
        d.rect(31,40,42,49,'#596877',4);d.rect(288,153,60,36,'#596877',4)
    elif kind=='blocks':
        d.path('M5 160 Q70 135 155 164 T395 161 V216 H5 Z','#2b647b');grid(d,8,5,28,70,35)
        for i,j,c in [(0,4,a),(1,4,a),(2,4,b),(2,3,b),(3,4,b),(4,4,a),(4,3,a),(4,2,a),(5,4,b),(6,4,b),(6,3,b)]:d.rect(70+i*28,35+j*28,25,25,c,3)
        d.rect(238,16,25,25,b,3);d.rect(266,16,25,25,b,3);d.rect(266,44,25,25,b,3)
        for x,y in [(40,80),(345,70),(323,125)]:d.circle(x,y,5,'none',stroke=a,stroke_width=2)
    elif kind=='graph':
        d.path('M45 167 L197 213 L355 135 M197 213 V18',stroke='#7b969e',stroke_width=2)
        def point(x,z):return (200+x*24+z*14,118+z*12-22*math.sin(x*.7)*math.cos(z*.6))
        for z in range(-4,5):d.parts.append('<polyline points="'+' '.join(f'{x:.1f},{y:.1f}' for x,y in [point(i,z) for i in range(-4,5)])+f'" fill="none" stroke="{a}" stroke-width="2"/>')
        for x in range(-4,5):d.parts.append('<polyline points="'+' '.join(f'{X:.1f},{y:.1f}' for X,y in [point(x,i) for i in range(-4,5)])+f'" fill="none" stroke="{b}" stroke-width="1"/>')
        d.text(315,206,'f(x, y)',16,b)
    else: raise ValueError(kind)


def make_svg(spec):
    id,title,caption,kind,v=spec
    seed=int(hashlib.sha256(id.encode()).hexdigest()[:8],16);rng=random.Random(seed)
    bg,a,b=PALETTES[seed%len(PALETTES)];d=Drawing(bg)
    d.rect(0,0,800,260,bg)
    # Architectural accents belong to the collection, not any game's UI.
    d.circle(716,28,160,a,opacity='.055');d.circle(784,241,134,b,opacity='.06')
    d.line(38,35,76,35,a,4);d.text(87,39,'ORIGINAL VECTOR CONCEPT',10,'#9ab0b9',letter_spacing='1.3')
    lines=title.split('|');fs=34 if max(map(len,lines))<15 else 27
    for i,line in enumerate(lines):d.text(38,103+i*44,line,fs,'#eff3e9',font_weight='bold',letter_spacing='-.6')
    # Wrap captions rather than shrinking them into illegibility.
    words=caption.split();lines2=['']
    for w in words:
        if len(lines2[-1])+len(w)>34:lines2.append(w)
        else:lines2[-1]+=(' ' if lines2[-1] else '')+w
    for i,line in enumerate(lines2):d.text(40,195+i*19,line,12,b,letter_spacing='.45')
    d.parts.append('<g transform="translate(383 18)">');scene(d,kind,v,a,b,rng);d.parts.append('</g>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="800" height="260" viewBox="0 0 800 260" role="img" aria-labelledby="title desc">\n'
            f'<title id="title">{html.escape(title.replace("|"," "))} — original concept illustration</title>\n'
            f'<desc id="desc">Hand-authored geometric illustration: {html.escape(caption)}. Not a gameplay screenshot; no game sprites, logos, or source images are used. Original artwork under the repository MIT license. See ARTWORK.md for inspection references.</desc>\n'
            +'\n'.join(d.parts)+'\n</svg>\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path,help='A new or empty output directory; existing files are refused.')
    parser.add_argument('--ids',nargs='+',help='Optional exact IDs, otherwise the full original-vector collection.')
    args=parser.parse_args();specs=[s for s in ART if not args.ids or s[0] in args.ids]
    if args.ids and set(args.ids)-{s[0] for s in specs}:parser.error('Unknown illustration ID')
    if len({s[0] for s in ART})!=len(ART):raise ValueError('Duplicate collection ID')
    targets=[args.output/(s[0]+'.svg') for s in specs]
    if any(p.exists() for p in targets):parser.error('Refusing to overwrite an existing SVG')
    args.output.mkdir(parents=True,exist_ok=True)
    for s,p in zip(specs,targets):p.write_text(make_svg(s),encoding='utf-8')
    print(f'Wrote {len(specs)} original SVG illustrations to {args.output}')

if __name__=='__main__': main()
