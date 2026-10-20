# 提交草稿：网页基础无障碍巡检报告

## 作品名称

```text
Lexmount A11y Inspector
```

## 想解决什么问题

```text
很多网站存在图片缺少 alt、控件缺少可访问名称、按钮没有文本、标题层级跳跃等问题。这些问题影响屏幕阅读器用户，但开发阶段经常被忽略。需要一份低成本、可复现的基础巡检报告。
```

## 怎么做的，云平台参与了什么

```text
脚本按 targets.json 读取六个公开页面，调用 Lexmount Web Fetch POST /v1/dom/dump 抓取云端 DOM。本地脚本保存 HTML 快照和 raw JSON，然后检查 html lang、页面标题、图片 alt、表单控件名称、按钮名称、标题层级和泛化链接文本，输出 report.md、issues.csv、summary.json、run_manifest.json 和 SHA256SUMS.txt。
```

## 结果与发现

```text
运行完成：2026-10-19 23:27 左右，北京时间。
6 个页面全部成功抓取，发现 High 36、Medium 3、Low 6。

重点对比：
- W3C WAI “Before” 演示页：34 个 high 问题；
- W3C WAI “After” 演示页：0 个 high 问题。

这说明基础规则能有效识别无障碍改进前后差异。Selenium 动态测试页也发现 2 个 high 问题。
```

## 作品演示或运行材料链接

```text
[待填：GitHub / 网盘链接]
```

## 材料访问说明　选填

```text
材料包含 a11y_inspector.py、targets.json、最终运行目录 artifacts/run-20261019T152205Z、report.md、issues.csv、dom-snapshots/*.html、raw/*.json、run_manifest.json 和 SHA256SUMS.txt。不包含 .env、API Key 或 Project ID。
```

## 是否基于已有项目或教程

```text
是。参考 Lexmount Web Fetch Dump DOM 官方文档和 W3C WAI 公开演示页；检查规则、脚本实现、目标清单、真实运行和成果组织均为本次活动新增。
```

## 作者与联系信息

```text
实际作者：[待填]
分工：独立完成选题、规则设计、脚本开发、真实运行、报告核验和材料整理，贡献 100%。
联系邮箱：[待填]
```
