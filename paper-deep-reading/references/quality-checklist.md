# Quality Checklist

Treat the report as acceptable only if all items below pass.

## Structural checks

- The report lives in its own folder.
- The folder contains `report.md`.
- The folder contains `images/`.
- The final handoff may omit transient helper files such as `wechat_paste.md` or `source_text.txt`.
- The report includes a header snapshot and `关键词`.
- The report does not expose a local filesystem PDF path; it prefers a DOI or official paper URL when available.
- The report does not include a separate `论文标题` line or an `输出时间` line.
- The top `#` title reads like a standard academic Chinese translation of the paper title, not a slogan-style summary.
- Section `1` explains the problem, the idea origin, and the innovation points.
- Section `2` contains technical-core screenshots and explanations.
- Section `3` contains experiment or simulation evidence screenshots and explanations, and its title matches the paper's evidence type rather than defaulting to a setup-heavy label.
- Section `4` contains exactly three numbered follow-up directions.
- Section `5` provides a final summary.

## Screenshot checks

- At least one section-2 technical-core image is present.
- At least one section-3 evidence image is present.
- The report places one title-author header image directly below the top `#` title.
- Each image referenced from `report.md` uses a hosted URL or an explicit `__PUBLIC_IMAGE_PREFIX__` placeholder rather than a local path.
- Each screenshot is readable without zooming aggressively.
- When the paper contains multiple complementary comparison figures or a comparison figure plus a summary table, section `3` includes more than one evidence screenshot.

## Content checks

- Innovation points are separated from generic background.
- The `##` headings read like a formal academic report rather than question prompts.
- The section-3 heading uses professional academic wording such as `仿真结果与对比分析`, `实验结果与对比分析`, or `仿真与实验验证` when those labels fit the paper better than `实验设计`.
- Markdown emphasis is present but restrained; bold and italics help reading rather than creating visual noise.
- Common keywords are translated into natural Chinese when standard translations exist.
- The section-2 explanation says what the block defines, assumes, guarantees, or changes in the method.
- For control-oriented papers, the report writes out the core system-model equations in LaTeX rather than leaving the model only in screenshots or prose.
- For control-oriented papers, the system-model formulas are accompanied by short symbol-level explanation of state, input, output, disturbance, gain, or error terms.
- If the paper uses supporting `Theorem`, `Lemma`, `Assumption`, `Property`, `Proposition`, or `Remark` blocks to support a theorem or method step, the report explains that dependency chain and the role of the citation.
- If a later theorem explicitly relies on an earlier theorem, the earlier theorem is not skipped merely because the later one looks more advanced.
- If the report explicitly discusses a `Lemma`, `Assumption`, `Property`, or `Remark`, section `2` includes the corresponding screenshot rather than only a downstream theorem screenshot.
- The section-3 explanation says what is measured, what baseline or comparison object is used, and what conclusion is justified.
- The three extension ideas are not trivial rewordings of the original paper.
- Each extension idea includes a mathematical derivation difficulty label.
- In section `4`, each extension item is concise: `标题 + 斜体核心想法 + 数学推导难度`, with no separate `说明` field in the default format.
- The final `report.md` also uses hosted image URLs or an explicit `__PUBLIC_IMAGE_PREFIX__` placeholder rather than local `images/...` paths.
- Longer formulas are broken onto separate lines with `$$...$$` rather than being forced into narrow inline layout.

## Repair strategy

If the report fails:

1. Fix structure first.
2. Fix screenshot coverage second.
3. Tighten the explanations and extension ideas last.
