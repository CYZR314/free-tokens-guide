# 免费 Tokens 白嫖攻略站

数据驱动的静态站点：**页面是壳，内容全在 `data.json`**。改内容不用碰 HTML/CSS，计数、代金券总额、详情页都会自动跟着数据变。

收录原则：只收**能领到具体数额**的东西——注册就送的代金券、学生认证能领的大额券、长期免费的模型额度。没有具体数的不收。

## 目录结构

```
free-tokens/
├── index.html          # 页面壳：结构 + 样式 + 渲染逻辑（唯一需要写代码的文件）
├── data.json           # ★ 所有内容：站点信息、入口、攻略、更新日志
├── start.bat           # 本地预览一键启动（起 http 服务 + 开浏览器）
├── images/             # 9 张卡片封面（SVG）+ favicon
└── README.md

封面生成脚本已经统一挪到仓库根目录的 `tools/gen_covers.py`，输出仍在 `free-tokens/images/`。
```

## 本地预览

页面用 `fetch()` 读 `data.json`，所以**不能直接双击 index.html**（浏览器安全策略会拒绝读本地 JSON）。

三种方式任选：

1. **双击 `start.bat`** —— 起服务并自动开浏览器，关窗口即停止（需要装过 Python）。
2. **VS Code + Live Server 插件** —— 右键 `index.html` → Open with Live Server。
3. **命令行** —— 在本目录执行 `python -m http.server 8123`，然后开 `http://127.0.0.1:8123/`。

## data.json 结构

```jsonc
{
  "site": { ... },          // 站点文案：标题、口号、简介、免责声明、更新时间
  "apiGuide": { ... },      // 首屏右侧那张「API Key 接入示例」卡片，删掉整段就不显示
  "changelog": [ ... ],     // 保留数据，页面已不展示更新日志
  "items": [ ... ]          // ★ 全部入口，加一条就多一张卡片
}
```

### `apiGuide` 里的字段（首屏右侧那张卡）

| 字段 | 说明 |
| --- | --- |
| `title` | 卡片标题，默认「API Key 接入示例」 |
| `subtitle` | 标题下的一行说明 |
| `fields[]` | `{ label, value }`，一行一个键值对：地址（base_url）、协议、模型、API Key |
| `steps[]` | 底部编号步骤，数组里一条一个 `li` |
| `note` | 可选，卡片底部一句补充（现在是空，删了也不影响） |

整段 `apiGuide` 删掉，右侧卡片就整体不渲染，首屏回到单栏。

### 一个入口的字段

| 字段 | 必填 | 说明 |
|---|---|---|
| `id` | ✅ | 唯一标识，详情页地址是 `#/p/<id>`，只能用英文数字和连字符 |
| `name` | ✅ | 平台名，卡片标题 |
| `url` | ✅ | 官网地址，卡片上那个链接（新标签页打开） |
| `domain` | ✅ | 链接上显示的域名文字，如 `cloud.siliconflow.cn` |
| `image` | ✅ | 封面图路径，如 `images/siliconflow.svg`；文件不存在时自动降级为渐变底 + 首字母 |
| `credits` | ✅ | 能领多少，卡片和详情页都用它算：`{ type, value, label, amount }`，见下 |
| `badge` | ✅ | 封面左上角小标签：`学生专属` / `注册就送` / `免费额度` / `每天免费` |
| `level` | ✅ | 推荐力度 1–5，卡片右上角显示星星，列表按它从高到低排 |
| `note` | ✅ | 卡片上的备注文字（超过 3 行自动截断，点开详情页看全文） |
| `tags` | ✅ | 卡片底部小标签，字符串数组，2–4 个比较好看 |
| `guide` | ✅ | 二级详情页内容，见下 |

### `credits` 里的字段（卡片上那个大数字）

| 字段 | 说明 |
|---|---|
| `type` | `voucher`（现金代金券）或 `quota`（免费额度）。代金券会自动累加进首屏「可直接领的代金券 ¥316」 |
| `value` | 大字显示的值：`¥300` / `100 万 tokens` / `2000 次/天` |
| `label` | 值后面那行小字：条件、有效期、怎么到账 |
| `amount` | 仅代金券需要，数字，用于求总额 |

### `guide` 里的字段

| 字段 | 说明 |
|---|---|
| `summary` | 一句话定位，详情页标题下面那段 |
| `steps` | 怎么领：字符串数组，按顺序渲染成 1 2 3 4 5 |
| `usage` | 怎么使用：字符串数组，怎么调用、密钥填在哪、base_url 是什么 |
| `watch` | 容易踩的坑：字符串数组，带警示圆点 |
| `models` | 支持模型：字符串数组，渲染成小标签；写成「能用在哪些模型/产品」都行 |
| `modelsNote` | 支持模型下面的一句补充说明，可省略（现在 8 条都没用） |

上面四个数组留空或删掉，对应板块会自动隐藏，不会留下空白框。

### 加一个入口（复制改改即可）

```json
{
  "id": "example",
  "name": "示例平台",
  "url": "https://example.com/",
  "domain": "example.com",
  "image": "images/example.svg",
  "badge": "注册就送",
  "level": 3,
  "credits": { "type": "voucher", "value": "¥20", "label": "注册实名后到账", "amount": 20 },
  "note": "卡片上的简短备注，写清楚怎么领、坑在哪。",
  "tags": ["注册送额度", "OpenAI 兼容"],
  "guide": {
    "summary": "一句话说清这个平台是干嘛的。",
    "steps": ["第一步", "第二步", "第三步"],
    "usage": ["拿到 key 后 base_url 填什么", "怎么发第一个请求"],
    "watch": ["坑 1", "坑 2"],
    "models": ["模型 A", "模型 B"]
  }
}
```

注意 JSON 语法：字符串用双引号，最后一项后面**不能有逗号**。VS Code 里如果 JSON 报红就是这类问题。

### 其它常见改动

- **改备注**：改 `note`（卡片）和 `guide.summary`（详情页）。
- **调推荐力度**：改 `level`（1–5），列表顺序会跟着变。
- **改额度数字**：改 `credits.value` 和 `label`；如果是代金券，记得同步改 `amount`，首屏总额才会对。
- **改入口个数**：不用改，`items` 有几条就显示几。
- **改更新时间**：改 `site.updated`，顶栏「最后更新」会跟着变（更新日志已从页面移除，`changelog` 只作为数据留存）。

## 换封面

优先级从高到低：

1. **用现成图片**：把图片丢进 `images/`，`image` 字段改成它的文件名。任意格式，PNG/JPG/SVG 都行，建议 640×400。
2. **重新生成全部封面**：改仓库根目录 `tools/gen_covers.py` 里的 `PROVIDERS` 列表（名称、域名、两个渐变色），然后**在仓库根目录**运行：

   ```bash
   python tools/gen_covers.py
   ```

   颜色、字体大小、渐变方向都在脚本里能调，看脚本开头的注释。

## 部署（GitHub + Cloudflare Pages）

纯静态站，没有构建步骤。仓库只有一个目的：给 Cloudflare Pages 当源。改了 `data.json` 提交一次，网站几十秒后自动更新。

**线上地址：<https://free-tokens-guide.pages.dev>**
**源码仓库：<https://github.com/CYZR314/free-tokens-guide>**

当前这套已经配好了：GitHub 仓库 `CYZR314/free-tokens-guide` 的 `main` 分支 → Cloudflare Pages 项目 `free-tokens-guide`（构建输出目录 `free-tokens`，框架 None，构建命令留空）。日常更新只需要改 `data.json` 再 `git push`，不用重新配置任何东西。

下面这段是「从零重来一遍」的步骤，留着备查。

### 一次性配置

**第 1 步：推到 GitHub**

```bash
cd free-tokens            # 本目录
git init                  # 如果还没建仓库
git add .
git commit -m "init: 免费 tokens 白嫖攻略"
git branch -M main
git remote add origin https://github.com/<你的用户名>/<仓库名>.git
git push -u origin main
```

**第 2 步：Cloudflare Pages 连仓库**

1. 打开 <https://dash.cloudflare.com> → 左侧 **Workers & Pages** → **Create** → **Pages** → **Connect to Git**。
2. 授权 GitHub，选中上面那个仓库。
3. 构建配置照抄：

| 配置项 | 值 |
| --- | --- |
| Framework preset | `None` |
| Build command | 留空 |
| Build output directory | `free-tokens` |
| Root directory | 留空 |

4. 点 **Save and Deploy**。第一次构建约 30 秒，完事会给你一个 `xxx.pages.dev` 的地址。
5. 想绑自己的域名：项目页 **Custom domains** → **Set up a custom domain**。

### 日常更新

```bash
# 改完 data.json
git add data.json
git commit -m "update: 加了 xx 入口"
git push
```

推送后 Cloudflare 会自动重新发布，不用手动传文件。也可以直接在 GitHub 网页上点开 `free-tokens/data.json`，用铅笔图标改完提交，效果一样。

### 缓存说明

仓库根目录的 `_headers`（部署时对所有路径生效）是 Cloudflare Pages 的响应头配置：`data.json` 和 `index.html` 设成 `no-cache`，保证改完刷新就生效；`images/*` 缓存一天。别的平台不认这个文件，删掉也不影响页面。

## 免责声明

本站只做入口整理和流程记录，不代领、不转卖、不提供任何账号。额度与规则以各平台官网为准，平台随时可能调整。