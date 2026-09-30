# -*- coding: utf-8 -*-
"""
产品画册跨页拆分 + 产品照片自动定位裁剪
输入: 产品资料/fengtu_*.jpg  (6889x4675 左右跨页)
输出:
  work/pages/     左右拆分页预览(760px, 带定位框)  —— 仅供人工核对
  work/crops/     裁出的产品照片(全分辨率 JPEG q88)
  work/sheets/    裁剪结果拼贴校验图
  work/manifest.json  裁剪清单(页码/坐标/尺寸/哈希)
"""
import os
import re
import glob
import json
import cv2
import numpy as np

SRC_DIR = r"C:/Project/Workbuddy/equ-us-ci/产品资料"
WORK = r"C:/Project/Workbuddy/equ-us-ci/work"
PAGES_DIR = os.path.join(WORK, "pages")
CROPS_DIR = os.path.join(WORK, "crops")
SHEETS_DIR = os.path.join(WORK, "sheets")
for d in (PAGES_DIR, CROPS_DIR, SHEETS_DIR):
    os.makedirs(d, exist_ok=True)

MIN_AREA_RATIO = 0.020   # 产品照片最小面积(占页比例)
MAX_AREA_RATIO = 0.55
MIN_SIDE = 380           # 全分辨率下最小边长(px)
ASPECT_LO, ASPECT_HI = 0.32, 3.4
FILL_MIN = 0.55          # 轮廓面积/外接矩形面积
TOP_EXCLUDE = 0.04       # 顶部4%内的框视为页眉装饰
HASH_SIZE = 16
DUP_HAMMING = 6


def imread_u(path):
    """支持中文路径的 imread"""
    data = np.fromfile(path, dtype=np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


def imwrite_u(path, img, params=None):
    """支持中文路径的 imwrite"""
    ext = os.path.splitext(path)[1]
    ok, buf = cv2.imencode(ext, img, params or [])
    if ok:
        buf.tofile(path)
    return ok


def find_gutter(img):
    """在中央区域找最白的一列带作为跨页中缝, 返回分割x坐标"""
    h, w = img.shape[:2]
    gray = img.min(axis=2)  # 三通道最小值, 接近白则高
    band0, band1 = int(w * 0.44), int(w * 0.56)
    col_white = (gray[:, band0:band1] > 238).mean(axis=0)
    best = int(np.argmax(col_white))
    if col_white[best] < 0.45:
        return w // 2
    return band0 + best


def detect_boxes(page):
    """在单页上定位产品照片矩形框, 返回按阅读顺序排序的 (x,y,w,h) 列表"""
    ph, pw = page.shape[:2]
    fg = (page.min(axis=2) < 232).astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (13, 13))
    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, kernel)
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, kernel)
    cnts, _ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []
    page_area = ph * pw
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        area = w * h
        if area < MIN_AREA_RATIO * page_area or area > MAX_AREA_RATIO * page_area:
            continue
        if min(w, h) < MIN_SIDE:
            continue
        aspect = w / float(h)
        if aspect < ASPECT_LO or aspect > ASPECT_HI:
            continue
        if cv2.contourArea(c) / float(area) < FILL_MIN:
            continue
        if y < TOP_EXCLUDE * ph:  # 页眉横幅
            continue
        boxes.append((x, y, w, h))
    boxes.sort(key=lambda b: (b[1] // (ph // 4), b[0]))
    return boxes


def ahash(img, size=HASH_SIZE):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    g = cv2.resize(g, (size, size))
    return (g > g.mean()).flatten()


def main():
    files = sorted(glob.glob(os.path.join(SRC_DIR, "fengtu_*.jpg")))
    manifest = {}
    seen = []  # 已收录的hash, 用于去重
    crop_id = 0

    for fp in files:
        num = re.search(r"fengtu_(\d+)", fp).group(1)
        img = imread_u(fp)
        if img is None:
            print("READ FAIL", fp)
            continue
        gx = find_gutter(img)
        halves = {"L": img[:, :gx], "R": img[:, gx:]}
        manifest[num] = []
        for side, page in halves.items():
            ph, pw = page.shape[:2]
            boxes = detect_boxes(page)
            # 预览图(带框)
            prev = cv2.resize(page, (760, int(ph * 760 / pw)))
            scale = 760 / pw
            for i, (x, y, w, h) in enumerate(boxes, 1):
                ptx, pty, ptw, pth = int(x * scale), int(y * scale), int(w * scale), int(h * scale)
                cv2.rectangle(prev, (ptx, pty), (ptx + ptw, pty + pth), (0, 0, 255), 3)
                cv2.putText(prev, f"{num}{side}-{i:02d}", (ptx + 4, pty + 34),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
            imwrite_u(os.path.join(PAGES_DIR, f"p{num}-{side}.jpg"), prev,
                      [cv2.IMWRITE_JPEG_QUALITY, 85])
            # 裁剪 + 去重
            for i, (x, y, w, h) in enumerate(boxes, 1):
                crop = page[y:y + h, x:x + w]
                hv = ahash(crop)
                is_dup = any(int(np.count_nonzero(hv != s)) <= DUP_HAMMING for s in seen)
                crop_id += 1
                cid = f"{num}{side}-{i:02d}"
                item = {"id": cid, "box": [int(x), int(y), int(w), int(h)],
                        "w": int(w), "h": int(h), "dup": False}
                if is_dup:
                    item["dup"] = True
                else:
                    seen.append(hv)
                    out = os.path.join(CROPS_DIR, f"{cid}.jpg")
                    imwrite_u(out, crop, [cv2.IMWRITE_JPEG_QUALITY, 88])
                    item["file"] = f"crops/{cid}.jpg"
                manifest[num].append(item)
        print(f"fengtu_{num}: gutter_x={gx}, crops={len(manifest[num])}")

    with open(os.path.join(WORK, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)

    # 拼贴校验图: 每张 4列x3行, 缩略图300px
    crops = []
    for num in manifest:
        for it in manifest[num]:
            if it.get("file"):
                crops.append(it)
    print("total unique crops:", len(crops))
    TH = 300
    COLS, ROWS = 4, 3
    per = COLS * ROWS
    for si in range(0, len(crops), per):
        batch = crops[si:si + per]
        rows = []
        for ri in range(0, len(batch), COLS):
            row_items = batch[ri:ri + COLS]
            cells = []
            for it in row_items:
                im = imread_u(os.path.join(WORK, it["file"]))
                h0, w0 = im.shape[:2]
                s = min(TH / float(w0), TH / float(h0))
                im = cv2.resize(im, (max(1, int(w0 * s)), max(1, int(h0 * s))))
                cv2.putText(im, it["id"], (6, 30), cv2.FONT_HERSHEY_SIMPLEX,
                            0.9, (0, 0, 255), 2)
                canvas = np.full((TH + 8, TH + 8, 3), 255, np.uint8)
                oy = (TH + 8 - im.shape[0]) // 2
                ox = (TH + 8 - im.shape[1]) // 2
                canvas[oy:oy + im.shape[0], ox:ox + im.shape[1]] = im
                cells.append(canvas)
            while len(cells) < COLS:
                cells.append(np.full((TH + 8, TH + 8, 3), 255, np.uint8))
            rows.append(np.hstack(cells))
        while len(rows) < ROWS:
            rows.append(np.full((TH + 8, (TH + 8) * COLS, 3), 255, np.uint8))
        sheet = np.vstack(rows)
        snum = si // per + 1
        imwrite_u(os.path.join(SHEETS_DIR, f"sheet-{snum:02d}.jpg"), sheet,
                  [cv2.IMWRITE_JPEG_QUALITY, 85])
        print("sheet", snum, sheet.shape)

    dups = sum(1 for num in manifest for it in manifest[num] if it["dup"])
    print("dup skipped:", dups)


if __name__ == "__main__":
    main()
