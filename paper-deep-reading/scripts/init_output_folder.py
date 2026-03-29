#!/usr/bin/env python3

import argparse
import re
from pathlib import Path


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "paper-report"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a dedicated output folder for a paper deep-reading report.",
    )
    parser.add_argument("pdf_path", help="Path to the source PDF")
    parser.add_argument(
        "--output-root",
        required=True,
        help="Root directory where the report folder should be created",
    )
    parser.add_argument(
        "--slug",
        help="Optional folder slug; defaults to a slugified PDF stem",
    )
    args = parser.parse_args()

    pdf_path = Path(args.pdf_path).expanduser().resolve()
    output_root = Path(args.output_root).expanduser().resolve()
    folder_name = args.slug or slugify(pdf_path.stem)
    report_dir = output_root / folder_name
    images_dir = report_dir / "images"
    report_path = report_dir / "report.md"

    report_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)

    if not report_path.exists():
        template = f"""# 论文标题的标准学术中文翻译待补充

![论文抬头：标题与作者](待补充)

- 关键词：待补充
- DOI / 论文链接：待补充

## 1. 研究背景、问题定义与核心思路
### 1.1 研究动机与关键挑战

### 1.2 方法框架与核心思路

### 1.3 主要创新点

## 2. 核心方法与技术主线解析
### 2.1 整体技术路线

### 2.2 关键技术块解析

## 3. 仿真结果与对比分析
### 3.1 仿真设置与对比对象

### 3.2 主要结果与对比说明

## 4. 后续研究方向
1. 标题：  
   *核心想法：*  
   数学推导难度：  
2. 标题：  
   *核心想法：*  
   数学推导难度：  
3. 标题：  
   *核心想法：*  
   数学推导难度：  

## 5. 总结与评价
"""
        report_path.write_text(template, encoding="utf-8")

    print(f"report_dir={report_dir}")
    print(f"images_dir={images_dir}")
    print(f"report_path={report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
