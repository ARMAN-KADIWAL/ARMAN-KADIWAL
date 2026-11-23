"""Render the pen plotter cover and GhostDock replay for the profile README."""

import argparse
import json
import math
from dataclasses import dataclass
from functools import lru_cache
from itertools import pairwise

from PIL import Image, ImageChops, ImageDraw
from render_profile_motion import ROOT, SCALE, Canvas, font, icon, write_animation

ASSETS = ROOT / "assets" / "workbench"


@dataclass(frozen=True)
class Paper:
    bg: str
    ink: str
    soft: str
    line: str
    grid: str
    copper: str
    shadow: str
    rim: str


DAY = Paper(
    "#f5f0e5",
    "#173931",
    "#46645a",
    "#c5c8b7",
    "#e3e1d1",
    "#ac542d",
    "#d9d8c6",
    "#587a70",
)
NIGHT = Paper(
    "#102622",
    "#f5eddb",
    "#b2c9bb",
    "#42665b",
    "#203c35",
    "#f0ac75",
    "#0d1e1c",
    "#7fa69a",
)


def polygon(canvas, points, fill):
    canvas.d.polygon(
        [(round(x * SCALE), round(y * SCALE)) for x, y in points], fill=fill
    )


class Plotter:
    """Project the moving gantry and the nib from the same bed coordinates."""

    def __init__(self, canvas, origin, zoom):
        self.canvas = canvas
        self.center_x, self.center_y = origin
        self.zoom = zoom

    def point(self, x, y, z=0):
        x -= 124
        y -= 76
        return (
            self.center_x + self.zoom * (x * 1.09 - y * 0.63),
            self.center_y + self.zoom * (x * 0.20 + y * 0.65 - z),
        )

    def line(self, world_points, color, width=1):
        self.canvas.line(
            [self.point(*p) for p in world_points], color, width * self.zoom
        )

    def slab(self, x, y, width, depth, top, height, colors, bevel=2):
        surface, front, edge = colors
        corners = [
            (x + bevel, y),
            (x + width - bevel, y),
            (x + width, y + bevel),
            (x + width, y + depth - bevel),
            (x + width - bevel, y + depth),
            (x + bevel, y + depth),
            (x, y + depth - bevel),
            (x, y + bevel),
        ]
        roof = [self.point(px, py, top) for px, py in corners]
        base = [self.point(px, py, top - height) for px, py in corners]
        for i, j in ((1, 2), (2, 3), (3, 4), (4, 5), (5, 6)):
            polygon(
                self.canvas,
                [roof[i], roof[j], base[j], base[i]],
                front if i >= 4 else edge,
            )
        polygon(self.canvas, roof, surface)
        self.canvas.line(roof + [roof[0]], edge, self.zoom * 0.65)

    def screw(self, x, y, z):
        center_x, center_y = self.point(x, y, z)
        self.canvas.circle(
            center_x, center_y, self.zoom * 2.5, "#b4c3ad", "#263c36", 0.6
        )
        self.line([(x - 1.3, y, z + 0.1), (x + 1.3, y, z + 0.1)], "#394f46", 0.55)


def draw_bed(plotter, palette):
    for mark in range(-15, 270, 22):
        plotter.line([(mark, -13, -20), (mark, 171, -20)], palette.grid, 0.6)
    for mark in range(-12, 177, 20):
        plotter.line([(-15, mark, -20), (264, mark, -20)], palette.grid, 0.6)
    polygon(
        plotter.canvas,
        [
            plotter.point(x + 4, y + 4, -18)
            for x, y in [(-4, -4), (252, -4), (252, 155), (-4, 155)]
        ],
        palette.shadow,
    )
    plotter.slab(-3, -4, 254, 161, -2, 13, ("#3e5e52", "#27473e", "#1b332d"), 8)
    plotter.slab(-2, -3, 252, 158, 1, 2.6, ("#96ada0", "#5c7669", "#506b5f"), 7)
    plotter.slab(0, 0, 248, 152, 4, 3, ("#345d50", "#294c41", palette.rim), 7)
    plotter.slab(23, 16, 202, 120, 5, 1, ("#23473e", "#193931", "#55796b"), 3)
    for x in range(31, 223, 12):
        plotter.line([(x, 19, 5.1), (x, 133, 5.1)], "#32574c", 0.48)
    for y in range(24, 136, 12):
        plotter.line([(26, y, 5.1), (222, y, 5.1)], "#32574c", 0.48)
    for x in range(28, 223, 5):
        depth = 4.6 if (x - 28) % 20 == 0 else 2.2
        plotter.line([(x, 142, 4.1), (x, 142 + depth, 4.1)], "#b0c2ae", 0.54)
    for x in range(46, 107, 4):
        plotter.line([(x, 157, -10), (x + 1.5, 157, -5)], "#446358", 0.8)
    for x in (11, 237):
        for y in (9, 143):
            plotter.slab(
                x - 5, y - 4, 10, 8, 11, 7, ("#889b8b", "#405b4d", "#455f55"), 1
            )
        plotter.line([(x, 9, 10), (x, 143, 10)], "#192e29", 3.6)
        plotter.line([(x, 9, 10.8), (x, 143, 10.8)], "#cdd3b9", 1.2)
    for x, y in ((6, 5), (241, 5), (6, 147), (242, 147)):
        plotter.screw(x, y, 4.2)


# Pen-up travel between strokes is part of the path, including the return home.
STROKES = [
    [(43, 115), (71, 40), (101, 115)],
    [(54, 87), (90, 87)],
    [(132, 115), (132, 40)],
    [(187, 40), (134, 82), (190, 115)],
]


def pen_route():
    moves = []
    for index, stroke in enumerate(STROKES):
        for start, end in pairwise(stroke):
            moves.append((start, end, True, math.dist(start, end)))
        home = STROKES[(index + 1) % len(STROKES)][0]
        moves.append((stroke[-1], home, False, math.dist(stroke[-1], home) * 0.56))
    return moves


MOVES = pen_route()
ROUTE_LENGTH = sum(move[3] for move in MOVES)


def draw_plotter_frame(plotter, phase):
    # The poster opens near the completed monogram, with both initials visible.
    offset = ((phase + 0.865) % 1) * ROUTE_LENGTH
    x, y = STROKES[0][0]
    lift = 0
    for stroke in STROKES:
        plotter.line([(px, py, 5.3) for px, py in stroke], "#809b84", 1.35)
    for start, end, writing, length in MOVES:
        fraction = min(1, offset / length)
        x = start[0] + (end[0] - start[0]) * fraction
        y = start[1] + (end[1] - start[1]) * fraction
        if writing:
            plotter.line([(*start, 5.7), (x, y, 5.7)], "#ffbe82", 2.15)
        lift = 0 if writing else 5 * math.sin(math.pi * fraction)
        if offset <= length:
            break
        offset -= length
    gantry_y = y - 11
    for rail_x in (11, 237):
        plotter.slab(
            rail_x - 6, gantry_y - 4, 12, 19, 22, 12, ("#59766a", "#25473d", "#324f44")
        )
        plotter.slab(
            rail_x - 4, gantry_y + 1, 8, 8, 39, 17, ("#648275", "#335b4d", "#426655")
        )
    plotter.slab(6, gantry_y, 239, 7, 40, 5, ("#c6cdb8", "#789082", "#6b8176"), 1)
    plotter.line([(12, gantry_y + 8, 34), (239, gantry_y + 8, 34)], "#d8d9be", 1.3)
    for tooth in range(21, 231, 7):
        plotter.line(
            [(tooth, gantry_y + 6.9, 36), (tooth + 2.8, gantry_y + 6.9, 36)],
            "#405e52",
            0.75,
        )
    plotter.slab(
        x - 10, gantry_y - 3, 21, 14, 47, 12, ("#355c4d", "#24463c", "#668c79")
    )
    plotter.screw(x - 4, gantry_y + 2, 47)
    plotter.line([(x, y, 7 + lift), (x, y, 43 + lift)], "#192e28", 4.8)
    plotter.line([(x, y, 12 + lift), (x, y, 44 + lift)], "#dda16a", 4)
    plotter.line([(x - 0.7, y, 16 + lift), (x - 0.7, y, 43 + lift)], "#ffe1a5", 1.3)
    plotter.line([(x, y, 6 + lift), (x, y, 14 + lift)], "#ecc792", 1.65)
    plotter.line([(x, y, 39 + lift), (x, y, 42 + lift)], "#724e39", 4.2)


def cover_layout(mobile):
    if mobile:
        return (
            (640, 588),
            (320, 346),
            1.25,
            [(35, 154, "Arman", 89, "serif"), (303, 154, "Kadiwal", 90, "italic")],
        )
    return (
        (1200, 430),
        (885, 226),
        1.41,
        [(52, 208, "Arman", 147, "serif"), (50, 339, "Kadiwal", 156, "italic")],
    )


@lru_cache(maxsize=4)
def cover_plate(palette, mobile):
    (width, height), origin, zoom, letters = cover_layout(mobile)
    canvas = Canvas(width, height, palette.bg)
    margin = 33 if mobile else 51
    head_y = 31 if mobile else 33
    canvas.line([(margin, head_y + 8), (margin + 24, head_y + 8)], palette.copper, 2.7)
    canvas.tracked(margin + 36, head_y, "ENGINEERING NOTEBOOK", 14, 1.8, palette.soft)
    if not mobile:
        canvas.line(
            [(margin + 292, head_y + 8), (1146, head_y + 8)], palette.line, 0.95
        )
    for x, baseline, label, size, face in letters:
        canvas.text(x, baseline, label, size, palette.ink, face, anchor="ls")
    for x, y in ((width - 23, 21), (22, height - 21)):
        canvas.line([(x - 4, y), (x + 4, y)], palette.line, 0.8)
        canvas.line([(x, y - 4), (x, y + 4)], palette.line, 0.8)
    draw_bed(Plotter(canvas, origin, zoom), palette)
    line_y = height - (82 if mobile else 57)
    canvas.line([(margin, line_y), (width - margin, line_y)], palette.line, 1)
    canvas.text(
        margin,
        line_y + 17,
        "Python  /  Systems  /  Android",
        22 if mobile else 21,
        palette.ink,
        "mono",
    )
    return canvas.image


@lru_cache(maxsize=2)
def name_mask(mobile):
    (width, height), _, _, letters = cover_layout(mobile)
    full = Image.new("L", (width * SCALE, height * SCALE))
    draw = ImageDraw.Draw(full)
    for x, baseline, label, size, face in letters:
        draw.text(
            (x * SCALE, baseline * SCALE),
            label,
            font=font(size, face),
            anchor="ls",
            fill=255,
        )
    bounds = full.getbbox()
    return full.crop(bounds), bounds[:2]


def cover_frame(phase, palette, mobile):
    size, origin, zoom, _ = cover_layout(mobile)
    canvas = Canvas(*size, palette.bg)
    canvas.image.paste(cover_plate(palette, mobile))
    mask, position = name_mask(mobile)
    band = Image.new("L", (mask.width, 1))
    center = (phase * 1.38 - 0.20) * mask.width
    spread = mask.width * 0.115
    band.putdata(
        [
            round(185 * max(0, 1 - abs(x - center) / spread) ** 2)
            for x in range(mask.width)
        ]
    )
    light = ImageChops.multiply(mask, band.resize(mask.size, Image.Resampling.NEAREST))
    x, y = position
    canvas.image.paste(palette.copper, (x, y, x + mask.width, y + mask.height), light)
    draw_plotter_frame(Plotter(canvas, origin, zoom), phase)
    command = "python3 -m ghostdock demo"
    # Hold at both ends, erasing and retyping once per plotter pass.
    if 0.30 < phase < 0.48:
        command = command[: round(len(command) * (0.48 - phase) / 0.18)]
    elif 0.48 <= phase < 0.80:
        command = command[: round(len(command) * (phase - 0.48) / 0.32)]
    left, top = (33, 554) if mobile else (815, 391)
    size = 18 if mobile else 19
    canvas.text(left, top, ">", size, palette.copper, "mono")
    text_x = left + 21
    canvas.text(text_x, top, command, size, palette.soft, "mono")
    caret = text_x + font(size, "mono").getlength(command) / SCALE + 3
    canvas.line([(caret, top), (caret, top + size)], palette.copper, 1.5)
    return canvas.finish()


EVENT_LABELS = {
    "CREATED": "Journal opened",
    "WATCHING": "Monitoring the app",
    "SUSPECT": "Health probe failed",
    "REPAIRING_LOCAL": "One local restart",
    "CLOUD_PREFLIGHT": "Checking prerequisites",
    "PROVISIONING": "Simulating an EC2 request",
    "VERIFYING_CLOUD": "Checking the replacement",
    "RECOVERED_CLOUD": "App identity verified",
}


def replay_frame(events, phase, mobile):
    # Equal time per entry keeps same-timestamp transitions visible.
    index = min(len(events) - 1, int(phase * len(events)))
    event = events[index]
    width, height = (640, 243) if mobile else (1120, 174)
    c = Canvas(width, height, "#142d29")
    pad = 27 if mobile else 36
    c.line([(pad, 27), (pad + 18, 27)], "#f0ab73", 2.5)
    c.tracked(pad + 29, 21, "SIMULATED INCIDENT", 13, 1.15, "#eac496")
    clock = f"t + {event['elapsed_seconds']:02d} s"
    c.text(width - pad, 20, clock, 19, "#c5daca", "mono", anchor="rt")
    c.text(
        pad, 63, EVENT_LABELS[event["status"]], 38 if mobile else 43, "#f6efdc", "serif"
    )
    if mobile:
        c.text(pad, 124, event["status"], 19, "#a9c4b3", "mono")
    else:
        c.text(width - pad, 81, event["status"], 18, "#a9c4b3", "mono", anchor="rt")
    track_y = height - 42
    step = (width - 2 * pad) / (len(events) - 1)
    c.line([(pad, track_y), (width - pad, track_y)], "#4c6b5c", 1.2)
    if index:
        c.line([(pad, track_y), (pad + index * step, track_y)], "#e1a46e", 2)
    for i in range(len(events)):
        x = pad + i * step
        c.circle(
            x,
            track_y,
            5.4 if i == index else 3.5,
            "#ffbd80" if i <= index else "#719483",
        )
        if i == index:
            c.circle(x, track_y, 9.3, outline="#d0a77c", width=1)
    c.text(pad, track_y + 15, "Journal order", 12, "#a9c4b3", "mono")
    c.text(
        width - pad,
        track_y + 15,
        f"Event {index + 1} of {len(events)}",
        12,
        "#a9c4b3",
        "mono",
        anchor="rt",
    )
    return c.finish()


def glyph_frame(phase, kind):
    c = Canvas(80, 80, "#e8edde")
    icon(c, kind, 7, 7, phase)
    return c.finish()


def calendar_link():
    c = Canvas(720, 76, "#e8edde")
    c.text(29, 25, "Open my GitHub contribution calendar", 23, "#253b32", "sans")
    c.line([(657, 39), (689, 39), (677, 29)], "#537365", 2)
    c.line([(689, 39), (677, 49)], "#537365", 2)
    return c.finish()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--only", help="Render one asset, e.g. cover-night or replay-mobile"
    )
    parser.add_argument(
        "--poster", action="store_true", help="Only render the static preview"
    )
    options = parser.parse_args()
    events = json.loads((ASSETS / "ghostdock-trace.json").read_text())["events"]
    assets = {}
    for theme, palette in (("day", DAY), ("night", NIGHT)):
        for mobile in (False, True):
            name = f"cover-{theme}" + ("-mobile" if mobile else "")
            assets[name] = (
                lambda phase, p=palette, m=mobile: cover_frame(phase, p, m),
                80,
                90,
            )
    for mobile in (False, True):
        name = "replay-mobile" if mobile else "replay"
        assets[name] = (
            lambda phase, m=mobile: replay_frame(events, phase, m),
            len(events),
            1050,
        )
    for kind in ("backup", "python", "android"):
        assets[f"glyph-{kind}"] = (lambda phase, k=kind: glyph_frame(phase, k), 40, 100)
    if options.only and options.only not in assets:
        parser.error(f"Unknown asset. Choose one of {', '.join(assets)}")
    for name, (render, frames, duration) in assets.items():
        if options.only and options.only != name:
            continue
        if options.poster:
            render(0).save(ASSETS / f"{name}-still.png", optimize=True)
        else:
            write_animation(name, render, frames, duration, ASSETS)
        if name in ("replay", "replay-mobile"):
            render((len(events) - 1) / len(events)).save(
                ASSETS / f"{name}-still.png", optimize=True
            )
    if not options.only:
        calendar_link().save(ASSETS / "calendar-link.png", optimize=True)


if __name__ == "__main__":
    main()
