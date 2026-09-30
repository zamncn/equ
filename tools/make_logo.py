#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generate the EquipSupply brand assets:
  - images/logo.svg                      vector master
  - images/logo-default-160x35.png (+320x70)   dark ink, for light backgrounds
  - images/logo-inverse-160x35.png (+320x70)   white ink, for dark backgrounds
  - images/logo-mark-512.png             square mark (og / apple touch source)
  - images/favicon.ico                   16/24/32/48
  - images/favicon-16/32/192/512.png
  - images/apple-touch-icon.png          180
Draws with Pillow so there is no external rasteriser dependency.
"""
import os, json
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "images")
os.makedirs(IMG, exist_ok=True)

NAVY = (16, 34, 47, 255)
AMBER = (255, 199, 44, 255)
WHITE = (255, 255, 255, 255)
SS = 4  # supersample factor

FONT_CANDIDATES = [
    (r"C:\Windows\Fonts\bahnschrift.ttf", ["Semibold", "SemiBold", "Bold", "Semi Condensed"]),
    (r"C:\Windows\Fonts\arialbd.ttf", []),
    (r"C:\Windows\Fonts\segoeuib.ttf", []),
    (r"C:\Windows\Fonts\verdanab.ttf", []),
]


def pick_font():
    for path, variations in FONT_CANDIDATES:
        if not os.path.exists(path):
            continue
        try:
            probe = ImageFont.truetype(path, 40)
            for v in variations:
                try:
                    probe.set_variation_by_name(v)
                    break
                except Exception:
                    continue
            return path
        except Exception:
            continue
    return None


FONT_PATH = pick_font()


def font_at(px):
    """px is in final (CSS) pixels; returns font scaled by supersample."""
    return ImageFont.truetype(FONT_PATH, int(round(px * SS)))


def tracked_width(font, text, tracking):
    w = 0.0
    for ch in text:
        w += font.getlength(ch)
    return w + tracking * max(0, len(text) - 1)


def draw_tracked(d, xy, text, font, fill, tracking):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill, anchor="lm")
        x += font.getlength(ch) + tracking


# ---------------------------------------------------------------- mark (icon)
def draw_mark(d, x, y, size, bg, fg):
    """Amber rounded square holding a navy 'E' whose middle bar is an arrow."""
    r = int(round(size * 0.24))
    d.rounded_rectangle([x, y, x + size, y + size], radius=r, fill=bg)
    u = size / 30.0

    def rect(x0, y0, x1, y1):
        d.rectangle([x + x0 * u, y + y0 * u, x + x1 * u, y + y1 * u], fill=fg)

    rect(5.2, 6.4, 9.6, 23.6)    # spine
    rect(5.2, 6.4, 21.6, 10.4)   # top bar
    rect(5.2, 19.6, 21.6, 23.6)  # bottom bar
    rect(5.2, 13.2, 17.4, 16.8)  # middle bar
    d.polygon(  # arrow head -> "supply / moving forward"
        [
            (x + 16.6 * u, y + 12.0 * u),
            (x + 24.6 * u, y + 15.0 * u),
            (x + 16.6 * u, y + 18.0 * u),
        ],
        fill=fg,
    )


# ------------------------------------------------------------- full wordmark
def render_wordmark(w, h, ink, accent, transparent=True):
    W, H = w * SS, h * SS
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0) if transparent else (255, 255, 255, 255))
    d = ImageDraw.Draw(im)

    pad = 2.0 * SS
    mark = h * 0.82 * SS
    my = (H - mark) / 2.0
    draw_mark(d, pad, my, mark, AMBER, NAVY)

    # wordmark: "EQUIP" (ink) + "SUPPLY" (accent)
    budget = W - (pad + mark + 7.0 * SS) - pad
    gap_ratio = 0.20  # visual space between the two words
    best = None
    for size in range(int(h * 0.60), 4, -1):
        f = font_at(size)
        tr = size * SS * 0.02
        w1 = tracked_width(f, "EQUIP", tr)
        w2 = tracked_width(f, "SUPPLY", tr)
        if w1 + w2 + size * SS * gap_ratio <= budget:
            best = (size, f, tr, w1, w2)
            break
    if best is None:
        raise RuntimeError("wordmark does not fit")
    size, f, tr, w1, w2 = best
    gap = size * SS * gap_ratio
    total = w1 + gap + w2
    tx = pad + mark + 7.0 * SS + max(0.0, (budget - total) / 2.0)
    draw_tracked(d, (tx, H / 2.0), "EQUIP", f, ink, tr)          # anchor lm
    draw_tracked(d, (tx + w1 + gap, H / 2.0), "SUPPLY", f, accent, tr)
    return im.resize((w, h), Image.LANCZOS)


def render_favicon(size):
    im = Image.new("RGBA", (size * SS, size * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    inset = size * 0.02 * SS
    draw_mark(d, inset, inset, size * SS - 2 * inset, AMBER, NAVY)
    return im.resize((size, size), Image.LANCZOS)


def write_svg():
    """Vector master: same geometry as the PNG renderer (viewBox 0 0 320 70)."""
    w, h = 320, 70
    pad, gap_css, mark = 2.0, 7.0, h * 0.82
    u = mark / 30.0
    my = (h - mark) / 2.0

    def R(x0, y0, x1, y1):
        x, y = pad, my
        return (f'<rect x="{x+x0*u:.2f}" y="{y+y0*u:.2f}" '
                f'width="{(x1-x0)*u:.2f}" height="{(y1-y0)*u:.2f}" fill="#10222F"/>')

    ax, ay = pad + 16.6 * u, my + 12.0 * u
    arrow = (f'<polygon points="{ax:.2f},{ay:.2f} '
             f'{pad+24.6*u:.2f},{my+15.0*u:.2f} '
             f'{ax:.2f},{my+18.0*u:.2f}" fill="#10222F"/>')

    # wordmark metrics (mirror the fit loop at CSS scale)
    size = 0
    for s in range(int(h * 0.60), 4, -1):
        est = 0.62 * s * 11 + 0.02 * s * 10 + 0.20 * s
        if est <= w - (pad + mark + gap_css) - pad:
            size = s
    if size == 0:
        size = 30
    tr = size * 0.02
    def width_of(t):
        return sum(0.62 for _ in t) * size + tr * (len(t) - 1)
    w1, w2 = width_of("EQUIP"), width_of("SUPPLY")
    gap = size * gap_css * 0.20 / 0.20
    gap = size * 0.20
    total = w1 + gap + w2
    budget = w - (pad + mark + gap_css) - pad
    tx = pad + mark + gap_css + max(0.0, (budget - total) / 2.0)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="EquipSupply">
  <g>
    <rect x="{pad}" y="{my:.2f}" width="{mark:.2f}" height="{mark:.2f}" rx="{0.24*mark:.2f}" fill="#FFC72C"/>
    {R(5.2, 6.4, 9.6, 23.6)}
    {R(5.2, 6.4, 21.6, 10.4)}
    {R(5.2, 19.6, 21.6, 23.6)}
    {R(5.2, 13.2, 17.4, 16.8)}
    {arrow}
  </g>
  <text x="{tx:.2f}" y="{h/2:.1f}" font-family="Bahnschrift, 'Arial Narrow', Arial, sans-serif" font-weight="600" font-size="{size}" letter-spacing="{tr:.2f}" fill="#10222F" dominant-baseline="central">EQUIP</text>
  <text x="{tx+w1+gap:.2f}" y="{h/2:.1f}" font-family="Bahnschrift, 'Arial Narrow', Arial, sans-serif" font-weight="600" font-size="{size}" letter-spacing="{tr:.2f}" fill="#FFC72C" dominant-baseline="central">SUPPLY</text>
</svg>
'''
    with open(os.path.join(IMG, "logo.svg"), "w", encoding="utf-8") as fh:
        fh.write(svg)
    print("logo.svg written")


def main():
    print("font:", FONT_PATH)
    out = {}

    # wordmarks -----------------------------------------------------------
    variants = [
        ("logo-default-160x35.png", 160, 35, NAVY),
        ("logo-default-320x70.png", 320, 70, NAVY),
        ("logo-inverse-160x35.png", 160, 35, WHITE),
        ("logo-inverse-320x70.png", 320, 70, WHITE),
    ]
    for name, w, h, ink in variants:
        im = render_wordmark(w, h, ink, AMBER)
        im.save(os.path.join(IMG, name))
        out[name] = [w, h]

    # square mark ---------------------------------------------------------
    for s in (512, 180):
        im = Image.new("RGBA", (s * SS, s * SS), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        draw_mark(d, 0, 0, s * SS, AMBER, NAVY)
        d2 = im.resize((s, s), Image.LANCZOS)
        p = os.path.join(IMG, "logo-mark-%d.png" % s)
        d2.save(p)
        out[os.path.basename(p)] = [s, s]
    # apple touch icon: amber square on solid dark plate (no transparency)
    at = Image.new("RGBA", (180 * SS, 180 * SS), NAVY)
    d = ImageDraw.Draw(at)
    draw_mark(d, 12 * SS, 12 * SS, 156 * SS, AMBER, NAVY)
    at.resize((180, 180), Image.LANCZOS).save(os.path.join(IMG, "apple-touch-icon.png"))

    # favicons ------------------------------------------------------------
    for s in (16, 32, 192, 512):
        p = os.path.join(IMG, "favicon-%d.png" % s)
        render_favicon(s).save(p)
        out["favicon-%d.png" % s] = [s, s]
    ico_path = os.path.join(IMG, "favicon.ico")
    render_favicon(64).save(
        ico_path, format="ICO", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64)]
    )

    write_svg()

    print(json.dumps(out, indent=2, ensure_ascii=False))
    print("font used:", FONT_PATH)


if __name__ == "__main__":
    main()
