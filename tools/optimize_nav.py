# -*- coding: utf-8 -*-
"""
优化全站导航栏: 把 Digger 模板遗留的 "Pages 1-4" 巨型菜单(含死链接 # 与模板演示页)
替换为符合 FENG TU 真实业务的导航结构, 并保持中英双语(i18n.js 按文本精确翻译)。

- 顶层: Home / About Us / Products / Industries / News / Contacts
- About Us ▾: About Us, Our Team
- Products ▾(mega): 重卡 / 半挂车 / 工程机械 三大类, 列出 21 个产品类别(指向 equipment.html)
- News ▾: News, News 2, Blog Post
- 演示页(typography/buttons/grid/...)从主导航移除(仍可通过 URL 访问), 顶部不再有死链接

脚本对每个 html 重新放置 active 高亮, 并在 i18n.js 字典中补全新标签。
幂等: 基于正则匹配 <ul class="rd-navbar-nav"> 到 <div class="rd-navbar-collapse"> 前。
"""
import os
import re

ROOT = r"C:/Project/Workbuddy/equ-us-ci"

# 每个文件对应的高亮项(无则 None)
FILE_ACTIVE = {
    "index.html": "Home",
    "about-us.html": "About Us",
    "privacy-policy.html": "About Us",
    "equipment.html": "Products",
    "gallery.html": "Products",
    "product-page.html": "Products",
    "industries.html": "Industries",
    "news.html": "News",
    "news-2.html": "News",
    "blog-post.html": "News",
    "contacts.html": "Contacts",
    # 演示页: 原高亮在已删除的 Pages 上, 现无对应项
    "typography.html": None,
    "buttons.html": None,
    "forms.html": None,
    "grid-system.html": None,
    "icon-lists.html": None,
    "timers-&-counters.html": None,
    "coming-soon.html": None,
    "search-results.html": None,
}

HREF = {
    "Home": "index.html",
    "About Us": "about-us.html",
    "Products": "equipment.html",
    "Industries": "industries.html",
    "News": "news.html",
    "Contacts": "contacts.html",
}

# Products 三大类 -> 产品类别(顺序对应 build_site_products.py 的 CAT)
TRUCKS = ["Dump Truck", "Tractor Truck", "Concrete Mixer Truck", "Water Tank Truck",
          "Fuel Tanker Truck", "Truck-Mounted Crane", "Boom Pump Truck"]
TRAILERS = ["Fence Semi-Trailer", "Lowbed Semi-Trailer", "Dump Semi-Trailer",
            "Flatbed Semi-Trailer", "Curtain-side Semi-Trailer", "Container Semi-Trailer",
            "Car Carrier Semi-Trailer", "Bulk Cement Semi-Trailer"]
MACHINERY = ["Excavator", "Backhoe Loader", "Bulldozer", "Truck Crane",
             "Road Roller", "Forklift"]


def mega_col(title, items, last=False):
    lis = "\n".join(
        f'                              <li class="rd-megamenu-list-item"><a class="rd-megamenu-list-link" href="equipment.html">{it}</a></li>'
        for it in items)
    return (
        '                          <li class="rd-megamenu-item">\n'
        f'                            <h6 class="rd-megamenu-title">{title}</h6>\n'
        '                            <ul class="rd-megamenu-list">\n'
        f'{lis}\n'
        '                            </ul>\n'
        '                          </li>' + ("" if last else "\n")
    )


def build_nav(active):
    a = active
    about_active = ' class="rd-nav-item active"' if a == "About Us" else ' class="rd-nav-item"'
    prod_active = ' class="rd-nav-item active"' if a == "Products" else ' class="rd-nav-item"'
    ind_active = ' class="rd-nav-item active"' if a == "Industries" else ' class="rd-nav-item"'
    news_active = ' class="rd-nav-item active"' if a == "News" else ' class="rd-nav-item"'
    con_active = ' class="rd-nav-item active"' if a == "Contacts" else ' class="rd-nav-item"'
    home_active = ' class="rd-nav-item active"' if a == "Home" else ' class="rd-nav-item"'

    products_mega = (
        '                        <ul class="rd-menu rd-navbar-megamenu">\n'
        + mega_col("Heavy Trucks", TRUCKS)
        + mega_col("Semi-Trailers", TRAILERS)
        + mega_col("Construction Machinery", MACHINERY, last=True)
        + '                        </ul>'
    )

    return (
        '                    <ul class="rd-navbar-nav">\n'
        f'                      <li{home_active}><a class="rd-nav-link" href="index.html">Home</a></li>\n'
        f'                      <li{about_active}><a class="rd-nav-link" href="about-us.html">About Us</a>\n'
        '                        <ul class="rd-menu rd-navbar-dropdown">\n'
        '                          <li class="rd-dropdown-item"><a class="rd-dropdown-link" href="about-us.html">About Us</a></li>\n'
        '                          <li class="rd-dropdown-item"><a class="rd-dropdown-link" href="about-us.html#team">Our Team</a></li>\n'
        '                        </ul>\n'
        '                      </li>\n'
        f'                      <li{prod_active}><a class="rd-nav-link" href="equipment.html">Products</a>\n'
        f'{products_mega}\n'
        '                      </li>\n'
        f'                      <li{ind_active}><a class="rd-nav-link" href="industries.html">Industries</a></li>\n'
        f'                      <li{news_active}><a class="rd-nav-link" href="news.html">News</a>\n'
        '                        <ul class="rd-menu rd-navbar-dropdown">\n'
        '                          <li class="rd-dropdown-item"><a class="rd-dropdown-link" href="news.html">News</a></li>\n'
        '                          <li class="rd-dropdown-item"><a class="rd-dropdown-link" href="news-2.html">News 2</a></li>\n'
        '                          <li class="rd-dropdown-item"><a class="rd-dropdown-link" href="blog-post.html">Blog Post</a></li>\n'
        '                        </ul>\n'
        '                      </li>\n'
        f'                      <li{con_active}><a class="rd-nav-link" href="contacts.html">Contacts</a></li>\n'
        '                    </ul>'
    )


NAV_RE = re.compile(
    r'<ul class="rd-navbar-nav">.*?</ul>\s*</div>\s*</div>\s*<div class="rd-navbar-collapse">',
    re.S,
)


def update_html(path):
    name = os.path.basename(path)
    active = FILE_ACTIVE.get(name, None)
    new_ul = build_nav(active)
    text = open(path, encoding="utf-8").read()

    def repl(m):
        # 保留匹配末尾的 </ul></div></div><div class="rd-navbar-collapse">
        tail = m.group(0)[m.group(0).rfind("</ul>") + 6:]
        return new_ul + tail

    if not NAV_RE.search(text):
        print("!! 未匹配导航:", name)
        return False
    text = NAV_RE.sub(repl, text, count=1)
    open(path, "w", encoding="utf-8", newline="\n").write(text)
    print("ok", name, "(active=%s)" % active)
    return True


def update_i18n():
    fp = os.path.join(ROOT, "js", "i18n.js")
    text = open(fp, encoding="utf-8").read()
    anchor = "    'Contacts': '联系我们',\n"
    addition = (
        "    'Products': '产品中心', 'Heavy Trucks': '重卡', 'Semi-Trailers': '半挂车',\n"
        "    'Construction Machinery': '工程机械',\n"
    )
    if "'Products':" in text:
        print("i18n 已含 Products, 跳过")
        return
    if anchor not in text:
        print("!! i18n 锚点未找到, 手动添加失败")
        return
    text = text.replace(anchor, anchor + addition, 1)
    open(fp, "w", encoding="utf-8", newline="\n").write(text)
    print("i18n 字典已更新")


def main():
    for f in sorted(os.listdir(ROOT)):
        if f.endswith(".html") and f in FILE_ACTIVE:
            update_html(os.path.join(ROOT, f))
    update_i18n()


if __name__ == "__main__":
    main()
