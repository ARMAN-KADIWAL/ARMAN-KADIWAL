#!/usr/bin/env python3
"""Render the profile's original, self-contained animated artwork.

Install Pillow, then run this script from any directory. No network calls,
API keys, user metrics, or third-party image services are used.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SCALE = 2
PAPER = "#f8f3e9"
INK = "#253b32"
MUTED = "#66796b"
TERRA = "#b66b49"
LINE = "#d9cdbb"
SAGE = "#e8edde"
WHITE = "#fffdf7"
FONT_DIR = Path(os.environ.get("PROFILE_FONT_DIR", "/usr/share/fonts/truetype/liberation"))


@lru_cache(maxsize=64)
def font(size: int, style: str = "sans") -> ImageFont.FreeTypeFont:
    names = {
        "sans": "LiberationSans-Regular.ttf",
        "bold": "LiberationSans-Bold.ttf",
        "mono": "LiberationMono-Regular.ttf",
        "serif": "LiberationSerif-Regular.ttf",
        "italic": "LiberationSerif-Italic.ttf",
    }
    path = FONT_DIR / names[style]
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}; install fonts-liberation or set PROFILE_FONT_DIR.")
    return ImageFont.truetype(str(path), size * SCALE)


def rgb(value: str) -> tuple[int, int, int]:
    return tuple(int(value[i : i + 2], 16) for i in (1, 3, 5))


def blend(a: str, b: str, fraction: float) -> tuple[int, int, int]:
    return tuple(round(x + (y - x) * fraction) for x, y in zip(rgb(a), rgb(b)))


class Canvas:
    def __init__(self, width: int, height: int, background: str = PAPER):
        self.image = Image.new("RGB", (width * SCALE, height * SCALE), background)
        self.d = ImageDraw.Draw(self.image)

    def box(self, xy, fill=None, outline=None, radius=0, width=1):
        coords = tuple(round(v * SCALE) for v in xy)
        self.d.rounded_rectangle(coords, radius=round(radius * SCALE), fill=fill,
                                 outline=outline, width=max(1, round(width * SCALE)))

    def line(self, points, color=LINE, width=1):
        self.d.line([(round(x * SCALE), round(y * SCALE)) for x, y in points],
                    fill=color, width=max(1, round(width * SCALE)), joint="curve")

    def circle(self, x, y, radius, fill=None, outline=None, width=1):
        self.d.ellipse(tuple(round(v * SCALE) for v in (x-radius, y-radius, x+radius, y+radius)),
                       fill=fill, outline=outline, width=max(1, round(width*SCALE)))

    def text(self, x, y, text, size=20, color=INK, style="sans", anchor="lt"):
        self.d.text((round(x * SCALE), round(y * SCALE)), text, font=font(size, style),
                    fill=color, anchor=anchor)

    def tracked(self, x, y, text, size=12, tracking=2, color=MUTED):
        f = font(size, "mono")
        for char in text:
            self.d.text((round(x * SCALE), round(y * SCALE)), char, font=f, fill=color, anchor="lt")
            x += self.d.textlength(char, font=f) / SCALE + tracking

    def finish(self):
        return self.image.resize((self.image.width // SCALE, self.image.height // SCALE), Image.Resampling.LANCZOS)


def paper_grid(c: Canvas, width, height):
    for y in range(20, height, 22):
        for x in range(20, width, 22):
            c.circle(x, y, 0.6, "#e8dfcf")


def kinetic_name(c: Canvas, text: str, x: float, y: float, size: int, phase: float, offset: int = 0):
    f = font(size, "serif")
    for index, char in enumerate(text):
        p = (phase - (index + offset) / 28) % 1
        wave = math.sin(p * math.tau)
        lift = 7 * max(0, wave) ** 4
        ink = blend(INK, TERRA, max(0, wave) ** 12 * 0.78)
        c.d.text((round(x * SCALE), round((y-lift) * SCALE)), char, font=f, fill=ink, anchor="lt")
        x += c.d.textlength(char, font=f) / SCALE
    return x


def hero(phase):
    c = Canvas(1280, 448)
    paper_grid(c, 1280, 448)
    c.box((16, 16, 1264, 432), outline=LINE, radius=12)
    c.tracked(59, 42, "THE WORKBENCH / CODE IN MOTION", size=12, tracking=2.2, color=TERRA)
    c.line([(59, 72), (1216, 72)])
    kinetic_name(c, "Arman", 58, 90, 120, phase)
    end = kinetic_name(c, "Kadiwal", 58, 208, 128, phase, offset=5)
    c.circle(end+17, 302, 6, TERRA)
    points = [(64 + i*5.4, 333+2.7*math.sin(i/19)+0.8*math.sin(i/4)) for i in range(107)]
    c.line(points, "#e8c5af", 2)
    progress = 0.32 + 0.68 * (1-math.cos(phase*math.tau))/2
    visible = points[:max(2, int(len(points)*progress))]
    c.line(visible, TERRA, 2.7)
    c.circle(*visible[-1], 3.5, INK)
    c.text(64, 359, "Python. Android. Systems.", 23, INK, "mono")
    c.text(64, 397, "Building useful things. Understanding how they work.", 16, MUTED)

    x = 834 + 3 * math.sin(phase*math.tau)
    y = 102 + 3 * math.cos(phase*math.tau)
    c.box((x+6, y+8, x+378, y+286), fill="#e4dccb", radius=12)
    c.box((x, y, x+372, y+278), fill=WHITE, outline="#bcc8b7", radius=12, width=1.3)
    c.circle(x+22, y+21, 3, TERRA)
    c.circle(x+35, y+21, 3, "#b9c5ac")
    c.circle(x+48, y+21, 3, "#d7cebd")
    c.tracked(x+75, y+17, "NOTES / ALWAYS OPEN", size=11, tracking=0.6)
    c.line([(x, y+43), (x+372, y+43)])
    c.line([(x+31, y+76), (x+31, y+205)], "#d7dfcf", 2)
    active = int(phase*3) % 3
    for index, (title, subtitle) in enumerate([
        ("Build the idea.", "start with something useful"),
        ("Test the edges.", "follow the unexpected result"),
        ("Make it better.", "keep the notes, try again"),
    ]):
        cy = y+78+index*64
        is_active = index == active
        c.circle(x+31, cy, 10, SAGE if is_active else WHITE, TERRA if is_active else "#9daf9c", 1.5)
        if index < active:
            c.line([(x+26,cy),(x+30,cy+4),(x+36,cy-5)], MUTED, 1.8)
        elif is_active:
            c.circle(x+31, cy, 3.5, TERRA)
        c.text(x+56, cy-9, title, 23, INK)
        c.text(x+56, cy+19, subtitle, 11, MUTED, "mono")
    c.line([(x+20,y+239),(x+351,y+239)])
    c.tracked(x+23,y+253,"CURIOSITY -> WORKING CODE",size=10,tracking=1)
    # Small orbiting mark: decorative, never a live-status indicator.
    angle = phase*math.tau
    c.line([(1240,40),(1240,58)], TERRA, 1.3)
    c.line([(1231,49),(1249,49)], TERRA, 1.3)
    c.circle(1240+12*math.cos(angle),49+12*math.sin(angle),2,INK)
    return c.finish()


def intro(phase):
    c = Canvas(1280, 88)
    c.box((1,1,1278,86), fill=PAPER, outline=LINE, radius=9)
    c.tracked(29,20,"A DEVELOPER'S NOTEBOOK",size=11,tracking=1.2,color=TERRA)
    c.text(29,43,"Small projects. Real lessons.",20,INK,"serif")
    c.line([(425,19),(425,69)])
    phrases = ["Build. Test. Learn. Repeat.", "Make it work. Understand why.", "Keep the curiosity. Improve the code."]
    cycle = phase*3
    index = int(cycle)%3
    local = cycle%1
    phrase = phrases[index]
    # The opening frame remains complete when GIF autoplay is disabled.
    if local < 0.54:
        count = len(phrase)
    elif local < 0.72:
        count = round(len(phrase)*(0.72-local)/0.18)
    else:
        phrase = phrases[(index+1)%3]
        count = round(len(phrase)*(local-0.72)/0.28)
    shown = phrase[:count]
    c.text(462,33,"> "+shown,25,INK,"mono")
    x = 462 + font(25,"mono").getlength("> "+shown)/SCALE
    c.box((x+5,31,x+7,58),fill=blend(TERRA,PAPER,0.35+0.3*math.sin(phase*math.tau*6)))
    return c.finish()


def hero_mobile(phase):
    c=Canvas(720,664)
    paper_grid(c,720,664)
    c.box((12,12,708,652),outline=LINE,radius=12)
    c.tracked(40,38,"THE WORKBENCH / CODE IN MOTION",12,tracking=1.3,color=TERRA)
    c.line([(40,69),(679,69)])
    kinetic_name(c,"Arman",38,104,132,phase)
    end=kinetic_name(c,"Kadiwal",38,244,144,phase,offset=5)
    c.circle(end+18,350,6,TERRA)
    points=[(43+i*6,391+2*math.sin(i/14)) for i in range(99)]
    c.line(points,"#e8c5af",2)
    count=max(2,int(len(points)*(0.32+0.68*(1-math.cos(phase*math.tau))/2)))
    c.line(points[:count],TERRA,2.7)
    c.circle(*points[count-1],3.5,INK)
    c.text(43,418,"Python. Android. Systems.",26,INK,"mono")
    c.text(43,459,"Building useful things. Understanding how they work.",18,MUTED)
    c.box((39,506,680,617),fill=WHITE,outline="#bcc8b7",radius=10)
    active=int(phase*3)%3
    xs=[69,278,489]
    c.line([(xs[0]+8,579),(xs[-1]+145,579)],LINE,1.4)
    for i,(x,title) in enumerate(zip(xs,["Build the idea.","Test the edges.","Make it better."])):
        c.text(x,532,title,21,INK)
        c.circle(x+8,579,5,TERRA if i==active else "#b8c5ac")
    c.circle(xs[0]+8+(xs[-1]+145-xs[0]-8)*phase,579,3,INK)
    return c.finish()


def intro_mobile(phase):
    c=Canvas(720,155)
    c.box((1,1,718,153),fill=PAPER,outline=LINE,radius=9)
    c.tracked(29,22,"A DEVELOPER'S NOTEBOOK",14,tracking=1.2,color=TERRA)
    c.text(29,49,"Small projects. Real lessons.",25,INK,"serif")
    c.line([(29,84),(689,84)])
    phrases=["Build. Test. Learn. Repeat.","Make it work. Understand why.","Keep the curiosity. Improve the code."]
    cycle=phase*3;index=int(cycle)%3;local=cycle%1
    phrase=phrases[index]
    if local<0.54:count=len(phrase)
    elif local<0.72:count=round(len(phrase)*(0.72-local)/0.18)
    else:
        phrase=phrases[(index+1)%3]
        count=round(len(phrase)*(local-0.72)/0.28)
    shown="> "+phrase[:count]
    c.text(29,107,shown,22,INK,"mono")
    x=29+font(22,"mono").getlength(shown)/SCALE
    c.box((x+5,105,x+7,132),fill=TERRA)
    return c.finish()


def icon(c, kind, x, y, phase):
    angle=phase*math.tau
    if kind=="recovery":
        positions=[(x+13,y+16),(x+51,y+16),(x+51,y+51),(x+13,y+51)]
        c.line(positions+[positions[0]],"#a7b99e",1.5)
        for px,py in positions:c.box((px-5,py-5,px+5,py+5),fill=WHITE,outline=INK,radius=2)
        stage=phase*4
        a=positions[int(stage)%4];b=positions[(int(stage)+1)%4];p=stage%1
        c.circle(a[0]+(b[0]-a[0])*p,a[1]+(b[1]-a[1])*p,3.5,TERRA)
    elif kind=="backup":
        c.box((x+14,y+15,x+51,y+50),fill=WHITE,outline=INK,radius=6,width=1.5)
        c.d.ellipse(tuple(round(v*SCALE) for v in (x+14,y+9,x+51,y+26)),fill=SAGE,outline=INK,width=2)
        c.line([(x+14,y+35),(x+51,y+35)],"#9daf9c",1)
        c.circle(x+33+29*math.cos(angle),y+33+29*math.sin(angle),3.5,TERRA)
    elif kind=="python":
        c.text(x+10,y+10,">_",23,INK,"mono")
        for i,w in enumerate((32,24,37)):
            c.line([(x+12,y+41+i*7),(x+12+w,y+41+i*7)],"#91a589",2)
        c.circle(x+12+37*phase,y+55,2.5,TERRA)
    elif kind=="android":
        c.box((x+19,y+5,x+48,y+60),fill=WHITE,outline=INK,radius=6,width=1.7)
        c.line([(x+28,y+11),(x+39,y+11)],MUTED,1.3)
        c.circle(x+33,y+53,1.6,MUTED)
        slide=8*math.sin(angle)
        c.box((x+25,y+22+slide,x+42,y+35+slide),fill="#c5d4bb",radius=3)
        c.line([(x+28,y+28+slide),(x+32,y+32+slide),(x+38,y+24+slide)],INK,1.3)


def project(kind, number, label, title, phase):
    c = Canvas(600,132)
    c.box((1,1,598,130),fill=PAPER,outline=LINE,radius=9)
    c.box((17,25,99,107),fill=SAGE,radius=10)
    icon(c,kind,25,33,phase)
    c.tracked(119,30,f"{number} / {label}",11,tracking=1.15,color=TERRA)
    c.text(117,58,title,34,INK,"serif")
    c.line([(119,108),(573,108)],LINE,1)
    dot=119+(573-119)*((1-math.cos(phase*math.tau))/2)
    c.circle(dot,108,2.8,TERRA)
    return c.finish()


def toolkit(phase):
    c=Canvas(1280,205)
    c.box((1,1,1278,203),fill=PAPER,outline=LINE,radius=10)
    c.tracked(28,23,"TOOLS I REACH FOR",12,tracking=1.6,color=TERRA)
    c.text(1252,23,"LEARN BY USING",12,MUTED,"mono",anchor="rt")
    tools=[("Py","Python"),("Kt","Kotlin"),("~","Linux"),("$_","Bash"),("[]","Docker"),("db","SQLite"),("+","Git"),("->","GitHub Actions")]
    for i,(symbol,title) in enumerate(tools):
        x=26+(i%4)*310;y=61+(i//4)*65
        local=(phase*8-i)%8
        strength=max(0,1-abs(local-0.5)*2) if local<1 else 0
        c.box((x,y,x+297,y+53),fill=blend(WHITE,SAGE,strength),outline=blend(LINE,TERRA,strength),radius=6,width=1.1)
        c.text(x+16,y+16,symbol,18,TERRA,"mono")
        c.text(x+65,y+17,title,19,INK,"bold")
        if strength>0:
            c.line([(x+65,y+42),(x+65+195*strength,y+42)],TERRA,1.6)
    return c.finish()


def toolkit_mobile(phase):
    c=Canvas(720,379)
    c.box((1,1,718,377),fill=PAPER,outline=LINE,radius=10)
    c.tracked(28,23,"TOOLS I REACH FOR",14,tracking=1.6,color=TERRA)
    tools=[("Py","Python"),("Kt","Kotlin"),("~","Linux"),("$_","Bash"),("[]","Docker"),("db","SQLite"),("+","Git"),("->","GitHub Actions")]
    for i,(symbol,title) in enumerate(tools):
        x=26+(i%2)*340;y=64+(i//2)*74
        local=(phase*8-i)%8
        strength=max(0,1-abs(local-0.5)*2) if local<1 else 0
        c.box((x,y,x+328,y+61),fill=blend(WHITE,SAGE,strength),outline=blend(LINE,TERRA,strength),radius=6,width=1.2)
        c.text(x+16,y+20,symbol,22,TERRA,"mono")
        c.text(x+65,y+21,title,23,INK,"bold")
        if strength>0:c.line([(x+65,y+49),(x+65+230*strength,y+49)],TERRA,1.7)
    return c.finish()


def method(phase):
    c=Canvas(1280,119)
    c.box((1,1,1278,117),fill=PAPER,outline=LINE,radius=10)
    c.tracked(29,20,"ONE HABIT",10,tracking=1.7,color=TERRA)
    c.text(29,43,"Keep iterating.",26,INK,"serif")
    c.line([(252,22),(252,95)])
    labels=["BUILD","TEST","LEARN","REPEAT"]
    xs=[310,552,793,1034]
    c.line([(xs[0],88),(xs[-1]+175,88)],LINE,1.4)
    for i,(label,x) in enumerate(zip(labels,xs)):
        active=int(phase*4)%4==i
        c.text(x,27,f"0{i+1}",11,TERRA if active else MUTED,"mono")
        c.text(x,48,label,23,INK,"bold")
        c.circle(x,88,4.5,TERRA if active else "#b8c5ac")
    travel=xs[0]+(xs[-1]+175-xs[0])*phase
    c.circle(travel,88,3.5,INK)
    return c.finish()


def method_mobile(phase):
    c=Canvas(720,188)
    c.box((1,1,718,186),fill=PAPER,outline=LINE,radius=10)
    c.tracked(29,22,"ONE HABIT",12,tracking=1.7,color=TERRA)
    c.text(690,21,"Keep iterating.",26,INK,"serif",anchor="rt")
    c.line([(29,61),(690,61)])
    xs=[39,217,395,573]
    c.line([(xs[0],153),(xs[-1]+104,153)],LINE,1.4)
    for i,(label,x) in enumerate(zip(["BUILD","TEST","LEARN","REPEAT"],xs)):
        active=int(phase*4)%4==i
        c.text(x,83,f"0{i+1}",13,TERRA if active else MUTED,"mono")
        c.text(x,109,label,25,INK,"bold")
        c.circle(x,153,4.5,TERRA if active else "#b8c5ac")
    c.circle(xs[0]+(xs[-1]+104-xs[0])*phase,153,3.5,INK)
    return c.finish()


def write_animation(name, renderer, frames, duration, target):
    rendered=[renderer(i/frames) for i in range(frames)]
    # One shared palette prevents per-frame color shimmer and keeps deltas small.
    sample=Image.new("RGB",(rendered[0].width,rendered[0].height*4))
    for i,index in enumerate((0,frames//4,frames//2,3*frames//4)):
        sample.paste(rendered[index],(0,i*rendered[0].height))
    palette=sample.quantize(colors=128,method=Image.Quantize.MEDIANCUT)
    converted=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in rendered]
    static=target/f"{name}-still.png"
    rendered[0].save(static,optimize=True)
    path=target/f"{name}.gif"
    converted[0].save(path,save_all=True,append_images=converted[1:],duration=duration,
                      loop=0,optimize=True,disposal=1)
    with Image.open(path) as image:
        record={"file":path.relative_to(ROOT).as_posix(),"width":image.width,"height":image.height,
                "frames":image.n_frames,"duration_ms":sum(frame.info.get("duration",0) for frame in _iter_frames(image)),
                "bytes":path.stat().st_size,"still":static.relative_to(ROOT).as_posix()}
    print(json.dumps(record),flush=True)
    return record


def _iter_frames(image):
    for index in range(image.n_frames):
        image.seek(index)
        yield image


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only",choices=["hero","hero-mobile","intro","intro-mobile","ghostdock","backup","python","android","toolkit","toolkit-mobile","method","method-mobile"])
    args=parser.parse_args()
    target=ROOT/"assets"/"motion"
    target.mkdir(parents=True,exist_ok=True)
    animations={
        "hero":(hero,96,80),
        "hero-mobile":(hero_mobile,96,80),
        "intro":(intro,150,80),
        "intro-mobile":(intro_mobile,150,80),
        "ghostdock":(lambda p:project("recovery","01","RELIABILITY","GhostDock",p),64,80),
        "backup":(lambda p:project("backup","02","BACKUP & RESTORE","Backup Recovery Tester",p),64,80),
        "python":(lambda p:project("python","03","PYTHON / LABS","Python Deep Dive",p),64,80),
        "android":(lambda p:project("android","04","KOTLIN / ANDROID","Android Experiments",p),64,80),
        "toolkit":(toolkit,96,80),
        "toolkit-mobile":(toolkit_mobile,96,80),
        "method":(method,80,80),
        "method-mobile":(method_mobile,80,80),
    }
    records=[]
    for name,(renderer,frames,duration) in animations.items():
        if not args.only or name==args.only:
            records.append(write_animation(name,renderer,frames,duration,target))
    if not args.only:
        (target/"manifest.json").write_text(json.dumps({"animations":records},indent=2)+"\n")


if __name__=="__main__":
    main()
