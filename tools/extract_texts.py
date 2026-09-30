# -*- coding: utf-8 -*-
"""提取 HTML 中所有「纯文本叶子元素」的文本（即 i18n 切换器在运行时按文本匹配翻译的对象）。
只提取没有子标签的元素（叶子），与 i18n.js 的翻译策略严格对齐。
"""
import glob, os, re
from html.parser import HTMLParser

CORE = ['index.html','equipment.html','gallery.html','about-us.html','contacts.html',
        'news.html','news-2.html','privacy-policy.html','blog-post.html','product-page.html',
        'industries.html']

class Txt(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.out = []
    def handle_starttag(self, tag, attrs):
        if self.stack:
            self.stack[-1]['kids'] = True
        self.stack.append({'tag': tag, 'text': '', 'kids': False})
    def handle_endtag(self, tag):
        if self.stack:
            e = self.stack.pop()
            if not e['kids'] and e['text'].strip():
                self.out.append((e['tag'], e['text'].strip()))
    def handle_data(self, data):
        if self.stack:
            self.stack[-1]['text'] += data

all_texts = {}
raw = {}
for fn in CORE:
    p = os.path.join(r'C:/Project/Workbuddy/equ-us-ci', fn)
    if not os.path.exists(p):
        print('MISSING', fn); continue
    html = open(p, encoding='utf-8').read()
    # 去掉 script/style 内文本
    html = re.sub(r'<script[\s\S]*?</script>', '', html, flags=re.I)
    html = re.sub(r'<style[\s\S]*?</style>', '', html, flags=re.I)
    t = Txt(); t.feed(html)
    items = []
    seen = set()
    for tag, txt in t.out:
        if txt not in seen:
            seen.add(txt); items.append(txt)
    raw[fn] = items
    for txt in items:
        all_texts.setdefault(txt, []).append(fn)

# 输出全站去重文本清单（按出现频率）
print('==== 全站叶子文本清单（去重）共 %d 条 ====' % len(all_texts))
for txt in sorted(all_texts, key=lambda x: (-len(all_texts[x]), x)):
    files = ','.join(sorted(set(all_texts[txt])))
    # 跳过明显中文/空/纯数字/URL
    if re.search(r'[一-鿿]', txt): 
        print('[中]', repr(txt), '->', files); continue
    if re.fullmatch(r'[\d\s\.\+kK\-]+', txt): continue
    if len(txt) > 120:  # 超长整句（Lorem 等）标记
        print('[长]', repr(txt[:80]+'...'), '->', files); continue
    print('[  ]', repr(txt), '->', files)
