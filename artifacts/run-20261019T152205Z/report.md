# 网页基础无障碍巡检报告

- 生成时间：`2026-10-19T15:27:52.756238Z`
- DOM 来源：Lexmount Web Fetch `https://api.lexmount.cn/v1/dom/dump`
- 目标数量：6
- 成功抓取：6/6
- High 问题：36
- Medium 问题：3
- 范围说明：这是基础静态 DOM 巡检，不能替代 WCAG 完整审计、屏幕阅读器测试或人工可用性评估。

## 总览

| 页面 | 结果 | High | Medium | Low | 图片/缺 alt | 控件/疑似缺 label | 按钮/缺名称 | DOM 快照 |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Example Domain | `inspected` | 0 | 0 | 0 | 0/0 | 0/0 | 0/0 | `dom-snapshots/example.html` |
| Python.org | `inspected` | 0 | 0 | 3 | 1/0 | 1/0 | 1/0 | `dom-snapshots/pythonorg.html` |
| Books to Scrape | `inspected` | 0 | 1 | 0 | 20/0 | 0/0 | 20/0 | `dom-snapshots/books.html` |
| W3C WAI Bad Demo Before | `inspected` | 34 | 1 | 2 | 43/33 | 1/1 | 0/0 | `dom-snapshots/wai-before.html` |
| W3C WAI Bad Demo After | `inspected` | 0 | 0 | 1 | 10/0 | 1/0 | 0/0 | `dom-snapshots/wai-after.html` |
| Selenium Dynamic Test Page | `inspected` | 2 | 1 | 0 | 0/0 | 1/1 | 0/0 | `dom-snapshots/selenium-dynamic.html` |

## 问题详情

### Example Domain

- 目标 URL：<https://example.com>
- 最终 URL：https://example.com
- Lexmount request_id：`f8c5d298-dbf9-4026-ad41-65841a408c70`
- Lexmount dom_id：`846882`
- 抓取引擎：`http`
- 页面标题：Example Domain
- HTML lang：`en`

未发现本次基础规则覆盖的问题。

### Python.org

- 目标 URL：<https://www.python.org/>
- 最终 URL：https://www.python.org/
- Lexmount request_id：`3ca1a073-e1e6-478b-8b8a-ed39f435ad87`
- Lexmount dom_id：`846894`
- 抓取引擎：`http`
- 页面标题：Welcome to Python.org
- HTML lang：`en`

| 严重度 | 规则 | 位置 | 说明 |
|---|---|---|---|
| low | `generic-link-text` | line 540, col 144 | 链接文本不够具体：Learn More |
| low | `generic-link-text` | line 740, col 223 | 链接文本不够具体：Learn more |
| low | `duplicate-h1` | - | 页面有 5 个 h1。 |

### Books to Scrape

- 目标 URL：<https://books.toscrape.com/>
- 最终 URL：https://books.toscrape.com/
- Lexmount request_id：`8e013dff-e2fb-4978-86c7-c127e3d32ab3`
- Lexmount dom_id：`846892`
- 抓取引擎：`http`
- 页面标题：All products | Books to Scrape - Sandbox
- HTML lang：`en-us`

| 严重度 | 规则 | 位置 | 说明 |
|---|---|---|---|
| medium | `heading-order` | line 684, col None | 标题层级从 h1 跳到 h3。 |

### W3C WAI Bad Demo Before

- 目标 URL：<https://www.w3.org/WAI/demos/bad/before/home.html>
- 最终 URL：https://www.w3.org/WAI/demos/bad/before/home.html
- Lexmount request_id：`f522cf2b-eec1-47d5-b8a8-26cc4c9ff84b`
- Lexmount dom_id：`846885`
- 抓取引擎：`http`
- 页面标题：Welcome to CityLights! [Inaccessible Home Page]
- HTML lang：`-`

| 严重度 | 规则 | 位置 | 说明 |
|---|---|---|---|
| high | `html-lang` | - | 页面 <html> 缺少 lang 属性。 |
| high | `image-alt` | line 173, col 60 | 图片缺少 alt 属性。 |
| high | `image-alt` | line 174, col 56 | 图片缺少 alt 属性。 |
| high | `image-alt` | line 175, col 61 | 图片缺少 alt 属性。 |
| high | `image-alt` | line 178, col 56 | 图片缺少 alt 属性。 |
| high | `image-alt` | line 183, col 37 | 图片缺少 alt 属性。 |
| high | `image-alt` | line 184, col 38 | 图片缺少 alt 属性。 |
| high | `image-alt` | line 185, col 37 | 图片缺少 alt 属性。 |
| high | `image-alt` | line 208, col 60 | 图片缺少 alt 属性。 |
| high | `image-alt` | line 233, col 65 | 图片缺少 alt 属性。 |
| high | `image-alt` | line 244, col 61 | 图片缺少 alt 属性。 |
| high | `image-alt` | line 245, col 80 | 图片缺少 alt 属性。 |
| high | `image-alt` | line 248, col 303 | 图片缺少 alt 属性。 |
| high | `image-alt` | line 251, col 61 | 图片缺少 alt 属性。 |
| high | `image-alt` | line 254, col 303 | 图片缺少 alt 属性。 |
| high | `image-alt` | line 257, col 61 | 图片缺少 alt 属性。 |
| high | `image-alt` | line 260, col 319 | 图片缺少 alt 属性。 |
| high | `image-alt` | line 263, col 61 | 图片缺少 alt 属性。 |
| high | `image-alt` | line 266, col 319 | 图片缺少 alt 属性。 |
| high | `image-alt` | line 269, col 61 | 图片缺少 alt 属性。 |
| high | `image-alt` | line 273, col 23 | 图片缺少 alt 属性。 |
| high | `image-alt` | line 280, col 40 | 图片缺少 alt 属性。 |
| high | `image-alt` | line 281, col 40 | 图片缺少 alt 属性。 |
| high | `image-alt` | line 282, col 40 | 图片缺少 alt 属性。 |
| high | `image-alt` | line 301, col 23 | 图片缺少 alt 属性。 |
| high | `image-alt` | line 305, col 81 | 图片缺少 alt 属性。 |
| high | `image-alt` | line 306, col 61 | 图片缺少 alt 属性。 |
| high | `image-alt` | line 312, col 35 | 图片缺少 alt 属性。 |
| high | `image-alt` | line 327, col 61 | 图片缺少 alt 属性。 |
| high | `image-alt` | line 333, col 30 | 图片缺少 alt 属性。 |
| high | `image-alt` | line 354, col 57 | 图片缺少 alt 属性。 |
| high | `image-alt` | line 357, col 75 | 图片缺少 alt 属性。 |
| high | `image-alt` | line 358, col 71 | 图片缺少 alt 属性。 |
| high | `image-alt` | line 359, col 76 | 图片缺少 alt 属性。 |
| medium | `control-label` | line 187, col 10 | 表单控件可能缺少可访问名称：select |
| low | `generic-link-text` | line 298, col 279 | 链接文本不够具体：Click here |
| low | `generic-link-text` | line 298, col 444 | 链接文本不够具体：Click here |

### W3C WAI Bad Demo After

- 目标 URL：<https://www.w3.org/WAI/demos/bad/after/home.html>
- 最终 URL：https://www.w3.org/WAI/demos/bad/after/home.html
- Lexmount request_id：`7f8cd492-3bd0-41fa-b701-f79fdbfb4e24`
- Lexmount dom_id：`846886`
- 抓取引擎：`http`
- 页面标题：Welcome to CityLights! [Accessible Home Page]
- HTML lang：`en`

| 严重度 | 规则 | 位置 | 说明 |
|---|---|---|---|
| low | `duplicate-h1` | - | 页面有 2 个 h1。 |

### Selenium Dynamic Test Page

- 目标 URL：<https://www.selenium.dev/selenium/web/dynamic.html>
- 最终 URL：https://www.selenium.dev/selenium/web/dynamic.html
- Lexmount request_id：`0b19b9d3-2c1a-4b27-b5c5-2bad965c17f7`
- Lexmount dom_id：`846887`
- 抓取引擎：`http`
- 页面标题：-
- HTML lang：`-`

| 严重度 | 规则 | 位置 | 说明 |
|---|---|---|---|
| high | `html-lang` | - | 页面 <html> 缺少 lang 属性。 |
| high | `page-title` | - | 页面缺少非空 <title>。 |
| medium | `control-label` | line 37, col 4 | 表单控件可能缺少可访问名称：text |

## 核验步骤

1. 打开 `dom-snapshots/*.html` 查看云端抓取到的页面结构。
2. 对照 `raw/*.json` 中的 request_id、dom_id、engine 和 final_url。
3. 查看 `issues.csv` 可机器处理的问题清单。
4. 使用 `SHA256SUMS.txt` 核对文件完整性。
