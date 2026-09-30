# -*- coding: utf-8 -*-
"""补裁: 参数修复条 + 双产品页下半部标题带 + 第四章标题带"""
import os
import numpy as np
import cv2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "产品资料")
OUT = os.path.join(ROOT, "work", "verify")
os.makedirs(OUT, exist_ok=True)


def imread_u(path):
    return cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)


def crop(page, side, fx0, fx1, fy0, fy1, tag):
    fp = os.path.join(SRC, f"fengtu_{page}.jpg")
    img = imread_u(fp)
    H, W = img.shape[:2]
    half = W // 2
    x0 = 0 if side == "L" else half
    cx0, cx1 = x0 + int(half * fx0), x0 + int(half * fx1)
    cy0, cy1 = int(H * fy0), int(H * fy1)
    c = img[cy0:cy1, cx0:cx1]
    out = os.path.join(OUT, f"p{page}-{side}-{tag}.jpg")
    cv2.imencode(".jpg", c, [cv2.IMWRITE_JPEG_QUALITY, 90])[1].tofile(out)
    print(os.path.basename(out), c.shape[1], "x", c.shape[0])


# 参数修复条
crop("18", "R", 0.22, 0.68, 0.18, 0.45, "fix3")   # 5-03 完整参数列
crop("20", "R", 0.24, 0.95, 0.14, 0.42, "fix3")   # 5-10 完整参数块
crop("21", "R", 0.24, 0.95, 0.14, 0.42, "fix3")   # 5-13 完整参数块
crop("22", "R", 0.24, 0.95, 0.14, 0.48, "fix3")   # 5-18 完整参数块
crop("23", "L", 0.55, 1.00, 0.13, 0.30, "fix2")   # 5-21 整车尺寸右半
# 双产品页下半部标题带(第二产品编号+名称)
for pg in ("05", "06", "07", "08"):
    crop(pg, "R", 0.0, 0.62, 0.42, 0.70, "mid")
crop("06", "L", 0.0, 0.62, 0.42, 0.70, "mid")
crop("08", "L", 0.0, 0.62, 0.42, 0.70, "mid")
# 第四章标题带 (半挂车 13-17)
for pg in ("13", "14", "15", "16", "17"):
    for sd in ("L", "R"):
        crop(pg, sd, 0.0, 0.62, 0.06, 0.34, "title")
