#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成站点封面图（SVG）。
新增平台时：在 PROVIDERS 里加一行，然后 `python tools/gen_covers.py`。
文字颜色会按底色亮度自动在深/浅之间切换，浅底色不会被白字糊掉。
"""
import os

# id, 显示名, 主色, 辅色, 背景大字, 域名
PROVIDERS = [
    ("aliyun-student", "阿里云云工开物",       "#C2410C", "#F97316", "云", "university.aliyun.com"),
    ("siliconflow",  "硅基流动",              "#4C3CFF", "#7B61FF", "SF", "cloud.siliconflow.cn"),
    ("moonshot",     "月之暗面 Kimi",          "#111827", "#3A4150", "月", "platform.kimi.com"),
    ("bailian",      "阿里云百炼",             "#E85D00", "#FFA23A", "百", "bailian.console.aliyun.com"),
    ("volcengine",   "火山方舟",              "#0E4FD1", "#4C8DFF", "火", "console.volcengine.com/ark"),
    ("modelscope",   "魔搭 ModelScope",       "#5A3FF5", "#8E7BFF", "MS", "modelscope.cn"),
    ("zhipu",        "智谱 GLM",              "#2A46D8", "#5B7BFF", "智", "bigmodel.cn"),
    ("hunyuan",      "腾讯混元",              "#0043A8", "#2F80ED", "混", "cloud.tencent.com"),
    ("aistudio",     "Google AI Studio",     "#1A73E8", "#4FA3FF", "G",  "aistudio.google.com"),
]

FONT = "system-ui, -apple-system, 'Segoe UI', 'Microsoft YaHei', 'PingFang SC', 'Noto Sans SC', sans-serif"

TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" width="640" height="400" viewBox="0 0 640 400" role="img" aria-label="{name}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{c1}"/>
      <stop offset="1" stop-color="{c2}"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.82" cy="0.12" r="0.85">
      <stop offset="0" stop-color="#ffffff" stop-opacity="{glow_op}"/>
      <stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
    </radialGradient>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M40 0H0V40" fill="none" stroke="{ink}" stroke-opacity="0.07" stroke-width="1"/>
    </pattern>
  </defs>
  <rect width="640" height="400" fill="url(#bg)"/>
  <rect width="640" height="400" fill="url(#grid)"/>
  <rect width="640" height="400" fill="url(#glow)"/>
  <circle cx="520" cy="300" r="160" fill="{ink}" fill-opacity="0.055"/>
  <circle cx="520" cy="300" r="98" fill="none" stroke="{ink}" stroke-opacity="0.12" stroke-width="1.5"/>
  <text x="576" y="292" text-anchor="end" font-family="{font}" font-size="190" font-weight="800"
        fill="{ink}" fill-opacity="{glyph_op}" letter-spacing="-4">{glyph}</text>
  <text x="40" y="{nsize_y}" font-family="{font}" font-size="{nsize}" font-weight="700"
        fill="{ink}">{name}</text>
  <text x="40" y="368" font-family="{font}" font-size="18"
        fill="{ink}" fill-opacity="0.76">{domain}</text>
</svg>
"""


def _lum(hex_color):
    """感知亮度，0(黑) ~ 1(白)。"""
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    def lin(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = lin(r), lin(g), lin(b)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def main():
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images")
    os.makedirs(out_dir, exist_ok=True)
    for pid, name, c1, c2, glyph, domain in PROVIDERS:
        n = len(name)
        size = 44 if n <= 10 else (38 if n <= 16 else 31)
        light_bg = _lum(c2) > 0.40
        ink = "#14161c" if light_bg else "#ffffff"
        svg = TEMPLATE.format(
            name=name, c1=c1, c2=c2, glyph=glyph, domain=domain, font=FONT,
            ink=ink,
            glow_op="0.18" if light_bg else "0.30",
            glyph_op="0.10" if light_bg else "0.14",
            nsize=size, nsize_y=330 if size >= 38 else 332,
        )
        with open(os.path.join(out_dir, pid + ".svg"), "w", encoding="utf-8") as f:
            f.write(svg)
        print("wrote", pid + ".svg", "ink=" + ink)

    favicon = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="14" fill="#4C3CFF"/>
  <path d="M18 40 L28 20 L34 32 L38 26 L46 40 Z" fill="#fff" fill-opacity="0.95"/>
</svg>
"""
    with open(os.path.join(out_dir, "favicon.svg"), "w", encoding="utf-8") as f:
        f.write(favicon)
    print("done")


if __name__ == "__main__":
    main()