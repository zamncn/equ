# -*- coding: utf-8 -*-
"""
整合 about-us.html 与 our-team.html 为单一页面(历史脚本, 已完成):
- about-us.html 已含 Our Team 区块, 故以它为合并后的唯一页面(our-team.html 已删除)。
- 全站 18 个 html 导航下拉里的 "Our Team" 链接 our-team.html -> about-us.html#team。
- 给 about-us.html 的 Our Team <section> 加 id="team" 以支持锚点跳转。

后续: 用户要求"关于页面只保留一个"(导航只留一个关于入口), 由 tools/simplify_about_nav.py
把 About Us 下拉折叠成单链接 <a href="about-us.html">About Us</a>(18 页, 幂等)。
本脚本若误重跑会把下拉加回来, 需再跑 simplify_about_nav.py 修正。
- 删除冗余的 our-team.html。
- 同步更新 tools/ 下引用 our-team.html 的脚本, 保证可重跑。
幂等: 基于精确字符串替换, 重复运行安全。
"""
import os
import re

ROOT = r"C:/Project/Workbuddy/equ-us-ci"

HTML_FILES = [
    "index.html", "about-us.html", "industries.html", "equipment.html", "contacts.html",
    "news.html", "news-2.html", "blog-post.html", "gallery.html", "product-page.html",
    "privacy-policy.html", "typography.html", "buttons.html", "forms.html", "grid-system.html",
    "icon-lists.html", "timers-&-counters.html", "search-results.html",
]

OLD_LINK = 'href="our-team.html">Our Team'
NEW_LINK = 'href="about-us.html#team">Our Team'


def update_nav_links():
    for f in HTML_FILES:
        p = os.path.join(ROOT, f)
        if not os.path.exists(p):
            continue
        t = open(p, encoding="utf-8").read()
        if OLD_LINK in t:
            t = t.replace(OLD_LINK, NEW_LINK)
            open(p, "w", encoding="utf-8", newline="\n").write(t)
            print("updated nav link:", f)
        else:
            print("skip (no our-team link):", f)


def add_team_anchor():
    p = os.path.join(ROOT, "about-us.html")
    t = open(p, encoding="utf-8").read()
    pat = re.compile(
        r'(<section class="section section-lg bg-gray-1">)'
        r'(\s*<div class="container">\s*<h3 class="text-center">Our Team</h3>)', re.S)
    if 'id="team"' in t:
        print("team anchor already present, skip")
        return
    t2, n = pat.subn(r'<section class="section section-lg bg-gray-1" id="team">\2', t)
    if n == 0:
        print("!! 未找到 Our Team section, 锚点未添加")
        return
    open(p, "w", encoding="utf-8", newline="\n").write(t2)
    print("added id=\"team\" to about-us Our Team section")


def delete_our_team():
    p = os.path.join(ROOT, "our-team.html")
    if os.path.exists(p):
        os.remove(p)
        print("deleted our-team.html")
    else:
        print("our-team.html 已不存在, skip")


if __name__ == "__main__":
    update_nav_links()
    add_team_anchor()
    delete_our_team()
