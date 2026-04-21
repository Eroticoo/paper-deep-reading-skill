#!/usr/bin/env python3

import re
import sys
from pathlib import Path


SECTION_NUMBERS = {
    "section1": 1,
    "section2": 2,
    "section3": 3,
    "section4": 4,
    "section5": 5,
}


SUPPORTING_BLOCKS = [
    (["Lemma", "引理"], "lemma", "missing_lemma_screenshot"),
    (["Remark", "备注"], "remark", "missing_remark_screenshot"),
    (["Assumption", "假设"], "assumption", "missing_assumption_screenshot"),
    (["Property", "性质"], "property", "missing_property_screenshot"),
]


CONTROL_CUES = [
    "状态方程",
    "系统模型",
    "误差系统",
    "观测器",
    "事件触发",
    "控制",
    "FMLSS",
    "observer",
    "error system",
    "event-triggered",
    "Lyapunov",
]


HEADING_KEYWORDS = {
    "section1": ["研究", "问题", "思路", "背景", "挑战"],
    "section2": ["方法", "技术", "主线", "理论", "解析"],
    "section3": ["仿真", "实验", "结果", "对比", "验证", "分析"],
    "section4": ["对象", "建议", "方向", "研究", "拓展"],
    "section5": ["总结", "评价", "结论"],
}


SECTION4_AUDIENCE_RULES = [
    (["入门者", "初学者", "新手"], "missing_section_4_beginner_item"),
    (["硕博学生", "研究生", "硕士生", "博士生", "硕博"], "missing_section_4_graduate_item"),
    (["教授", "导师"], "missing_section_4_professor_item"),
]


RELATION_TERMS = [
    "关系",
    "支撑",
    "铺垫",
    "引用",
    "用于",
    "提供",
    "说明",
    "约束",
    "前提",
    "闭包",
    "递推",
    "derive",
    "derived",
    "based on",
    "referring to",
    "clarify",
    "support",
    "bridge",
]


def numbered_heading(content: str, number: int) -> str | None:
    match = re.search(rf"^## {number}\. .+$", content, flags=re.M)
    return match.group(0) if match else None


def section_text(content: str, heading: str | None) -> str:
    if not heading:
        return ""
    match = re.search(rf"{re.escape(heading)}\n(.*?)(?=\n## |\Z)", content, flags=re.S)
    return match.group(1) if match else ""


def image_links_in(text: str) -> list[str]:
    return re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text)


def image_entries_in(text: str) -> list[tuple[str, str]]:
    return re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", text)


def is_remote_or_placeholder_image(link: str) -> bool:
    return bool(re.match(r"^(https?:)?//", link) or link.startswith("__PUBLIC_IMAGE_PREFIX__/"))


def has_display_math(text: str) -> bool:
    return bool(re.search(r"\$\$[\s\S]+?\$\$", text))


def extract_numbered_items(text: str) -> list[str]:
    parts = re.split(r"(?m)^\d+\.\s", text)
    return [part.strip() for part in parts[1:] if part.strip()]


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate_report.py <report.md>", file=sys.stderr)
        return 1

    report_path = Path(sys.argv[1]).expanduser().resolve()
    if not report_path.exists():
        print(f"missing_report={report_path}")
        return 1

    content = report_path.read_text(encoding="utf-8")
    failures: list[str] = []

    resolved_headings = {}
    for section_key, number in SECTION_NUMBERS.items():
        heading = numbered_heading(content, number)
        resolved_headings[section_key] = heading
        if not heading:
            failures.append(f"missing_heading=## {number}.")

    for section_key, heading in resolved_headings.items():
        if not heading:
            continue
        if not any(keyword in heading for keyword in HEADING_KEYWORDS[section_key]):
            failures.append(f"{section_key}_heading_lacks_expected_academic_terms")

    section1 = section_text(content, resolved_headings["section1"])
    section2 = section_text(content, resolved_headings["section2"])
    section3 = section_text(content, resolved_headings["section3"])
    section4 = section_text(content, resolved_headings["section4"])
    preamble = content.split("\n## ", 1)[0]
    section2_images = image_entries_in(section2)

    image_links = image_links_in(content)
    if "- 关键词：" not in content:
        failures.append("missing_keywords_metadata")
    if "- 论文标题：" in content:
        failures.append("unexpected_paper_title_metadata")
    if "- 输出时间：" in content:
        failures.append("unexpected_output_time_metadata")
    if len(image_links) < 3:
        failures.append("image_count<3")
    if not image_links_in(preamble):
        failures.append("missing_header_image")
    if not image_links_in(section2):
        failures.append("missing_section_2_image")
    if not image_links_in(section3):
        failures.append("missing_section_3_image")

    section4_items = extract_numbered_items(section4)
    if len(section4_items) != 3:
        failures.append(f"section_4_item_count={len(section4_items)}")

    if "创新点" not in content:
        failures.append("missing_innovation_points_language")

    if len(section4_items) == 3:
        for index, item in enumerate(section4_items, start=1):
            if "标题：" not in item:
                failures.append(f"section_4_item_{index}_missing_title")
            if "核心建议：" not in item:
                failures.append(f"section_4_item_{index}_missing_core_advice")
            if "数学推导难度：" not in item:
                failures.append(f"section_4_item_{index}_missing_difficulty")
        for item, (tokens, failure_name) in zip(section4_items, SECTION4_AUDIENCE_RULES):
            if not any(token in item for token in tokens):
                failures.append(failure_name)
    else:
        if "数学推导难度：" not in section4:
            failures.append("missing_difficulty_labels")
        if "标题：" not in section4:
            failures.append("missing_section_4_title_fields")
        if "核心建议：" not in section4:
            failures.append("missing_section_4_core_advice_fields")

    if "核心想法：" in section4 and "核心建议：" not in section4:
        failures.append("section_4_uses_old_core_idea_label")

    system_formula_scope = section1 + "\n" + section2
    if any(cue in system_formula_scope for cue in CONTROL_CUES) and not has_display_math(system_formula_scope):
        failures.append("missing_system_formula_block")

    supporting_tokens = [token for tokens, _, _ in SUPPORTING_BLOCKS for token in tokens]
    if any(token in section2 for token in supporting_tokens):
        if not any(term in section2 for term in RELATION_TERMS):
            failures.append("missing_supporting_block_relationship_language")

    for tokens, image_key, failure_name in SUPPORTING_BLOCKS:
        if any(token in section2 for token in tokens):
            if not any(image_key in (alt + " " + link).lower() for alt, link in section2_images):
                failures.append(failure_name)

    if any(not is_remote_or_placeholder_image(link) for link in image_links):
        failures.append("report_md_contains_local_image_paths")

    if failures:
        for item in failures:
            print(item)
        return 1

    print("report_valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
