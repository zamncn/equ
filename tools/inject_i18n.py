# -*- coding: utf-8 -*-
"""Inject <script src="js/i18n.js"></script> before </body> in every HTML page (idempotent)."""
import glob, os

ROOT = r'C:/Project/Workbuddy/equ-us-ci'
TAG = '<script src="js/i18n.js"></script>'

files = sorted(glob.glob(os.path.join(ROOT, '*.html')))
changed = 0
for f in files:
    html = open(f, encoding='utf-8').read()
    if 'js/i18n.js' in html:
        print('skip(already)', os.path.basename(f)); continue
    if '</body>' not in html:
        print('WARN no </body>', os.path.basename(f)); continue
    html = html.replace('</body>', TAG + '\n</body>', 1)
    open(f, 'w', encoding='utf-8').write(html)
    changed += 1
    print('injected', os.path.basename(f))
print('--- total injected:', changed, '/', len(files))
