#!/usr/bin/env python3
"""Fetch rendered DOM snapshots through Lexmount and run basic static accessibility checks."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

from lexapi import checksum_dir, compact, credentials, retry_call, run_stamp, utc_now, write_json

ROOT = Path(__file__).resolve().parent
FORM_TYPES = {"text", "search", "email", "url", "password", "tel", "number", "date", "time", "datetime-local", "month", "week"}
GENERIC_LINKS = {"click here", "here", "read more", "more", "learn more", "点击这里", "这里", "更多", "了解更多"}


class BasicDomParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.html_attrs: dict[str, str] = {}
        self.title = ""
        self._in_title = False
        self.images: list[dict] = []
        self.controls: list[dict] = []
        self.labels_for: set[str] = set()
        self.buttons: list[dict] = []
        self.links: list[dict] = []
        self.headings: list[dict] = []
        self._current_heading: int | None = None
        self._current_button: dict | None = None
        self._current_link: dict | None = None
        self.landmarks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_map = {key: (value or "") for key, value in attrs}
        line, offset = self.getpos()
        tag_lower = tag.lower()
        if tag_lower == "html":
            self.html_attrs = attrs_map
        elif tag_lower == "title":
            self._in_title = True
        elif tag_lower == "img":
            self.images.append({
                "src": compact(attrs_map.get("src"), 500),
                "alt": compact(attrs_map.get("alt"), 300),
                "has_alt": "alt" in attrs_map,
                "line": line,
                "column": offset,
            })
        elif tag_lower == "label" and attrs_map.get("for"):
            self.labels_for.add(attrs_map["for"])
        elif tag_lower == "input":
            input_type = (attrs_map.get("type") or "text").lower()
            if input_type not in {"hidden", "submit", "button", "reset", "image"}:
                self.controls.append({
                    "tag": "input", "type": input_type, "id": attrs_map.get("id", ""),
                    "name": attrs_map.get("name", ""), "aria_label": attrs_map.get("aria-label", ""),
                    "aria_labelledby": attrs_map.get("aria-labelledby", ""), "title": attrs_map.get("title", ""),
                    "placeholder": attrs_map.get("placeholder", ""), "line": line, "column": offset,
                })
        elif tag_lower in {"select", "textarea"}:
            self.controls.append({
                "tag": tag_lower, "type": "", "id": attrs_map.get("id", ""), "name": attrs_map.get("name", ""),
                "aria_label": attrs_map.get("aria-label", ""), "aria_labelledby": attrs_map.get("aria-labelledby", ""),
                "title": attrs_map.get("title", ""), "placeholder": "", "line": line, "column": offset,
            })
        elif tag_lower == "button":
            self._current_button = {"text": "", "aria_label": attrs_map.get("aria-label", ""), "aria_labelledby": attrs_map.get("aria-labelledby", ""), "title": attrs_map.get("title", ""), "value": attrs_map.get("value", ""), "line": line, "column": offset}
        elif tag_lower == "a":
            self._current_link = {"text": "", "href": attrs_map.get("href", ""), "aria_label": attrs_map.get("aria-label", ""), "title": attrs_map.get("title", ""), "line": line, "column": offset}
        elif tag_lower in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._current_heading = int(tag_lower[1])
        elif tag_lower in {"main", "nav", "header", "footer"} or attrs_map.get("role") in {"main", "navigation", "banner", "contentinfo"}:
            self.landmarks.append(tag_lower if tag_lower in {"main", "nav", "header", "footer"} else str(attrs_map.get("role")))

    def handle_endtag(self, tag: str) -> None:
        tag_lower = tag.lower()
        if tag_lower == "title":
            self._in_title = False
        elif tag_lower == "button" and self._current_button is not None:
            self.buttons.append(self._current_button)
            self._current_button = None
        elif tag_lower == "a" and self._current_link is not None:
            self.links.append(self._current_link)
            self._current_link = None
        elif tag_lower in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.headings.append({"level": int(tag_lower[1]), "line": self.getpos()[0]})
            self._current_heading = None

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        if self._current_button is not None:
            self._current_button["text"] += data
        if self._current_link is not None:
            self._current_link["text"] += data


def control_has_name(control: dict, labels_for: set[str]) -> bool:
    control_id = control.get("id", "")
    if control_id and control_id in labels_for:
        return True
    return any(control.get(key) for key in ["aria_label", "aria_labelledby", "title"])


def button_has_name(button: dict) -> bool:
    return bool(button.get("text", "").strip() or button.get("value", "").strip() or button.get("aria_label") or button.get("aria_labelledby") or button.get("title"))


def inspect(html: str) -> tuple[list[dict], dict]:
    parser = BasicDomParser()
    parser.feed(html)
    issues: list[dict] = []

    def add(rule: str, severity: str, message: str, **extra) -> None:
        issues.append({"rule": rule, "severity": severity, "message": message, **extra})

    if not parser.html_attrs.get("lang"):
        add("html-lang", "high", "页面 <html> 缺少 lang 属性。")
    if not parser.title.strip():
        add("page-title", "high", "页面缺少非空 <title>。")
    for image in parser.images:
        if not image["has_alt"]:
            add("image-alt", "high", "图片缺少 alt 属性。", src=image["src"], line=image["line"], column=image["column"])
    for control in parser.controls:
        if not control_has_name(control, parser.labels_for):
            label_source = control.get("placeholder") or control.get("name") or control.get("type") or control.get("tag")
            add("control-label", "medium", f"表单控件可能缺少可访问名称：{label_source}", tag=control.get("tag"), line=control["line"], column=control["column"])
    for button in parser.buttons:
        if not button_has_name(button):
            add("button-name", "high", "按钮没有可访问名称。", line=button["line"], column=button["column"])
    for link in parser.links:
        text = compact(link.get("text"), 100)
        if text.lower() in GENERIC_LINKS or text in GENERIC_LINKS:
            if not (link.get("aria_label") or link.get("title")):
                add("generic-link-text", "low", f"链接文本不够具体：{text or '(空)'}", href=link.get("href"), line=link["line"], column=link["column"])
    heading_levels = [item["level"] for item in parser.headings]
    if heading_levels and heading_levels[0] != 1:
        add("heading-order", "medium", f"第一个标题是 h{heading_levels[0]}，建议页面从 h1 开始。")
    for previous, current in zip(heading_levels, heading_levels[1:]):
        if current > previous + 1:
            add("heading-order", "medium", f"标题层级从 h{previous} 跳到 h{current}。", line=parser.headings[heading_levels.index(current)]["line"])
    h1_count = heading_levels.count(1)
    if h1_count > 1:
        add("duplicate-h1", "low", f"页面有 {h1_count} 个 h1。")

    metrics = {
        "images": len(parser.images), "images_missing_alt": sum(1 for x in parser.images if not x["has_alt"]),
        "form_controls": len(parser.controls), "controls_missing_label": sum(1 for c in parser.controls if not control_has_name(c, parser.labels_for)),
        "buttons": len(parser.buttons), "buttons_missing_name": sum(1 for b in parser.buttons if not button_has_name(b)),
        "links": len(parser.links), "generic_links": sum(1 for l in parser.links if compact(l.get("text"), 100).lower() in GENERIC_LINKS),
        "headings": len(parser.headings), "landmarks": sorted(set(parser.landmarks)),
        "has_lang": bool(parser.html_attrs.get("lang")), "lang": parser.html_attrs.get("lang", ""),
        "title": compact(parser.title, 200),
    }
    return issues, metrics


def severity_score(issues: list[dict]) -> int:
    weights = {"high": 5, "medium": 2, "low": 1}
    return sum(weights.get(item["severity"], 1) for item in issues)


def read_targets(path: Path) -> list[dict[str, str]]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))["targets"]
    seen: set[str] = set()
    targets = []
    for item in data:
        target_id = compact(item.get("id"), 80)
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", target_id) or target_id in seen:
            raise ValueError(f"invalid or duplicate target id: {target_id}")
        seen.add(target_id)
        targets.append({"id": target_id, "name": compact(item.get("name"), 120), "url": compact(item.get("url"), 1000)})
    if not targets:
        raise ValueError("no targets configured")
    return targets


def render_report(generated_at: str, rows: list[dict], endpoint: str) -> str:
    success = sum(r["ok"] for r in rows)
    high = sum(1 for r in rows for issue in r["issues"] if issue["severity"] == "high")
    medium = sum(1 for r in rows for issue in r["issue in rows".replace("issue in rows", "issues")] if issue["severity"] == "medium")
    lines = [
        "# 网页基础无障碍巡检报告",
        "",
        f"- 生成时间：`{generated_at}`",
        f"- DOM 来源：Lexmount Web Fetch `{endpoint}`",
        f"- 目标数量：{len(rows)}",
        f"- 成功抓取：{success}/{len(rows)}",
        f"- High 问题：{high}",
        f"- Medium 问题：{medium}",
        "- 范围说明：这是基础静态 DOM 巡检，不能替代 WCAG 完整审计、屏幕阅读器测试或人工可用性评估。",
        "",
        "## 总览",
        "",
        "| 页面 | 结果 | High | Medium | Low | 图片/缺 alt | 控件/疑似缺 label | 按钮/缺名称 | DOM 快照 |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        counts = row["severity_counts"]
        metrics = row["metrics"]
        lines.append(
            f"| {row['name']} | `{row['status']}` | {counts['high']} | {counts['medium']} | {counts['low']} | "
            f"{metrics.get('images', 0)}/{metrics.get('images_missing_alt', 0)} | {metrics.get('form_controls', 0)}/{metrics.get('controls_missing_label', 0)} | "
            f"{metrics.get('buttons', 0)}/{metrics.get('buttons_missing_name', 0)} | `{row.get('snapshot_relative') or '-'}` |"
        )
    lines.extend(["", "## 问题详情", ""])
    for row in rows:
        lines.extend([f"### {row['name']}", "", f"- 目标 URL：<{row['url']}>", f"- 最终 URL：{row.get('final_url') or '-'}",
                      f"- Lexmount request_id：`{row.get('request_id') or '-'}`", f"- Lexmount dom_id：`{row.get('dom_id') or '-'}`",
                      f"- 抓取引擎：`{row.get('engine') or '-'}`", f"- 页面标题：{row['metrics'].get('title') or '-'}",
                      f"- HTML lang：`{row['metrics'].get('lang') or '-'}`", ""])
        if not row["issues"]:
            lines.extend(["未发现本次基础规则覆盖的问题。", ""])
            continue
        lines.append("| 严重度 | 规则 | 位置 | 说明 |")
        lines.append("|---|---|---|---|")
        for issue in row["issues"]:
            location = f"line {issue.get('line')}, col {issue.get('column')}" if issue.get("line") else "-"
            lines.append(f"| {issue['severity']} | `{issue['rule']}` | {location} | {issue['message']} |")
        lines.append("")
    lines.extend([
        "## 核验步骤",
        "",
        "1. 打开 `dom-snapshots/*.html` 查看云端抓取到的页面结构。",
        "2. 对照 `raw/*.json` 中的 request_id、dom_id、engine 和 final_url。",
        "3. 查看 `issues.csv` 可机器处理的问题清单。",
        "4. 使用 `SHA256SUMS.txt` 核对文件完整性。",
        "",
    ])
    return "\n".join(lines)


def run(args: argparse.Namespace) -> int:
    env_path = args.env if args.env.is_absolute() else Path.cwd() / args.env
    targets_path = args.targets if args.targets.is_absolute() else Path.cwd() / args.targets
    targets = read_targets(targets_path)
    if args.only:
        wanted = {x.strip().lower() for x in args.only.split(",") if x.strip()}
        targets = [target for target in targets if target["id"].lower() in wanted]
        if not targets:
            raise ValueError("no target matched --only")
    api_key, project_id, base_url = credentials(env_path)
    if args.dry_run:
        print("DRY-RUN OK")
        print(f"targets={len(targets)}")
        print(f"base_url={base_url}")
        print(f"api_key_present={bool(api_key)}")
        print(f"project_id_present={bool(project_id)}")
        return 0
    if not api_key or not project_id:
        print("Missing LEXMOUNT_API_KEY or LEXMOUNT_PROJECT_ID", file=sys.stderr)
        return 2

    generated_at = utc_now()
    out_dir = ROOT / "artifacts" / f"run-{run_stamp()}"
    raw_dir = out_dir / "raw"
    snapshot_dir = out_dir / "dom-snapshots"
    raw_dir.mkdir(parents=True, exist_ok=True)
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    endpoint = base_url + "/v1/dom/dump"
    rows = []
    calls = []
    success = 0

    for index, target in enumerate(targets, 1):
        print(f"[{index}/{len(targets)}] {target['name']}: {target['url']}")
        payload = {"url": target["url"], "options": {"engine_preference": args.engine, "timeout_ms": 30000, "filter_scripts_styles": False}}
        response, http_status, attempts = retry_call(endpoint, payload, api_key, project_id, args.attempts, args.timeout)
        raw_path = raw_dir / f"{target['id']}.json"
        write_json(raw_path, response)
        html = response.get("html") if isinstance(response.get("html"), str) else ""
        snapshot_path = snapshot_dir / f"{target['id']}.html"
        snapshot_path.write_text(html or "", encoding="utf-8")
        issues, metrics = (inspect(html) if html else ([], {}))
        counts = {level: sum(1 for issue in issues if issue["severity"] == level) for level in ["high", "medium", "low"]}
        request_id = compact(response.get("request_id"), 100) or compact(attempts[-1].get("request_id"), 100)
        dom_id = compact(response.get("dom_id"), 100)
        raw_relative = raw_path.relative_to(out_dir).as_posix()
        snapshot_relative = snapshot_path.relative_to(out_dir).as_posix()
        row = {
            "id": target["id"], "name": target["name"], "url": target["url"], "ok": bool(html),
            "status": "inspected" if html else "dom_not_returned",
            "final_url": compact(response.get("final_url"), 1000), "target_status_code": response.get("status_code"),
            "engine": compact(response.get("engine"), 40), "request_id": request_id, "dom_id": dom_id,
            "issues": issues, "metrics": metrics, "severity_counts": counts,
            "raw_relative": raw_relative, "snapshot_relative": snapshot_relative,
            "attempts": attempts, "generated_at": generated_at,
        }
        rows.append(row)
        success += int(row["ok"])
        calls.append({
            "target_id": target["id"], "endpoint": endpoint, "url": target["url"], "http_status": http_status,
            "target_status_code": response.get("status_code"), "dom_returned": bool(html), "request_id": request_id,
            "dom_id": dom_id, "engine": row["engine"], "raw_file": raw_relative, "snapshot_file": snapshot_relative,
            "issue_counts": counts, "attempts": attempts,
        })

    report_path = out_dir / "report.md"
    summary_path = out_dir / "summary.json"
    csv_path = out_dir / "issues.csv"
    manifest_path = out_dir / "run_manifest.json"
    report_path.write_text(render_report(generated_at, rows, endpoint), encoding="utf-8")
    write_json(summary_path, {"generated_at": generated_at, "endpoint": endpoint, "scope": "basic static DOM checks", "targets": len(rows), "success": success, "results": rows})
    fields = ["page", "severity", "rule", "message", "src", "href", "tag", "url", "final_url", "line", "column", "request_id", "dom_id", "snapshot_file"]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            for issue in row["issues"]:
                writer.writerow({
                    "page": row["name"], **issue, "url": row["url"], "final_url": row["final_url"],
                    "request_id": row["request_id"], "dom_id": row["dom_id"], "snapshot_file": row["snapshot_relative"],
                })
    write_json(manifest_path, {"generated_at": generated_at, "endpoint": endpoint, "engine_preference": args.engine, "security_note": "No API key or project id is stored.", "calls": calls})
    files = [report_path, summary_path, csv_path, manifest_path, *(raw_dir / f"{r['id']}.json" for r in rows), *(snapshot_dir / f"{r['id']}.html" for r in rows)]
    checksum_dir(out_dir, files)
    print(f"Artifact directory: {out_dir}")
    final_counts = {level: sum(1 for row in rows for issue in row["issues"] if issue["severity"] == level) for level in ["high", "medium", "low"]}
    print(f"Success: {success}/{len(rows)}; high={final_counts['high']}; medium={final_counts['medium']}")
    print(f"Report: {report_path}")
    return 0 if success == len(rows) else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", type=Path, default=ROOT / ".env")
    parser.add_argument("--targets", type=Path, default=ROOT / "targets.json")
    parser.add_argument("--only", help="Comma-separated target IDs to inspect")
    parser.add_argument("--engine", default="lightmount_domstable", choices=["http", "chrome", "chrome_cdp", "lightmount_lite", "lightmount_dcl", "lightmount_domstable"])
    parser.add_argument("--attempts", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    try:
        raise SystemExit(run(parse_args()))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)




