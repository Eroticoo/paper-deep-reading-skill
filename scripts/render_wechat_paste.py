#!/usr/bin/env python3

import argparse
import json
import re
from pathlib import Path
from urllib.parse import quote, urlparse


PLACEHOLDER_PREFIX = "__PUBLIC_IMAGE_PREFIX__"
INLINE_FORMULA_MAX_LEN = 72


def load_mapping(path: str | None) -> dict[str, str]:
    if not path:
        return {}
    mapping_path = Path(path).expanduser().resolve()
    return json.loads(mapping_path.read_text(encoding="utf-8"))


def build_remote_url(local_path: str, prefix: str, mapping: dict[str, str]) -> str:
    normalized = local_path.replace("\\", "/")
    if re.match(r"^(https?:)?//", normalized):
        parsed = urlparse(normalized if normalized.startswith("http") else f"https:{normalized}")
        filename = Path(parsed.path).name
    else:
        filename = Path(normalized).name
    if normalized in mapping:
        return mapping[normalized]
    if filename in mapping:
        return mapping[filename]
    return prefix.rstrip("/") + "/" + quote(filename)


def split_code_fences(text: str) -> list[tuple[str, str]]:
    parts: list[tuple[str, str]] = []
    chunks = re.split(r"(```.*?```)", text, flags=re.S)
    for chunk in chunks:
        if not chunk:
            continue
        if chunk.startswith("```"):
            parts.append(("code", chunk))
        else:
            parts.append(("text", chunk))
    return parts


def cleanup_generated_formula_pngs(images_dir: Path) -> None:
    for image_path in images_dir.glob("wechat_math_*.png"):
        image_path.unlink(missing_ok=True)


def replace_block_math(text: str, images_dir: Path, prefix: str, mapping: dict[str, str]) -> str:
    pattern = re.compile(r"(?<!\\)\$\$(.+?)(?<!\\)\$\$", flags=re.S)

    def repl(match: re.Match[str]) -> str:
        formula = match.group(1).strip()
        return f"\n\n$$\n{formula}\n$$\n\n"

    return pattern.sub(repl, text)


def replace_inline_math(text: str, images_dir: Path, prefix: str, mapping: dict[str, str]) -> str:
    pattern = re.compile(r"(?<!\\)\$(?!\$)(.+?)(?<!\\)\$(?!\$)")

    def repl(match: re.Match[str]) -> str:
        formula = match.group(1).strip()
        if should_keep_inline(formula):
            return match.group(0)
        return f"\n\n$$\n{formula}\n$$\n\n"

    return pattern.sub(repl, text)


def should_keep_inline(formula: str) -> bool:
    if not formula or "\n" in formula or len(formula) > INLINE_FORMULA_MAX_LEN:
        return False
    if formula.count("=") > 1:
        return False
    return True


def replace_images(text: str, prefix: str, mapping: dict[str, str], force_remote_rewrite: bool = False) -> str:
    pattern = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")

    def repl(match: re.Match[str]) -> str:
        alt, path = match.groups()
        if re.match(r"^(https?:)?//", path) and not force_remote_rewrite:
            return match.group(0)
        remote_url = build_remote_url(path, prefix, mapping)
        return f"![{alt}]({remote_url})"

    return pattern.sub(repl, text)


def cleanup_metadata(text: str) -> str:
    lines = []
    for line in text.splitlines():
        if line.startswith("- 源 PDF："):
            continue
        lines.append(line)
    return "\n".join(lines).strip() + "\n"


def write_manifest(images_dir: Path, output_dir: Path, prefix: str) -> None:
    manifest_path = output_dir / "wechat_assets_manifest.txt"
    rows = []
    for image_path in sorted(images_dir.glob("*")):
        if image_path.is_file():
            remote = prefix.rstrip("/") + "/" + quote(image_path.name)
            rows.append(f"{image_path.name}\t{remote}")
    manifest_path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a WeChat-paste markdown file with public image URLs and preserved LaTeX formulas.",
    )
    parser.add_argument("report_md", help="Path to report.md")
    parser.add_argument("output_md", help="Path to wechat_paste.md")
    parser.add_argument(
        "--image-url-prefix",
        default=PLACEHOLDER_PREFIX,
        help=(
            "Public URL prefix that hosts the contents of the local images directory. "
            "Defaults to a placeholder prefix for handoff workflows."
        ),
    )
    parser.add_argument(
        "--mapping-file",
        help="Optional JSON mapping from local relative path or filename to full remote URL",
    )
    parser.add_argument(
        "--rewrite-report-images",
        action="store_true",
        help="Rewrite image links in report.md to the same remote URLs used for wechat_paste.md",
    )
    parser.add_argument(
        "--force-rewrite-remote-images",
        action="store_true",
        help="Rewrite existing remote image links to the provided prefix too, useful when moving from @main to a commit-pinned CDN URL",
    )
    args = parser.parse_args()

    report_path = Path(args.report_md).expanduser().resolve()
    output_path = Path(args.output_md).expanduser().resolve()
    report_dir = report_path.parent
    images_dir = report_dir / "images"
    mapping = load_mapping(args.mapping_file)
    text = report_path.read_text(encoding="utf-8")
    cleanup_generated_formula_pngs(images_dir)

    if args.rewrite_report_images:
        rewritten_report = replace_images(
            text,
            args.image_url_prefix,
            mapping,
            force_remote_rewrite=args.force_rewrite_remote_images,
        )
        report_path.write_text(rewritten_report, encoding="utf-8")
        text = rewritten_report

    parts = []
    for part_type, part_text in split_code_fences(text):
        if part_type == "code":
            parts.append(part_text)
            continue
        updated = replace_block_math(part_text, images_dir, args.image_url_prefix, mapping)
        updated = replace_inline_math(updated, images_dir, args.image_url_prefix, mapping)
        updated = replace_images(
            updated,
            args.image_url_prefix,
            mapping,
            force_remote_rewrite=args.force_rewrite_remote_images,
        )
        parts.append(updated)

    final_text = cleanup_metadata("".join(parts))
    output_path.write_text(final_text, encoding="utf-8")
    write_manifest(images_dir, output_path.parent, args.image_url_prefix)
    print(f"wrote={output_path}")
    if args.image_url_prefix == PLACEHOLDER_PREFIX:
        print("placeholder_prefix_in_use=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
