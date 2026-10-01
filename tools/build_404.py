#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成根目录 404.html（页面未找到 / Not Found）。

用途：
- GitHub Pages 会在任何找不到的路径（含 /products/p999.html、/dump-trucks2.html 等）
  自动返回站点根目录的 404.html，作为“无产品 / 无分类”的统一兜底页。
- 页面风格与全站一致：从 index.html 抽取 header（RD Navbar）与 footer+scripts 拼接，
  正文复用 about-us/contacts 的 parallax 面包屑写法。

数据驱动 / 模板化：
- header、footer、脚本引入均来自 index.html，导航改了重跑即同步。
- 正文为固定双语文案，可在此文件修改。

运行：
    python tools/build_404.py
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INDEX = os.path.join(ROOT, "index.html")
OUT = os.path.join(ROOT, "404.html")


def _extract(src, start_marker, end_marker, end_inclusive=True, not_found_ok=False):
    """在 src 中截取 [start_marker, end_marker] 区间。"""
    i = src.find(start_marker)
    if i < 0:
        if not_found_ok:
            return ""
        raise RuntimeError(f"找不到起始标记: {start_marker!r}")
    j = src.find(end_marker, i)
    if j < 0:
        if not_found_ok:
            return src[i:]
        raise RuntimeError(f"找不到结束标记: {end_marker!r}")
    end = j + len(end_marker) if end_inclusive else j
    return src[i:end]


def build():
    html = open(INDEX, encoding="utf-8").read()

    # 1) header：从 <body> 到 </header>（含 RD Navbar）
    header = _extract(html, "<body>", "</header>")

    # 2) footer + 脚本：从 <!-- Page Footer--> 到文件末尾
    footer = _extract(html, "<!-- Page Footer-->", "</html>", end_inclusive=False) + "</html>"

    # 3) 404 正文：与 about-us/contacts 一致的 parallax 面包屑 + 404 区块
    body = """      <section class="parallax-container" data-parallax-img="images/title-bg.jpg">
        <div class="parallax-content breadcrumbs-custom context-dark">
          <div class="container">
            <div class="row justify-content-center">
              <div class="col-12 col-lg-9">
                <h2 class="breadcrumbs-custom-title"><span data-zh="页面未找到">Page Not Found</span></h2>
                <ul class="breadcrumbs-custom-path">
                  <li><a href="index.html">Home</a></li>
                  <li class="active"><span data-zh="404 错误">404 Error</span></li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>
      <section class="section section-xl bg-gray-700">
        <div class="container text-center">
          <div class="row justify-content-center">
            <div class="col-md-10 col-lg-8">
              <div style="font-size:120px;line-height:1;font-weight:700;color:#fff;" class="wow fadeIn">404</div>
              <h3 class="title-decorate mt-3"><span data-zh="页面不存在">This page could not be found</span></h3>
              <p class="text-opacity-80" data-zh="抱歉，您访问的产品或分类不存在，或已被移动。请浏览我们的产品目录，或返回首页继续。">Sorry, the product or category you are looking for does not exist or has been moved. Browse our product catalog or return to the homepage.</p>
              <div class="group-md mt-4">
                <a class="button button-lg button-primary" href="equipment.html" data-zh="浏览产品">Browse Products</a>
                <a class="button button-lg button-gray-4" href="index.html" data-zh="返回首页">Back to Home</a>
              </div>
            </div>
          </div>
        </div>
      </section>
"""

    out = (
        "<!DOCTYPE html>\n"
        '<html class="wide wow-animation" lang="en">\n'
        "  <head>\n"
        "    <title>404 - Page Not Found - EquipSupply</title>\n"
        '    <meta name="description" content="The product or category you are looking for could not be found. Browse the full EquipSupply heavy-duty truck, semi-trailer and construction machinery catalog." data-zh="您访问的产品或分类不存在。浏览 EquipSupply 全系列重卡、半挂车与工程机械产品目录。">\n'
        '    <meta charset="utf-8">\n'
        '    <meta name="viewport" content="width=device-width, height=device-height, initial-scale=1.0">\n'
        '    <meta http-equiv="X-UA-Compatible" content="IE=edge">\n'
        '    <link rel="icon" href="images/favicon.ico" sizes="any">\n'
        '    <link rel="icon" type="image/png" sizes="32x32" href="images/favicon-32.png">\n'
        '    <link rel="icon" type="image/png" sizes="16x16" href="images/favicon-16.png">\n'
        '    <link rel="apple-touch-icon" href="images/apple-touch-icon.png">\n'
        '    <link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css?family=Roboto:300,300i,400,700,900i%7CRoboto+Condensed:300,400,700">\n'
        '    <link rel="stylesheet" href="css/bootstrap.css">\n'
        '    <link rel="stylesheet" href="css/fonts.css">\n'
        '    <link rel="stylesheet" href="css/style.css">\n'
        '    <style>.ie-panel{display: none;background: #212121;padding: 10px 0;box-shadow: 3px 3px 5px 0 rgba(0,0,0,.3);clear: both;text-align:center;position: relative;z-index: 1;} html.ie-10 .ie-panel, html.lt-ie-10 .ie-panel {display: block;}</style>\n'
        "  </head>\n"
        + header
        + body
        + footer
    )

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(out)
    print("已生成", os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    build()
