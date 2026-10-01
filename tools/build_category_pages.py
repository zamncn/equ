# -*- coding: utf-8 -*-
"""
为每个产品分类生成独立页面(以 equipment.html 为模板):
  dump-trucks.html / tractor-trucks.html / special-trucks.html
  semi-trailers.html / construction-machinery.html
页内按子类型分组(带 id 锚点), 供导航 mega menu 直接跳转到具体机型。
数据源: work/products_real.json
"""
import os
import json
import re
from build_site_products import (ROOT, WORK, CAT_ORDER, CAT_PAGES, GROUPS,
                                 group_id, product_card, product_href, _esc)

TEMPLATE = os.path.join(ROOT, "equipment.html")


def build():
    products = json.load(open(os.path.join(WORK, "products_real.json"), encoding="utf-8"))
    by_id = {p["id"]: p for p in products}
    tmpl = open(TEMPLATE, encoding="utf-8").read()
    made = []
    for cat in CAT_ORDER:
        fname, title_en, title_zh, intro_en, intro_zh = CAT_PAGES[cat]
        text = tmpl
        # 标题
        text = re.sub(r"<title>.*?</title>", f"<title>{title_en} - EquipSupply</title>", text, count=1)
        # 面包屑标题
        text = re.sub(
            r'<h2 class="breadcrumbs-custom-title">.*?</h2>',
            f'<h2 class="breadcrumbs-custom-title"><span data-zh="{title_zh}">{title_en}</span></h2>',
            text, count=1, flags=re.S)
        # 面包屑路径: Home / Products / 当前分类
        text = re.sub(
            r'<li><a href="index\.html">Home</a></li>\s*<li class="active">.*?</li>',
            '<li><a href="index.html">Home</a></li>\n'
            '                  <li><a href="equipment.html">Products</a></li>\n'
            f'                  <li class="active"><span data-zh="{title_zh}">{title_en}</span></li>',
            text, count=1, flags=re.S)
        # 简介 + 分组
        blocks = [f'''          <p class="text-opacity-80" data-zh="{_esc(intro_zh)}">{_esc(intro_en)}</p>''']
        for gen, gzh, ids in GROUPS[cat]:
            items = [by_id[i] for i in ids if i in by_id]
            cards = "\n".join(product_card(p, href=product_href(p)) for p in items)
            blocks.append(
                f'''              <h3 class="title-decorate" id="{group_id(gen)}"><span data-zh="{gzh}">{gen}</span></h3>
              <div class="row row-15 row-gutters-14 products-grid">
{cards}
              </div>''')
        body = "\n".join(blocks)
        inner = f'''
      <section class="section-lg section bg-gray-1">
        <div class="container">
{body}
        </div>
      </section>
      '''
        # 幂等替换产品区块
        sentinel = '      <!-- PRODUCTS-CATALOG:start -->'
        if sentinel in text:
            i = text.index(sentinel)
            j = text.index('      <!-- Page Footer-->', i)
            text = text[:i] + sentinel + inner + text[j:]
        else:
            start = '      <section class="section-lg section bg-gray-1">'
            i = text.index(start)
            j = text.index('      <!-- Page Footer-->', i)
            text = text[:i] + sentinel + inner + text[j:]
        out = os.path.join(ROOT, fname)
        open(out, "w", encoding="utf-8", newline="\n").write(text)
        made.append(fname)
        print("ok", fname, "groups:", len(GROUPS[cat]))
    return made


if __name__ == "__main__":
    build()
