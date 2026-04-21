#!/usr/bin/env python3

from __future__ import annotations

import io
import re
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import fitz  # type: ignore
except ImportError:  # pragma: no cover
    import pymupdf as fitz  # type: ignore

from PIL import Image

try:
    import pytesseract  # type: ignore
    from pytesseract import Output as TesseractOutput  # type: ignore
except ImportError:  # pragma: no cover
    pytesseract = None
    TesseractOutput = None


USAGE = """usage:
  pdf_tool.py probe <pdf>
  pdf_tool.py extract-text <pdf> <output>
  pdf_tool.py find <pdf> <query> [--mode auto|pdf|ocr] [--max N]
  pdf_tool.py render-page <pdf> <page-index> <output> [--scale S]
  pdf_tool.py snapshot-query <pdf> <query> <match-index> <output> [--preset exact|generic|theorem|figure|figure-column|table] [--mode auto|pdf|ocr] [--scale S]
  pdf_tool.py snapshot-rect <pdf> <page-index> <x> <y> <w> <h> <output> [--preset exact|generic|theorem|figure|figure-column|table] [--scale S]
"""


@dataclass
class MatchRecord:
    page_index: int
    rect: fitz.Rect
    text: str
    source: str


class ToolError(Exception):
    pass


def expanded_path(path: str) -> str:
    return str(Path(path).expanduser().resolve())


def ensure_parent(path: str) -> None:
    Path(path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)


def load_document(path: str) -> fitz.Document:
    resolved = expanded_path(path)
    try:
        return fitz.open(resolved)
    except Exception as exc:  # pragma: no cover - library-specific failure
        raise ToolError(f"failed_to_open_pdf={resolved}") from exc


def load_page(document: fitz.Document, page_index: int) -> fitz.Page:
    try:
        return document.load_page(page_index)
    except Exception as exc:
        raise ToolError(f"failed_to_open_page={page_index}") from exc


def option_value(arguments: list[str], name: str, default_value: str) -> str:
    try:
        index = arguments.index(name)
    except ValueError:
        return default_value
    if index + 1 < len(arguments):
        return arguments[index + 1]
    return default_value


def page_bounds_pdf(page: fitz.Page) -> fitz.Rect:
    rect = page.rect
    return fitz.Rect(0, 0, rect.width, rect.height)


def pymupdf_to_pdf_rect(rect: fitz.Rect, page_height: float) -> fitz.Rect:
    return fitz.Rect(rect.x0, page_height - rect.y1, rect.x1, page_height - rect.y0)


def pdf_to_pymupdf_rect(rect: fitz.Rect, page_height: float) -> fitz.Rect:
    return fitz.Rect(rect.x0, page_height - rect.y1, rect.x1, page_height - rect.y0)


def intersect_rect(a: fitz.Rect, b: fitz.Rect) -> fitz.Rect:
    x0 = max(a.x0, b.x0)
    y0 = max(a.y0, b.y0)
    x1 = min(a.x1, b.x1)
    y1 = min(a.y1, b.y1)
    if x1 < x0 or y1 < y0:
        return fitz.Rect(0, 0, 0, 0)
    return fitz.Rect(x0, y0, x1, y1)


def render_page_image(page: fitz.Page, crop_rect_pdf: fitz.Rect | None, scale: float) -> Image.Image:
    bounds_pdf = page_bounds_pdf(page)
    target_rect_pdf = intersect_rect(crop_rect_pdf or bounds_pdf, bounds_pdf)
    clip = pdf_to_pymupdf_rect(target_rect_pdf, page.rect.height)
    pixmap = page.get_pixmap(matrix=fitz.Matrix(scale, scale), clip=clip, alpha=False)
    return Image.open(io.BytesIO(pixmap.tobytes("png"))).copy()


def write_png(image: Image.Image, output_path: str) -> None:
    resolved = expanded_path(output_path)
    ensure_parent(resolved)
    image.save(resolved, format="PNG")


def safe_print(line: str) -> None:
    sys.stdout.buffer.write((line + "\n").encode("utf-8", errors="replace"))


def print_match(index: int, match: MatchRecord) -> None:
    text = match.text.replace("\n", " ").replace("\t", " ")
    safe_print(
        f"match={index} source={match.source} page={match.page_index} "
        f"x={match.rect.x0:.1f} y={match.rect.y0:.1f} w={match.rect.width:.1f} h={match.rect.height:.1f} "
        f"text={text}"
    )


def two_column_crop_bounds(page_bounds: fitz.Rect, anchor: fitz.Rect) -> tuple[float, float]:
    if page_bounds.width < 500:
        return (page_bounds.x0 + 24, page_bounds.x1 - 24)
    midpoint = (page_bounds.x0 + page_bounds.x1) / 2
    gutter = 16
    if (anchor.x0 + anchor.x1) / 2 < midpoint:
        return (page_bounds.x0 + 24, midpoint - gutter)
    return (midpoint + gutter, page_bounds.x1 - 24)


def is_same_column(page_bounds: fitz.Rect, reference: fitz.Rect, candidate: fitz.Rect) -> bool:
    if page_bounds.width < 500:
        return True
    midpoint = (page_bounds.x0 + page_bounds.x1) / 2
    return ((reference.x0 + reference.x1) / 2 < midpoint) == ((candidate.x0 + candidate.x1) / 2 < midpoint)


def match_rects(document: fitz.Document, page_index: int, query: str) -> list[fitz.Rect]:
    page = load_page(document, page_index)
    page_height = page.rect.height
    results = []
    for rect in page.search_for(query):
        results.append(pymupdf_to_pdf_rect(rect, page_height))
    return results


def page_text_blocks_pdf(page: fitz.Page) -> list[tuple[fitz.Rect, str]]:
    page_height = page.rect.height
    blocks: list[tuple[fitz.Rect, str]] = []
    for block in page.get_text("blocks"):
        x0, y0, x1, y1, text, *_ = block
        text = text.strip()
        if not text:
            continue
        rect = pymupdf_to_pdf_rect(fitz.Rect(x0, y0, x1, y1), page_height)
        blocks.append((rect, text))
    blocks.sort(key=lambda item: (-item[0].y1, item[0].x0))
    return blocks


def normalize_query(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def first_line(text: str) -> str:
    return text.strip().splitlines()[0].strip()


def starts_with_prefixes(text: str, prefixes: tuple[str, ...]) -> bool:
    return text.startswith(prefixes)


def block_heading_matches(page: fitz.Page, query: str) -> list[tuple[fitz.Rect, str]]:
    query_norm = normalize_query(query)
    if not query_norm:
        return []

    matches: list[tuple[fitz.Rect, str]] = []
    for rect, text in page_text_blocks_pdf(page):
        line = first_line(text)
        if not line:
            continue
        first_norm = normalize_query(line)
        if first_norm.startswith(query_norm):
            matches.append((rect, text))
    return matches


def is_section_like_text(text: str) -> bool:
    line = first_line(text)
    if re.match(r"^\d+\.\s", line):
        return True
    if re.match(r"^\d+(\.\d+)+\s", line):
        return True
    if line in {"CONCLUSION", "REFERENCES", "Conclusion", "References"}:
        return True
    return False


GENERIC_BLOCK_PREFIXES = (
    "Algorithm",
    "Objective",
    "Problem",
    "System Model",
    "Architecture",
    "Framework",
    "Loss",
    "Optimization",
)


def theorem_blocks_crop(
    page: fitz.Page,
    page_bounds: fitz.Rect,
    anchor: fitz.Rect,
) -> fitz.Rect | None:
    blocks = [
        (rect, text)
        for rect, text in page_text_blocks_pdf(page)
        if is_same_column(page_bounds, anchor, rect)
    ]
    if not blocks:
        return None

    anchor_index = None
    for index, (rect, _) in enumerate(blocks):
        if intersect_rect(rect, anchor).get_area() > 0:
            anchor_index = index
            break
    if anchor_index is None:
        return None

    stop_prefixes = (
        "Proof",
        "Remark",
        "Theorem",
        "Lemma",
        "Proposition",
        "Corollary",
        "Assumption",
        "Property",
        "Definition",
        "Algorithm",
        "Problem",
    )

    included: list[fitz.Rect] = []
    previous_rect: fitz.Rect | None = None
    for index in range(anchor_index, len(blocks)):
        rect, text = blocks[index]
        first_line = text.strip().splitlines()[0].strip()
        if index > anchor_index:
            if first_line.startswith(stop_prefixes) or is_section_like_text(text):
                break
            if previous_rect is not None and previous_rect.y0 - rect.y1 > 60:
                break
        included.append(rect)
        previous_rect = rect

    if not included:
        return None

    column_left, column_right = two_column_crop_bounds(page_bounds, anchor)
    left = max(page_bounds.x0 + 14, column_left - 8)
    right = min(page_bounds.x1 - 10, column_right + 26)
    bottom = max(page_bounds.y0 + 6, min(rect.y0 for rect in included) + 1)
    top = min(page_bounds.y1 - 10, max(rect.y1 for rect in included) + 2)
    return intersect_rect(fitz.Rect(left, bottom, right, top), page_bounds)


def anchor_block_index(blocks: list[tuple[fitz.Rect, str]], anchor: fitz.Rect) -> int | None:
    for index, (rect, _) in enumerate(blocks):
        if intersect_rect(rect, anchor).get_area() > 0:
            return index
    return None


def generic_blocks_crop(
    page: fitz.Page,
    page_bounds: fitz.Rect,
    anchor: fitz.Rect,
) -> fitz.Rect | None:
    blocks = [
        (rect, text)
        for rect, text in page_text_blocks_pdf(page)
        if is_same_column(page_bounds, anchor, rect)
    ]
    if not blocks:
        return None

    anchor_index = anchor_block_index(blocks, anchor)
    if anchor_index is None:
        return None

    anchor_line = first_line(blocks[anchor_index][1])
    if not starts_with_prefixes(anchor_line, GENERIC_BLOCK_PREFIXES):
        return None

    stop_prefixes = (
        "Proof",
        "Remark",
        "Theorem",
        "Lemma",
        "Proposition",
        "Corollary",
        "Assumption",
        "Property",
        "Definition",
        "Algorithm",
        "Problem",
        "Objective",
        "System Model",
        "Architecture",
        "Framework",
        "Loss",
        "Optimization",
        "Fig.",
        "Figure",
        "Table",
        "Tab.",
        "TABLE",
    )

    included: list[fitz.Rect] = []
    previous_rect: fitz.Rect | None = None
    for index in range(anchor_index, len(blocks)):
        rect, text = blocks[index]
        line = first_line(text)
        if index > anchor_index:
            if starts_with_prefixes(line, stop_prefixes) or is_section_like_text(text):
                break
            if previous_rect is not None and previous_rect.y0 - rect.y1 > 60:
                break
        included.append(rect)
        previous_rect = rect

    if not included:
        return None

    left = max(page_bounds.x0 + 10, min(rect.x0 for rect in included) - 10)
    right = min(page_bounds.x1 - 10, max(rect.x1 for rect in included) + 12)
    bottom = max(page_bounds.y0 + 8, min(rect.y0 for rect in included) - 6)
    top = min(page_bounds.y1 - 8, max(rect.y1 for rect in included) + 4)
    return intersect_rect(fitz.Rect(left, bottom, right, top), page_bounds)


def nearest_stop_below_rect(
    document: fitz.Document,
    page_index: int,
    page_bounds: fitz.Rect,
    anchor: fitz.Rect,
    queries: list[str],
    max_distance: float,
) -> fitz.Rect | None:
    candidates: list[fitz.Rect] = []
    for query in queries:
        for rect in match_rects(document, page_index, query):
            if not is_same_column(page_bounds, anchor, rect):
                continue
            if rect.y1 >= anchor.y0:
                continue
            if anchor.y0 - rect.y1 > max_distance:
                continue
            candidates.append(rect)
    if not candidates:
        return None
    return max(candidates, key=lambda rect: rect.y1)


def nearest_stop_above_rect(
    document: fitz.Document,
    page_index: int,
    page_bounds: fitz.Rect,
    anchor: fitz.Rect,
    queries: list[str],
    max_distance: float,
) -> fitz.Rect | None:
    candidates: list[fitz.Rect] = []
    for query in queries:
        for rect in match_rects(document, page_index, query):
            if not is_same_column(page_bounds, anchor, rect):
                continue
            if rect.y0 <= anchor.y1:
                continue
            if rect.y0 - anchor.y1 > max_distance:
                continue
            candidates.append(rect)
    if not candidates:
        return None
    return min(candidates, key=lambda rect: rect.y0)


def crop_rect(
    preset: str,
    page_bounds: fitz.Rect,
    anchor: fitz.Rect,
    document: fitz.Document | None = None,
    page_index: int | None = None,
) -> fitz.Rect:
    theorem_stop_queries = [
        "Proof",
        "Remark",
        "Theorem",
        "Lemma",
        "Proposition",
        "Corollary",
        "Assumption",
        "Property",
        "Definition",
        "Algorithm",
        "Problem",
    ]
    caption_queries = ["Fig.", "Figure", "Table", "Tab.", "TABLE"]
    section_stop_queries = ["CONCLUSION", "REFERENCES", "Conclusion", "References"]

    if preset == "exact":
        return intersect_rect(anchor, page_bounds)

    if preset == "theorem":
        if document is not None and page_index is not None:
            page = load_page(document, page_index)
            block_crop = theorem_blocks_crop(page, page_bounds, anchor)
            if block_crop is not None:
                if block_crop.height >= 45:
                    return block_crop
                margin_x = 90
                margin_y = 90
                return intersect_rect(
                    fitz.Rect(
                        anchor.x0 - margin_x,
                        anchor.y0 - margin_y,
                        anchor.x1 + margin_x,
                        anchor.y1 + margin_y,
                    ),
                    page_bounds,
                )
        column_left, column_right = two_column_crop_bounds(page_bounds, anchor)
        left = max(page_bounds.x0 + 14, column_left - 8)
        right = min(page_bounds.x1 - 10, column_right + 26)
        bottom = max(page_bounds.y0 + 10, anchor.y0 - 340)
        if document is not None and page_index is not None:
            stop_rect = nearest_stop_below_rect(
                document,
                page_index,
                page_bounds,
                anchor,
                theorem_stop_queries,
                420,
            )
            if stop_rect is not None:
                bottom = max(bottom, stop_rect.y1 + 1)
        top = min(page_bounds.y1 - 10, anchor.y1 + 2)
        return intersect_rect(fitz.Rect(left, bottom, right, top), page_bounds)

    if preset == "figure-column":
        column_left, column_right = two_column_crop_bounds(page_bounds, anchor)
        left = max(page_bounds.x0 + 14, column_left - 8)
        right = min(page_bounds.x1 - 10, column_right + 26)
        bottom = max(page_bounds.y0 + 10, anchor.y0 - 10)
        top = min(page_bounds.y1 - 10, anchor.y1 + 220)
        if document is not None and page_index is not None:
            previous_caption = nearest_stop_above_rect(
                document,
                page_index,
                page_bounds,
                anchor,
                caption_queries,
                360,
            )
            if previous_caption is not None:
                top = min(top, previous_caption.y0 - 12)
        return intersect_rect(fitz.Rect(left, bottom, right, top), page_bounds)

    if preset == "figure":
        left = page_bounds.x0 + 18
        right = page_bounds.x1 - 18
        bottom = max(page_bounds.y0 + 10, anchor.y0 - 10)
        top = min(page_bounds.y1 - 10, anchor.y1 + 220)
        return intersect_rect(fitz.Rect(left, bottom, right, top), page_bounds)

    if preset == "table":
        left, right = two_column_crop_bounds(page_bounds, anchor)
        bottom = max(page_bounds.y0 + 10, anchor.y0 - 102)
        top = min(page_bounds.y1 - 10, anchor.y1 + 28)
        if document is not None and page_index is not None:
            previous_caption = nearest_stop_above_rect(
                document,
                page_index,
                page_bounds,
                anchor,
                caption_queries,
                260,
            )
            if previous_caption is not None:
                top = min(top, previous_caption.y0 - 12)
            next_section = nearest_stop_below_rect(
                document,
                page_index,
                page_bounds,
                anchor,
                section_stop_queries,
                220,
            )
            if next_section is not None:
                bottom = max(bottom, next_section.y1 + 10)
        return intersect_rect(fitz.Rect(left, bottom, right, top), page_bounds)

    if preset == "generic" and document is not None and page_index is not None:
        page = load_page(document, page_index)
        block_crop = generic_blocks_crop(page, page_bounds, anchor)
        if block_crop is not None:
            return block_crop

    margin_x = 90
    margin_y = 90
    rect = fitz.Rect(anchor.x0 - margin_x, anchor.y0 - margin_y, anchor.x1 + margin_x, anchor.y1 + margin_y)
    return intersect_rect(rect, page_bounds)


def pdf_text_matches(document: fitz.Document, query: str, max_count: int) -> list[MatchRecord]:
    records: list[MatchRecord] = []
    for page_index in range(document.page_count):
        page = load_page(document, page_index)
        for rect, text in block_heading_matches(page, query):
            records.append(MatchRecord(page_index=page_index, rect=rect, text=text, source="pdf-block"))
            if len(records) >= max_count:
                return records

    for page_index in range(document.page_count):
        page = load_page(document, page_index)
        page_height = page.rect.height

        for rect in page.search_for(query):
            pdf_rect = pymupdf_to_pdf_rect(rect, page_height)
            if any(
                item.page_index == page_index and intersect_rect(item.rect, pdf_rect).get_area() > 0
                for item in records
            ):
                continue
            text = page.get_textbox(rect).strip() or query
            records.append(MatchRecord(page_index=page_index, rect=pdf_rect, text=text, source="pdf"))
            if len(records) >= max_count:
                return records
    return records


def require_tesseract() -> None:
    if pytesseract is None or TesseractOutput is None:
        raise ToolError("ocr_unavailable=install_pytesseract_and_tesseract")


def ocr_observations(page: fitz.Page, scale: float = 2.0) -> list[tuple[fitz.Rect, str]]:
    require_tesseract()
    image = render_page_image(page, None, scale)
    data = pytesseract.image_to_data(image, output_type=TesseractOutput.DICT)
    observations: list[tuple[fitz.Rect, str]] = []
    for index, text in enumerate(data["text"]):
        text = text.strip()
        if not text:
            continue
        width = int(data["width"][index])
        height = int(data["height"][index])
        if width <= 0 or height <= 0:
            continue
        left = float(data["left"][index]) / scale
        top = float(data["top"][index]) / scale
        right = left + width / scale
        bottom = top + height / scale
        pdf_rect = pymupdf_to_pdf_rect(fitz.Rect(left, top, right, bottom), page.rect.height)
        observations.append((pdf_rect, text))
    return observations


def ocr_matches(document: fitz.Document, query: str, max_count: int) -> list[MatchRecord]:
    query_lower = query.lower()
    records: list[MatchRecord] = []
    for page_index in range(document.page_count):
        page = load_page(document, page_index)
        for rect, text in ocr_observations(page):
            if query_lower in text.lower():
                records.append(MatchRecord(page_index=page_index, rect=rect, text=text, source="ocr"))
                if len(records) >= max_count:
                    return records
    return records


def collect_matches(document: fitz.Document, query: str, mode: str, max_count: int) -> list[MatchRecord]:
    if mode == "pdf":
        return pdf_text_matches(document, query, max_count)
    if mode == "ocr":
        return ocr_matches(document, query, max_count)
    direct = pdf_text_matches(document, query, max_count)
    if direct:
        return direct
    try:
        return ocr_matches(document, query, max_count)
    except ToolError:
        return []


def page_text(document: fitz.Document, page_index: int, use_ocr_fallback: bool) -> str:
    page = load_page(document, page_index)
    text = page.get_text("text").strip()
    if text:
        return text
    if not use_ocr_fallback:
        return ""
    try:
        observations = ocr_observations(page)
    except ToolError:
        return ""
    observations.sort(key=lambda item: (-((item[0].y0 + item[0].y1) / 2), item[0].x0))
    return "\n".join(text for _, text in observations)


def run() -> None:
    arguments = sys.argv
    if len(arguments) < 3:
        raise ToolError(USAGE.strip())

    command = arguments[1]

    if command == "probe":
        document = load_document(arguments[2])
        safe_print(f"pdf={expanded_path(arguments[2])}")
        safe_print(f"page_count={document.page_count}")
        title = (document.metadata or {}).get("title", "").strip()
        if title:
            safe_print(f"title={title}")
        return

    if command == "extract-text":
        if len(arguments) < 4:
            raise ToolError("extract-text requires <pdf> <output>")
        document = load_document(arguments[2])
        output = expanded_path(arguments[3])
        ensure_parent(output)
        sections = []
        for page_index in range(document.page_count):
            text = page_text(document, page_index, use_ocr_fallback=True)
            sections.append(f"===== Page {page_index + 1} =====\n{text}")
        Path(output).write_text("\n\n".join(sections), encoding="utf-8")
        safe_print(f"wrote={output}")
        return

    if command == "find":
        if len(arguments) < 4:
            raise ToolError("find requires <pdf> <query>")
        document = load_document(arguments[2])
        query = arguments[3]
        mode = option_value(arguments, "--mode", "auto")
        max_count = int(option_value(arguments, "--max", "10"))
        matches = collect_matches(document, query, mode, max_count)
        if not matches:
            raise ToolError(f"no_match={query}")
        for index, match in enumerate(matches):
            print_match(index, match)
        return

    if command == "render-page":
        if len(arguments) < 5:
            raise ToolError("render-page requires <pdf> <page-index> <output>")
        document = load_document(arguments[2])
        page_index = int(arguments[3])
        output = arguments[4]
        scale = float(option_value(arguments, "--scale", "2.0"))
        page = load_page(document, page_index)
        image = render_page_image(page, None, scale)
        write_png(image, output)
        safe_print(f"wrote={expanded_path(output)}")
        return

    if command == "snapshot-query":
        if len(arguments) < 6:
            raise ToolError("snapshot-query requires <pdf> <query> <match-index> <output>")
        document = load_document(arguments[2])
        query = arguments[3]
        match_index = int(arguments[4])
        output = arguments[5]
        preset = option_value(arguments, "--preset", "generic")
        mode = option_value(arguments, "--mode", "auto")
        scale = float(option_value(arguments, "--scale", "4.0"))
        matches = collect_matches(document, query, mode, match_index + 1)
        if match_index < 0 or match_index >= len(matches):
            raise ToolError(f"no_match={query}")
        match = matches[match_index]
        page = load_page(document, match.page_index)
        target_rect = crop_rect(
            preset,
            page_bounds_pdf(page),
            match.rect,
            document=document,
            page_index=match.page_index,
        )
        image = render_page_image(page, target_rect, scale)
        write_png(image, output)
        safe_print(f"wrote={expanded_path(output)}")
        print_match(match_index, match)
        return

    if command == "snapshot-rect":
        if len(arguments) < 9:
            raise ToolError("snapshot-rect requires <pdf> <page-index> <x> <y> <w> <h> <output>")
        document = load_document(arguments[2])
        page_index = int(arguments[3])
        x = float(arguments[4])
        y = float(arguments[5])
        w = float(arguments[6])
        h = float(arguments[7])
        output = arguments[8]
        preset = option_value(arguments, "--preset", "generic")
        scale = float(option_value(arguments, "--scale", "4.0"))
        page = load_page(document, page_index)
        anchor = fitz.Rect(x, y, x + w, y + h)
        target_rect = crop_rect(
            preset,
            page_bounds_pdf(page),
            anchor,
            document=document,
            page_index=page_index,
        )
        image = render_page_image(page, target_rect, scale)
        write_png(image, output)
        safe_print(f"wrote={expanded_path(output)}")
        return

    raise ToolError(f"unknown_command={command}")


if __name__ == "__main__":
    try:
        run()
    except ToolError as error:
        sys.stderr.write(f"{error}\n")
        raise SystemExit(1)
