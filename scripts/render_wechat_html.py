#!/usr/bin/env python3

import argparse
import html
import re
from pathlib import Path


STYLE = """
body {
  margin: 0;
  background: #f6f2e9;
  color: #1f1f1f;
  font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
}
.wechat-shell {
  max-width: 820px;
  margin: 0 auto;
  padding: 40px 20px 80px;
}
.wechat-article {
  background: #fffdf8;
  border: 1px solid #e7dcc5;
  box-shadow: 0 18px 60px rgba(84, 60, 28, 0.08);
  padding: 42px 34px 52px;
}
.article-title {
  margin: 0 0 18px;
  font-size: 34px;
  line-height: 1.28;
  letter-spacing: 0.02em;
  color: #2d2417;
}
.meta-box {
  margin: 0 0 28px;
  padding: 16px 18px;
  background: #fbf5e8;
  border-left: 4px solid #b58b45;
}
.meta-item {
  margin: 6px 0;
  font-size: 15px;
  line-height: 1.8;
}
.meta-label {
  font-weight: 700;
  color: #6d5223;
}
h2, h3, h4 {
  color: #3d2d14;
}
h2 {
  margin: 34px 0 14px;
  padding-left: 12px;
  border-left: 5px solid #b58b45;
  font-size: 28px;
  line-height: 1.35;
}
h3 {
  margin: 24px 0 10px;
  font-size: 22px;
  line-height: 1.4;
}
h4 {
  margin: 18px 0 8px;
  font-size: 18px;
}
p, li {
  font-size: 16px;
  line-height: 1.9;
}
p {
  margin: 14px 0;
}
ul, ol {
  margin: 14px 0;
  padding-left: 1.5em;
}
blockquote {
  margin: 18px 0;
  padding: 12px 16px;
  background: #f7f1e4;
  border-left: 4px solid #ccb07a;
}
code {
  padding: 0.1em 0.35em;
  background: #f1eadc;
  border-radius: 4px;
  font-family: "SFMono-Regular", Consolas, monospace;
  font-size: 0.92em;
}
pre {
  margin: 18px 0;
  padding: 14px 16px;
  overflow-x: auto;
  background: #f1eadc;
  border-radius: 8px;
}
pre code {
  padding: 0;
  background: transparent;
}
.image-block {
  margin: 22px 0;
  text-align: center;
}
.image-block img {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  border: 1px solid #eadfcb;
}
.image-caption {
  margin-top: 10px;
  color: #6c604d;
  font-size: 14px;
}
a {
  color: #1d63c4;
  text-decoration: none;
}
strong {
  color: #2e2415;
}
hr {
  margin: 28px 0;
  border: none;
  border-top: 1px solid #eadfcb;
}
"""


def inline_format(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", escaped)
    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', escaped)
    return escaped


def is_ordered_item(line: str) -> bool:
    return bool(re.match(r"^\d+\.\s+", line))


def is_unordered_item(line: str) -> bool:
    return bool(re.match(r"^[-*]\s+", line))


def render_image(line: str) -> str | None:
    match = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", line)
    if not match:
        return None
    alt, src = match.groups()
    alt = html.escape(alt)
    src = html.escape(src)
    caption = f'<div class="image-caption">{alt}</div>' if alt else ""
    return f'<figure class="image-block"><img src="{src}" alt="{alt}" />{caption}</figure>'


def consume_list(lines: list[str], index: int) -> tuple[str, int]:
    ordered = is_ordered_item(lines[index])
    tag = "ol" if ordered else "ul"
    items: list[str] = []
    while index < len(lines):
        line = lines[index]
        if ordered and not is_ordered_item(line):
            break
        if not ordered and not is_unordered_item(line):
            break
        content = re.sub(r"^(\d+\.\s+|[-*]\s+)", "", line)
        items.append(f"<li>{inline_format(content.strip())}</li>")
        index += 1
    return f"<{tag}>\n" + "\n".join(items) + f"\n</{tag}>", index


def render_body(lines: list[str], start_index: int) -> str:
    blocks: list[str] = []
    paragraph: list[str] = []
    index = start_index
    in_code = False
    code_lines: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            text = " ".join(part.strip() for part in paragraph if part.strip())
            if text:
                blocks.append(f"<p>{inline_format(text)}</p>")
        paragraph = []

    while index < len(lines):
        raw = lines[index]
        line = raw.rstrip("\n")
        stripped = line.strip()

        if stripped.startswith("```"):
            flush_paragraph()
            if in_code:
                code_html = html.escape("\n".join(code_lines))
                blocks.append(f"<pre><code>{code_html}</code></pre>")
                code_lines = []
                in_code = False
            else:
                in_code = True
            index += 1
            continue

        if in_code:
            code_lines.append(line)
            index += 1
            continue

        if not stripped:
            flush_paragraph()
            index += 1
            continue

        image_html = render_image(stripped)
        if image_html:
            flush_paragraph()
            blocks.append(image_html)
            index += 1
            continue

        if stripped == "---":
            flush_paragraph()
            blocks.append("<hr />")
            index += 1
            continue

        heading = re.match(r"^(#{2,6})\s+(.*)$", stripped)
        if heading:
            flush_paragraph()
            level = len(heading.group(1))
            blocks.append(f"<h{level}>{inline_format(heading.group(2).strip())}</h{level}>")
            index += 1
            continue

        if stripped.startswith(">"):
            flush_paragraph()
            blocks.append(f"<blockquote>{inline_format(stripped.lstrip('>').strip())}</blockquote>")
            index += 1
            continue

        if is_ordered_item(stripped) or is_unordered_item(stripped):
            flush_paragraph()
            list_html, index = consume_list([ln.strip() for ln in lines], index)
            blocks.append(list_html)
            continue

        paragraph.append(stripped)
        index += 1

    flush_paragraph()
    return "\n".join(blocks)


def extract_header(lines: list[str]) -> tuple[str, dict[str, str], int]:
    title = "论文精读"
    metadata: dict[str, str] = {}
    index = 0

    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip()
        index = 1

    while index < len(lines):
        stripped = lines[index].strip()
        if not stripped:
            index += 1
            continue
        meta = re.match(r"^- ([^：:]+)[：:]\s*(.*)$", stripped)
        if not meta:
            break
        metadata[meta.group(1).strip()] = meta.group(2).strip()
        index += 1

    return title, metadata, index


def render_document(markdown_text: str) -> str:
    lines = markdown_text.splitlines()
    title, metadata, body_start = extract_header(lines)
    meta_html = ""
    if metadata:
        items = []
        preferred_order = ["关键词", "DOI / 论文链接"]
        seen = set()
        for key in preferred_order:
            if key in metadata:
                seen.add(key)
                items.append(
                    f'<div class="meta-item"><span class="meta-label">{html.escape(key)}：</span>{inline_format(metadata[key])}</div>'
                )
        for key, value in metadata.items():
            if key in seen:
                continue
            items.append(
                f'<div class="meta-item"><span class="meta-label">{html.escape(key)}：</span>{inline_format(value)}</div>'
            )
        meta_html = '<section class="meta-box">\n' + "\n".join(items) + "\n</section>"

    body_html = render_body(lines, body_start)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(title)}</title>
  <style>{STYLE}</style>
</head>
<body>
  <div class="wechat-shell">
    <article class="wechat-article">
      <h1 class="article-title">{html.escape(title)}</h1>
      {meta_html}
      {body_html}
    </article>
  </div>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render a paper deep-reading markdown report into a WeChat-ready HTML article.",
    )
    parser.add_argument("report_md", help="Path to report.md")
    parser.add_argument("output_html", help="Path to output HTML")
    args = parser.parse_args()

    report_path = Path(args.report_md).expanduser().resolve()
    output_path = Path(args.output_html).expanduser().resolve()

    markdown_text = report_path.read_text(encoding="utf-8")
    html_text = render_document(markdown_text)
    output_path.write_text(html_text, encoding="utf-8")
    print(f"wrote={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
