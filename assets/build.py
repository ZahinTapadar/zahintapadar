#!/usr/bin/env python3
"""Builds the README's SVG panels in the portfolio's terminal style.

Each panel is self-contained (GitHub serves README images through a proxy that
blocks external fonts and images), so the font subset and the artwork are
embedded as data URIs. Edit the content below and run `python3 assets/build.py`.
"""
import base64
import html
import os
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'src')

# Portfolio tokens (NewPortfolio/src/components/MinimalPortfolio.css)
BG, FG, FG2, DIM, LINE, ACCENT = '#000000', '#e6e6e6', '#abb2bf', '#7f848e', '#444444', '#98c379'

W = 840            # panel width
FS = 14            # font size
CW = FS * 0.6      # JetBrains Mono advance width
LH = 24            # line height
PAD = 22

# ---- content ---------------------------------------------------------------

ABOUT = [
    "i'm a computer science student trying to get better at systems,",
    "algorithms, and low-level programming. basically, figuring out how",
    "things work under the hood while still building interfaces people",
    "can actually use.",
]

FEATURED = [
    ('2026', 'ATLAS', 'macos time tracker, swift + claude'),
    ('2026', 'Schwarzschild Lab', 'black hole ray tracer, rust/wasm'),
    ('2026', 'wortraum', 'wordle solver, lua + c + wasm'),
]

ARCHIVE = ['LoveBites dotfiles', 'ADB App Manager', 'Razer Mouse Manager', 'BeautifyOllama', 'Tech For Life',
           'BTR GOV', 'Personify', 'Quize', 'WebGeny']

STACK = [
    ('systems', ['C', 'C++', 'Rust', 'WebAssembly']),
    ('graphics', ['OpenGL', 'WebGL2', 'GLSL']),
    ('languages', ['Python', 'Lua', 'LuaJIT', 'TypeScript']),
    ('gamedev', ['Unity', 'LÖVE']),
    ('web', ['React', 'Next.js', 'Astro', 'Svelte', 'Tailwind CSS', 'GSAP', 'Tauri']),
    ('infra', ['Firebase', 'Vercel', 'GitHub Actions']),
    ('tools', ['Neovim', 'IDA Pro', 'Ghidra']),
]

POSTS = [
    ('1 nov 2026', 'Building a Synthetic Telescope'),
    ('1 nov 2026', 'Pillars and Superclusters in Every Band'),
    ('30 oct 2026', 'Schwarzschild Lab — Findings'),
    ('23 oct 2026', 'Building a Black Hole Simulator'),
    ('23 oct 2026', 'Making a Wordle Solver That Actually Thinks'),
]

CHIPS = ['portfolio', 'blog', 'linkedin', 'email', 'atlas', 'schwarzschild-lab', 'wortraum', 'dotfiles']

# ---- helpers ---------------------------------------------------------------

used_text: list[str] = []


def t(s: str) -> str:
    used_text.append(s)
    return html.escape(s)


def data_uri(path: str, mime: str) -> str:
    with open(path, 'rb') as f:
        return f'data:{mime};base64,' + base64.b64encode(f.read()).decode()


def font_face() -> str:
    """Subset JetBrains Mono to the characters actually drawn."""
    chars = ''.join(sorted(set(''.join(used_text)) | set('$:~/ .-')))
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, 'font.woff')
        subprocess.run(['pyftsubset', os.path.join(SRC, 'JetBrainsMono-Regular.ttf'),
                        f'--text={chars}', '--flavor=woff', f'--output-file={out}',
                        '--layout-features=', '--no-hinting'], check=True)
        uri = data_uri(out, 'font/woff')
    return f"@font-face{{font-family:'JBM';src:url({uri}) format('woff');}}"


STYLE = """
text{{font-family:'JBM','JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,monospace;font-size:{fs}px;fill:{fg};white-space:pre}}
.u{{fill:{accent}}} .p{{fill:{fg2}}} .d{{fill:{dim}}} .w{{fill:#ffffff}} .a{{fill:{accent}}}
.lead{{font-size:17px}}
.row{{opacity:0;animation:in .35s ease-out forwards}}
@keyframes in{{from{{opacity:0;transform:translateY(4px)}}to{{opacity:1;transform:none}}}}
@media (prefers-reduced-motion:reduce){{.row{{animation:none;opacity:1}}}}
"""


def svg(width: float, height: float, body: str, font: str) -> str:
    style = STYLE.format(fs=FS, fg=FG, fg2=FG2, dim=DIM, accent=ACCENT)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:g}" height="{height:g}" '
            f'viewBox="0 0 {width:g} {height:g}">'
            f'<style>{font}{style}</style>{body}</svg>')


def panel_frame(height: float) -> str:
    return ('<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0" stop-color="#0b0d10"/><stop offset="1" stop-color="#000"/></linearGradient></defs>'
            f'<rect x="0.5" y="0.5" width="{W - 1}" height="{height - 1}" rx="4" fill="url(#bg)" '
            f'stroke="{LINE}" stroke-dasharray="4 3"/>')


def prompt(y: float, cmd: str, x: float = PAD) -> str:
    return (f'<text x="{x}" y="{y}"><tspan class="u">{t("zahin@dev")}</tspan><tspan class="d">:</tspan>'
            f'<tspan class="p">~</tspan><tspan class="d">$ </tspan>{t(cmd)}</text>')


class Rows:
    """Rows fade in one after another, like the portfolio's terminal panels."""

    def __init__(self):
        self.n = 0

    def __call__(self, inner: str) -> str:
        self.n += 1
        return f'<g class="row" style="animation-delay:{0.15 + self.n * 0.06:.2f}s">{inner}</g>'


# ---- panels ----------------------------------------------------------------

def about() -> tuple[float, str]:
    row = Rows()
    y = PAD + 14
    body = [prompt(y, 'cat about.txt')]
    y += LH + 12
    body.append(row(f'<text x="{PAD}" y="{y}" class="w lead">{t("hey, i’m zahin.")}</text>'))
    y += LH
    body.append(row(f'<text x="{PAD}" y="{y}" class="d">{t("cs student · systems, graphics & low-level")}</text>'))
    y += LH + 8
    for line in ABOUT:
        body.append(row(f'<text x="{PAD}" y="{y}" class="p">{t(line)}</text>'))
        y += LH
    # avatar, top right, framed like the portfolio's
    size = 96
    ax, ay = W - PAD - size, PAD
    body.append(f'<clipPath id="av"><rect x="{ax}" y="{ay}" width="{size}" height="{size}" rx="4"/></clipPath>'
                f'<image href="{data_uri(os.path.join(SRC, "avatar.jpg"), "image/jpeg")}" x="{ax}" y="{ay}" '
                f'width="{size}" height="{size}" clip-path="url(#av)" preserveAspectRatio="xMidYMid slice"/>'
                f'<rect x="{ax + .5}" y="{ay + .5}" width="{size - 1}" height="{size - 1}" rx="4" fill="none" stroke="{LINE}"/>')
    h = y - LH + PAD + 8
    return h, panel_frame(h) + ''.join(body)


def projects() -> tuple[float, str]:
    row = Rows()
    y = PAD + 14
    body = [prompt(y, 'ls -l ~/projects')]
    y += LH + 8
    for year, title, detail in FEATURED:
        body.append(row(f'<text x="{PAD}" y="{y}"><tspan class="d">{t("drwxr-xr-x  " + year + "  ")}</tspan>'
                        f'<tspan class="w">{t(title.ljust(19))}</tspan><tspan class="d">{t(detail)}</tspan></text>'))
        y += LH
    y += 14
    body.append(prompt(y, 'ls ~/projects/archive'))
    y += LH + 4
    line, lines = '', []
    for name in ARCHIVE:
        piece = name + '   '
        if len(line) + len(piece) > (W - 2 * PAD) / CW:
            lines.append(line)
            line = ''
        line += piece
    lines.append(line)
    for line in lines:
        body.append(row(f'<text x="{PAD}" y="{y}" class="d">{t(line.rstrip())}</text>'))
        y += LH
    h = y - LH + PAD + 8
    return h, panel_frame(h) + ''.join(body)


def blog() -> tuple[float, str]:
    row = Rows()
    y = PAD + 14
    body = [prompt(y, 'ls -t ~/blog')]
    y += LH + 8
    for date, title in POSTS:
        body.append(row(f'<text x="{PAD}" y="{y}"><tspan class="d">{t(date.ljust(13))}</tspan>'
                        f'<tspan class="w">{t(title)}</tspan></text>'))
        y += LH
    h = y - LH + PAD + 8
    return h, panel_frame(h) + ''.join(body)


def stack() -> tuple[float, str]:
    row = Rows()
    y = PAD + 14
    body = [prompt(y, 'tree ~/stack')]
    y += LH + 8
    for i, (d, items) in enumerate(STACK):
        branch = '└── ' if i == len(STACK) - 1 else '├── '
        parts = [f'<text x="{PAD}" y="{y}"><tspan class="d">{t(branch)}</tspan><tspan class="a">{t(d + "/")}</tspan></text>']
        x = PAD + CW * 16
        for item in items:
            w = len(item) * CW + 14
            parts.append(f'<rect x="{x:.1f}" y="{y - 15}" width="{w:.1f}" height="21" rx="3" '
                         f'fill="rgba(255,255,255,0.03)" stroke="{LINE}"/>'
                         f'<text x="{x + 7:.1f}" y="{y}" class="p">{t(item)}</text>')
            x += w + 8
        body.append(row(''.join(parts)))
        y += LH + 6
    h = y - LH - 6 + PAD + 8
    return h, panel_frame(h) + ''.join(body)


def art(name: str, src: str, w: float, h: float, fade: str) -> tuple[float, float, str]:
    """Artwork as a frame: the image dissolves into black at the given edge."""
    img = data_uri(os.path.join(SRC, src), 'image/jpeg')
    defs = ''
    mask = ''
    if fade == 'top':
        defs = ('<defs><linearGradient id="f" x1="0" y1="0" x2="0" y2="1">'
                '<stop offset="0" stop-color="#fff" stop-opacity="0"/>'
                '<stop offset="0.45" stop-color="#fff" stop-opacity="1"/></linearGradient>'
                f'<mask id="m"><rect width="{w}" height="{h}" fill="url(#f)"/></mask></defs>')
        mask = ' mask="url(#m)"'
    body = (f'{defs}<rect width="{w}" height="{h}" rx="4" fill="{BG}"/>'
            f'<image href="{img}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice"{mask}/>')
    return w, h, body


def chip(label: str) -> tuple[float, float, str]:
    text = label + ' ↗'
    w = len(text) * CW + 18
    h = 26
    body = ('<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="{ACCENT}" stop-opacity="0.16"/>'
            f'<stop offset="1" stop-color="{ACCENT}" stop-opacity="0.04"/></linearGradient></defs>'
            f'<rect x="0.5" y="0.5" width="{w - 1:.1f}" height="{h - 1}" rx="3" fill="url(#g)" '
            f'stroke="{ACCENT}" stroke-opacity="0.45"/>'
            f'<text x="9" y="17.5" class="a">{t(text)}</text>')
    return w, h, body


def eof() -> tuple[float, float, str]:
    w, h, body = art('eof', 'art-eof.jpg', W, W * 9 / 16, 'top')
    body += f'<text x="{PAD}" y="{PAD + 14}" class="d">{t("EOF")}</text>'
    return w, h, body


# ---- write -----------------------------------------------------------------

def main():
    out: dict[str, tuple[float, float, str]] = {}
    for name, fn in [('about', about), ('projects', projects), ('blog', blog), ('stack', stack)]:
        h, body = fn()
        out[name] = (W, h, body)
    out['art'] = art('art', 'art-top.jpg', W, W * 414 / 736, 'none')
    out['eof'] = eof()
    for label in CHIPS:
        out[f'chip-{label}'] = chip(label)

    font = font_face()   # after every panel, so the subset covers all text
    for name, (w, h, body) in out.items():
        with open(os.path.join(HERE, f'{name}.svg'), 'w') as f:
            f.write(svg(w, h, body, font))
    print('wrote', ', '.join(f'{n}.svg' for n in out))


if __name__ == '__main__':
    main()
