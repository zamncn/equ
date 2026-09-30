# -*- coding: utf-8 -*-
"""把所有表单统一到 Web3Forms(免注册静态表单服务)。
幂等：重复运行安全。仅改 action 属性与引入脚本标签。
access_key 集中在 js/form-handler.js (REPLACE_WITH_YOUR_WEB3FORMS_KEY)，替换一处即全站生效。
收信邮箱在 web3forms.com 获取 access key 时绑定。
"""
import os
import glob

ROOT = r"C:/Project/Workbuddy/equ-us-ci"
ENDPOINT = "https://api.web3forms.com/submit"
SCRIPT_LINE = '<script src="js/script.js"></script>'
SCRIPT_TAG = '    <script src="js/form-handler.js"></script>'
NEED_MARKERS = ('data-form-type', 'mailchimp-mailform', 'campaign-mailform', 'rd-form-centered')


def convert(path):
    with open(path, encoding='utf-8') as f:
        s = f.read()
    orig = s

    # 1) 原始 PHP 表单
    s = s.replace('action="bat/rd-mailform.php"', 'action="%s"' % ENDPOINT)
    # 2) 上一轮改成的 Formspree 占位端点 -> Web3Forms
    s = s.replace('action="https://formspree.io/f/REPLACE_WITH_YOUR_FORM_ID"', 'action="%s"' % ENDPOINT)
    # 3) 临时用过的 Web3Forms 端点(同值, 保持幂等)
    s = s.replace('action="https://api.web3forms.com/submit"', 'action="%s"' % ENDPOINT)
    # 4) 临时用过的 formsubmit.co 端点 -> Web3Forms
    s = s.replace('action="https://formsubmit.co/tonny@chenn.com.cn"', 'action="%s"' % ENDPOINT)
    # 5) forms.html: Mailchimp / Campaign Monitor 占位表单(action="#" 兜底, 仅在仍为 # 时)
    s = s.replace(
        '<form class="rd-form mailchimp-mailform rd-form-inline" data-form-output="form-output-global" action="#" method="post">',
        '<form class="rd-form rd-form-inline" data-form-type="subscribe" data-form-output="form-output-global" action="%s" method="post">' % ENDPOINT)
    s = s.replace(
        '<form class="rd-form campaign-mailform rd-form-inline" data-form-output="form-output-global" action="#" method="post">',
        '<form class="rd-form rd-form-inline" data-form-type="subscribe" data-form-output="form-output-global" action="%s" method="post">' % ENDPOINT)
    # 6) forms.html: Login / Registration 演示表单(无 action、无 data-form-type)
    s = s.replace(
        '<form class="rd-form rd-mailform rd-form-centered">',
        '<form class="rd-form rd-form-centered" data-form-type="contact" data-form-output="form-output-global" action="%s" method="post">' % ENDPOINT)

    # 7) 引入 form-handler.js (在 js/script.js 之后)
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
