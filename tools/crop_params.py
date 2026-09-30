# -*- coding: utf-8 -*-
"""从画册跨页裁出产品参数表区域(原生分辨率)，用于精确转录校验。
每页 side 的参数列约在 x [1380, 3260]（页内坐标），按产品块 y 范围裁剪。
用法: python crop_params.py <page> <L|R> <top|bottom|full>
"""
import sys, os, json
import numpy as np
import cv2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "产品资料")
OUT = os.path.join(ROOT, "work", "verify")
os.makedirs(OUT, exist_ok=True)


def imread_u(path):
    return cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)


def main():
    page, side, block = sys.argv[1], sys.argv[2].upper(), sys.argv[3]
    fp = os.path.join(SRC, f"fengtu_{page}.jpg")
    img = imread_u(fp)
    H, W = img.shape[:2]
    half = W // 2
    x0 = 0 if side == "L" else half
    side_w = half
    # 参数列横向范围: 页 side 内 x 40%..97%
    cx0 = x0 + int(side_w * 0.40)
    cx1 = x0 + int(side_w * 0.97)
    if block == "full":
        cy0, cy1 = 0, H
        tag = "full"
    elif block == "top":
        cy0, cy1 = 0, int(H * 0.52)
        tag = "top"
    else:
        cy0, cy1 = int(H * 0.50), H
        tag = "bot"
    crop = img[cy0:cy1, cx0:cx1]
    out = os.path.join(OUT, f"p{page}-{side}-{tag}.jpg")
    cv2.imencode(".jpg", crop, [cv2.IMWRITE_JPEG_QUALITY, 90])[1].tofile(out)
    print(out, crop.shape[1], "x", crop.shape[0])


if __name__ == "__main__":
    main()
