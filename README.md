# 我的站点仓库

一个仓库、一个 Cloudflare Pages 项目（输出目录 = 仓库根目录），同时提供两个站点：

| 地址 | 是什么 | 文件在哪 |
| --- | --- | --- |
| `/` | **我的收藏夹**：一个 `index.html` + 一个 `data.json` + 一个 `images/`，六个入口在同一页面里切换，不跳转 | 仓库根目录 |
线上地址：<https://c7314r.xyz>
## 目录

```
.
├── index.html                 # ★ 收藏夹唯一的页面：六个入口 + Tokens + 简历 + 占位页
├── data.json                  # ★ 收藏夹唯一的数据：site / entries / tokens / resume
├── images/                    # ★ 封面图 + favicon（16 张）
└── tools/                     # 工具都放这里，双击 .bat 即可
    ├── push.bat               #   双击 = 提交 + 上传（推荐）
    ├── push.py                #   上传脚本：git push → 失败自动改走 GitHub API
    ├── preview.bat            #   双击 = 本地预览（8124 端口）
    ├── gen_covers.py          #   生成 9 张 Tokens 封面（根 images/ 和 free-tokens/images/ 各写一份）
    ├── gen_covers_home.py     #   生成收藏夹自己的 6 张封面
    ├── sync_tokens_data.py    #   把 free-tokens/data.json 同步进根 data.json 的 tokens 段
    └── .secrets/              #   本地 GitHub token（已被 .gitignore 忽略）
```

