# -*- coding: utf-8 -*-
"""验证 i18n 翻译覆盖率：提取核心页叶子英文文本，对照 i18n.js 的 DICT + data-zh + 正则规则，
输出「应该翻译但未被覆盖」的短语，便于补全字典。"""
import os, re
from html.parser import HTMLParser

ROOT = r'C:/Project/Workbuddy/equ-us-ci'
CORE = ['index.html','equipment.html','gallery.html','about-us.html','contacts.html',
        'news.html','news-2.html','privacy-policy.html','blog-post.html','product-page.html',
        'industries.html']

# --- 1. 提取 DICT keys ---
js = open(os.path.join(ROOT,'js/i18n.js'),encoding='utf-8').read()
m = re.search(r'var DICT\s*=\s*\{(.*?)\n  \};', js, re.S)
block = m.group(1)
keys = set(re.findall(r"'([^']+)'\s*:", block))
print('DICT keys:', len(keys))

# --- 2. 提取核心页叶子文本（与 i18n.js collect 对齐：无子元素的元素直接文本） ---
class Txt(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.stack=[]; self.out=[]
    def handle_starttag(self,tag,attrs):
        if self.stack: self.stack[-1]['kids']=True
        self.stack.append({'tag':tag,'text':'','kids':False})
    def handle_endtag(self,tag):
        if self.stack:
            e=self.stack.pop()
            if not e['kids'] and e['text'].strip(): self.out.append(e['text'].strip())
    def handle_data(self,data):
        if self.stack: self.stack[-1]['text']+=data

leaf_texts={}
for fn in CORE:
    p=os.path.join(ROOT,fn)
    html=open(p,encoding='utf-8').read()
    html=re.sub(r'<script[\s\S]*?</script>','',html,flags=re.I)
    html=re.sub(r'<style[\s\S]*?</style>','',html,flags=re.I)
    t=Txt(); t.feed(html)
    for x in t.out: leaf_texts.setdefault(x,set()).add(fn)

# --- 3. 判断覆盖 ---
def covered(t):
    if t in keys: return 'DICT'
    if re.match(r'^(\d+)\s+models$', t): return 'models'
    if re.match(r'^([A-Z][A-Za-z &\-]+) \d{2}$', t): return 'product(data-zh)'
    return None

# 不需要翻译的（占位/专有/符号）
SKIP_RE = [
    r'[一-鿿]', r'^\d+$', r'https?://', r'@', r'^\d{3,}$', r'\+?\d[\d\-]{6,}',
    r'^[A-Z][a-zA-Z]+ [A-Z][a-zA-Z]+$',  # 人名 John Smith / Sam McMillan 等
    r'Lorem|Eabitant|Morbi|Sed ut|tristique|consectetur|perspiciatis|Quis autem|Ut enim',
    r'^©$', r'^Digger$', r'^Loading\.\.\.$', r'^zoom$', r'^\.$', r'^#$', r'^[a-z]$',
    r'^\d{1,2}/\d{1,2}/\d{4}$', r'^\d{4}$', r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+$',
]
def skip(t):
    for r in SKIP_RE:
        if re.search(r,t): return True
    return False

miss=[]
for t in sorted(leaf_texts):
    c=covered(t)
    if c: continue
    if skip(t): continue
    miss.append((t, ','.join(sorted(leaf_texts[t]))))

print('\n==== 未覆盖且可能需翻译的短语（%d 条）====' % len(miss))
for t,fs in miss:
    print(repr(t),'->',fs)
