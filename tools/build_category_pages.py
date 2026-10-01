# -*- coding: utf-8 -*-
"""
为每个产品分类生成独立页面(以 equipment.html 为模板):
  dump-trucks.html / tractor-trucks.html / special-trucks.html
  semi-trailers.html / construction-machinery.html / agriculture-machinery.html
页内按子类型分组(带 id 锚点), 供导航 mega menu 直接跳转到具体机型。
数据源: work/products_real.json

空分类/空子分组处理(用户要求"空分类关联到 404 页"):
- 某分类引用到的产品总数为 0 时, 该分类页渲染为 404 风格的 not-found 区块,
  并回链 equipment.html / index.html(与根 404.html 视觉一致)。
- 某子分组解析到的产品为 0 时, 该子分组渲染一行提示并链接到 404.html。
这样后续通过模板新增分类/子分组, 即使暂无产品也不会出现空白页。
"""
import os
import json
import re
from build_site_products import (ROOT, WORK, CAT_ORDER, CAT_PAGES, GROUPS,
                                 group_id, product_card, product_href, _esc)

TEMPLATE = os.path.join(ROOT, "equipment.html")


def not_found_block():
    """空分类时渲染的 404 风格区块(链接为根相对, 分类页位于站点根目录)。"""
    return '''      <section class="section section-xl bg-gray-700">
        <div class="container text-center">
          <div class="row justify-content-center">
            <div class="col-md-10 col-lg-8">
              <div style="font-size:120px;line-height:1;font-weight:700;color:#fff;" class="wow fadeIn">404</div>
              <h3 class="title-decorate mt-3"><span data-zh="该分类暂无产品">No products in this category yet</span></h3>
              <p class="text-opacity-80" data-zh="该分类暂时没有可展示的产品。请浏览我们的完整产品目录，或返回首页。">This category currently has no products to display. Browse our full catalog or return to the homepage.</p>
              <div class="group-md mt-4">
                <a class="button button-lg button-primary" href="equipment.html" data-zh="浏览产品">Browse Products</a>
                <a class="button button-lg button-gray-4" href="index.html" data-zh="返回首页">Back to Home</a>
              </div>
            </div>
          </div>
        </div>
      </section>
'''


def empty_group_note(gid):
    return (f'              <p class="text-opacity-80" data-zh="该子分类暂无产品，'
            f'<a href="404.html">查看其他分类</a>。">No products in this sub-category yet. '
            f'<a href="404.html">View other categories</a>.</p>')


def render_category_body(cat, products, by_id):
    """返回分类页主体( product 区块区域 ), 已含空分类/空子分组处理。"""
    intro_en, intro_zh = CAT_PAGES[cat][3], CAT_PAGES[cat][4]
    blocks = [f'''          <p class="text-opacity-80" data-zh="{_esc(intro_zh)}">{_esc(intro_en)}</p>''']
    total = 0
    for gen, gzh, ids in GROUPS[cat]:
        items = [by_id[i] for i in ids if i in by_id]
        total += len(items)
        if not items:
            # 空子分组: 仅标题 + 一行提示(链接到 404.html)
            blocks.append(
                f'''              <h3 class="title-decorate" id="{group_id(gen)}"><span data-zh="{gzh}">{gen}</span></h3>
{empty_group_note(group_id(gen))}''')
            continue
        cards = "\n".join(product_card(p, href=product_href(p)) for p in items)
        blocks.append(
            f'''              <h3 class="title-decorate" id="{group_id(gen)}"><span data-zh="{gzh}">{gen}</span></h3>
              <div class="row row-15 row-gutters-14 products-grid">
{cards}
              </div>''')
    if total == 0:
        # 整页空分类: 直接渲染 404 风格区块
        return not_found_block()
    return "\n".join(blocks)


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
        body = render_category_body(cat, products, by_id)
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
