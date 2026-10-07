# -*- coding: utf-8 -*-
"""
彻底移除站点的中文 i18n(用户要求"去掉中文")。

做三件事(幂等):
1) 删除全站 HTML 里的 data-zh="..." 属性(属性值均为中文, 删除后页面只留英文);
2) 删除页面末尾的 <script src="js/i18n.js"></script> 引用(含产品页的 ../js/i18n.js);
3) 报告统计。js/i18n.js 文件本身由调用方另行删除。

页面文字默认即为英文(中文只在 data-zh / DICT 里, 需 JS 切换才显示),
因此删除后视觉效果不变, 只是源码不再含任何中文。

运行:
    python tools/remove_i18n.py
"""
import os
import re
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 匹配 data-zh="..." 属性(含前面可能的一个空格), 值内无转义引号
RE_DATA_ZH = re.compile(r'\s+data-zh="[^"]*"')
# 匹配整行 i18n.js 引用(含缩进与换行), 兼容 js/ 与 ../js/
RE_I18N_LINE = re.compile(r'[ \t]*<script src="(?:\.\./)?js/i18n\.js"></script>[ \t]*\r?\n?')


def main():
    files = sorted(glob.glob(os.path.join(ROOT, "*.html")) +
                   glob.glob(os.path.join(ROOT, "products", "*.html")))
    tot_attr, tot_script, touched = 0, 0, 0
    for fp in files:
        s = open(fp, encoding="utf-8").read()
        n_attr = len(RE_DATA_ZH.findall(s))
        n_script = len(RE_I18N_LINE.findall(s))
        if n_attr == 0 and n_script == 0:
            continue
        s = RE_DATA_ZH.sub("", s)
        s = RE_I18N_LINE.sub("", s)
        with open(fp, "w", encoding="utf-8") as f:
            f.write(s)
        tot_attr += n_attr
        tot_script += n_script
        touched += 1

    rel = lambda p: os.path.relpath(p, ROOT)
    print(f"处理文件: {touched} 个")
    print(f"删除 data-zh 属性: {tot_attr} 处")
    print(f"删除 i18n.js 引用: {tot_script} 处")

    # 复查残留
    left_attr = sum(len(RE_DATA_ZH.findall(open(p, encoding="utf-8").read()))
                    for p in files)
    left_script = sum(len(RE_I18N_LINE.findall(open(p, encoding="utf-8").read()))
                      for p in files)
    print(f"复查残留 -> data-zh: {left_attr}, i18n.js 引用: {left_script}")


if __name__ == "__main__":
    main()
