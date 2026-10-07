# -*- coding: utf-8 -*-
"""
修复导航 Products 巨型菜单。
损坏模式(旧脚本非贪婪正则所致):
    <li ...>Products</a>
      <ul class="rd-menu rd-navbar-megamenu">   <- 新菜单(完整3列,正确)
        ...新3列...
      </ul>
        </li>
        <li class="rd-megamenu-item">半挂车…   <- 旧菜单残留尾部
        ...
      </ul>   <- 旧菜单外层的收尾
    </li>
本脚本直接把「mega 菜单起点 ~ 旧菜单残留结束」整段替换为干净的新菜单, 边界用文本锚点精确定位。幂等。
"""
import os
import re
import glob

ROOT = r"C:/Project/Workbuddy/equ-us-ci"

MENU = [
    ("Heavy Trucks", "重型卡车", [
        ("Dump Trucks", "自卸车", "dump-trucks.html"),
        ("Tractor Trucks", "牵引车", "tractor-trucks.html"),
        ("Special Trucks", "专用车", "special-trucks.html"),
        ("Concrete Mixer Truck", "混凝土搅拌车", "special-trucks.html#g-concrete-mixer-truck"),
        ("Water Tank Truck", "洒水车", "special-trucks.html#g-water-tank-truck"),
        ("Fuel Tanker Truck", "油罐车", "special-trucks.html#g-fuel-tanker-truck"),
        ("Truck Crane", "起重车", "special-trucks.html#g-crane-truck"),
    ]),
    ("Semi-Trailers", "半挂车", [
        ("All Semi-Trailers", "全部半挂车", "semi-trailers.html"),
        ("Fence Semi-Trailer", "仓栏半挂车", "semi-trailers.html#p4-01"),
        ("Low Flatbed Semi-Trailer", "低平板半挂车", "semi-trailers.html#p4-02"),
        ("Dump Semi-Trailer", "自卸半挂车", "semi-trailers.html#p4-03"),
        ("Flatbed Semi-Trailer", "平板半挂车", "semi-trailers.html#p4-04"),
        ("Curtain-side Semi-Trailer", "侧帘半挂车", "semi-trailers.html#p4-07"),
        ("Skeleton Semi-Trailer", "骨架半挂车", "semi-trailers.html#p4-08"),
        ("Car Carrier Semi-Trailer", "轿运半挂车", "semi-trailers.html#p4-09"),
        ("Bulk Cement Semi-Trailer", "水泥粉罐半挂车", "semi-trailers.html#p4-10"),
    ]),
    ("Construction Machinery", "工程机械", [
        ("All Construction Machinery", "全部工程机械", "construction-machinery.html"),
        ("Excavator", "挖掘机", "construction-machinery.html#g-excavator"),
        ("Backhoe Loader", "挖掘装载机", "construction-machinery.html#g-backhoe-loader"),
        ("Bulldozer", "推土机", "construction-machinery.html#g-bulldozer"),
        ("Truck Crane", "汽车起重机", "construction-machinery.html#g-truck-crane"),
        ("Road Roller", "压路机", "construction-machinery.html#g-road-roller"),
        ("Forklift", "叉车", "construction-machinery.html#g-forklift"),
        ("Boom Pump Truck", "泵车", "construction-machinery.html#g-boom-pump-truck"),
    ]),
    ("Agriculture Machinery", "农业机械", [
        ("All Agriculture Machinery", "全部农业机械", "agriculture-machinery.html"),
        ("Tractor", "拖拉机", "agriculture-machinery.html#g-tractor"),
        ("Harvester", "收割机", "agriculture-machinery.html#g-harvester"),
        ("Seeding & Tillage Implements", "播种与耕整机具",
         "agriculture-machinery.html#g-seeding-tillage-implements"),
        ("Farm Transport & Others", "农用运输及其他",
         "agriculture-machinery.html#g-farm-transport-others"),
    ]),
]

MEGA_OPEN = '<ul class="rd-menu rd-navbar-megamenu">'


def menu_html(indent="                        "):
    cols = []
    for cen, czh, items in MENU:
        lis = "\n".join(
            f'''                              <li class="rd-megamenu-list-item"><a class="rd-megamenu-list-link" href="{href}">{en}</a></li>'''
            for en, zh, href in items)
        cols.append(f'''                          <li class="rd-megamenu-item">
                            <h6 class="rd-megamenu-title">{cen}</h6>
                            <ul class="rd-megamenu-list">
{lis}
                            </ul>
                          </li>''')
    return (indent + MEGA_OPEN + "\n" + "\n".join(cols) + f"\n{indent}</ul>\n                      </li>")


def fix_file(fp):
    text = open(fp, encoding="utf-8").read()
    if MEGA_OPEN not in text:
        return "skip"
    k = text.find(MEGA_OPEN)
    # 结束边界: Products 之后的下一个 rd-nav-item(即 Industries)
    m = re.search(r'<li class="rd-nav-item[^"]*"><a class="rd-nav-link" href="industries\.html">',
                  text[k:])
    if not m:
        return "FAIL(no-industries)"
    end = k + m.start()
    new = text[:k] + menu_html() + "\n" + text[end:]
    # 关键: 带子菜单的 <li> 必须有 rd-navbar-submenu 类, 否则 RD Navbar 不展开
    def _add_submenu(mm):
        active, href, label, gap = mm.group(1) or "", mm.group(2), mm.group(3), mm.group(4)
        return (f'<li class="rd-nav-item{active} rd-navbar-submenu">'
                f'<a class="rd-nav-link" href="{href}">{label}</a>{gap}<ul class="rd-menu')

    new = re.sub(
        r'<li class="rd-nav-item( active)?"><a class="rd-nav-link" href="(\w[\w\-]*\.html)"(?!\s+class)[^>]*>([^<]+)</a>(\s*\n\s*)<ul class="rd-menu',
        _add_submenu, new)
    if new == text:
        return "unchanged"
    open(fp, "w", encoding="utf-8", newline="\n").write(new)
    return "fixed"


def main():
    for fp in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
        print(f"{fix_file(fp):18s} {os.path.basename(fp)}")


if __name__ == "__main__":
    main()
