#!/usr/bin/env python3
"""
Generate hero.svg -- a dark terminal-card SVG that "types" my name in like a
terminal then freezes (one-shot, no loop except a single blinking cursor).

Every animation is SMIL <animate>/<animateTransform> so GitHub renders it when
the SVG is embedded via <img>. Set STATIC=1 to render the final frozen frame
only (handy for quick local previews).
"""
import os

STATIC = bool(os.environ.get("STATIC"))

HERE = os.path.dirname(__file__)
OUT_PATH = os.path.join(HERE, "..", "hero.svg")

FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

BG1 = "#0d1117"
BG2 = "#111722"
FRAME = "#1f6feb"
MUTED = "#7d8590"
TITLE_TXT = "#8b949e"
NAME_TXT = "#e6edf3"
KEY = "#ffa657"
DESC = "#c9d1d9"
DOTS = ["#ff5f56", "#ffbd2e", "#27c93f"]

TITLEBAR_H = 34
PAD = 30

# (key, description) role rows
ROLES = [
    ("Frontend", "React, Next.js, Tailwind CSS"),
    ("App", "Flutter & Dart"),
    ("Backend", "Django, Node.js, FastAPI, Docker, Kubernetes, CI/CD"),
    ("GenAI", "LangChain, LangFlow, LangGraph, RAG"),
]

NAME = "Suppp! I'm Rehbar Khan"

CANVAS_W = 780
CANVAS_H = 300

NAME_Y = TITLEBAR_H + 60
NAME_FS = 30
# approx char width for monospace-bold name at NAME_FS; buffer so the
# reveal wipe never freezes mid-glyph and clips the last letters.
NAME_W = int(len(NAME) * NAME_FS * 0.66) + 18

ROLE_START_Y = NAME_Y + 46
ROLE_STEP = 34
ROLE_FS = 16

# timing
WIPE_DUR = 1.1          # name reveal
ROLE_STAGGER = 0.15     # gap between role rows
ROLE_FADE = 0.5


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def render():
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
        f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="{FONT}">',
        '<defs>',
        '<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BG1}"/><stop offset="1" stop-color="{BG2}"/></linearGradient>',
        '<clipPath id="nameClip"><rect x="0" y="0" '
        f'width="{NAME_W if STATIC else 0}" height="{CANVAS_H}">',
    ]
    if not STATIC:
        parts.append(
            f'<animate attributeName="width" from="0" to="{NAME_W}" '
            f'begin="0.3s" dur="{WIPE_DUR}s" fill="freeze"/>'
        )
    parts.append('</rect></clipPath></defs>')

    # card
    parts.append(f'<rect width="{CANVAS_W}" height="{CANVAS_H}" rx="12" fill="url(#bg)"/>')
    parts.append(
        f'<rect x="0.5" y="0.5" width="{CANVAS_W-1}" height="{CANVAS_H-1}" rx="12" '
        f'fill="none" stroke="{FRAME}" stroke-width="1" stroke-opacity="0.55"/>'
    )
    parts.append(
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{CANVAS_W}" y2="{TITLEBAR_H}" '
        f'stroke="{FRAME}" stroke-opacity="0.35"/>'
    )
    for i, dot in enumerate(DOTS):
        parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dot}"/>')
    parts.append(
        f'<text x="{CANVAS_W/2}" y="{TITLEBAR_H/2 + 4}" fill="{TITLE_TXT}" font-size="12" '
        f'text-anchor="middle">rehbar@github: ~$ whoami</text>'
    )

    # name, revealed via clip wipe
    parts.append(
        f'<g clip-path="url(#nameClip)">'
        f'<text x="{PAD}" y="{NAME_Y}" fill="{NAME_TXT}" font-size="{NAME_FS}" '
        f'font-weight="700">{esc(NAME)}</text></g>'
    )

    # cursor riding the wipe edge; fades out when wipe finishes
    cur_h = NAME_FS
    cur_y = NAME_Y - NAME_FS + 4
    if STATIC:
        pass  # frozen: no riding cursor
    else:
        parts.append(
            f'<rect x="{PAD}" y="{cur_y}" width="11" height="{cur_h}" fill="{NAME_TXT}">'
            f'<animate attributeName="x" from="{PAD}" to="{PAD + NAME_W}" '
            f'begin="0.3s" dur="{WIPE_DUR}s" fill="freeze"/>'
            f'<animate attributeName="opacity" from="1" to="0" '
            f'begin="{0.3 + WIPE_DUR}s" dur="0.25s" fill="freeze"/>'
            f'</rect>'
        )

    roles_begin = 0.3 + WIPE_DUR + 0.1

    # role rows -- fade + slide in, staggered
    for i, (key, desc) in enumerate(ROLES):
        y = ROLE_START_Y + i * ROLE_STEP
        begin = roles_begin + i * ROLE_STAGGER
        opacity0 = "1" if STATIC else "0"
        g = [f'<g opacity="{opacity0}" transform="translate(0,{0 if STATIC else 5})">']
        if not STATIC:
            g.append(
                f'<animate attributeName="opacity" from="0" to="1" '
                f'begin="{begin:.2f}s" dur="{ROLE_FADE}s" fill="freeze"/>'
            )
            g.append(
                f'<animateTransform attributeName="transform" type="translate" '
                f'from="0 5" to="0 0" begin="{begin:.2f}s" dur="{ROLE_FADE}s" fill="freeze"/>'
            )
        g.append(
            f'<text x="{PAD}" y="{y}" font-size="{ROLE_FS}">'
            f'<tspan fill="{KEY}" font-weight="700">{esc(key)}</tspan>'
            f'<tspan fill="{MUTED}"> &#8212; </tspan>'
            f'<tspan fill="{DESC}">{esc(desc)}</tspan></text>'
        )
        g.append('</g>')
        parts.append("".join(g))

    # single steady blinking cursor at end of last line
    last_y = ROLE_START_Y + (len(ROLES) - 1) * ROLE_STEP
    last_len = len(f"{ROLES[-1][0]} — {ROLES[-1][1]}")
    cur_x = PAD + int(last_len * ROLE_FS * 0.60) + 4
    blink_begin = roles_begin + (len(ROLES) - 1) * ROLE_STAGGER + ROLE_FADE
    parts.append(
        f'<rect x="{cur_x}" y="{last_y - ROLE_FS + 3}" width="8" height="{ROLE_FS}" '
        f'fill="{KEY}"'
    )
    if STATIC:
        parts.append(' opacity="1"/>')
    else:
        parts.append(
            f'><animate attributeName="opacity" values="0;0;1;1" keyTimes="0;0.5;0.5;1" '
            f'dur="1.1s" begin="{blink_begin:.2f}s" repeatCount="indefinite"/></rect>'
        )

    parts.append("</svg>")
    return "".join(parts)


if __name__ == "__main__":
    svg = render()
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    size = os.path.getsize(OUT_PATH)
    print(f"wrote {os.path.abspath(OUT_PATH)} ({size} bytes)")
