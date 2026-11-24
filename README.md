# 我的站点仓库

一个仓库里放两个纯静态站点：已经上线的「免费 Tokens 白嫖攻略」，和正在本地做的「我的收藏夹」。

## 目录

```
.
├── README.md                  # 本文件：整个仓库怎么用
├── free-tokens/               # 站点① 免费 Tokens 白嫖攻略（已上线）
│   ├── index.html             #   页面壳：结构 + 样式 + 渲染逻辑
│   ├── data.json              #   ★ 全部内容都在这里
│   ├── images/                #   9 张卡片封面 + favicon
│   ├── _headers               #   Cloudflare 缓存头
│   ├── start.bat              #   单独预览这个站（8123 端口）
│   └── README.md              #   data.json 字段说明
│
├── home/                      # 站点② 我的收藏夹（本地，待部署）
│   ├── index.html             #   一级界面：六个入口
│   ├── data.json              #   ★ 六个入口的标题/说明/链接
│   ├── images/                #   六张封面 + favicon
│   ├── tokens/                #   入口①：免费 Tokens（free-tokens 的原样副本）
│   │   ├── index.html         #     与 free-tokens/index.html 完全相同
│   │   ├── data.json          #     与 free-tokens/data.json 完全相同
│   │   ├── images/
│   │   └── view.html          #     二级外壳：返回条 + iframe
│   ├── resume/                #   入口②：个人简历
│   │   ├── index.html
│   │   └── data.json          #   ★ 简历内容都在这里
│   └── blank/index.html       #   入口③-⑥ 共用的占位页
│
├── tools/                     # 所有脚本，都在仓库根目录运行
│   ├── gen_covers.py          #   生成 free-tokens/images 的封面
│   ├── gen_covers_home.py     #   生成 home/images 的封面
│   └── sync_tokens.py         #   把 free-tokens 的页面同步进 home/tokens
│
├── push.bat                   # 双击 = 提交 + 上传（推荐）
├── push.py                    # 上传脚本：git push → 失败自动改走 GitHub API
├── preview.bat                # 双击 = 本地预览 home（8124 端口）
├── .secrets/                  # 本地 GitHub token（已被 .gitignore 忽略）
└── .preview/                  # 截图草稿（已被 .gitignore 忽略）
```

线上地址：<https://free-tokens-guide.pages.dev>（Cloudflare Pages 的构建目录是 `free-tokens/`，`home/` 目前不参与部署）

## 日常怎么改

| 想改什么 | 改哪个文件 | 然后 |
| --- | --- | --- |
| 免费 Tokens 站的入口、额度、攻略 | `free-tokens/data.json` | 双击 `push.bat` |
| 收藏夹首页的六个入口 | `home/data.json` | 双击 `preview.bat` 看效果 |
| 简历内容 | `home/resume/data.json` | 双击 `preview.bat` 看效果 |
| 占位页要指向的页面 | `home/data.json` 里那条的 `href` | 同上 |

在 `free-tokens/` 里改完数据后，**跑一次 `python tools/sync_tokens.py`**，收藏夹里的那份副本才会跟上（脚本会告诉你哪些文件更新了）。

## 本地预览

- `preview.bat` → <http://127.0.0.1:8124/home/>（整个仓库根目录起服务，两个站都能看）
- `free-tokens/start.bat` → <http://127.0.0.1:8123/>（只预览 Tokens 站）

两个站都用 `fetch` 读 json，**直接双击 html 打不开**（浏览器不让 `file://` 读 json），必须走本地服务。

## 上传（为什么用 push.bat 而不是 VS Code 的推送按钮）

这台机器访问 `github.com:443` 时通时不通，VS Code 的「同步」只走 `git push`，经常报 `Failed to connect to github.com:443`。双击 `push.bat` 会：

1. 清理 Windows 保留名垃圾文件（`CON` 之类会让 `git add` 失败）
2. 自动提交（message 用当前时间）
3. 先试 `git push`
4. 不通就改走 GitHub API 上传（`api.github.com` 一直通），提交 sha 与本地完全一致

传上去 30–60 秒后 Cloudflare Pages 自动重建，线上即刻生效。也可以在 GitHub 网页上直接编辑 `free-tokens/data.json`，效果一样。

## 重新生成封面

```bash
python tools/gen_covers.py        # → free-tokens/images/*.svg
python tools/gen_covers_home.py   # → home/images/*.svg
```

改脚本里的 `PROVIDERS` / `COVERS` 列表就能加平台、换配色。图片也可以直接换成随便什么 PNG/JPG，建议 640×400。