#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Rebrand FENG TU -> EquipSupply across the static site + attach new favicons."""
import os, re, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NAVBAR_OLD = '<div class="rd-navbar-brand"><a href="index.html" class="brand-wordmark">FENG TU</a></div>'
NAVBAR_NEW = (
    '<div class="rd-navbar-brand"><a href="index.html" class="brand-logo">'
    '<img src="images/logo-inverse-160x35.png" alt="EquipSupply" width="160" height="35" '
    'srcset="images/logo-inverse-320x70.png 2x"></a></div>'
)

FAV_RE = re.compile(r'<link rel="icon" href="images/favicon\.ico"[^>]*>')
FAV_NEW = (
    '<link rel="icon" href="images/favicon.ico" sizes="any">\n'
    '    <link rel="icon" type="image/png" sizes="32x32" href="images/favicon-32.png">\n'
    '    <link rel="icon" type="image/png" sizes="16x16" href="images/favicon-16.png">\n'
    '    <link rel="apple-touch-icon" href="images/apple-touch-icon.png">'
)


def process(path, is_html):
    with open(path, "rb") as fh:
        s = fh.read().decode("utf-8")
    orig = s
    if is_html:
        s = s.replace(NAVBAR_OLD, NAVBAR_NEW)
        s = FAV_RE.sub(FAV_NEW, s)
    s = s.replace("FENG TU", "EquipSupply").replace("丰途", "EquipSupply")
    s = s.replace("欢迎来到EquipSupply", "欢迎来到 EquipSupply")
    if s != orig:
        with open(path, "wb") as fh:
            fh.write(s.encode("utf-8"))
        return True
    return False


def main():
    changed = []
    for p in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
        if process(p, True):
            changed.append(os.path.basename(p))
    for p in [os.path.join(ROOT, "js", "i18n.js")]:
        if process(p, False):
            changed.append("js/i18n.js")

    # css: swap the text wordmark rules for the image logo rules
    css = os.path.join(ROOT, "css", "style.css")
    with open(css, "rb") as fh:
        s = fh.read().decode("utf-8")
    old_css = (
        '.brand-wordmark{display:inline-block;font-family:"Roboto Condensed",'
        '-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;'
        'font-size:28px;font-weight:700;line-height:35px;letter-spacing:1px;'
        'text-transform:uppercase;color:#ffd541;}'
        '\n.rd-navbar-fixed .brand-wordmark{font-size:24px;line-height:56px;}'
    )
    new_css = (
        ".brand-logo{display:inline-block;line-height:0;}"
        "\n.brand-logo img{display:block;width:160px;height:auto;}"
        "\n.rd-navbar-fixed .brand-logo img{width:140px;height:auto;}"
    )
    if old_css in s:
        s = s.replace(old_css, new_css)
        with open(css, "wb") as fh:
            fh.write(s.encode("utf-8"))
        changed.append("css/style.css")
    else:
        print("WARN: brand-wordmark CSS block not found verbatim")

    print("changed files:", len(changed))
    for c in changed:
        print(" -", c)
    # sanity: nothing left behind
    left = 0
    for p in glob.glob(os.path.join(ROOT, "*.html")) + [os.path.join(ROOT, "js", "i18n.js")]:
        with open(p, "rb") as fh:
            t = fh.read().decode("utf-8")
        n = t.count("FENG TU") + t.count("丰途") + t.count("brand-wordmark")
        if n:
            print("LEFTOVER", os.path.basename(p), n)
        left += n
    print("leftover brand refs:", left)


if __name__ == "__main__":
    main()
