# -*- coding: utf-8 -*-
"""
修复导航里失效的半挂车子分类锚点。

原导航半挂车子项使用 `semi-trailers.html#p4-01` 等"产品 id"格式,
但半挂车分类页按子分组渲染, 锚点为 `g-...` 形式, 导致这些链接落空。
本脚本将 8 个失效锚点映射回正确的子分组锚点(与 special/construction/agriculture 分类一致)。

幂等: 重复运行无副作用。
"""
import os
import re
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 产品 id 末两位 -> 目标子分组锚点
MAP = {
    "01": "g-fence-flatbed-lowbed-semi-trailers",
    "02": "g-fence-flatbed-lowbed-semi-trailers",
    "03": "g-fence-flatbed-lowbed-semi-trailers",
    "04": "g-fence-flatbed-lowbed-semi-trailers",
    "07": "g-curtain-side-skeleton-semi-trailers",
    "08": "g-curtain-side-skeleton-semi-trailers",
    "09": "g-car-carrier-bulk-cement-special-semi-trailers",
    "10": "g-car-carrier-bulk-cement-special-semi-trailers",
}


def fix_text(text):
    def repl(m):
        num = m.group(1)
        return f'semi-trailers.html#{MAP.get(num, m.group(0).split("#")[-1])}'
    return re.sub(r'semi-trailers\.html#p4-(\d+)', repl, text)


def main():
    count = 0
    for path in glob.glob(os.path.join(ROOT, "*.html")):
        with open(path, encoding="utf-8") as f:
            text = f.read()
        new = fix_text(text)
        if new != text:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(new)
            count += 1
            print("fixed", os.path.basename(path))
    print(f"已修复 {count} 个文件")


if __name__ == "__main__":
    main()
