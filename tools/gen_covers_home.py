# -*- coding: utf-8 -*-
"""
生成个人主页的封面 SVG（640x400）。
用法：python tools/gen_covers_home.py
说明：这个脚本放在站点目录之外（站点目录只留 html / json / images）。
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images")

COVERS = [
    ("tokens", "白", "免费 Tokens 白嫖攻略", "#2B4BF2", "#5C7CFF"),
    ("resume", "CV", "个人简历", "#0F766E", "#14B8A6"),
    ("b3", "三", "入口三 · 待定", "#64748B", "#94A3B8"),
    ("b4", "四", "入口四 · 待定", "#7C3AED", "#A78BFA"),
    ("b5", "五", "入口五 · 待定", "#B45309", "#F59E0B"),
    ("b6", "六", "入口六 · 待定", "#0E7490", "#22D3EE"),
]

TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" width="640" height="400" viewBox="0 0 640 400" role="img" aria-label="{title}">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{c1}"/>
      <stop offset="100%" stop-color="{c2}"/>
    </linearGradient>
    <pattern id="p" width="32" height="32" patternUnits="userSpaceOnUse">
      <path d="M32 0H0V32" fill="none" stroke="#FFFFFF" stroke-opacity="0.10" stroke-width="1"/>
    </pattern>
    <radialGradient id="r" cx="0.82" cy="0.16" r="0.62">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.28"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="640" height="400" fill="url(#g)"/>
  <rect width="640" height="400" fill="url(#p)"/>
  <rect width="640" height="400" fill="url(#r)"/>
  <text x="48" y="250" font-family="'Inter','Helvetica Neue',Arial,'Microsoft YaHei',sans-serif"
        font-size="{size}" font-weight="700" fill="#FFFFFF" fill-opacity="0.96"
        letter-spacing="-2">{char}</text>
  <text x="50" y="330" font-family="'Inter','Helvetica Neue',Arial,'Microsoft YaHei',sans-serif"
        font-size="17" fill="#FFFFFF" fill-opacity="0.86" letter-spacing="0.4">{title}</text>
</svg>
"""


def gen():
    os.makedirs(OUT, exist_ok=True)
    for slug, char, title, c1, c2 in COVERS:
        size = 128 if len(char) == 1 else 96
        svg = TEMPLATE.format(title=title, char=char, c1=c1, c2=c2, size=size)
        with open(os.path.join(OUT, slug + ".svg"), "w", encoding="utf-8") as f:
            f.write(svg)
        print("写好了 images/%s.svg  (%s)" % (slug, title))

    # favicon：小方块 + 字母 H
    fav = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <defs><linearGradient id="f" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#2B4BF2"/><stop offset="100%" stop-color="#8B5CF6"/>
  </linearGradient></defs>
  <rect width="64" height="64" rx="14" fill="url(#f)"/>
  <text x="32" y="45" text-anchor="middle" font-family="Arial,sans-serif" font-size="34"
        font-weight="700" fill="#FFFFFF">H</text>
</svg>
"""
    with open(os.path.join(OUT, "favicon.svg"), "w", encoding="utf-8") as f:
        f.write(fav)
    print("写好了 images/favicon.svg")


if __name__ == "__main__":
    gen()