---
name: paper-deep-reading
description: Read local academic PDFs in depth and produce a screenshot-backed Markdown report. Use when Codex receives a local paper PDF and must explain the paper's problem setting, idea origin, innovation points, technical core (such as a theorem, algorithm, objective, system model, or method block), experimental or simulation evidence, title, keywords, authors, institutions, and three audience-specific section-4 recommendations for beginners, master's/PhD students, and professors, especially when the final deliverable should keep `report.md` plus a local `images/` folder while the Markdown itself uses public image URLs.
---

# Paper Deep Reading

## Goal

Read a local paper PDF end to end, capture source-grounded snapshots from the PDF itself, and write a report that stays anchored to the paper. In the final deliverable, keep `report.md` together with the local `images/` folder; remove only transient helper artifacts such as temporary exported Markdown files or `source_text.txt` unless the user asks to keep them. The final `report.md` must use public image URLs rather than local `images/...` paths.

## Section Choice Rules

- Section `2` is the paper's technical core, not a theorem-only bucket.
- If the paper has formal result blocks, prefer `Theorem`, `Lemma`, `Proposition`, `Corollary`, `Assumption`, `Property`, or `Remark`.
- When choosing supporting blocks around a main theorem, consider `Lemma`, `Assumption`, and `Property` at the same importance level. Do not ignore a paper's key assumptions or properties just because it has no lemma section.
- If a `Theorem` depends on one or more earlier `Theorem`, `Lemma`, `Assumption`, `Property`, or `Remark` blocks, treat them as one dependency chain rather than isolated screenshots.
- If section `2` discusses a cited `Lemma`, `Assumption`, `Property`, or `Remark`, include its own screenshot in the report rather than explaining it only in prose.
- If a later theorem explicitly says it is derived from, based on, or referring to an earlier theorem, include that earlier theorem in section `2` rather than jumping straight to the downstream theorem.
- For control-oriented, estimation-oriented, filtering, or observer-design papers, the system-model equation group is mandatory content. Do not summarize the dynamics only in prose.
- In those papers, transcribe the core system equations into LaTeX in `report.md` rather than leaving the system model only as a screenshot.
- If the paper does not have formal result blocks, capture the most informative technical artifact instead: algorithm block, problem formulation, system model, objective or loss, key equation group, framework diagram, or architecture panel.
- Section `3` is the evidence section. Prefer result figures, but use result tables or qualitative comparison panels when figures are absent or weak.
- When the paper provides multiple complementary comparison panels, do not stop at a single table or a single figure. Prefer a compact evidence set that includes the main comparison plot plus one additional sensitivity, ablation, communication-tradeoff, or robustness panel when available.

## Workflow

1. Create the output folder first
- Run `python scripts/init_output_folder.py "<pdf-path>" --output-root "<root-dir>"`.
- Write the final report into the generated `report.md`.
- Save every snapshot into the generated `images/` directory. Do not scatter images elsewhere.
- If the user already gave an output folder, honor it and keep the same `report.md` plus `images/` layout.

2. Extract and inspect the paper text
- Run `python scripts/pdf_tool.py probe "<pdf-path>"` to confirm the page count.
- Run `python scripts/pdf_tool.py extract-text "<pdf-path>" "<output-dir>/source_text.txt"` before summarizing the paper.
- Prefer the extracted text as the primary reading artifact. Treat OCR output as a fallback when the PDF text layer is missing or broken.
- Prefer filling the report metadata with a DOI URL such as `https://doi.org/<doi>`. Search the extracted text for `Digital Object Identifier`, `DOI`, or a `10.xxxx/...` pattern. If no DOI or official paper URL is available, omit the source-link line rather than exposing a local filesystem path.
- Verify the author list against PDF page 1 and keep author names in English rather than translating them into Chinese.
- Verify affiliations against the PDF before writing `学校`. Use standard Chinese institution names when the translation is conventional; if the institution cannot be resolved confidently, keep the verified English institution name rather than inventing a Chinese form.

3. Capture the report-header snapshot first
- Capture one compact snapshot from the first page that contains the paper title and author list.
- Place this header image immediately under the top `#` title in `report.md`.
- Keep the crop tight: include the paper title and authors, but avoid abstract text whenever possible.

4. Capture section-2 technical-core snapshots
- Load [snapshot-playbook.md](./references/snapshot-playbook.md).
- Search formal-result anchors first with `python scripts/pdf_tool.py find`.
- If no strong formal-result anchors exist, search method anchors such as `Algorithm`, `Objective`, `Problem`, `System Model`, `Architecture`, `Framework`, `Loss`, or other paper-specific labels.
- Use `python scripts/pdf_tool.py snapshot-query` with the `theorem` preset for formal result blocks.
- Use `python scripts/pdf_tool.py snapshot-query` with the `generic` preset for algorithm blocks, equation groups, system models, and framework panels. If the crop is still poor, switch to `snapshot-rect --preset exact`.
- For algorithm screenshots, inspect the `find` output before trusting the crop. If `Algorithm n` first matches a prose sentence instead of the actual pseudocode block, rerun with the block-heading hit or the full heading line, then crop again.
- For control-oriented papers, locate the main system-model equation group early. Even if you capture a screenshot for context, also rewrite that equation group in LaTeX inside the report.
- The theorem crop should end with the theorem statement itself. Do not leave `Proof` or the next theorem block in the screenshot unless the user explicitly asks for proof details.
- When a theorem explicitly cites an earlier theorem, lemma, assumption, property, proposition, or remark, capture the minimum supporting set needed to explain that chain rather than only the final theorem block.
- If the report text names `Lemma x`, `Assumption x`, `Property x`, or `Remark y`, the corresponding screenshot should also appear in section `2`.
- Prefer 2 to 5 technical-core snapshots that cover the paper's logic rather than every nearby block.
- After each image is saved, explain what the block defines or proves, why it matters, how it connects to the paper's main argument, and what role it plays in the theorem chain.

5. Capture section-3 evidence snapshots
- Search for `Fig.`, `Figure`, `Table`, and `Tab.` with `python scripts/pdf_tool.py find`.
- Use `python scripts/pdf_tool.py snapshot-query` with the `figure` preset for main result figures.
- If the page is double-column and the default figure crop is too wide, use the `figure-column` preset or `snapshot-rect --preset exact`.
- If `figure-column` still leaves page-header residue, gutter leakage, or neighboring-column slivers, render the whole page with `render-page` and finalize the figure with `snapshot-rect --preset exact`.
- Use `python scripts/pdf_tool.py snapshot-query` with the `table` preset for result tables whose title is above the table body.
- For result tables or mixed qualitative panels, use `snapshot-rect --preset exact` when the automatic crop still leaks into neighboring figures or text.
- A figure crop should contain the full figure panel plus its caption, but not the next figure, the next table, or unrelated body text.
- Prefer 2 to 4 evidence snapshots that cover the benchmark, the main performance result, and any robustness, ablation, sensitivity, or communication-tradeoff result if present.
- If the paper contains both a summary table and a comparison figure, include both whenever they communicate different evidence.
- Explain the setup, comparison object, baseline, metric, and what the evidence proves versus what it only suggests.

6. Write the report in the required structure
- Load [report-structure.md](./references/report-structure.md).
- Follow the exact section order in the template unless the user explicitly asks for a different order.
- Cover:
  - header snapshot, author names, institution names, keywords, and DOI / paper link when available
  - how the idea arises and what problem it solves
  - innovation points
  - technical-core walkthrough with screenshots
  - experiment or simulation walkthrough with screenshots, including comparison figures when the paper provides them
  - exactly three section-4 recommendations tailored to `入门者`, `硕博学生`, and `教授`, each with mathematical derivation difficulty
  - final summary
- Keep the report source-grounded. Separate confirmed statements from your own extensions or inferences.
- Keep formulas in LaTeX form. Use `$...$` for short formulas and `$$...$$` on separate lines for long formulas.
- For control-oriented papers, write the system-model equation group explicitly in LaTeX near section `1.2` or `2.1`. Do not replace the main dynamics with prose only.
- The report title should be the paper title rendered as a standard academic Chinese translation. Do not invent a contribution-style slogan or a free paraphrase for the top `#` title.
- Do not add a separate `论文标题` metadata line; the header snapshot already carries the original title and author information.
- Do not add an `输出时间` line.
- Add `作者` and `学校` metadata lines near the top of the report.
- Keep `作者` in English. Do not translate author names into Chinese.
- Keep `学校` as verified standard Chinese institution names when the translation is clear and conventional. If the institution naming is ambiguous, prefer the verified English institution name over an invented Chinese translation.
- Translate common keywords into standard Chinese when the translation is conventional, but leave rare or awkward terms in English.
- Choose the section-3 title according to the paper's evidence type. Prefer labels such as `仿真结果与对比分析`, `实验结果与对比分析`, or `仿真与实验验证`.
- Do not write three generic extension ideas in section `4`. Instead, write exactly three numbered items for `入门者`, `硕博学生`, and `教授` in that order. Each item should contain a short title, one italicized `核心建议` line, and a `数学推导难度` line.

7. Rewrite image links inside `report.md`
- If the user already gave a public image prefix, run `python scripts/render_wechat_paste.py "<output-dir>/report.md" "<output-dir>/report.rendered.md" --image-url-prefix "<public-image-prefix>" --rewrite-report-images`.
- Prefer an immutable public prefix when assets are already uploaded, such as a jsDelivr URL pinned to a Git commit hash rather than `@main`, so updated screenshots do not get masked by stale CDN caches.
- If no public hosting information is available yet, still run `python scripts/render_wechat_paste.py "<output-dir>/report.md" "<output-dir>/report.rendered.md" --rewrite-report-images`. The exporter will insert `__PUBLIC_IMAGE_PREFIX__` placeholder URLs and write `wechat_assets_manifest.txt` so the user can upload the images and replace the prefix later.

8. Validate and iterate
- Run `python scripts/validate_report.py "<output-dir>/report.md"` after the image URLs inside `report.md` are finalized.
- Load [quality-checklist.md](./references/quality-checklist.md) if the report misses any required element.
- If screenshots are too narrow or too wide, rerun `snapshot-query` or `snapshot-rect --preset exact` and replace the image.

9. Perform a final self-review before handoff
- Treat self-review as mandatory, not optional polish.
- Re-check the final `report.md` after the public image URLs are already in place. Do not rely only on an earlier validation run against local paths or placeholder URLs.
- Manually inspect every screenshot actually referenced in `report.md`, especially the section-3 evidence images, and confirm it meets the screenshot standard:
  - header image: contains the full paper title and author list, while avoiding abstract spillover when possible
  - theorem / lemma / assumption / property / proposition / remark / algorithm image: contains the complete target block, but does not spill into `Proof`, the next result block, or unrelated body text
  - figure / table image: contains the full panel plus caption, but does not leak into the next figure, next table, or unrelated paragraph text
- If multiple candidate crops exist for the same evidence block, keep the cleanest one in the deliverable and avoid referencing a weaker crop by mistake.
- Confirm every image link inside the final `report.md` is a hosted URL or an explicit placeholder URL, never a local `images/...` path.
- Confirm the final output folder keeps `report.md` plus `images/`, and removes transient helper artifacts such as `source_text.txt`, `report.rendered.md`, and page-render cache folders unless the user explicitly asked to keep them.
- In the final user-facing response, include a short self-review summary that states whether validation passed and whether the screenshots satisfy the standard.

## Operating Rules

- Treat screenshots as mandatory, not optional decoration.
- Prefer `python scripts/pdf_tool.py ...` as the primary PDF helper entrypoint. On Windows PowerShell, `.\scripts\pdf_tool.ps1 ...` is also supported.
- Keep every report in one dedicated folder while processing, and keep the local `images/` folder in the final handoff by default.
- Put a title-and-author header snapshot immediately below the top `#` title in `report.md`.
- Fill in `作者` and `学校` explicitly near the top of `report.md`.
- Fill in keywords explicitly near the top of `report.md`.
- Prefer a DOI URL or official paper URL in the report metadata. Do not expose a local filesystem source path in the final report.
- Prefer PDF-native text search first. Use OCR fallback when the paper is scanned or the text layer is unusable.
- Verify `作者` and `学校` against the PDF itself rather than trusting filenames, folder names, or prior notes.
- Explain theorem blocks in plain technical language. Do not paste theorem statements without interpretation.
- Explain supporting theorem, lemma, assumption, property, and remark blocks as part of the proof or design chain, not as isolated trivia.
- Explain non-theorem technical blocks in terms of symbols, modules, objectives, constraints, or update rules.
- In control-oriented reports, explain the system-model formulas in terms of state, input, output, disturbance, observer gain, and error propagation symbols rather than only saying the model is "constructed" or "given".
- Explain experiment or simulation evidence in terms of variables, metrics, baselines, comparison objects, and conclusions.
- Before handoff, manually audit the screenshots that are actually referenced by `report.md`; do not assume an automatically generated crop is acceptable without checking it.
- When several candidate crops exist for the same result block, prefer the cleanest acceptable crop and remove or ignore weaker unused crops rather than leaving ambiguity in the deliverable.
- In section `4`, tailor the three numbered items to `入门者`, `硕博学生`, and `教授`, and score or label the mathematical derivation difficulty explicitly.
- Keep user-facing output in the user's language unless the user asks otherwise. Preserve original theorem and figure labels in English when helpful.
- Do not leave local image paths such as `images/foo.png` inside the final `report.md`; replace them with public URLs or explicit placeholder URLs.
- Preserve formulas in LaTeX form; keep short formulas inline and move long formulas to `$$...$$` blocks instead of rasterizing them.
- For control-oriented papers, at least one display-math block in section `1` or `2` should contain the core system-model equations in LaTeX.
- Do not claim a contribution or limitation that the PDF does not support.
- In the final response to the user, briefly report the self-review result instead of silently assuming the deliverable is standard-compliant.

## Typical Requests

- "Use $paper-deep-reading to read this local PDF, capture the important theorem screenshots, and write a Chinese markdown report."
- "Use $paper-deep-reading to explain the proof flow of this paper and save a report folder with images."
- "Use $paper-deep-reading to read this PDF, summarize the innovation points, explain the technical core and the experiments, and finish section 4 with advice for beginners, graduate students, and professors."
- "Use $paper-deep-reading to handle this empirical paper even though it has no theorem section. Capture the method block and the main result table."
- "Use $paper-deep-reading to write a report for this PDF, place the title-author header image under the title, and keep `report.md` plus the local `images/` folder."

## Resources

- `scripts/init_output_folder.py`: Create a dedicated report folder with `report.md` and `images/`.
- `scripts/pdf_tool.py`: Primary cross-platform PDF helper built on PyMuPDF. It probes PDFs, extracts text, finds anchors, renders pages, and crops theorem or figure snapshots from the PDF itself.
- `scripts/pdf_tool.ps1`: Windows PowerShell wrapper for `pdf_tool.py`. It tries `python` first and then `py -3`.
- `scripts/pdf_tool.sh`: Compatibility wrapper that dispatches to `pdf_tool.py` when Python is available and only falls back to the legacy Swift implementation when needed.
- `scripts/pdf_snapshot.swift`: Legacy macOS-oriented implementation kept as a fallback.
- `scripts/render_wechat_paste.py`: Replace local image paths with hosted URLs or placeholder URLs, preserve LaTeX formulas, and optionally rewrite image links inside `report.md`.
- `scripts/validate_report.py`: Check whether a generated report meets the required section and screenshot structure.
- [report-structure.md](./references/report-structure.md): Required Markdown structure and writing expectations.
- [snapshot-playbook.md](./references/snapshot-playbook.md): How to choose theorem and figure anchors and when to recrop.
- [quality-checklist.md](./references/quality-checklist.md): Acceptance checklist for self-review and iteration.
