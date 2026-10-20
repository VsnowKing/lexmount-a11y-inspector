# 方案：网页基础无障碍巡检报告

## 任务

把多个公开页面抓成 DOM 快照，自动检查常见无障碍问题，生成带行号、规则、严重度和来源证据的报告。

## Lexmount 参与

每个页面调用：

```http
POST https://api.lexmount.cn/v1/dom/dump
```

Lexmount 返回渲染后的 HTML、`request_id`、`dom_id`、`engine` 和 `final_url`。本地脚本保存 DOM 快照，并执行基础规则检查。

## 检查规则

- `<html lang>`
- `<title>`
- 图片 `alt`
- 表单控件 label / aria-label / aria-labelledby / title
- 按钮 accessible name
- 标题顺序与 h1 数量
- 泛化链接文本

## 真实结果

- 成功：6/6
- High：36
- Medium：3
- Low：6
- W3C “Before” 演示页发现 34 个 high 问题；
- 同站 “After” 演示页 high 问题为 0，说明规则能区分明显改进。

## 成果

- `issues.csv`
- `report.md`
- `summary.json`
- `run_manifest.json`
- `dom-snapshots/*.html`
- `raw/*.json`
- `SHA256SUMS.txt`

## 核验方式

1. 打开 `dom-snapshots/*.html`；
2. 对照 raw JSON 中的 `dom_id` 和 `request_id`；
3. 查看 `issues.csv` 中的规则和位置；
4. 用 `SHA256SUMS.txt` 校验材料。

## 后续

可增加 Cloud Browser 截图、键盘焦点测试、颜色对比、ARIA 检查和 WCAG 映射。
