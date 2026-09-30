# -*- coding: utf-8 -*-
"""裁每页 side 的标题带(编号徽章+产品名)，用于确认产品编号与名称。
x: side 内 0..60%, y: 8%..30%
用法: python crop_titles.py   (无参数，批量生成)
"""
import os
import numpy as np
import cv2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "产品资料")
OUT = os.path.join(ROOT, "work", "verify")
os.makedirs(OUT, exist_ok=True)

PAGES = ["03", "04", "05", "06", "07", "08", "09",
         "10", "11", "12", "18", "19", "20", "21", "22", "23"]


def imread_u(path):
    return cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)


def main():
    for page in PAGES:
        fp = os.path.join(SRC, f"fengtu_{page}.jpg")
        if not os.path.exists(fp):
            print("missing", fp)
            continue
        img = imread_u(fp)
        H, W = img.shape[:2]
        half = W // 2
        for side in ("L", "R"):
            x0 = 0 if side == "L" else half
            cx0 = x0
            cx1 = x0 + int(half * 0.60)
            cy0, cy1 = int(H * 0.08), int(H * 0.32)
            crop = img[cy0:cy1, cx0:cx1]
            out = os.path.join(OUT, f"p{page}-{side}-title.jpg")
            cv2.imencode(".jpg", crop, [cv2.IMWRITE_JPEG_QUALITY, 90])[1].tofile(out)
            print(os.path.basename(out), crop.shape[1], "x", crop.shape[0])


if __name__ == "__main__":
    main()
