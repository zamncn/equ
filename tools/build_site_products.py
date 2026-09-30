# -*- coding: utf-8 -*-
"""
用画册转录的真实产品(型号/参数/图片)构建网站产品数据并注入模板页面
数据源:
  work/products_transcribe.json  52个真实产品(名称/参数/文本描述)
  work/products_real_map.json    产品id -> 画册主图crop id
输出:
  images/products/p{id}-thumb.jpg(600w) / p{id}-large.jpg(1200w)
  work/products_real.json  网站用产品数据
  重写 gallery.html / equipment.html / index.html 产品区块(幂等)
"""
import os
import re
import json
from PIL import Image

ROOT = r"C:/Project/Workbuddy/equ-us-ci"
WORK = os.path.join(ROOT, "work")
OUT = os.path.join(ROOT, "images", "products")
os.makedirs(OUT, exist_ok=True)

# --- 产品id -> 分类(按画册章节) ---
CAT_BY_ID = {}
def _set_cat(prefix, en, zh):
    for i in range(1, 100):
        CAT_BY_ID[f"{prefix}-{i:02d}"] = (en, zh)

_set_cat("1", "Dump Truck", "自卸车")
_set_cat("2", "Tractor Truck", "牵引车")
_set_cat("3", "Special Truck", "专用车")
_set_cat("4", "Semi-Trailer", "半挂车")
_set_cat("5", "Construction Machinery", "工程机械")
_set_cat("6", "Agriculture Machinery", "农业机械")

CAT_ORDER = ["Dump Truck", "Tractor Truck", "Special Truck",
             "Semi-Trailer", "Construction Machinery", "Agriculture Machinery"]

# --- 分类页: cat -> (文件名, 面包屑标题en/zh, 简介en/zh) ---
CAT_PAGES = {
    "Dump Truck": ("dump-trucks.html", "Dump Trucks", "自卸车",
                   "Heavy-duty dump trucks from 6x4 to 8x4 and 6x6, powered by Sinotruk, "
                   "Shacman, Foton and FAW chassis - built for mining, quarry and earthmoving jobs.",
                   "重型自卸车涵盖 6×4、8×4 与 6×6 驱动型式，底盘来自中国重汽、陕汽、福田与一汽，"
                   "适用于矿山、采石场与土方工程作业。"),
    "Tractor Truck": ("tractor-trucks.html", "Tractor Trucks", "牵引车",
                      "4x2 and 6x4 tractor trucks for long-haul and regional transport, "
                      "with 340-560 hp engines and full air-brake trailer packages.",
                      "4×2 与 6×4 牵引车，适用于长途与区域运输，匹配 340-560 马力发动机与全套气压制动挂车接口。"),
    "Special Truck": ("special-trucks.html", "Special Trucks", "专用车",
                      "Purpose-built special trucks: concrete mixers, water and fuel tankers, "
                      "and crane trucks on reliable heavy-truck chassis.",
                      "专用作业车辆：混凝土搅拌车、洒水车、油罐车与起重车，均基于成熟重卡底盘改装。"),
    "Semi-Trailer": ("semi-trailers.html", "Semi-Trailers", "半挂车",
                     "A complete semi-trailer programme - fence, lowbed, flatbed, dump, "
                     "curtain-side, skeleton, car carrier, bulk cement and special trailers.",
                     "完整半挂车产品线 —— 仓栏、低平板、平板、自卸、侧帘、骨架、轿运、粉罐与特种半挂车。"),
    "Construction Machinery": ("construction-machinery.html", "Construction Machinery", "工程机械",
                               "Excavators, backhoe loaders, bulldozers, truck cranes, road rollers, "
                               "forklifts and concrete pump trucks from China's leading brands.",
                               "挖掘机、挖掘装载机、推土机、汽车起重机、压路机、叉车与混凝土泵车，"
                               "均来自国内一线品牌。"),
    "Agriculture Machinery": ("agriculture-machinery.html", "Agriculture Machinery", "农业机械",
                              "Agricultural tractors, combine harvesters, seeding and tillage implements, "
                              "and farm transport vehicles - matching the needs of farms, plantations "
                              "and agricultural contractors.",
                              "农业拖拉机、联合收割机、播种与耕整机具，以及农用运输车辆，"
                              "适用于农场、种植园与农业作业承包商。"),
}

# --- 分类页内的子类型分组: cat -> [(组名en, 组名zh, [产品id...])] ---
GROUPS = {
    "Dump Truck": [
        ("6x4 Dump Trucks", "6×4 自卸车", ["1-05", "1-07", "1-09", "1-11", "1-13"]),
        ("8x4 Dump Trucks", "8×4 自卸车", ["1-04", "1-06", "1-08", "1-10", "1-12", "1-14"]),
        ("6x6 Dump Trucks", "6×6 自卸车", ["1-03"]),
    ],
    "Tractor Truck": [
        ("4x2 Tractor Trucks", "4×2 牵引车", ["2-01", "2-03", "2-05", "2-07"]),
        ("6x4 Tractor Trucks", "6×4 牵引车", ["2-02", "2-04", "2-06", "2-08"]),
    ],
    "Special Truck": [
        ("Concrete Mixer Truck", "混凝土搅拌车", ["3-01", "3-02"]),
        ("Water Tank Truck", "洒水车", ["3-03", "3-04", "3-05", "3-16", "3-17"]),
        ("Fuel Tanker Truck", "油罐车", ["3-06"]),
        ("Crane Truck", "起重车", ["3-11", "3-12"]),
    ],
    "Semi-Trailer": [
        ("Fence / Flatbed / Lowbed Semi-Trailers", "仓栏 / 平板 / 低平板半挂车",
         ["4-01", "4-02", "4-03", "4-04", "4-13"]),
        ("Curtain-side / Skeleton Semi-Trailers", "侧帘 / 骨架半挂车", ["4-07", "4-08"]),
        ("Car Carrier / Bulk Cement / Special Semi-Trailers", "轿运 / 粉罐 / 特种半挂车",
         ["4-09", "4-10", "4-14"]),
    ],
    "Construction Machinery": [
        ("Excavator", "挖掘机", ["5-01", "5-03"]),
        ("Backhoe Loader", "挖掘装载机", ["5-07"]),
        ("Bulldozer", "推土机", ["5-08"]),
        ("Truck Crane", "汽车起重机", ["5-09", "5-10", "5-11"]),
        ("Road Roller", "压路机", ["5-13"]),
        ("Forklift", "叉车", ["5-16", "5-17", "5-18"]),
        ("Boom Pump Truck", "泵车", ["5-21"]),
    ],
    "Agriculture Machinery": [
        ("Tractor", "拖拉机", ["6-01", "6-02", "6-03"]),
        ("Harvester", "收割机", ["6-04", "6-05", "6-06"]),
        ("Seeding & Tillage Implements", "播种与耕整机具", ["6-07", "6-08"]),
        ("Farm Transport & Others", "农用运输及其他", ["6-09", "6-10"]),
    ],
}


def group_id(en):
    """子类型分组锚点 id"""
    return "g-" + re.sub(r"[^a-z0-9]+", "-", en.lower()).strip("-")


# 首页精选(明确产品id, 每章取代表)
HOME_IDS = ["1-03", "2-02", "3-01", "4-02", "5-03", "5-08", "5-10", "5-16"]

# 参数key -> 中文 (data-zh)
PARAM_ZH = {
    "Overall size": "整车尺寸", "Vehicle size": "整车尺寸",
    "Overall machine weight": "整机重量", "Machine weight": "整机重量",
    "Machine working weight": "整机工作重量", "Operating weight": "工作重量",
    "Working weight": "工作重量", "Weight": "整机重量",
    "Engine": "发动机", "Engine type": "发动机型号", "Engine power": "发动机功率",
    "The engine power": "发动机功率", "Horsepower": "马力",
    "Transmission": "变速箱", "Tire": "轮胎", "Cab": "驾驶室",
    "Rear axle": "后桥", "Axle": "轴数", "Wheelbase": "轴距",
    "Cargo box type": "货箱型式", "Cargo box size": "货箱尺寸",
    "Dumper box size": "货箱尺寸", "Loading capacity": "载重能力",
    "Traction capacity": "牵引总重", "Gross vehicle weight": "整车总质量",
    "Oil tank": "油箱容量", "Tank size": "罐体尺寸",
    "Water tank volume": "水罐容积", "Lifting weight": "起重量",
    "Max lifting moment": "最大起重力矩", "Max lifting capacity": "最大起重量",
    "Rotation angle": "回转角度", "Standard bucket capacity": "标准斗容量",
    "Bucket capacity": "铲斗容量", "Bucket capacity (loader)": "铲斗容量(装载端)",
    "Rated load capacity (loader)": "额定载重量(装载端)",
    "Digging depth": "挖掘深度", "Max digging depth": "最大挖掘深度",
    "Digging radius": "挖掘半径", "Max digging radius": "最大挖掘半径",
    "Digging Force": "挖掘力", "Blade width": "铲刀宽度",
    "Max traction force": "最大牵引力", "Max rated lifting capacity": "最大额定起重量",
    "Working radius": "工作幅度", "Lifting height": "起升高度",
    "Lifting arm length": "起重臂长度", "Max travel speed": "最大行驶速度",
    "Max climbing grade": "最大爬坡度", "Rated total lifting capacity": "额定总起重量",
    "Basic arm lifting torque": "基本臂起重力矩",
    "Max lifting height of main arm": "主臂最大起升高度",
    "Driving speed": "行驶速度", "Vibration frequency": "振动频率",
    "Fuel tank": "燃油箱", "Rated lifting capacity": "额定起重量",
    "Load center distance": "载荷中心距", "Lifting speed": "起升速度",
    "Mast inclination": "门架倾角", "Chassis series": "底盘系列",
    "Steering type": "转向型式", "Color": "颜色", "Brand": "品牌",
    "Classification": "分类", "Digging force": "挖掘力", "Driving type": "驱动型式",
    "Front axle": "前桥", "Gradeability": "爬坡度", "Operation mode": "操作方式",
    "Pumping capacity": "泵送量", "Pumping height": "泵送高度",
    "Rear axle allowable load": "后桥允许载荷", "Tank volume": "罐体容积",
    "Top brand name": "上装品牌", "Travel speed": "行驶速度",
    "Vehicle weight": "整车重量",
    # --- Agriculture Machinery ---
    "Rated power": "额定功率", "Drive type": "驱动型式",
    "PTO speed": "动力输出转速", "Lifting capacity": "提升力",
    "Gearbox": "变速箱", "Track width": "履带宽度",
    "Ground pressure": "接地比压", "Cutting width": "割幅",
    "Grain tank": "粮箱容积", "Working efficiency": "作业效率",
    "Rows": "行数", "Row spacing": "行距",
    "Working width": "工作幅宽", "Working depth": "耕深",
    "Blade type": "刀片型式", "Matched power": "配套动力",
    "Fertilizer box": "肥箱容积", "Box volume": "货箱容积",
    "Tipping type": "卸料方式", "Boom width": "喷幅",
    "Pump flow": "泵流量",
}
SKIP_KEYS = {"Color"}


def load_products():
    trans = json.load(open(os.path.join(WORK, "products_transcribe.json"), encoding="utf-8"))
    rmap = json.load(open(os.path.join(WORK, "products_real_map.json"), encoding="utf-8"))
    manifest = json.load(open(os.path.join(WORK, "manifest.json"), encoding="utf-8"))
    by_id = {}
    for items in manifest.values():
        for it in items:
            by_id[it["id"]] = it

    # 清掉旧版生成的图片(旧命名 <crop>-thumb/-large.jpg)
    for f in os.listdir(OUT):
        if re.match(r"^\d\d[LR]-\d\d-(thumb|large)\.jpg$", f):
            os.remove(os.path.join(OUT, f))

    products = []
    for pid in sorted(trans, key=lambda k: (int(k.split("-")[0]), int(k.split("-")[1]))):
        t = trans[pid]
        # 占位图条目(农业机械): 图片已由 tools/make_agri_placeholders.py 生成, 无画册裁剪源
        if t.get("placeholder_img"):
            thumb = os.path.join(OUT, f"p{pid}-thumb.jpg")
            large = os.path.join(OUT, f"p{pid}-large.jpg")
            if not (os.path.exists(thumb) and os.path.exists(large)):
                print(f"!! placeholder image missing for {pid} - run tools/make_agri_placeholders.py")
                continue
            im = Image.open(large).convert("RGB")
            crop_id = ""
        else:
            crop_id = rmap[pid]["crop"]
            src_item = by_id[crop_id]
            src = os.path.join(WORK, src_item["file"])
            im = Image.open(src).convert("RGB")
            for key, width, q in (("thumb", 600, 82), ("large", 1200, 85)):
                out = os.path.join(OUT, f"p{pid}-{key}.jpg")
                if not os.path.exists(out):
                    w, h = im.size
                    if w > width:
                        im2 = im.resize((width, int(h * width / w)), Image.LANCZOS)
                    else:
                        im2 = im
                    im2.save(out, "JPEG", quality=q, optimize=True)
        cat_en, cat_zh = t.get("cat_override") or CAT_BY_ID[pid]
        specs = []
        for k, v in t.get("params", {}).items():
            if k in SKIP_KEYS:
                continue
            specs.append({"k": k, "k_zh": PARAM_ZH.get(k, k), "v": v})
        products.append({
            "id": pid,
            "name_en": t["name_en"], "name_zh": t["name_zh"],
            "cat_en": cat_en, "cat_zh": cat_zh,
            "crop": crop_id,
            "thumb": f"images/products/p{pid}-thumb.jpg",
            "large": f"images/products/p{pid}-large.jpg",
            "w": im.size[0], "h": im.size[1],
            "specs": specs,
            "desc_en": t.get("desc_en", ""), "desc_zh": t.get("desc_zh", ""),
        })

    # 校验参数key全部有中文映射(除被跳过的)
    miss = sorted({s["k"] for p in products for s in p["specs"]} - set(PARAM_ZH))
    if miss:
        print("!! PARAM_ZH missing:", miss)
    with open(os.path.join(WORK, "products_real.json"), "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=1)
    print("products:", len(products))
    return products


def replace_block(text, start_marker, sentinel, end_marker, inner, name):
    """把 start..end 之间替换为 sentinel + inner; 支持 sentinel 二次替换(幂等)"""
    if sentinel in text:
        i = text.index(sentinel)
        j = text.index(end_marker, i)
        return text[:i] + sentinel + inner + text[j:]
    if start_marker in text:
        i = text.index(start_marker)
        j = text.index(end_marker, i)
        return text[:i] + sentinel + inner + text[j:]
    print("!! marker not found:", name)
    return text


def gallery_items(products):
    out = []
    for p in products:
        out.append(
            f'''          <div class="col-12 col-sm-6 col-md-4 col-lg-3">
            <div class="gallery-item-classic"><img src="{p['thumb']}" alt="{p['name_en']}" width="465" height="383"/>
              <div class="gallery-item-classic-caption"><a href="{p['large']}" data-lightgallery="item">zoom</a></div>
            </div>
          </div>''')
    return "\n".join(out)


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def product_card(p, cols="col-md-6 col-lg-3", href="gallery.html", anchor=False):
    tw = 600 if p["w"] >= 600 else p["w"]
    th = int(p["h"] * tw / p["w"]) if p["w"] >= 600 else p["h"]
    anchor_attr = f' id="p{p["id"]}"' if anchor else ''
    specs = ""
    if p["specs"]:
        lis = []
        for s in p["specs"][:4]:
            lis.append(f'''                        <li><span class="spec-k" data-zh="{_esc(s['k_zh'])}">{_esc(s['k'])}</span>: <span class="spec-v">{_esc(s['v'])}</span></li>''')
        specs = ('\n                    <ul class="box-product-specs">\n'
                 + "\n".join(lis) + "\n                    </ul>")
    elif p["desc_en"]:
        de, dz = _esc(p["desc_en"][:150]), _esc(p["desc_zh"][:110])
        specs = f'\n                    <p class="box-product-desc" data-zh="{dz}">{de}</p>'
    return f'''                <div class="col-12 col-sm-6 {cols}"{anchor_attr}><a class="box-product" href="{href}">
                    <div class="box-product-figure"><img src="{p['thumb']}" alt="{p['name_en']}" width="{tw}" height="{th}"/>
                    </div>
                    <div class="box-product-caption">
                      <h4 class="box-product-title"><span data-zh="{_esc(p['name_zh'])}">{_esc(p['name_en'])}</span></h4>{specs}
                      <div class="box-product-divider"></div>
                    </div></a>
                </div>'''


def write_gallery(products):
    fp = os.path.join(ROOT, "gallery.html")
    text = open(fp, encoding="utf-8").read()
    inner = f'''
      <section class="section section-xl bg-default">
        <div class="row row-30">
{gallery_items(products)}
        </div>
      </section>
      '''
    text = replace_block(
        text,
        '      <section class="section section-xl bg-default">',
        '      <!-- PRODUCTS-GALLERY:start -->',
        '      <!-- Page Footer-->',
        inner, "gallery")
    open(fp, "w", encoding="utf-8", newline="\n").write(text)
    print("gallery.html ok")


def write_equipment(products):
    fp = os.path.join(ROOT, "equipment.html")
    text = open(fp, encoding="utf-8").read()
    groups = []
    for cat in CAT_ORDER:
        items = [p for p in products if p["cat_en"] == cat]
        if not items:
            continue
        href = CAT_PAGES[cat][0]
        cards = "\n".join(product_card(p, href=href) for p in items)
        groups.append(f'''              <div class="cat-head">
                <h3 class="title-decorate"><span data-zh="{items[0]['cat_zh']}">{cat}</span></h3>
                <a class="cat-more" href="{href}" data-zh="查看全部">View all</a>
              </div>
              <div class="row row-15 row-gutters-14 products-grid">
{cards}
              </div>''')
    body = "\n".join(groups)
    inner = f'''
      <section class="section-lg section bg-gray-1">
        <div class="container">
{body}
        </div>
      </section>
      '''
    text = replace_block(
        text,
        '      <section class="section-lg section bg-gray-1">',
        '      <!-- PRODUCTS-CATALOG:start -->',
        '      <!-- Page Footer-->',
        inner, "equipment")
    open(fp, "w", encoding="utf-8", newline="\n").write(text)
    print("equipment.html ok")


INTRO_EN = ("EquipSupply supplies a full range of heavy-duty trucks, semi-trailers and "
            "construction machinery - dump trucks, tractor trucks, mixers, excavators, "
            "cranes, rollers, forklifts and more.")
INTRO_ZH = "EquipSupply 提供全系列重卡、半挂车与工程机械 —— 自卸车、牵引车、搅拌车、挖掘机、起重机、压路机、叉车等。"


def write_index(products):
    fp = os.path.join(ROOT, "index.html")
    text = open(fp, encoding="utf-8").read()
    by_id = {p["id"]: p for p in products}
    picks = [by_id[i] for i in HOME_IDS if i in by_id]
    cards = "\n".join(product_card(p, cols="col-md-6 col-lg-3", href=CAT_PAGES[p["cat_en"]][0])
                      for p in picks)
    inner = f'''
      <section class="section section-xl bg-gray-700">
        <div class="container">
          <div class="row row-30 align-items-lg-end">
            <div class="col-lg-4 wow-outer">
              <div class="wow slideInRight">
                <h3 class="title-decorate"><span>Our Products</span></h3>
              </div>
            </div>
            <div class="col-lg-8 wow-outer">
              <div class="wow slideInLeft">
                <p class="text-opacity-80" data-zh="{INTRO_ZH}">{INTRO_EN} <a class="text-primary" href="equipment.html">View the full catalog</a></p>
              </div>
            </div>
          </div>
          <div class="row row-15 row-gutters-14 products-grid">
{cards}
          </div>
        </div>
      </section>
      '''
    text = replace_block(
        text,
        '      <section class="section tabs-custom tabs-horizontal tabs-creative" id="tabs-1">',
        '      <!-- PRODUCTS-INDEX:start -->',
        '      <!-- Brands-->',
        inner, "index")
    open(fp, "w", encoding="utf-8", newline="\n").write(text)
    print("index.html ok")


if __name__ == "__main__":
    products = load_products()
    write_gallery(products)
    write_equipment(products)
    write_index(products)
