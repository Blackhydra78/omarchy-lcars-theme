#!/usr/bin/env python3
"""Generate the LCARS backgrounds as SVG and render them to PNG with rsvg-convert.

Usage: scripts/gen-backgrounds.py   (run from the theme root)
"""
import random
import subprocess
from pathlib import Path

W, H = 2560, 1600
OUT = Path(__file__).resolve().parent.parent / "backgrounds"

ORANGE, PEACH, TAN = "#ff9900", "#ffcc99", "#ff9966"
LILAC, VIOLET, BLUE = "#cc99cc", "#9999cc", "#9999ff"
RED, ROSE = "#cc6666", "#cc6699"
FONT = "Nimbus Sans Narrow, Liberation Sans Narrow, Arial Narrow, sans-serif"


def stars(seed, n, x0=0, y0=0, x1=W, y1=H):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        r = rnd.choice([0.8, 0.8, 1.1, 1.1, 1.6, 2.2])
        o = rnd.uniform(0.25, 0.9)
        c = rnd.choice(["#ffffff", "#ffffff", PEACH, "#bbddff"])
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{c}" opacity="{o:.2f}"/>')
    return "\n".join(out)


def block(x, y, w, h, color, label=None):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}"/>'
    if label:
        s += (
            f'<text x="{x + w - 16}" y="{y + h - 14}" text-anchor="end" font-family="{FONT}" '
            f'font-weight="bold" font-size="30" fill="#000000">{label}</text>'
        )
    return s


def bar(x0, x1, y, h, segments, gap=10):
    """Horizontal run of segments; each is (weight, color)."""
    total = sum(w for w, _ in segments)
    span = x1 - x0 - gap * (len(segments) - 1)
    out, x = [], x0
    for w, c in segments:
        sw = span * w / total
        out.append(f'<rect x="{x:.0f}" y="{y}" width="{sw:.0f}" height="{h}" fill="{c}"/>')
        x += sw + gap
    return "\n".join(out)


def svg(body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
        f'<rect width="{W}" height="{H}" fill="#000000"/>\n{body}\n</svg>\n'
    )


def frame():
    m, sw = 60, 300  # outer margin, sidebar width
    sx = m + sw  # sidebar right edge
    r_out, r_in, bh = 120, 60, 40  # elbow radii, bar height
    split = 520  # y where the two sections meet
    ex = 900  # x where elbows end and segmented bars start

    top_elbow = (
        f'<path fill="{LILAC}" d="M{m},300 H{sx} V{split - bh - r_in} '
        f'A{r_in},{r_in} 0 0 0 {sx + r_in},{split - bh} H{ex} V{split} H{m + r_out} '
        f'A{r_out},{r_out} 0 0 1 {m},{split - r_out} Z"/>'
    )
    y2 = split + 20
    bottom_elbow = (
        f'<path fill="{ORANGE}" d="M{m + r_out},{y2} H{ex} V{y2 + bh} H{sx + r_in} '
        f'A{r_in},{r_in} 0 0 0 {sx},{y2 + bh + r_in} V800 H{m} V{y2 + r_out} '
        f'A{r_out},{r_out} 0 0 1 {m + r_out},{y2} Z"/>'
    )
    parts = [
        stars(1701, 260, sx + 80, m, W - m, H - m),
        block(m, m, sw, 110, VIOLET, "03-1701"),
        block(m, 180, sw, 110, TAN, "47-0240"),
        top_elbow,
        bar(ex + 10, W - m, split - bh, bh, [(5, LILAC), (1, RED), (8, PEACH), (2, VIOLET), (4, LILAC)]),
        bottom_elbow,
        bar(ex + 10, W - m, y2, bh, [(2, ORANGE), (9, TAN), (1, BLUE), (3, ORANGE), (3, ROSE)]),
        block(m, 810, sw, 150, PEACH, "12-4077"),
        block(m, 970, sw, 70, RED, "05-9364"),
        block(m, 1050, sw, 230, BLUE, "21-3058"),
        block(m, 1290, sw, 110, LILAC, "08-7421"),
        block(m, 1410, sw, H - m - 1410, TAN, "30-1987"),
        f'<text x="{W - m}" y="{m + 150}" text-anchor="end" font-family="{FONT}" font-weight="bold" '
        f'font-size="170" fill="{ORANGE}">MAIN COMPUTER</text>',
        f'<text x="{W - m}" y="{m + 240}" text-anchor="end" font-family="{FONT}" font-weight="bold" '
        f'font-size="64" fill="{VIOLET}">LIBRARY ACCESS AND RETRIEVAL • MODE 47</text>',
    ]
    return svg("\n".join(parts))


def starfield():
    m, bh = 60, 28
    parts = [
        stars(47, 700),
        bar(m, W - m, m, bh, [(1, ORANGE), (10, LILAC), (2, PEACH), (1, RED), (6, VIOLET)]),
        bar(m, W - m, H - m - bh, bh, [(6, TAN), (1, BLUE), (3, ORANGE), (9, LILAC), (1, ROSE)]),
    ]
    return svg("\n".join(parts))


def main():
    OUT.mkdir(exist_ok=True)
    for name, doc in (("1-lcars-frame", frame()), ("2-starfield", starfield())):
        src = OUT / f"{name}.svg"
        src.write_text(doc)
        subprocess.run(["rsvg-convert", str(src), "-o", str(OUT / f"{name}.png")], check=True)
        src.unlink()


if __name__ == "__main__":
    main()
