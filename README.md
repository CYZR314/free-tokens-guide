# 免费 Tokens 白嫖攻略

纯静态站点，页面代码在 [`free-tokens/`](free-tokens/) 目录里。

- 线上地址：<https://free-tokens-guide.pages.dev>
- 站点入口：[`free-tokens/index.html`](free-tokens/index.html)
- 数据文件：[`free-tokens/data.json`](free-tokens/data.json) —— 加一个入口、改额度、改攻略，都只动这个文件
- 使用说明：[`free-tokens/README.md`](free-tokens/README.md)

## 更新流程（推荐用 push.bat）

改完 `free-tokens/data.json` 保存，然后**双击仓库根目录的 `push.bat`**，它会：

1. 把改动自动提交（message 用当前时间）
2. 先试 `git push`
3. 连不上 github.com 时，自动改用 GitHub API 上传（这台机器访问 github.com:443 时通时不通，但 `api.github.com` 一直通）

传上去 30–60 秒后 Cloudflare Pages 自动重新构建，线上即刻生效。

> 为什么不直接用 VS Code 的「同步/推送」按钮：它只会走 `git push`，而这台机器到 `github.com` 的连接经常被重置，于是就报 `Failed to connect to github.com:443`。这不是 SSH 或密码的问题，是网络。`push.py` 里那条 API 备用通道就是为这个准备的。

也可以用浏览器改：在 GitHub 打开 `free-tokens/data.json`，点右上角铅笔，改完提交，效果一样。

### 相关文件

| 文件 | 作用 |
| --- | --- |
| `push.bat` | 双击即可上传（内部调用 `push.py`） |
| `push.py` | 上传脚本：先 git push，失败自动改走 GitHub API |
| `.secrets/github_token` | 本地存 GitHub token，一行；已被 `.gitignore` 忽略，别提交 |

## 本地预览

Windows 下双击 `free-tokens/start.bat`，会在 `http://127.0.0.1:8123/` 打开页面。

## 目录

```
.
├── push.bat                 # 一键上传
├── push.py                  # 上传脚本（git push + API 备用通道）
├── free-tokens/             # 站点本体（Cloudflare 的构建目录就是这里）
│   ├── index.html
│   ├── data.json            # 所有内容都在这里
│   ├── images/              # 封面 SVG
│   ├── tools/               # 封面生成脚本
│   ├── start.bat            # 本地预览
│   └── README.md            # data.json 字段说明
└── .secrets/                # 本地凭据（不提交）
```