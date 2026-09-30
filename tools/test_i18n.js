// DOM-level test for the EN/ZH switcher using jsdom.
const { JSDOM } = require('jsdom');
const path = require('path');
const ROOT = 'C:/Project/Workbuddy/equ-us-ci';
const wait = (ms) => new Promise((r) => setTimeout(r, ms));

async function testPage(file, zhChecks, enChecks) {
  const fs = require('fs');
  let html = fs.readFileSync(path.join(ROOT, file), 'utf-8');
  const i18n = fs.readFileSync(path.join(ROOT, 'js/i18n.js'), 'utf-8');
  html = html.replace('<script src="js/i18n.js"></script>', '<script>' + i18n + '</script>');
  const dom = new JSDOM(html, {
    runScripts: 'dangerously', url: 'http://localhost/' + file,
  });
  await wait(300); // init runs on DOMContentLoaded
  const doc = dom.window.document;
  const zh = doc.querySelector('.lang-btn[data-lang="zh"]');
  const en = doc.querySelector('.lang-btn[data-lang="en"]');
  let ok = true;
  const run = (checks, expectLang) => {
    for (const [sel, expect] of checks) {
      const el = doc.querySelector(sel);
      const got = el ? el.textContent.trim() : '(missing)';
      const pass = got === expect;
      if (!pass) ok = false;
      console.log((pass ? 'PASS' : 'FAIL'), file, '[' + expectLang + ']', sel, '=>', JSON.stringify(got), 'expect', JSON.stringify(expect));
    }
  };
  zh.click(); await wait(60); run(zhChecks, 'zh');
  en.click(); await wait(60); run(enChecks, 'en');
  console.log(file, ok ? 'OK' : 'FAIL');
  return ok;
}

(async () => {
  let all = true;
  all = (await testPage('index.html',
    [['a.rd-nav-link[href="index.html"]', '首页'],
     ['.box-product-title span[data-zh]', '自卸车 01'],
     ['a.rd-nav-link[href="contacts.html"]', '联系我们'],
     ['.lang-btn[data-lang="zh"]', '中文']],
    [['a.rd-nav-link[href="index.html"]', 'Home'],
     ['.box-product-title span[data-zh]', 'Dump Truck 01'],
     ['a.rd-nav-link[href="contacts.html"]', 'Contacts']])) && all;

  all = (await testPage('equipment.html',
    [['.title-decorate span[data-zh]', '自卸车'],
     ['.box-product-title span[data-zh]', '自卸车 01'],
     ['a.rd-nav-link[href="equipment.html"]', '产品']],
    [['.title-decorate span[data-zh]', 'Dump Truck'],
     ['.box-product-title span[data-zh]', 'Dump Truck 01'],
     ['a.rd-nav-link[href="equipment.html"]', 'Products']])) && all;

  console.log('ALL', all ? 'OK' : 'FAIL');
  process.exit(all ? 0 : 1);
})();
