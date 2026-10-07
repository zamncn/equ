# -*- coding: utf-8 -*-
"""
全局右下角 WhatsApp 浮动联系图标。

需求: 全站(根目录 26 页 + products/ 62 页)右下角固定一个 WhatsApp 联系按钮。
账号: 用户提供 @chennsa —— wa.me 只接受纯数字号码, 故此处用 WA_NUMBER 配置真实号码,
      拿到号码前先用占位, 改一行重跑即可全站生效。

实现要点:
  * 用 sentinel 注释包裹, 幂等: 重复运行只会替换区块内容, 不会叠加。
  * 根目录页与 products/ 子目录页的 css/js 相对路径不同 -> 由 is_sub 决定前缀。
  * 纯 CSS 实现, 不依赖模板的 script.js, 也不影响 .snackbars / preloader。
  * 品牌绿 #25D366, 固定右下 (bottom/right 24px), 移动端略缩小, 悬停展开文字标签。

运行:
    python tools/add_whatsapp.py
"""
import os
import glob
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# 配置: 真实号码待用户提供后替换(格式: 国家码+号码, 不含 + 、空格、横线)
# 例: 中国手机号 138 1234 5678 -> "8613812345678"
# ---------------------------------------------------------------------------
WA_NUMBER = "447724694614"      # 用户提供: +44 7724 694614 (英国)
WA_DISPLAY = "+44 7724 694614"  # 鼠标悬停/无障碍标签显示的内容

WA_URL = f"https://wa.me/{WA_NUMBER}"

START = "<!-- WHATSAPP-FLOAT:start -->"
END = "<!-- WHATSAPP-FLOAT:end -->"

# WhatsApp 官方 glyph (SVG path, 24x24 viewBox)
WA_SVG = (
    '<svg class="wa-svg" viewBox="0 0 24 24" width="30" height="30" '
    'aria-hidden="true" focusable="false">'
    '<path fill="currentColor" d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15'
    '-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761'
    '-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.297-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371'
    '-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372'
    '-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625'
    '.712.227 1.36.195 1.872.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004'
    'a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884'
    ' 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297'
    'A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654'
    'a11.88 11.88 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413Z"/></svg>'
)

CSS = """
  /* 右下角 WhatsApp 浮动联系按钮 */
  .wa-float {
    position: fixed;
    right: 24px;
    bottom: 24px;
    z-index: 1000;
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px;
    color: #fff;
    background: #25D366;
    border-radius: 50px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, .25);
    text-decoration: none;
    transition: padding .25s ease, background-color .25s ease, transform .25s ease;
  }
  .wa-float:hover,
  .wa-float:focus {
    color: #fff;
    background: #1EBE5A;
    padding-right: 20px;
    transform: translateY(-2px);
    text-decoration: none;
  }
  .wa-float .wa-svg { display: block; width: 30px; height: 30px; flex: 0 0 30px; }
  .wa-float .wa-label {
    max-width: 0;
    overflow: hidden;
    white-space: nowrap;
    font-size: 15px;
    font-weight: 700;
    line-height: 1;
    opacity: 0;
    transition: max-width .25s ease, opacity .25s ease;
  }
  .wa-float:hover .wa-label,
  .wa-float:focus .wa-label { max-width: 200px; opacity: 1; }
  @media (max-width: 767px) {
    .wa-float { right: 16px; bottom: 16px; padding: 10px; }
    .wa-float .wa-svg { width: 26px; height: 26px; flex-basis: 26px; }
  }
  /* 桌面端给模板自带的返回顶部按钮(.ui-to-top, right 40 / bottom 40, 60x60)让位:
     WhatsApp 堆叠在其正上方, 右边缘对齐 */
  @media (min-width: 576px) {
    .wa-float { right: 40px; bottom: 112px; }
  }
  @media print {
    .wa-float { display: none !important; }
  }
"""


def block(is_sub: bool) -> str:
    """生成注入区块。is_sub=True 表示位于 products/ 子目录。"""
    return (
        f"{START}\n"
        f'<style>{CSS}</style>\n'
        f'<a class="wa-float" href="{WA_URL}" target="_blank" rel="noopener noreferrer" '
        f'aria-label="Chat with us on WhatsApp {WA_DISPLAY}" title="WhatsApp {WA_DISPLAY}">\n'
        f'  {WA_SVG}\n'
        f'  <span class="wa-label">WhatsApp</span>\n'
        f'</a>\n'
        f"{END}"
    )


RE_BLOCK = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)


def inject(s: str, is_sub: bool) -> str:
    b = block(is_sub)
    if RE_BLOCK.search(s):
        return RE_BLOCK.sub(lambda m: b, s, count=1)
    # 插在 snackbars 之前(页面主体末尾), 保证在 </body> 内
    anchor = '<div class="snackbars"'
    idx = s.find(anchor)
    if idx == -1:
        idx = s.rfind("</body>")
        if idx == -1:
            return s
        return s[:idx] + b + "\n    " + s[idx:]
    return s[:idx] + b + "\n    " + s[idx:]


def main():
    files = sorted(glob.glob(os.path.join(ROOT, "*.html")) +
                   glob.glob(os.path.join(ROOT, "products", "*.html")))
    changed, already, skipped = [], [], []
    for fp in files:
        is_sub = os.path.basename(os.path.dirname(fp)) == "products"
        s = open(fp, encoding="utf-8").read()
        if RE_BLOCK.search(s):
            new = inject(s, is_sub)
            if new == s:
                already.append(fp)
                continue
        elif "</body>" not in s:
            skipped.append(fp)
            continue
        new = inject(s, is_sub)
        with open(fp, "w", encoding="utf-8") as f:
            f.write(new)
        changed.append(fp)

    rel = lambda p: os.path.relpath(p, ROOT)
    print(f"WhatsApp 浮标: 已修改 {len(changed)} 个, 已是最新 {len(already)} 个")
    if skipped:
        print(f"跳过(无 </body>): {[rel(p) for p in skipped]}")
    for p in changed[:5]:
        print("  e.g.", rel(p))
    print(f"目标链接: {WA_URL}")


if __name__ == "__main__":
    main()
