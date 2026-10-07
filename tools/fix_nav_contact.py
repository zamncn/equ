# -*- coding: utf-8 -*-
"""
导航栏右上角联系方式: 电话图标 + 电话号码 -> 邮箱图标 + 邮箱地址(占位)。

只改 RD Navbar 的 list-contact-info 行(导航栏右上角), 不动 footer 里的其它 tel 链接。
幂等: 已改过的文件跳过。

原行(模板):
  <li><span class="icon mdi mdi-phone icon-sm icon-primary"></span><span class="list-item-text"><a href="tel:#">1-800-123-1234</a></span></li>
改为:
  <li><span class="icon mdi mdi-email icon-sm icon-primary"></span><span class="list-item-text"><a href="mailto:#">info@example.com</a></span></li>

邮箱地址为占位(info@example.com), 待用户提供真实邮箱后替换 MAIL_ADDR 重跑即可。

运行:
    python tools/fix_nav_contact.py
"""
import os
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 占位邮箱(用户说"先不写, 占位")。拿到真实邮箱后改这里重跑。
MAIL_ADDR = "info@example.com"

OLD = ('<li><span class="icon mdi mdi-phone icon-sm icon-primary"></span>'
       '<span class="list-item-text"><a href="tel:#">1-800-123-1234</a></span></li>')
NEW = ('<li><span class="icon mdi mdi-email icon-sm icon-primary"></span>'
       f'<span class="list-item-text"><a href="mailto:{MAIL_ADDR}">{MAIL_ADDR}</a></span></li>')


def main():
    files = sorted(glob.glob(os.path.join(ROOT, "*.html")) +
                   glob.glob(os.path.join(ROOT, "products", "*.html")))
    changed, already, none = [], [], []
    for fp in files:
        s = open(fp, encoding="utf-8").read()
        if NEW in s:
            already.append(fp)
            continue
        if OLD not in s:
            none.append(fp)
            continue
        s = s.replace(OLD, NEW)
        with open(fp, "w", encoding="utf-8") as f:
            f.write(s)
        changed.append(fp)

    rel = lambda p: os.path.relpath(p, ROOT)
    print(f"已修改: {len(changed)} 个文件")
    print(f"已是最新(跳过): {len(already)} 个")
    if none:
        print(f"未找到模板行(需人工确认): {len(none)} 个 -> {[rel(p) for p in none][:10]}")
    for p in changed[:5]:
        print("  e.g.", rel(p))


if __name__ == "__main__":
    main()
