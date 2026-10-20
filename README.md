# Lexmount A11y Inspector

用 Lexmount Web Fetch 抓取公开网页 DOM 快照，并对图片 alt、表单 label、按钮名称、标题层级、页面 lang/title、泛化链接文本做基础无障碍巡检。

## 目标

- Example Domain
- Python.org
- Books to Scrape
- W3C WAI Bad Demo Before
- W3C WAI Bad Demo After
- Selenium Dynamic Test Page

## 运行

```powershell
# 本地校验
python .\a11y_inspector.py --dry-run --env ..\lexmount-status-watch\.env

# 真实运行
python .\a11y_inspector.py --engine http --env ..\lexmount-status-watch\.env
```

## 最终运行

- 运行完成：2026-10-19 23:27 左右，北京时间
- 成功抓取：6/6
- 输出目录：`artifacts/run-20261019T152205Z`
- High 问题：36
- Medium 问题：3
- Low 问题：6

重点结果：

| 页面 | High | Medium | Low |
|---|---:|---:|---:|
| Example Domain | 0 | 0 | 0 |
| Python.org | 0 | 0 | 3 |
| Books to Scrape | 0 | 1 | 0 |
| W3C WAI Before | 34 | 1 | 2 |
| W3C WAI After | 0 | 0 | 1 |
| Selenium Dynamic Test Page | 2 | 1 | 0 |

## 输出

- `report.md`
- `issues.csv`
- `summary.json`
- `run_manifest.json`
- `raw/*.json`
- `dom-snapshots/*.html`
- `SHA256SUMS.txt`

## 范围与局限

这是基础静态 DOM 巡检，不能替代 WCAG 完整审计、屏幕阅读器测试或人工可用性评估。规则只覆盖常见、可自动检测的问题，不判定整站是否无障碍。

## 后续

可增加颜色对比、焦点顺序、ARIA 使用检查、键盘路径巡检和 Cloud Browser 截图证据。
