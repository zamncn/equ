#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""生成农业机械占位图（本地绘制，不消耗额度）。
   风格与站点一致：NAVY #10222F 底 + AMBER #FFC72C 强调 + 机器剪影 + 型号文字。
   输出 images/products/p6-XX-thumb.jpg (600w) / p6-XX-large.jpg (1200w)
"""
import os, json
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "images", "products")
DATA = os.path.join(ROOT, "work", "agri_products.json")
os.makedirs(OUT, exist_ok=True)

NAVY = (16, 34, 47)
NAVY2 = (24, 48, 66)
AMBER = (255, 199, 44)
WHITE = (255, 255, 255)
GRAY = (150, 168, 180)

F_EN = "C:/Windows/Fonts/arialbd.ttf"
F_ZH = "C:/Windows/Fonts/msyhbd.ttc"
F_ENS = "C:/Windows/Fonts/arial.ttf"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def ctext(d, xy, text, f, fill, anchor="mm"):
    d.text(xy, text, font=f, fill=fill, anchor=anchor)


def silhouette(d, kind, cx, cy, s, col):
    """粗略画一个农机剪影，kind 决定造型。s = 缩放基准。"""
    w = d
    lw = max(3, int(s * 0.022))

    def rr(box, r, fill):
        w.rounded_rectangle(box, radius=int(r), fill=fill, outline=col, width=lw)

    if kind == "tractor":
        # 后大轮 + 前小轮 + 车身 + 驾驶室
        w.ellipse([cx - s*0.42, cy + s*0.06, cx - s*0.06, cy + s*0.42], outline=col, width=lw)
        w.ellipse([cx + s*0.16, cy + s*0.14, cx + s*0.40, cy + s*0.38], outline=col, width=lw)
        w.ellipse([cx - s*0.36, cy + s*0.12, cx - s*0.12, cy + s*0.36], outline=col, width=lw)
        w.ellipse([cx + s*0.20, cy + s*0.18, cx + s*0.36, cy + s*0.34], outline=col, width=lw)
        w.polygon([(cx - s*0.30, cy + s*0.12), (cx + s*0.02, cy + s*0.12),
                   (cx + s*0.02, cy - s*0.14), (cx - s*0.24, cy - s*0.14)], outline=col, width=lw)
        rr([cx - s*0.34, cy - s*0.34, cx - s*0.10, cy - s*0.10], s*0.03, None)
        # 排气管
        w.line([(cx - s*0.04, cy - s*0.14), (cx - s*0.04, cy - s*0.44)], fill=col, width=lw)
    elif kind == "harvester":
        # 割台 + 机身 + 粮箱
        w.polygon([(cx - s*0.55, cy + s*0.16), (cx + s*0.02, cy + s*0.16),
                   (cx + s*0.02, cy + s*0.30), (cx - s*0.55, cy + s*0.30)],
                  outline=col, width=lw)
        for i in range(7):
            x = cx - s*0.50 + i * s*0.075
            w.line([(x, cy + s*0.17), (x, cy + s*0.29)], fill=col, width=max(2, lw-1))
        rr([cx - s*0.02, cy - s*0.14, cx + s*0.34, cy + s*0.20], s*0.04, None)
        rr([cx + s*0.02, cy - s*0.30, cx + s*0.30, cy - s*0.10], s*0.03, None)
        w.line([(cx - s*0.30, cy + s*0.16), (cx - s*0.18, cy - s*0.06)], fill=col, width=lw)
        w.ellipse([cx + s*0.16, cy + s*0.14, cx + s*0.42, cy + s*0.40], outline=col, width=lw)
    elif kind == "seeder":
        # 机架 + 多组开沟器
        rr([cx - s*0.52, cy - s*0.10, cx + s*0.42, cy + s*0.02], s*0.02, None)
        for i in range(5):
            x = cx - s*0.44 + i * s*0.22
            w.line([(x, cy + s*0.02), (x - s*0.05, cy + s*0.26)], fill=col, width=lw)
            w.ellipse([x - s*0.11, cy + s*0.24, x + s*0.01, cy + s*0.36], outline=col, width=lw)
        rr([cx - s*0.30, cy - s*0.30, cx + s*0.02, cy - s*0.12], s*0.03, None)
    else:  # sprayer / trailer
        rr([cx - s*0.48, cy - s*0.18, cx + s*0.16, cy + s*0.14], s*0.04, None)
        w.line([(cx + s*0.16, cy + s*0.02), (cx + s*0.56, cy - s*0.06)], fill=col, width=lw)
        for i in range(6):
            x = cx + s*0.20 + i * s*0.062
            w.line([(x, cy - s*0.05), (x, cy + s*0.14)], fill=col, width=max(2, lw-1))
        w.ellipse([cx - s*0.36, cy + s*0.10, cx - s*0.14, cy + s*0.32], outline=col, width=lw)
        w.ellipse([cx + s*0.00, cy + s*0.10, cx + s*0.22, cy + s*0.32], outline=col, width=lw)


KIND = {"6-01": "tractor", "6-02": "tractor", "6-03": "tractor",
        "6-04": "harvester", "6-05": "harvester", "6-06": "harvester",
        "6-07": "seeder", "6-08": "seeder",
        "6-09": "other", "6-10": "other"}


def make(pid, name_en, name_zh, W=1200, H=800):
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    # 背景渐变
    for y in range(H):
        t = y / H
        c = tuple(int(NAVY[i] + (NAVY2[i] - NAVY[i]) * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    # 网格纹理
    for x in range(0, W, 60):
        d.line([(x, 0), (x, H)], fill=(24, 46, 62), width=1)
    for y in range(0, H, 60):
        d.line([(0, y), (W, y)], fill=(24, 46, 62), width=1)
    # 底部品牌黄条
    d.rectangle([0, H - 14, W, H], fill=AMBER)
    d.rectangle([0, 0, W, 6], fill=AMBER)
    # 剪影
    silhouette(d, KIND.get(pid, "other"), W * 0.5, H * 0.42, H * 0.62, AMBER)
    # 文字
    ctext(d, (W*0.5, H*0.80), name_en, font(F_EN, int(H*0.070)), WHITE)
    ctext(d, (W*0.5, H*0.90), name_zh, font(F_ZH, int(H*0.052)), GRAY)
    # 角标
    ctext(d, (W*0.5, H*0.09), "PLACEHOLDER IMAGE", font(F_ENS, int(H*0.030)), (120, 140, 155))
    return im


def main():
    data = json.load(open(DATA, encoding="utf-8"))
    n = 0
    for g in data["groups"]:
        for p in g["products"]:
            im = make(p["id"], p["name_en"], p["name_zh"])
            large = im
            large.save(os.path.join(OUT, f"p{p['id']}-large.jpg"), quality=85)
            thumb = im.resize((600, int(600 * im.height / im.width)), Image.LANCZOS)
            thumb.save(os.path.join(OUT, f"p{p['id']}-thumb.jpg"), quality=82)
            n += 2
            print(f"  p{p['id']}  {p['name_en']}")
    print(f"生成 {n} 个文件 -> images/products/")


if __name__ == "__main__":
    main()
