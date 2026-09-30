# -*- coding: utf-8 -*-
"""导航结构严格校验: ul/li 标签是否配对平衡, 是否有重复菜单残留"""
import os
import re
import glob

ROOT = r"C:/Project/Workbuddy/equ-us-ci"
PAT_TAG = re.compile(r"<(/?)(ul|li)\b[^>]*>")
# 巨幕菜单列数（Heavy Trucks / Semi-Trailers / Construction Machinery / Agriculture Machinery）
EXPECTED_COLS = 4


def check(html):
    """返回 (ok, detail)"""
    depth = {"ul": 0, "li": 0}
    stack = []
    for m in PAT_TAG.finditer(html):
        closing, tag = m.group(1), m.group(2)
        if closing:
            depth[tag] -= 1
            if depth[tag] < 0:
                return False, f"extra </{tag}> at {m.start()}"
        else:
            depth[tag] += 1
    bad = {k: v for k, v in depth.items() if v != 0}
    return (not bad), (bad or "balanced")


def main():
    allok = True
    for fp in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
        text = open(fp, encoding="utf-8").read()
        i = text.find('<ul class="rd-navbar-nav">')
        if i < 0:
            continue
        j = text.find("<!-- Swiper-->", i)
        j = j if j > 0 else text.find("</header>", i)
        nav = text[i:j]
        ok, detail = check(nav)
        # mega 菜单项数: 应为 4 列(Heavy Trucks/Semi-Trailers/Construction/Agriculture); 残留会出现 >4
        items = nav.count('class="rd-megamenu-item"')
        dup = items != EXPECTED_COLS or nav.count('class="rd-menu rd-navbar-megamenu"') != 1
        if not ok or dup:
            allok = False
        print(f"{'OK  ' if ok and not dup else 'FAIL'} {os.path.basename(fp):30s} {detail} itemCols={items}")
    print("\n✅ 全部导航结构正常" if allok else "\n❌ 仍有问题")


if __name__ == "__main__":
    main()
