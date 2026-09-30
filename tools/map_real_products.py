#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把 52 款真实产品映射到画册主图裁片, 生成 work/products_real.json"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, "work")

manifest = json.load(open(os.path.join(WORK, "manifest.json"), encoding="utf-8"))
trans = json.load(open(os.path.join(WORK, "products_transcribe.json"), encoding="utf-8"))

# 按半页分组: "02R" -> [pid...]
halves = {}
for pid, info in trans.items():
    if not re.match(r"^[1-5]-\d\d$", pid):
        continue
    halves.setdefault(info["page"], []).append(pid)

def main_crops(half):
    pg = half[:-1]
    out = []
    for it in manifest.get(pg, []):
        cid = it.get("id", "")
        if not cid.startswith(half + "-"):
            continue
        if it.get("dup") or "file" not in it:
            continue
        if 1250 <= it["w"] <= 1600:          # 主图宽约1430
            out.append(it)
    out.sort(key=lambda it: it["box"][1])     # 按y从上到下
    return out

mapping, problems = {}, []
for half, pids in halves.items():
    crops = main_crops(half)
    pids.sort()
    if len(crops) < len(pids):
        problems.append((half, len(pids), len(crops)))
    for i, pid in enumerate(pids):
        if i < len(crops):
            mapping[pid] = {"crop": crops[i]["id"], "w": crops[i]["w"], "h": crops[i]["h"]}
        else:
            problems.append((pid, "NO-CROP"))

json.dump(mapping, open(os.path.join(WORK, "products_real_map.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("mapped:", len(mapping))
print("problems:", problems)
for pid in sorted(mapping):
    print(pid, "->", mapping[pid]["crop"], mapping[pid]["w"], "x", mapping[pid]["h"])
