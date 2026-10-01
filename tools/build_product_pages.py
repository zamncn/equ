# -*- coding: utf-8 -*-
"""
为每个真实产品生成独立详情页: products/p{id}.html
模板: product-page.html
数据源: work/products_real.json

== 模板化 / 可扩展说明 ==
- 产品来自 work/products_real.json(由 build_site_products.load_products() 从画册转录生成)。
- 新增产品: 在 products_real.json 增加条目(或改 products_transcribe.json 后重跑 load_products), 再跑本脚本即可。
- 新增分类: 在 build_site_products.py 的 CAT_ORDER / CAT_PAGES / GROUPS 增加配置, 本脚本与
  build_category_pages.py 会自动覆盖。
- 产品介绍(desc): 若 products_real.json 中 desc_en/desc_zh 有内容则直接用; 否则由"型号 + 分类 + 关键参数"
  自动生成中英双语文本(可后续人工润色覆盖)。
- 详情页放在 products/ 子目录, 所有 css/js/images/页面链接均加 ../ 前缀, 相对路径正确。
"""
import os
import re
import json
from build_site_products import ROOT, CAT_PAGES, product_href, _esc

TPL = os.path.join(ROOT, "product-page.html")
SRC = os.path.join(ROOT, "work", "products_real.json")
OUTDIR = os.path.join(ROOT, "products")
os.makedirs(OUTDIR, exist_ok=True)

# 各分类的典型使用场景(用于自动生成简介)
USE_CASE = {
    "Dump Truck": (
        "Built for mining, quarry and earthmoving duty where high payload and ruggedness matter.",
        "面向矿山、采石场与土方工程，强调高载重量与耐用性。"),
    "Tractor Truck": (
        "Developed for long-haul and regional freight, balancing power, fuel economy and cab comfort.",
        "面向长途与区域货运，兼顾动力、油耗与驾驶室舒适性。"),
    "Special Truck": (
        "Configured for specialized municipal and jobsite tasks with purpose-built upper equipment.",
        "针对市政与作业现场专用任务，配备专用上装。"),
    "Semi-Trailer": (
        "Engineered to couple with prime movers across logistics, bulk-haul and specialized transport.",
        "与牵引车配套，覆盖物流、散货与特种运输场景。"),
    "Construction Machinery": (
        "Suited to excavation, lifting, compaction and general construction site works.",
        "适用于挖掘、起重、压实及各类土石方与基建作业。"),
    "Agriculture Machinery": (
        "Developed for plowing, planting, harvesting and farm transport operations.",
        "适用于耕整、播种、收割与农用运输等作业。"),
}


def first_token(name):
    parts = name.split()
    return parts[0] if parts else ""


def gen_desc(p):
    """优先用数据自带 desc; 否则按规格自动生成中英双语简介。"""
    de = (p.get("desc_en") or "").strip()
    dz = (p.get("desc_zh") or "").strip()
    if de and dz:
        return de, dz
    uc_en, uc_zh = USE_CASE.get(
        p["cat_en"], ("A dependable machine for professional use.",
                      "面向专业作业场景的可靠设备。"))
    brand = first_token(p["name_en"])
    specs = p.get("specs", [])[:3]

    def fmt(s):
        return f"{s['k']} {s['v']}"

    if len(specs) == 1:
        spec_en = fmt(specs[0])
        spec_zh = f"{specs[0]['k_zh']} {specs[0]['v']}"
    elif len(specs) == 2:
        spec_en = f"{fmt(specs[0])} and {fmt(specs[1])}"
        spec_zh = f"{specs[0]['k_zh']} {specs[0]['v']}、{specs[1]['k_zh']} {specs[1]['v']}"
    elif len(specs) >= 3:
        spec_en = f"{fmt(specs[0])}, {fmt(specs[1])} and {fmt(specs[2])}"
        spec_zh = (f"{specs[0]['k_zh']} {specs[0]['v']}、"
                   f"{specs[1]['k_zh']} {specs[1]['v']}、"
                   f"{specs[2]['k_zh']} {specs[2]['v']}")
    else:
        spec_en = "key specifications listed below"
        spec_zh = "详细参数见下表"
    brand_suffix = f" built on a {brand} chassis" if brand else ""
    en = (f"The {p['name_en']} is a {p['cat_en'].lower()} from EquipSupply{brand_suffix}. "
          f"{uc_en} It is specified with {spec_en}, giving operators dependable "
          f"performance for demanding jobs.")
    zh = (f"{p['name_zh']} 是 EquipSupply 旗下{p['cat_zh']}。{uc_zh}"
          f"其主要参数包括{spec_zh}，为高强度作业提供可靠表现。")
    return en, zh


def build_section(p, cat_page, desc_en, desc_zh):
    w, h = p["w"], p["h"]
    top = p.get("specs", [])[:4]
    lis = "\n".join(
        '                  <li><dl class="list-terms-inline">'
        f'<dt data-zh="{_esc(s["k_zh"])}">{_esc(s["k"])}</dt>'
        f'<dd>{_esc(s["v"])}</dd></dl></li>'
        for s in top)
    rows = "\n".join(
        f'                    <tr><td data-zh="{_esc(s["k_zh"])}">{_esc(s["k"])}</td>'
        f'<td>{_esc(s["v"])}</td></tr>'
        for s in p.get("specs", []))
    return f'''      <section class="section section-xl bg-default">
        <div class="container">
          <div class="row row-50">
            <div class="col-lg-6">
              <div class="product-item-info">
                <div class="product-item-info-name">
                  <h3><span data-zh="{_esc(p['name_zh'])}">{_esc(p['name_en'])}</span></h3>
                </div>
                <p class="product-cat text-primary" data-zh="{_esc(p['cat_zh'])}">{_esc(p['cat_en'])}</p>
                <ul class="team-info-list">
{lis}
                </ul>
                <p data-zh="{_esc(desc_zh)}">{_esc(desc_en)}</p>
                <a class="button button-primary button-lg" href="../contacts.html" data-zh="获取报价">Request a Quote</a>
                <a class="button button-secondary button-lg" href="../{cat_page}" data-zh="返回分类">Back to {p['cat_en']}</a>
              </div>
            </div>
            <div class="col-lg-6"><img class="img-responsive" src="../{p['large']}" alt="{_esc(p['name_en'])}" width="{w}" height="{h}"/></div>
          </div>
          <div class="row row-50">
            <div class="col-12">
              <h4 data-zh="技术参数">Specifications</h4>
              <table class="table table-custom product-spec-table">
                <tbody>
{rows}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>'''


def prefix_assets(text):
    reps = [
        ('href="css/', 'href="../css/'),
        ('href="js/', 'href="../js/'),
        ('src="css/', 'src="../css/'),
        ('src="js/', 'src="../js/'),
        ('src="images/', 'src="../images/'),
        ('href="images/', 'href="../images/'),
        ('srcset="images/', 'srcset="../images/'),
        ('data-parallax-img="images/', 'data-parallax-img="../images/'),
    ]
    for a, b in reps:
        text = text.replace(a, b)
    # 页面间链接(其它 .html)加 ../
    text = re.sub(r'href="([A-Za-z0-9_-]+\.html)"', r'href="../\1"', text)
    return text


def build():
    products = json.load(open(SRC, encoding="utf-8"))
    tmpl = open(TPL, encoding="utf-8").read()
    made = []
    for p in products:
        cat_page = CAT_PAGES[p["cat_en"]][0]
        de, dz = gen_desc(p)
        text = tmpl
        text = re.sub(r'<title>.*?</title>',
                      f'<title>{_esc(p["name_en"])} - EquipSupply</title>', text, count=1)
        meta = f'    <meta name="description" content="{_esc(de[:160])}" data-zh="{_esc(dz[:110])}">'
        text = text.replace('</title>', '</title>\n' + meta, 1)
        text = text.replace(
            '<h2 class="breadcrumbs-custom-title">Product Page</h2>',
            f'<h2 class="breadcrumbs-custom-title"><span data-zh="{_esc(p["name_zh"])}">{_esc(p["name_en"])}</span></h2>')
        text = re.sub(
            r'<ul class="breadcrumbs-custom-path">.*?</ul>',
            f'''<ul class="breadcrumbs-custom-path">
              <li><a href="../index.html">Home</a></li>
              <li><a href="../equipment.html">Products</a></li>
              <li><a href="../{cat_page}" data-zh="{_esc(p["cat_zh"])}">{_esc(p["cat_en"])}</a></li>
              <li class="active"><span data-zh="{_esc(p["name_zh"])}">{_esc(p["name_en"])}</span></li>
            </ul>''',
            text, count=1, flags=re.S)
        sec = build_section(p, cat_page, de, dz)
        start = text.index('<section class="section section-xl bg-default">')
        end = text.index('</section>', start) + len('</section>')
        text = text[:start] + sec + text[end:]
        text = prefix_assets(text)
        out = os.path.join(OUTDIR, f"p{p['id']}.html")
        open(out, "w", encoding="utf-8", newline="\n").write(text)
        made.append(out)
    return made


if __name__ == "__main__":
    made = build()
    print(len(made), "product pages written into", OUTDIR)
