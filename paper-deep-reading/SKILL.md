---
name: paper-deep-reading
description: Read local academic PDFs in depth and produce a screenshot-backed Markdown report. Use when Codex receives a local paper PDF and must explain the paper's problem setting, idea origin, innovation points, technical core (such as a theorem, algorithm, objective, system model, or method block), experimental or simulation evidence, title, keywords, and three follow-up research directions, especially when the final deliverable should keep `report.md` plus a local `images/` folder while the Markdown itself uses public image URLs.
---

# Paper Deep Reading

## Goal

Read a local paper PDF end to end, capture source-grounded snapshots from the PDF itself, and write a report that stays anchored to the paper. In the final deliverable, keep `report.md` together with the local `images/` folder; remove only transient helper artifacts such as temporary exported Markdown files or `source_text.txt` unless the user asks to keep them. The final `report.md` must use public image URLs rather than local `images/...` paths.

## Section Choice Rules

- Section `2` is the paper's technical core, not a theorem-only bucket.
- If the paper has formal result blocks, prefer `Theorem`, `Lemma`, `Proposition`, `Corollary`, `Assumption`, `Property`, or `Remark`.
- When choosing supporting blocks around a main theorem, consider `Lemma`, `Assumption`, and `Property` at the same importance level. Do not ignore a paper's key assumptions or properties just because it has no lemma section.
- If a `Theorem` depends on one or more earlier `Theorem`, `Lemma`, `Assumption`, `Property`, or `Remark` blocks, treat them as one dependency chain rather than isolated screenshots.
- Do not stop at restating the theorem: explain which earlier theorem supplies the closure formula, which lemma provides the bound, which assumption fixes the admissible setting, which property gives the algebraic tool, and which remark clarifies parameter choice, conservatism, or applicability.
- If section `2` discusses a cited `Lemma`, `Assumption`, `Property`, or `Remark`, include its own screenshot in the report rather than explaining it only in prose.
- If a later theorem explicitly says it is derived from, based on, or referring to an earlier theorem, include that earlier theorem in section `2` rather than jumping straight to the downstream theorem.
- For control-oriented, estimation-oriented, filtering, or observer-design papers, the system-model equation group is mandatory content. Do not summarize the dynamics only in prose.
- In those papers, transcribe the core system equations into LaTeX in `report.md` rather than leaving the system model only as a screenshot. The report should show the main state equation, output equation, observer equation, trigger law, or error-system equation group that the rest of the paper builds on.
- If the paper does not have formal result blocks, capture the most informative technical artifact instead: algorithm block, problem formulation, system model, objective or loss, key equation group, framework diagram, or architecture panel.
- Section `3` is the evidence section. Prefer result figures, but use result tables or qualitative comparison panels when figures are absent or weak.
- When the paper provides multiple complementary comparison panels, do not stop at a single table or a single figure. Prefer a compact evidence set that includes the main comparison plot plus one additional sensitivity, ablation, communication-tradeoff, or robustness panel when available.
- Do not force a theorem narrative onto a paper that is empirical, systems-oriented, or design-heavy.

## Workflow

1. Create the output folder first
- Run `python3 scripts/init_output_folder.py "<pdf-path>" --output-root "<root-dir>"`.
- Write the final report into the generated `report.md`.
- Save every snapshot into the generated `images/` directory. Do not scatter images elsewhere.
- If the user already gave an output folder, honor it and keep the same `report.md` plus `images/` layout.

2. Extract and inspect the paper text
- Run `bash scripts/pdf_tool.sh probe "<pdf-path>"` to confirm the page count.
- Run `bash scripts/pdf_tool.sh extract-text "<pdf-path>" "<output-dir>/source_text.txt"` before summarizing the paper.
- Prefer the extracted text as the primary reading artifact. Treat OCR output as a fallback when the PDF text layer is missing or broken.
- Prefer filling the report metadata with a DOI URL such as `https://doi.org/<doi>`. Search the extracted text for `Digital Object Identifier`, `DOI`, or a `10.xxxx/...` pattern. If no DOI or official paper URL is available, omit the source-link line rather than exposing a local filesystem path.

3. Capture the report-header snapshot first
- Capture one compact snapshot from the first page that contains the paper title and author list.
- Place this header image immediately under the top `#` title in `report.md`.
- Keep the crop tight: include the paper title and authors, but avoid abstract text whenever possible.

4. Capture section-2 technical-core snapshots
- Load [snapshot-playbook.md](./references/snapshot-playbook.md).
- Search formal-result anchors first with `bash scripts/pdf_tool.sh find`.
- If no strong formal-result anchors exist, search method anchors such as `Algorithm`, `Objective`, `Problem`, `System Model`, `Architecture`, `Framework`, `Loss`, or other paper-specific labels.
- Use `bash scripts/pdf_tool.sh snapshot-query` with the `theorem` preset for formal result blocks.
- Use `bash scripts/pdf_tool.sh snapshot-query` with the `generic` preset for algorithm blocks, equation groups, system models, and framework panels. If the crop is still poor, switch to `snapshot-rect --preset exact`.
- For control-oriented papers, locate the main system-model equation group early. Even if you capture a screenshot for context, also rewrite that equation group in LaTeX inside the report.
- The theorem crop should end with the theorem statement itself. Do not leave `Proof` or the next theorem block in the screenshot unless the user explicitly asks for proof details.
- When a theorem explicitly cites an earlier theorem, lemma, assumption, property, proposition, or remark, capture the minimum supporting set needed to explain that chain rather than only the final theorem block.
- If several supporting blocks appear nearby, prefer the one that is explicitly referenced in the proof logic, model admissibility, parameter design, or algebraic manipulation, not the one that merely appears nearby on the page.
- If the report text names `Lemma x`, `Assumption x`, `Property x`, or `Remark y`, the corresponding screenshot should also appear in section `2`.
- Prefer 2 to 5 technical-core snapshots that cover the paper's logic rather than every nearby block.
- After each image is saved, explain what the block defines or proves, why it matters, how it connects to the paper's main argument, and what role it plays in the theorem chain.

5. Capture section-3 evidence snapshots
- Search for `Fig.`, `Figure`, `Table`, and `Tab.` with `bash scripts/pdf_tool.sh find`.
- Use `bash scripts/pdf_tool.sh snapshot-query` with the `figure` preset for main result figures.
- If the page is double-column and the default figure crop is too wide, use the `figure-column` preset or `snapshot-rect --preset exact`.
- Use `bash scripts/pdf_tool.sh snapshot-query` with the `table` preset for result tables whose title is above the table body.
- For result tables or mixed qualitative panels, use `snapshot-rect --preset exact` when the automatic crop still leaks into neighboring figures or text.
- A figure crop should contain the full figure panel plus its caption, but not the next figure, the next table, or unrelated body text.
- Prefer 2 to 4 evidence snapshots that cover the benchmark, the main performance result, and any robustness, ablation, sensitivity, or communication-tradeoff result if present.
- If the paper contains both a summary table and a comparison figure, include both whenever they communicate different evidence.
- Explain the setup, comparison object, baseline, metric, and what the evidence proves versus what it only suggests.
- Keep the simulation or experiment commentary concise: one short paragraph per evidence block is usually enough, but it should still say what is being compared and what conclusion is justified.

6. Write the report in the required structure
- Load [report-structure.md](./references/report-structure.md).
- Follow the exact section order in the template unless the user explicitly asks for a different order.
- Cover:
  - header snapshot, keywords, and DOI / paper link when available
  - how the idea arises and what problem it solves
  - innovation points
  - technical-core walkthrough with screenshots
  - experiment or simulation walkthrough with screenshots, including comparison figures when the paper provides them
  - exactly three follow-up directions with mathematical derivation difficulty
  - final summary
- Keep the report source-grounded. Separate confirmed statements from your own extensions or inferences.
- Use professional academic section titles rather than conversational headings. A focused question is allowed only in `1.1`, and it should still read like academic Chinese rather than casual speech.
- Keep formulas in LaTeX form. Use `$...$` for short formulas and `$$...$$` on separate lines for long formulas.
- For control-oriented papers, write the system-model equation group explicitly in LaTeX near section `1.2` or `2.1`. Do not replace the main dynamics with prose only.
- Preserve the structure of coupled equations when transcribing the model. If the renderer safely supports it, use one `$$ ... $$` block with `aligned`; otherwise split the model into consecutive `$$ ... $$` blocks rather than rasterizing it.
- When the paper gives several related dynamics, prefer the minimal complete group that the later theorem chain depends on: state equation, output equation, observer update, trigger law, or error-system recursion.
- The report title should be the paper title rendered as a standard academic Chinese translation. Do not invent a contribution-style slogan or a free paraphrase for the top `#` title.
- Do not add a separate `论文标题` metadata line; the header snapshot already carries the original title and author information.
- Do not add an `输出时间` line.
- Translate common keywords into standard Chinese when the translation is conventional, but leave rare or awkward terms in English.
- Section `1.1` may use a tightly focused question-style heading to pull the reader into the problem, but phrasing such as `为何...` is preferred over colloquial wording, and the body should remain technically rigorous.
- Choose the section-3 title according to the paper's evidence type. Prefer labels such as `仿真结果与对比分析`, `实验结果与对比分析`, or `仿真与实验验证`; avoid setup-heavy headings when the section mainly reports comparative evidence.
- If the paper contains supporting `Theorem`, `Lemma`, `Assumption`, `Property`, `Proposition`, or `Remark` blocks that are cited by a theorem or algorithmic step, name them explicitly in section `2`.
- If a downstream theorem explicitly relies on an earlier theorem, include that earlier theorem in the writeup and explain what technical skeleton it contributes.
- If `Lemma`, `Assumption`, `Property`, or `Remark` blocks are named explicitly in section `2`, pair each one with its own screenshot rather than only showing the downstream theorem.
- For each cited supporting block, explain the relation in plain technical language:
  - what the supporting block establishes
  - which theorem, proposition, or step later uses it
  - whether it supplies a bound, feasibility argument, equivalence bridge, parameter rule, or interpretation boundary
  - whether it fixes the admissible model setting, positivity condition, closure formula, or algebraic manipulation rule
  - why that citation matters to the paper's proof flow or method credibility
- Keep section `4` concise. For each direction, write only a short title, one italicized `核心想法` line, and a `数学推导难度` line. Do not add a separate `说明` field unless the user explicitly asks for a longer format.

7. Rewrite image links inside `report.md`
- If the user already gave a public image prefix, run `python3 scripts/render_wechat_paste.py "<output-dir>/report.md" "<output-dir>/report.rendered.md" --image-url-prefix "<public-image-prefix>" --rewrite-report-images`.
- Prefer an immutable public prefix when assets are already uploaded, such as a jsDelivr URL pinned to a Git commit hash rather than `@main`, so updated screenshots do not get masked by stale CDN caches.
- If the user already has per-image hosted URLs, also pass `--mapping-file "<mapping.json>"` when useful.
- If no public hosting information is available yet, still run `python3 scripts/render_wechat_paste.py "<output-dir>/report.md" "<output-dir>/report.rendered.md" --rewrite-report-images`. The exporter will insert `__PUBLIC_IMAGE_PREFIX__` placeholder URLs and write `wechat_assets_manifest.txt` so the user can upload the images and replace the prefix later.
- The exporter rewrites local image paths inside `report.md` to remote URLs.
- Preserve all formulas in LaTeX form.
- For formulas that are too long for inline reading, move them onto their own lines with `$$...$$`.
- After the rewrite is complete, keep `report.md` together with the local `images/` folder and remove only transient artifacts unless the user asked to keep them.

8. Validate and iterate
- Run `python3 scripts/validate_report.py "<output-dir>/report.md"` after the image URLs inside `report.md` are finalized.
- Load [quality-checklist.md](./references/quality-checklist.md) if the report misses any required element.
- If screenshots are too narrow or too wide, rerun `snapshot-query` or `snapshot-rect --preset exact` and replace the image.

## Operating Rules

- Treat screenshots as mandatory, not optional decoration.
- Keep every report in one dedicated folder while processing, and keep the local `images/` folder in the final handoff by default.
- Put a title-and-author header snapshot immediately below the top `#` title in `report.md`.
- Fill in keywords explicitly near the top of `report.md`.
- Prefer a DOI URL or official paper URL in the report metadata. Do not expose a local filesystem source path in the final report.
- Prefer PDF-native text search first. Use OCR fallback when the paper is scanned or the text layer is unusable.
- Explain theorem blocks in plain technical language. Do not paste theorem statements without interpretation.
- Explain supporting theorem, lemma, assumption, property, and remark blocks as part of the proof or design chain, not as isolated trivia.
- Explain non-theorem technical blocks in terms of symbols, modules, objectives, constraints, or update rules.
- In control-oriented reports, explain the system-model formulas in terms of state, input, output, disturbance, observer gain, and error propagation symbols rather than only saying the model is "constructed" or "given".
- Explain experiment or simulation evidence in terms of variables, metrics, baselines, comparison objects, and conclusions.
- When proposing the three follow-up directions, score or label the mathematical derivation difficulty explicitly.
- Use section titles that read like a formal academic report, not like prompts to the assistant. In section `3`, prefer professional labels such as `仿真结果与对比分析` or `实验结果与对比分析` over conversational or setup-centric wording.
- Use Markdown emphasis sparingly but intentionally: highlight theorem names, key conclusions, and crucial innovation labels with `**bold**`; use `*italics*` for short evaluative remarks or cautionary boundaries.
- In section `4`, italicize the `核心想法` line for each extension direction and omit the old `说明` line.
- Keep user-facing output in the user's language unless the user asks otherwise. Preserve original theorem and figure labels in English when helpful.
- Do not leave local image paths such as `images/foo.png` inside the final `report.md`; replace them with public URLs or explicit placeholder URLs.
- Preserve formulas in LaTeX form; keep short formulas inline and move long formulas to `$$...$$` blocks instead of rasterizing them.
- For control-oriented papers, at least one display-math block in section `1` or `2` should contain the core system-model equations in LaTeX.
- Do not claim a contribution or limitation that the PDF does not support.

## Typical Requests

- "Use $paper-deep-reading to read this local PDF, capture the important theorem screenshots, and write a Chinese markdown report."
- "Use $paper-deep-reading to explain the proof flow of this paper and save a report folder with images."
- "Use $paper-deep-reading to read this PDF, summarize the innovation points, explain the technical core and the experiments, and propose three publishable extensions."
- "Use $paper-deep-reading to handle this empirical paper even though it has no theorem section. Capture the method block and the main result table."
- "Use $paper-deep-reading to write a report for this PDF, place the title-author header image under the title, and keep `report.md` plus the local `images/` folder."

## Resources

- `scripts/init_output_folder.py`: Create a dedicated report folder with `report.md` and `images/`.
- `scripts/pdf_tool.sh`: Run the PDF helper implemented in `scripts/pdf_snapshot.swift` with a safe Swift module cache path.
- `scripts/pdf_snapshot.swift`: Probe PDFs, extract text, find anchors, render pages, and crop theorem or figure snapshots from the PDF itself.
- `scripts/render_wechat_paste.py`: Replace local image paths with hosted URLs or placeholder URLs, preserve LaTeX formulas, and optionally rewrite image links inside `report.md`.
- `scripts/validate_report.py`: Check whether a generated report meets the required section and screenshot structure.
- [report-structure.md](./references/report-structure.md): Required Markdown structure and writing expectations.
- [snapshot-playbook.md](./references/snapshot-playbook.md): How to choose theorem and figure anchors and when to recrop.
- [quality-checklist.md](./references/quality-checklist.md): Acceptance checklist for self-review and iteration.
