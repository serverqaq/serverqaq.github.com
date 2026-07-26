# 网站维护说明

最后更新：2026-07-26

---

## 一件必须先知道的事

**不要直接编辑 `en/` 或 `zh/` 里的文件。** 那两个目录是生成出来的，下次构建会被整个覆盖。

所有内容都改 **`_src/`** 里的 6 个文件，然后运行构建。

```
_src/index.html      ← 你编辑这些
_src/works.html
_src/about.html
_src/cv.html
_src/statement.html
_src/contact.html
        │
        │  python build.py
        ↓
en/*.html   zh/*.html   根目录跳转页   sitemap.xml   robots.txt
```

`_src/` 以下划线开头，GitHub Pages 不会把它发布出去，所以源文件不会被外人访问到。

---

## 改一处文字

在 `_src/` 里找到对应元素，它长这样：

```html
<p class="artwork-card__title" data-en="Moonlight" data-cn="月光">Moonlight</p>
```

三处都要改：

- `data-en="..."` — 英文版用这个
- `data-cn="..."` — 中文版用这个
- 标签之间的文字 — **也是英文版**（英文取标签内的原文，这样书名的 `<em>` 斜体能保留）

所以改英文要同时改 `data-en` 和标签内的文字，两处保持一致。

改完执行：

```bash
python build.py
```

然后提交推送：

```bash
git add -A && git commit -m "说明改了什么" && git push origin master
```

GitHub Pages 约 1–2 分钟后生效。

---

## 加一件作品

1. 图片放进 `img/works/<系列名>/`，准备两个尺寸：
   - 大图 `xxx.jpg` —— 长边 1600px 左右，给灯箱用
   - 缩略图 `xxx-800.jpg` —— 长边 800px，给网格用
2. 在 `_src/works.html` 里复制一整块 `<div class="artwork-card ...">`，改这几处：
   - `data-src` → 大图路径
   - `<img src>` → 缩略图路径
   - `alt` → 作品描述
   - 标题和媒介的 `data-en` / `data-cn`
   - `data-category` → 决定它归到哪个筛选分类（`oil` / `china` / `print` / `iwasai` / `sketch` / `calligraphy`）
3. 竖幅作品加上 `artwork-card--portrait` 类，否则会被裁成 4:3 横构图
4. `python build.py`，提交推送

**灯箱标题不用单独填**：它直接读卡片上显示的标题和媒介，中英文自动跟随页面语言。

---

## 加一个展览 / 一条履历

改 `_src/about.html`（Awards & Exhibitions 区块）或 `_src/cv.html`。
复制一个 `<div class="timeline-item">` 改内容即可。同样记得 `data-en` / `data-cn` / 标签内文字三处。

---

## 改页面标题或搜索结果里的描述

**不在 HTML 里改** —— `<head>` 是构建时生成的。
改 `build.py` 顶部的 `PAGES` 字典：

```python
"works": dict(
    og_type="website",
    en_title="Works — Ewen Wang",
    zh_title="作品 — 王志",
    en_desc="...",     # 出现在 Google 搜索结果里
    zh_desc="...",
),
```

---

## 待办事项

| 事项 | 怎么做 |
|---|---|
| **询价表单还没启用** | 去 formspree.io 免费注册建一个 form，把 `_src/contact.html` 里的 `REPLACE_WITH_FORM_ID` 换成拿到的 ID，重新构建。在此之前表单自动隐藏、只显示邮箱，不会出现提交报错 |
| **9 件水墨还标着"无题"** | 拿到题目、年代、尺寸后改 `_src/works.html` 和 `_src/index.html` |
| **英文版 Artist Statement 缺失** | 目前 `/en/statement.html` 显示一段英文说明 + 中文原文（已用 `lang="zh-Hans"` 正确标注语言）。拿到英文正文后，替换那段说明并给各段补上 `data-en` |
| **主域名 wdanyi.com 打不开** | 阿里云加 apex A 记录，见另行说明 |

---

## 目录结构

| 路径 | 说明 |
|---|---|
| `_src/` | **内容源文件，只改这里**。不会被发布 |
| `build.py` | 构建脚本 |
| `en/` `zh/` | 生成的两套页面，不要手改 |
| `*.html`（根目录） | 生成的跳转页，把旧网址导到 `/en/`。不要手改 |
| `style.css` | 样式，含内嵌的自托管字体声明 |
| `main.js` | 交互：筛选、灯箱、移动端菜单、表单 |
| `fonts/` | 自托管字体（大陆访问不受影响） |
| `img/` | 图片 |
| `press-chuangrong-2025.html` | 已下线的创荣时代专题，保留但不进搜索引擎 |
| `sitemap.xml` `robots.txt` | 构建时生成 |
| `_originals-highres/`（在仓库外，Desktop\wdanyi 下） | 9 张水墨的高分辨率原件备份 |

---

## 出问题时

构建脚本报错，或者改完发现页面不对：

```bash
git checkout -- .
```

这条命令把所有未提交的改动还原。已经推送上线的版本可以用 `git log` 找到提交号再回滚。
