"""Small illustrated loops for three projects in the profile's engineering notebook."""

from dataclasses import dataclass
from functools import lru_cache

from render_profile_motion import SCALE, Canvas, blend, font


@dataclass(frozen=True)
class Study:
    label: str
    first_line: str
    second_line: str
    detail: str
    paper: str
    ink: str
    muted: str
    rule: str
    accent: str


STUDIES = {
    "backup": Study(
        "SQLITE / RESTORE TEST",
        "Forty rows.",
        "One edit.",
        "order_id = 1   /   amount +0.50",
        "#e4ecdd",
        "#203e32",
        "#48614e",
        "#b4c4ac",
        "#96522f",
    ),
    "python": Study(
        "PYTHON / LAB 82",
        "Two clients.",
        "One listener.",
        "Threaded TCP   /   request and reply",
        "#f1eadc",
        "#3e342c",
        "#6a5948",
        "#d0c0a8",
        "#9c502c",
    ),
    "android": Study(
        "ANDROID / BOUNCE LAB",
        "From a tap",
        "to a rebound.",
        "Touch input   /   Kotlin Canvas",
        "#172435",
        "#fbf1de",
        "#b3c6ce",
        "#3e5264",
        "#85e3d2",
    ),
}


def ellipse(c, x, y, rx, ry, fill=None, outline=None, width=1):
    points = (x - rx, y - ry, x + rx, y + ry)
    c.d.ellipse(
        tuple(round(v * SCALE) for v in points),
        fill=fill,
        outline=outline,
        width=max(1, round(width * SCALE)),
    )


def smooth(value):
    t = min(1, max(0, value))
    return t * t * (3 - 2 * t)


@lru_cache(maxsize=6)
def study_paper(kind, mobile):
    style = STUDIES[kind]
    w, h = (496, 292) if mobile else (960, 218)
    c = Canvas(w, h, style.paper)
    x, y = (22, 17) if mobile else (36, 30)
    c.line([(x, y + 6), (x + 15, y + 6)], style.accent, 2.4)
    c.tracked(x + 25, y, style.label, 12 if mobile else 14, 1.4, style.muted)
    if mobile:
        size, baseline = 35, 70
        c.text(x, baseline, style.first_line, size, style.ink, "serif", "ls")
        offset = font(size, "serif").getlength(style.first_line + " ") / SCALE
        c.text(x + offset, baseline, style.second_line, size, style.ink, "italic", "ls")
        c.line([(22, 253), (474, 253)], style.rule)
        c.text(22, 266, style.detail, 15, style.muted, "mono")
    else:
        c.text(x - 1, 98, style.first_line, 47, style.ink, "serif", "ls")
        c.text(x - 2, 148, style.second_line, 51, style.ink, "italic", "ls")
        c.line([(x, 168), (406, 168)], style.rule)
        c.text(x, 182, style.detail, 15, style.muted, "mono")
        c.line([(438, 25), (438, 193)], style.rule)
    return c.image


# These stylized bar patterns illustrate the table content hashes.
FINGERPRINTS = (
    (2, 1, 3, 1, 2, 4, 1, 2, 1, 3, 2, 1, 4, 1, 2, 1, 3, 2, 4, 1),
    (1, 3, 1, 2, 4, 1, 2, 3, 1, 1, 4, 2, 1, 3, 1, 4, 2, 1, 3, 2),
)


def ledger_ticket(c, x, title, bars, sweep, restored):
    c.box((x + 4, 22, x + 199, 153), "#c4d0bb", radius=6)
    c.box((x + 2, 17, x + 197, 149), "#e7e7d5", "#b6c2a9", 6)
    c.box((x, 12, x + 195, 145), "#fff9e8", "#869881", 6, 1.2)
    c.tracked(x + 13, 25, title, 13, 1.2, "#42624e")
    c.line([(x + 13, 48), (x + 181, 48)], "#c2c8b2")
    c.text(x + 13, 58, "40 rows", 25, "#274738", "bold")
    c.text(x + 181, 67, "orders", 12, "#546854", "mono", "rt")
    c.line([(x + 13, 93), (x + 181, 93)], "#d1d4bd")
    c.text(x + 13, 112, "hash", 13, "#5c705a", "mono")
    start = x + 59
    position = start
    for width in bars:
        c.box(
            (position, 104, position + width * 1.65, 131),
            "#914d30" if restored else "#375744",
        )
        position += width * 1.65 + 2.0
    if 0 < sweep < 1:
        scan = start + sweep * (position - start)
        c.box((scan - 2, 100, scan + 2, 135), "#efa466", radius=1)
        c.line([(scan, 100), (scan, 135)], "#743e27", 0.9)


def backup_scene(c, phase):
    cycle = (phase + 0.66) % 1
    scan = smooth((cycle - 0.07) / 0.48)
    ledger_ticket(c, 8, "MANIFEST", FINGERPRINTS[0], scan, False)
    ledger_ticket(c, 264, "RESTORE", FINGERPRINTS[1], scan, True)
    cy, cx = 84, 235
    c.line([(204, cy), (263, cy)], "#869981", 1.4)
    reveal = smooth((cycle - 0.49) / 0.12) * (1 - smooth((cycle - 0.88) / 0.12))
    stamp = blend("#506c54", "#964a2c", reveal)
    c.circle(cx, cy, 16, stamp, "#f9f1d9", 1.4)
    if reveal < 0.5:
        c.circle(cx - 1.5, cy - 1.5, 5, outline="#fff2d8", width=1.7)
        c.line([(cx + 2, cy + 2), (cx + 7, cy + 7)], "#fff2d8", 1.8)
    else:
        for offset in (-2.8, 2.8):
            c.line([(cx - 7, cy + offset), (cx + 7, cy + offset)], "#fff2d8", 1.9)
        c.line(
            [(cx - 5, cy + 9), (cx - 5 + 10 * reveal, cy + 9 - 18 * reveal)],
            "#fff2d8",
            2.1,
        )


def terminal(c, y, label, command):
    c.box((11, y + 3, 152, y + 62), "#d0c3ab", radius=7)
    c.box((8, y, 149, y + 59), "#fff7e7", "#a18b70", 7, 1.1)
    c.tracked(20, y + 10, label, 12, 1, "#71604d")
    c.text(20, y + 30, "> " + command, 19, "#38332c", "mono")
    c.circle(148, y + 34, 3.4, "#695848")


def wire_point(t, start_y, end_y):
    return 149 + 162 * t, start_y + (end_y - start_y) * smooth(t)


def python_scene(c, phase):
    for index, (start_y, end_y) in enumerate(((44, 64), (129, 104))):
        path = [wire_point(i / 40, start_y, end_y) for i in range(41)]
        c.line(path, "#9d8c73", 2)
        tick = (phase + (0.19 if index == 0 else 0.49)) % 1
        returning = tick > 0.53
        outgoing = smooth(tick / 0.39)
        t = 1 - smooth((tick - 0.53) / 0.38) if returning else outgoing
        stroke = "#396353" if returning else "#a75932"
        x, y = wire_point(t, start_y, end_y)
        c.box((x - 9, y - 5, x + 9, y + 5), stroke, radius=4)
        direction = -1 if returning else 1
        c.line(
            [
                (x - 2 * direction, y - 2.5),
                (x + 1.5 * direction, y),
                (x - 2 * direction, y + 2.5),
            ],
            "#fff7da",
            1.3,
        )
    terminal(c, 10, "CLIENT A", "time")
    terminal(c, 95, "CLIENT B", "stats")
    c.box((315, 32, 463, 141), "#cabda5", radius=8)
    c.box((311, 26, 459, 136), "#355647", "#233f35", 8, 1.3)
    c.line([(323, 29), (448, 29)], "#75917c", 1)
    c.line([(321, 108), (449, 108)], "#52715d")
    c.tracked(331, 43, "TCP SERVER", 13, 1.0, "#e5ead2")
    c.text(330, 68, ":8888", 25, "#ffe8bd", "mono")
    for y, shift in ((64, 0.19), (104, 0.49)):
        pulse = max(0, 1 - abs((phase + shift) % 1 - 0.45) / 0.20)
        c.circle(311, y, 4.7, "#2c4235", "#d6c7a3", 1)
        c.circle(311, y, 2.2, blend("#8a9d80", "#ffc78a", pulse))
    for x in range(330, 405, 7):
        c.line([(x, 121), (x + 2, 116)], "#95a58b", 1.2)


FLOOR = 135


def height_above_floor(s):
    if s < 0.33:
        return 75 * (1 - (s / 0.33) ** 2)
    for start, end, peak in ((0.33, 0.66, 49), (0.66, 0.88, 22), (0.88, 1, 7)):
        if s <= end:
            u = (s - start) / (end - start)
            return 4 * peak * u * (1 - u)
    return 0


def bounce_point(s):
    return 47 + 375 * s, FLOOR - 12 - height_above_floor(s)


def android_scene(c, phase):
    c.box((5, 6, 466, 161), "#101c30", "#42586a", 11, 1.2)
    for y in (40, 70, 100):
        for x in range(22, 456, 16):
            c.circle(x, y, 0.7, "#37495e")
    c.line([(22, FLOOR), (449, FLOOR)], "#68818c", 1.3)
    for impact in (0.33, 0.66, 0.88):
        x, _ = bounce_point(impact)
        c.line([(x - 6, FLOOR + 4), (x + 6, FLOOR + 4)], "#f0bd88", 1.7)
    for step in range(69):
        c.circle(*bounce_point(step / 68), 1.15, "#698791")
    start_x, start_y = bounce_point(0)
    c.circle(start_x, start_y, 7, outline="#86c6bd")
    t = (phase + 0.50) % 1
    if t < 0.22:
        ripple = t / 0.22
        c.circle(
            start_x,
            start_y,
            9 + 16 * ripple,
            outline=blend("#94dfcd", "#101c30", ripple),
            width=1.5,
        )
    s = min(1, max(0, (t - 0.06) / 0.86))
    x, _ = bounce_point(s)
    height = height_above_floor(s)
    visibility = smooth(t / 0.06) * (1 - smooth((t - 0.93) / 0.07))
    for delay, color in ((0.068, "#38515e"), (0.035, "#557d83")):
        if delay < s < 0.98:
            c.circle(*bounce_point(s - delay), 8.4, outline=color, width=1.1)
    if visibility <= 0:
        return
    squeeze = max(
        max(0, 1 - abs(s - hit) / 0.026) * strength
        for hit, strength in ((0.33, 1), (0.66, 0.78), (0.88, 0.48))
    )
    rx, ry = (13 + 5.4 * squeeze) * visibility, (13 - 5.2 * squeeze) * visibility
    cy = FLOOR - ry - height
    contact = max(0, 1 - height / 75)
    ellipse(
        c,
        x,
        FLOOR + 1,
        (5 + 9 * contact) * visibility,
        1.5 + contact,
        blend("#111d30", "#698f90", contact * visibility * 0.8),
    )
    ellipse(c, x, cy, rx, ry, "#469d99", "#a0f3db", 1)
    ellipse(c, x - rx * 0.12, cy - ry * 0.15, rx * 0.74, ry * 0.73, "#72d7c5")
    ellipse(c, x - rx * 0.29, cy - ry * 0.34, rx * 0.23, ry * 0.13, "#e0ffed")


SCENES = {"backup": backup_scene, "python": python_scene, "android": android_scene}


def study_frame(phase, kind, mobile):
    style = STUDIES[kind]
    width, height = (496, 292) if mobile else (960, 218)
    card = Canvas(width, height, style.paper)
    card.image.paste(study_paper(kind, mobile))
    scene = Canvas(472, 168, style.paper)
    SCENES[kind](scene, phase)
    x, y = (12, 80) if mobile else (462, 25)
    card.image.paste(scene.image, (x * SCALE, y * SCALE))
    return card.finish()
