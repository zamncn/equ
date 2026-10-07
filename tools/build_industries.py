# -*- coding: utf-8 -*-
"""
生成行业领域页(industries.html)的行业模块区块。

把「行业领域」分类下的模块与产品分类关联:
- 每个行业模块(box-product 卡片)的 href 指向其关联的产品分类页(主分类);
- 卡片上的 "N models" 由关联分类的真实产品数实时统计, 不再是模板假数字;
- 支持一个行业关联多个分类(如 Mining = 自卸车 + 工程机械), 模型数取并集计数。

数据来源:
  work/products_real.json        产品数据(用于统计每个分类的产品数)
  build_site_products.INDUSTRIES 行业配置(名称/图片/关联分类)

模板化 / 数据驱动(与分类页一致):
- 增改行业: 编辑 tools/build_site_products.py 的 INDUSTRIES, 重跑本脚本即更新。
- industries.html 中由 sentinel 注释包裹的区块会被本脚本重写(幂等):
      <!-- INDUSTRIES-GRID:start -->  ...  <!-- INDUSTRIES-GRID:end -->

运行:
    python tools/build_industries.py
"""
import os
import json
import re

from build_site_products import (ROOT, WORK, CAT_PAGES, INDUSTRIES,
                                 product_href, _esc)

PAGE = os.path.join(ROOT, "industries.html")
SENTINEL_START = "<!-- INDUSTRIES-GRID:start -->"
SENTINEL_END = "<!-- INDUSTRIES-GRID:end -->"


def industry_card(name_en, name_zh, img, cats, count):
    """单个行业卡片。href 指向主分类页; 无关联分类时指向全部产品目录。"""
    primary = cats[0] if cats else None
    href = CAT_PAGES[primary][0] if primary and primary in CAT_PAGES else "equipment.html"
    cat_zh = "、".join(CAT_PAGES[c][2] for c in cats if c in CAT_PAGES)
    models_en = f"{count} models"
    return f'''            <div class="col-md-6 col-lg-4 wow fadeInUp"><a class="box-product" href="{href}">
                <div class="box-product-figure"><img src="{img}" alt="{_esc(name_en)}" width="379" height="291"/>
                </div>
                <div class="box-product-caption">
                  <h4 class="box-product-title">{_esc(name_en)}</h4>
                  <p>{models_en}</p>
                  <div class="box-product-divider"></div>
                </div></a>
            </div>'''


def render_grid(by_cat):
    """生成整个 INDUSTRIES-GRID 区块内容(含 sentinel)。"""
    cards = []
    for name_en, name_zh, img, cats in INDUSTRIES:
        # 关联分类的产品数(并集: 同一产品不会跨分类, 直接求和即可)
        count = sum(len(by_cat.get(c, [])) for c in cats)
        cards.append(industry_card(name_en, name_zh, img, cats, count))
    inner = "\n".join(cards)
    return (f'{SENTINEL_START}\n'
            f'          <div class="row row-15 row-gutters-14 industries-grid">\n'
            f'{inner}\n'
            f'          </div>\n'
            f'          {SENTINEL_END}')


def build():
    products = json.load(open(os.path.join(WORK, "products_real.json"), encoding="utf-8"))
    by_cat = {}
    for p in products:
        by_cat.setdefault(p["cat_en"], []).append(p)

    html = open(PAGE, encoding="utf-8").read()
    grid = render_grid(by_cat)

    i = html.find(SENTINEL_START)
    j = html.find(SENTINEL_END)
    if i < 0 or j < 0:
        raise RuntimeError(
            f"未找到注入区 sentinel, 请先在 industries.html 的行业 section 中加入:\n"
            f"  {SENTINEL_START} ... {SENTINEL_END}")
    j += len(SENTINEL_END)
    new_html = html[:i] + grid + html[j:]

    with open(PAGE, "w", encoding="utf-8") as f:
        f.write(new_html)

    print(f"已更新 {os.path.relpath(PAGE, ROOT)}: {len(INDUSTRIES)} 个行业模块")
    for name_en, name_zh, img, cats in INDUSTRIES:
        count = sum(len(by_cat.get(c, [])) for c in cats)
        print(f"  {name_en:16} -> {cats}  ({count} models)")


if __name__ == "__main__":
    build()
