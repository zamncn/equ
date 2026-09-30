#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把参数区裁片横向拼接成对图，减少转录读取次数；并补双产品页编号徽章裁片。"""
import os
import numpy as np
import cv2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "产品资料")
V = os.path.join(ROOT, "work", "verify")
os.makedirs(V, exist_ok=True)


def imread_u(p):
    return cv2.imdecode(np.fromfile(p, dtype=np.uint8), cv2.IMREAD_COLOR)


def crop(page, side, fx0, fx1, fy0, fy1):
    img = imread_u(os.path.join(SRC, f"fengtu_{page}.jpg"))
    H, W = img.shape[:2]
    half = W // 2
    x0 = 0 if side == "L" else half
    return img[int(H * fy0):int(H * fy1), x0 + int(half * fx0):x0 + int(half * fx1)]


def save(name, img):
    out = os.path.join(V, name)
    cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 88])[1].tofile(out)
    print(name, img.shape[1], "x", img.shape[0])


def hpair(name, imgs):
    """horizontal pair, white separator, bottom-aligned via top padding"""
    h = max(i.shape[0] for i in imgs)
    fixed = []
    for im in imgs:
        if im.shape[0] < h:
            pad = np.full((h - im.shape[0], im.shape[1], 3), 255, np.uint8)
            im = np.vstack([pad, im])
        fixed.append(im)
    bar = np.full((h, 8, 3), 255, np.uint8)
    out = fixed[0]
    for im in fixed[1:]:
        out = np.hstack([out, bar, im])
    save(name, out)


# ---- 第二产品编号徽章 (double-product sides) --------------------------------
b1 = crop("05", "R", 0.00, 0.55, 0.40, 0.72)   # 1-10 badge
b2 = crop("10", "L", 0.00, 0.55, 0.42, 0.74)   # 3-02 badge
b3 = crop("11", "L", 0.00, 0.55, 0.42, 0.74)   # 3-05 badge
b4 = crop("12", "L", 0.00, 0.55, 0.42, 0.74)   # 3-12 badge
b5 = crop("12", "R", 0.00, 0.55, 0.42, 0.74)   # 3-17 badge
hpair("badges-pair1.jpg", [b1, b2])
hpair("badges-pair2.jpg", [b3, b4])
save("badges-pair3.jpg", b5)

# ---- 参数对拼图 (ch01-03) ---------------------------------------------------
def bot(pg, sd):
    y0, y1 = {"03L": .42, "03R": .38, "04L": .38, "04R": .38, "05L": .38,
              "05R": .48, "06L": .48, "06R": .48, "07L": .38, "07R": .48,
              "08L": .35, "08R": .48, "09L": .38, "09R": .35,
              "10L": .50, "10R": .35, "11L": .50, "11R": .35,
              "12L": .50, "12R": .50}.get(pg + sd, .38), .99
    x0 = .40 if pg + sd == "10R" else (.40 if pg + sd == "11R" else .36)
    return crop(pg, sd, x0, .98, y0, y1)


def top(pg, sd):
    return crop(pg, sd, .36, .98, .03, .52)


hpair("pair-p03-bot.jpg", [bot("03", "L"), bot("03", "R")])
hpair("pair-p04-bot.jpg", [bot("04", "L"), bot("04", "R")])
hpair("pair-p05-bot.jpg", [bot("05", "L"), bot("05", "R")])
hpair("pair-p05-top.jpg", [top("05", "R")])
hpair("pair-p06-top.jpg", [top("06", "L"), top("06", "R")])
hpair("pair-p06-bot.jpg", [bot("06", "L"), bot("06", "R")])
hpair("pair-p07-a.jpg", [bot("07", "L"), top("07", "R")])
hpair("pair-p07-b.jpg", [bot("07", "R")])
hpair("pair-p08-a.jpg", [bot("08", "L"), top("08", "R")])
hpair("pair-p08-b.jpg", [bot("08", "R")])
hpair("pair-p09-bot.jpg", [bot("09", "L"), bot("09", "R")])
hpair("pair-p10-a.jpg", [top("10", "L"), bot("10", "R")])
hpair("pair-p10-b.jpg", [bot("10", "L")])
hpair("pair-p11-a.jpg", [top("11", "L"), bot("11", "R")])
hpair("pair-p11-b.jpg", [bot("11", "L")])
hpair("pair-p12-top.jpg", [top("12", "L"), top("12", "R")])
hpair("pair-p12-bot.jpg", [bot("12", "L"), bot("12", "R")])
save("pair-p02R.jpg", crop("02", "R", .36, .98, .30, .99))

# ---- 第04章 半挂车文字页 ----------------------------------------------------
for pg in ("13", "14", "15", "16", "17"):
    for sd in ("L", "R"):
        save(f"p4-{pg}{sd}.jpg", crop(pg, sd, 0.0, 1.0, 0.04, 0.99))

# ---- 第05章剩余 ------------------------------------------------------------
hpair("pair-ch05L-a.jpg", [crop("18", "L", 0, .45, .05, .50), crop("19", "L", 0, .45, .05, .52)])
hpair("pair-ch05L-b.jpg", [crop("20", "L", 0, .45, .05, .50), crop("21", "L", 0, .45, .05, .50)])
t = crop("22", "L", 0, .45, .05, .48)
b = crop("22", "L", 0, .45, .50, .95)
save("pair-ch05L-c.jpg", np.vstack([t, np.full((12, t.shape[1], 3), 255, np.uint8), b]))
# 5-18 品牌行
save("p22R-brand.jpg", crop("22", "R", 0.0, 0.95, 0.55, 0.75))
print("done")
