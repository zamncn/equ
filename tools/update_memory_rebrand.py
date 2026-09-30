# -*- coding: utf-8 -*-
import os
BASE = "C:/Project/Workbuddy/equ-us-ci/.workbuddy/memory"

# 1) update MEMORY.md
mem = os.path.join(BASE, "MEMORY.md")
s = open(mem, encoding="utf-8").read()
s = s.replace(
    "基于 Digger 静态 HTML 模板(Bootstrap+RD Navbar)",
    "基于 Digger 静态 HTML 模板(已重品牌为 FENG TU/丰途, Bootstrap+RD Navbar)")
s = s.replace(
    "timers-&-counters.html 重命名)", "timers-&-counters.html 已重命名✅)")
s = s.replace(
    "产品名称目前为\"类别+编号\"占位, 真实型号待转录或用户提供清单。",
    "产品名称目前为\"类别+编号\"占位, 真实型号待转录或用户提供清单。")
open(mem, "w", encoding="utf-8").write(s)

# 2) append to daily log
log = os.path.join(BASE, "2026-09-28.md")
note = (
    "\n## 全站品牌重命名(Digger -> FENG TU / 丰途)\n"
    "- 用户要求继续改站点, 先收拾模板占位品牌。\n"
    "- `tools/rebrand.py`: 18 个 html 的 Digger -> FENG TU(页脚版权/Hero副标题/模板证言); "
    "删除 mobanwang 模板署名链接; 导航栏 `<img brand-logo-light>` -> `<a class=\"brand-wordmark\">FENG TU</a>` 文字标识。幂等。\n"
    "- `tools/fix_i18n_brand.py` + 手改: js/i18n.js 同步品牌(英键 FENG TU、中值 丰途; Hero 'Welcome to FENG TU'->'欢迎来到丰途'; 4条证言中英双语 Digger->FENG TU/丰途)。\n"
    "- `tools/add_wordmark_css.py`: css/style.css 末尾追加 .brand-wordmark 金色样式(适配深浅导航栏, 移动端 24px)。\n"
    "- `timers-&-counters.html` 重命名为 `timers-counters.html`(无引用, 卫生处理)。\n"
    "- 验证: Digger 全站零残留; brand-wordmark 注入 18 页; 本地预览 200; i18n.js 语法 OK; "
    "jsdom 双语测试复跑 ALL OK(修正了 equipment 导航期望值 Products/产品, 旧值 Equipment/设备中心 是 optimize_nav 改导航后的过期期望)。\n"
)
open(log, "a", encoding="utf-8").write(note)
print("memory updated")
