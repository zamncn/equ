# -*- coding: utf-8 -*-
import os
F = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "css", "style.css")
s = open(F, encoding="utf-8").read()
rule = (
    "\n.brand-wordmark{display:inline-block;"
    "font-family:\"Roboto Condensed\",-apple-system,BlinkMacSystemFont,\"Segoe UI\",Roboto,\"Helvetica Neue\",Arial,sans-serif;"
    "font-size:28px;font-weight:700;line-height:35px;letter-spacing:1px;"
    "text-transform:uppercase;color:#ffd541;}\n"
    ".rd-navbar-fixed .brand-wordmark{font-size:24px;line-height:56px;}\n"
)
if ".brand-wordmark" not in s:
    open(F, "w", encoding="utf-8").write(s.rstrip("\n") + rule)
    print("appended brand-wordmark rule")
else:
    print("already present")
