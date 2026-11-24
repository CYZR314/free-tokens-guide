# 我的站点仓库

一个仓库里放两个纯静态站点：

- **`home/`** —— 我的收藏夹：单页应用，一个 `index.html` + 一个 `data.json` + 一个 `images/`，六个入口全在同一个页面里切换，不会跳转。
- **`free-tokens/`** —— 已经上线的「免费 Tokens 白嫖攻略」独立站，还在线上跑着。

## 目录

```
.
├── README.md                  # 本文件：整个仓库怎么用
│
├── home/                      # 站点① 我的收藏夹（单文件站点）
│   ├── index.html             #   ★ 唯一的页面：六个入口 + Tokens + 简历 + 占位页
│   ├── data.json              #   ★ 唯一的数据：site / entries / tokens / resume
│   └── images/                #   封面图 + favicon
│
├── free-tokens/               # 站点② 免费 Tokens 白嫖攻略（已上线，保持原样）
│   ├── index.html
│   ├── data.json              #   Tokens 内容的主副本
│   ├── images/
│   ├── _headers               #   Cloudflare 缓存头
│   ├── start.bat              #   单独预览这个站（8123 端口）
│   └── README.md
│
├── tools/                     # 所有脚本，都在仓库根目录运行
│   ├── gen_covers.py          #   生成 9 张 Tokens 封面（两个站点各写一份）
│   ├── gen_covers_home.py     #   生成收藏夹自己的 6 张封面
│   └── sync_tokens_data.py    #   把 free-tokens/data.json 同步进 home/data.json
│
├── push.bat                   # 双击 = 提交 + 上传（推荐）
├── push.py                    # 上传脚本：git push → 失败自动改走 GitHub API
├── preview.bat                # 双击 = 本地预览（8124 端口）
├── .secrets/                  # 本地 GitHub token（已被 .gitignore 忽略）
└── .preview/                  # 截图草稿（已被 .gitignore 忽略）
```

线上地址：<https://free-tokens-guide.pages.dev>（Cloudflare Pages 的构建目录是 `free-tokens/`，`home/` 目前不参与部署）

## 收藏夹里有什么

`home/index.html` 用 hash 路由在同一个页面里切换视图，点任何入口都不会加载新页面：

| 地址 | 显示什么 | 数据在哪 |
| --- | --- | --- |
| `#/` | 六个入口卡片 | `data.json` 的 `entries` |
| `#/tokens` | 免费 Tokens 白嫖攻略（原页面） | `data.json` 的 `tokens.items` |
| `#/tokens/<id>` | 单条攻略：怎么领 / 怎么使用 / 容易踩的坑 / 支持模型 | 同上，每条 item |
| `#/resume` | 简历 | `data.json` 的 `resume` |
| `#/blank/b3` … `b6` | 占位页 | `data.json` 的 `entries` |

`data.json` 的四个顶层字段各管一块，互不影响：

```jsonc
{
  "site":    { "title": "我的收藏夹", "intro": "…", "footnote": "…" },
  "entries": [ { "id": "tokens", "title": "…", "href": "#/tokens", "image": "images/tokens.svg", "tag": "已上线", "status": "ready" } ],
  "tokens":  { "site": {…}, "apiGuide": {…}, "items": [ … 9 条 … ] },
  "resume":  { "meta": {…}, "profile": {…}, "about": "…", "blocks": [ … ] }
}
```

## 日常怎么改

| 想改什么 | 改哪个文件 | 然后 |
| --- | --- | --- |
| 六个入口的标题、说明、链接 | `home/data.json` → `entries` | 刷新页面 |
| 免费 Tokens 的入口、额度、攻略 | `free-tokens/data.json` | 跑一次 `python tools/sync_tokens_data.py`，再双击 `push.bat` |
| 简历内容 | `home/data.json` → `resume` | 刷新页面 |
| 占位页要换成真页面 | `home/data.json` 里那条的 `href` | 改成 `#/xxx`，再在 `index.html` 的路由里加一个分支 |
| 封面图 | `python tools/gen_covers.py` 或直接换 `images/` 里的图 | 建议 640×400 |

**为什么 Tokens 内容要同步一次**：`free-tokens/` 那个站还单独在线，所以它有自己的 `data.json`（主副本）；收藏夹是单文件站点，数据只能放在 `home/data.json` 里。改完主副本跑一次同步脚本，两份就一致了。

## 本地预览

- `preview.bat` → <http://127.0.0.1:8124/> 或 <http://127.0.0.1:8124/home/>
- `free-tokens/start.bat` → <http://127.0.0.1:8123/>（只预览 Tokens 站）

页面用 `fetch` 读 json，**直接双击 html 打不开**（浏览器不让 `file://` 读 json），必须走本地服务。

## 上传（为什么用 push.bat 而不是 VS Code 的推送按钮）

这台机器访问 `github.com:443` 时通时不通，VS Code 的「同步」只走 `git push`，经常报 `Failed to connect to github.com:443`。双击 `push.bat` 会：

1. 清理 Windows 保留名垃圾文件（`CON` 之类会让 `git add` 失败）
2. 自动提交（message 用当前时间）
3. 先试 `git push`
4. 不通就改走 GitHub API 上传（`api.github.com` 一直通），提交 sha 与本地完全一致

传上去 30–60 秒后 Cloudflare Pages 自动重建，线上即刻生效。

## 重新生成封面

```bash
python tools/gen_covers.py        # → free-tokens/images/*.svg + home/images/*.svg（9 张 Tokens 封面）
python tools/gen_covers_home.py   # → home/images/*.svg（收藏夹自己的 6 张）
python tools/sync_tokens_data.py  # → 把 Tokens 数据同步进 home/data.json
```

改脚本里的 `PROVIDERS` / `COVERS` 列表就能加平台、换配色。图片也可以直接换成随便什么 PNG/JPG，建议 640×400。