# -*- coding: utf-8 -*-
"""按版式知识批量生成产品参数区高分辨率裁片(原生分辨率)，用于精确转录校验。"""
import os
import numpy as np
import cv2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "产品资料")
OUT = os.path.join(ROOT, "work", "verify")
os.makedirs(OUT, exist_ok=True)


def imread_u(path):
    return cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)


# (page, side) -> list of (tag, y0, y1, x0, x1)  y/x 为 side 内比例
SPEC = {
    "02R": [("full", 0.36, 0.98, 0.38, 0.98)],
    "03L": [("bot", 0.42, 0.99, 0.36, 0.98)],
    "03R": [("bot", 0.38, 0.99, 0.36, 0.98)],
    "04L": [("bot", 0.38, 0.99, 0.36, 0.98)],
    "04R": [("bot", 0.38, 0.99, 0.36, 0.98)],
    "05L": [("bot", 0.38, 0.99, 0.36, 0.98)],
    "05R": [("top", 0.03, 0.52, 0.36, 0.98), ("bot", 0.48, 0.99, 0.36, 0.98)],
    "06L": [("top", 0.03, 0.52, 0.36, 0.98), ("bot", 0.48, 0.99, 0.36, 0.98)],
    "06R": [("top", 0.03, 0.52, 0.36, 0.98), ("bot", 0.48, 0.99, 0.36, 0.98)],
    "07L": [("bot", 0.38, 0.99, 0.36, 0.98)],
    "07R": [("top", 0.03, 0.52, 0.36, 0.98), ("bot", 0.48, 0.99, 0.36, 0.98)],
    "08L": [("bot", 0.35, 0.99, 0.36, 0.98)],
    "08R": [("top", 0.03, 0.52, 0.36, 0.98), ("bot", 0.48, 0.99, 0.36, 0.98)],
    "09L": [("bot", 0.38, 0.99, 0.36, 0.98)],
    "09R": [("bot", 0.35, 0.99, 0.36, 0.98)],
    "10L": [("top", 0.03, 0.55, 0.36, 0.98), ("bot", 0.50, 0.99, 0.36, 0.98)],
    "10R": [("bot", 0.35, 0.99, 0.40, 0.99)],
    "11L": [("top", 0.03, 0.55, 0.36, 0.98), ("bot", 0.50, 0.99, 0.36, 0.98)],
    "11R": [("bot", 0.35, 0.99, 0.40, 0.99)],
    "12L": [("top", 0.03, 0.55, 0.36, 0.98), ("bot", 0.50, 0.99, 0.36, 0.98)],
    "12R": [("top", 0.03, 0.55, 0.36, 0.98), ("bot", 0.50, 0.99, 0.36, 0.98)],
    # 第5章 工程机械: 参数多在左/中列
    "18L": [("top", 0.05, 0.50, 0.00, 0.45)],
    "18R": [("top", 0.05, 0.50, 0.35, 0.80)],
    "19L": [("top", 0.05, 0.52, 0.00, 0.45)],
    "19R": [("top", 0.05, 0.52, 0.35, 0.80)],
    "20L": [("top", 0.05, 0.50, 0.00, 0.45)],
    "20R": [("top", 0.05, 0.50, 0.35, 0.80)],
    "21L": [("top", 0.05, 0.50, 0.00, 0.45)],
    "21R": [("top", 0.05, 0.50, 0.35, 0.80)],
    "22L": [("top", 0.05, 0.48, 0.00, 0.45), ("bot", 0.50, 0.95, 0.00, 0.45)],
    "22R": [("top", 0.05, 0.50, 0.35, 0.80)],
    "23L": [("mid", 0.08, 0.80, 0.22, 0.70)],
}


def main():
    for key, zones in SPEC.items():
        page, side = key[:-1], key[-1]
        fp = os.path.join(SRC, f"fengtu_{page}.jpg")
        img = imread_u(fp)
        H, W = img.shape[:2]
        half = W // 2
        x_off = 0 if side == "L" else half
        for tag, y0, y1, fx0, fx1 in zones:
            crop = img[int(H * y0):int(H * y1),
                       x_off + int(half * fx0):x_off + int(half * fx1)]
            out = os.path.join(OUT, f"p{page}-{side}-{tag}.jpg")
            cv2.imencode(".jpg", crop, [cv2.IMWRITE_JPEG_QUALITY, 90])[1].tofile(out)
            print(os.path.basename(out), crop.shape[1], "x", crop.shape[0])


if __name__ == "__main__":
    main()
