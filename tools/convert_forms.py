# -*- coding: utf-8 -*-
"""把静态站所有表单从 bat/rd-mailform.php 改到 Formspree(占位端点)。
幂等：重复运行安全。仅改动 action 属性与引入脚本标签，不碰其它内容。
端点占位 token: REPLACE_WITH_YOUR_FORM_ID (在 form-handler.js 与各处 action 统一替换即可)。
"""
import os
import glob

ROOT = r"C:/Project/Workbuddy/equ-us-ci"
ENDPOINT = "https://formspree.io/f/REPLACE_WITH_YOUR_FORM_ID"
SCRIPT_LINE = '<script src="js/script.js"></script>'
SCRIPT_TAG = '    <script src="js/form-handler.js"></script>'

# 仅在确实需要处理表单的页面注入脚本
NEED_MARKERS = ('data-form-type', 'mailchimp-mailform', 'campaign-mailform', 'rd-form-centered')


def convert(path):
    with open(path, encoding='utf-8') as f:
        s = f.read()
    orig = s

    # 1) 主表单: bat/rd-mailform.php -> 端点
    s = s.replace('action="bat/rd-mailform.php"', 'action="%s"' % ENDPOINT)

    # 2) forms.html: Mailchimp / Campaign Monitor 占位表单
    s = s.replace(
        '<form class="rd-form mailchimp-mailform rd-form-inline" data-form-output="form-output-global" action="#" method="post">',
        '<form class="rd-form rd-form-inline" data-form-type="subscribe" data-form-output="form-output-global" action="%s" method="post">' % ENDPOINT)
    s = s.replace(
        '<form class="rd-form campaign-mailform rd-form-inline" data-form-output="form-output-global" action="#" method="post">',
        '<form class="rd-form rd-form-inline" data-form-type="subscribe" data-form-output="form-output-global" action="%s" method="post">' % ENDPOINT)

    # 3) forms.html: Login / Registration 演示表单(无 action、无 data-form-type)
    s = s.replace(
        '<form class="rd-form rd-mailform rd-form-centered">',
        '<form class="rd-form rd-form-centered" data-form-type="contact" data-form-output="form-output-global" action="%s" method="post">' % ENDPOINT)

    # 4) 引入 form-handler.js (在 js/script.js 之后)
    need = any(m in s for m in NEED_MARKERS)
    if SCRIPT_LINE in s and need and SCRIPT_TAG.strip() not in s:
        s = s.replace(SCRIPT_LINE, SCRIPT_LINE + '\n' + SCRIPT_TAG, 1)

    if s != orig:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(s)
        return True
    return False


def main():
    count = 0
    for path in glob.glob(os.path.join(ROOT, '*.html')):
        if convert(path):
            count += 1
            print('updated:', os.path.basename(path))
    print('done. updated %d file(s).' % count)


if __name__ == '__main__':
    main()
