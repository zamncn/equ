# -*- coding: utf-8 -*-
"""Sync brand rename into js/i18n.js dictionary (keys + ZH values + header)."""
import os

F = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "js", "i18n.js")
t = open(F, encoding="utf-8").read()
orig = t

# header comment
t = t.replace("static Digger template", "static FENG TU site")

out = []
for line in t.split("\n"):
    if "Digger" in line and ("': " in line):
        # split key/value on the dict delimiter ': '
        idx = line.index("': ")
        key, val = line[:idx], line[idx:]
        key = key.replace("Digger ", "FENG TU ")
        val = val.replace("Digger ", "丰途 ")
        line = key + val
    elif "Digger" in line:
        line = line.replace("Digger", "FENG TU")
    out.append(line)

t = "\n".join(out)
if t != orig:
    open(F, "w", encoding="utf-8").write(t)
    print("i18n.js updated")
else:
    print("i18n.js unchanged")
