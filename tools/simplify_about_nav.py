# -*- coding: utf-8 -*-
"""
导航"关于我们"入口只保留一个: 去掉 About Us 下拉(About Us / Our Team 两项),
改为单个 about-us.html 链接。幂等, 可重复跑。
"""
import os
import re
import glob

ROOT = r"C:/Project/Workbuddy/equ-us-ci"

PAT = re.compile(
    r'<li class="rd-nav-item[^"]*"><a class="rd-nav-link" href="about-us\.html">About Us</a>\s*'
    r'<ul class="rd-menu rd-navbar-dropdown">.*?</ul>\s*'
    r'</li>',
    re.S)
NEW = '<li class="rd-nav-item"><a class="rd-nav-link" href="about-us.html">About Us</a></li>'


def main():
    changed = 0
    for fp in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
        text = open(fp, encoding="utf-8").read()
        new, n = PAT.subn(NEW, text)
        if n:
            open(fp, "w", encoding="utf-8", newline="\n").write(new)
            changed += 1
            print("ok  ", os.path.basename(fp))
    print("changed:", changed)
    # 残留检查
    left = []
    for fp in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
        t = open(fp, encoding="utf-8").read()
        if 'href="about-us.html#team"' in t:
            left.append(os.path.basename(fp))
    print("leftover #team nav links:", left)


if __name__ == "__main__":
    main()
