# Report Structure

Write the final output as a single Markdown file named `report.md` inside the dedicated report folder.

## Required section order

```markdown
# <论文标题的标准学术中文翻译>

![论文抬头：标题与作者](<public-image-url>)

- 作者：
- 单位：
- 关键词：
- DOI / 论文链接：

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

## 4. 面向不同对象的后续建议
1. 面向入门者
   标题：
   *核心建议：*
   数学推导难度：
2. 面向硕博学生
   标题：
   *核心建议：*
   数学推导难度：
3. 面向教授
   标题：
   *核心建议：*
   数学推导难度：

## 5. 总结与评价
```

## Writing rules

- The top `#` title should be the paper title written as a standard academic Chinese translation. Do not replace it with a contribution summary sentence or an overly free paraphrase.
- Place one tight header snapshot immediately below the top title. That image should contain the paper title and author list from the PDF first page.
- Do not add a separate `论文标题` metadata line; the header snapshot already covers the original title information.
- Fill `作者` using the verified English names from the PDF. Do not translate author names into Chinese.
- Fill `单位` using standard Chinese institution names when the translation is clear and conventional. If the institution naming is ambiguous, prefer the verified English institution name over an invented Chinese translation.
- Fill `关键词` as a compact list such as `区间估计；非线性等式约束；optimization；泰勒展开；zonotope`.
- Prefer `DOI / 论文链接` as a DOI URL such as `https://doi.org/...`. If neither DOI nor an official paper URL is available, omit the line instead of exposing a local PDF path.
- Do not include an `输出时间` line.
- Keep formulas in LaTeX form. Use `$...$` for short formulas and move long formulas to separate lines with `$$...$$`.
- For control-oriented papers, include the core system-model equation group explicitly in LaTeX in section `1.2` or section `2.1`. Do not leave the main dynamics only in screenshots or prose.
- Keep the `##` headings professional and declarative. Do not phrase them as prompts to the assistant.
- The section-3 title should match the paper's evidence style. Prefer labels such as `仿真结果与对比分析`, `实验结果与对比分析`, or `仿真与实验验证` instead of a generic `实验设计` heading when the section mainly reports comparative evidence.
- Use Markdown emphasis sparingly but intentionally. Prefer `**bold**` for key theorem names, innovation labels, and takeaways; use `*italics*` for short cautionary remarks or interpretation boundaries.
- In section `4`, keep each item concise: one audience label, one short title, one italicized `核心建议` line, and one `数学推导难度` line. Do not add a separate `说明` field unless the user explicitly asks for it.
- Keep section `4` as an explicitly numbered list with exactly three items in fixed order: `入门者`, `硕博学生`, and `教授`.
- In section `4`, do not write three generic extension ideas. The beginner item should answer what to learn first from the paper and suggest one concrete entry direction. The graduate-student item should suggest one research direction worth extending. The professor item should give one practical supervision suggestion on how to guide students.
- Put image links directly under the paragraph that introduces the theorem or figure.
- In the final `report.md`, use public image URLs or explicit `__PUBLIC_IMAGE_PREFIX__/<file>` placeholders rather than local `images/...` paths.
- Keep each image caption short and functional.
- Translate common keywords into standard Chinese when that wording is conventional; leave rare technical terms in English when forced translation would sound unnatural.
- In section `2`, explain the role of each technical block.
- If the block is theorem-like, explain:
  - what it assumes
  - what it guarantees
  - why it matters to the method
- If the paper contains supporting `Theorem`, `Lemma`, `Assumption`, `Property`, `Proposition`, or `Remark` blocks, explain:
  - what that supporting block establishes or clarifies
  - which later theorem, proposition, or algorithmic step cites it
  - whether it functions as a bound, decomposition step, feasibility condition, equivalence bridge, parameter rule, interpretation boundary, model admissibility condition, closure formula, or algebraic tool
  - why that citation matters to the paper's proof flow or engineering credibility
- If a later theorem explicitly depends on an earlier theorem, include that earlier theorem in section `2` and explain what downstream statement it unlocks.
- If section `2` discusses a specific `Lemma`, `Assumption`, `Property`, or `Remark`, include the corresponding screenshot directly under that discussion rather than relying only on the theorem screenshot.
- If the block is algorithmic or structural, explain:
  - what object, symbol set, or module is being defined
  - how it fits into the method pipeline
  - why it is central rather than incidental
- If the paper is control-oriented, the writeup should also:
  - transcribe the main state, output, observer, trigger, or error-system equations in LaTeX
  - explain the meaning of the main symbols such as state, input, output, disturbance, gain, and error terms
  - keep long coupled equations in display-math form with `$$...$$`
- In section `3`, explain:
  - what the simulation variable or metric is
  - what baseline is being compared
  - what conclusion is safe to draw
- When section `3` contains multiple complementary comparison plots or tables, include more than one evidence image and give concise comparison commentary for each block.
- In section `4`, give each item:
  - the intended audience (`入门者`, `硕博学生`, or `教授`)
  - a short title
  - one italicized `核心建议` line that answers what this audience should learn, explore, or use to guide students
  - the expected mathematical derivation difficulty such as `低 / 中 / 高 / 很高`

## Minimum screenshot coverage

- Section `2`: at least one technical-core image such as a theorem, algorithm block, equation group, system model, or framework panel.
- Control-oriented papers: section `1` or `2` should also contain at least one display-math system-model block in LaTeX, not only screenshots.
- Section `3`: at least one result-side image such as a figure, table, or qualitative comparison panel.
- When the paper provides multiple comparison figures or a comparison figure plus a summary table, section `3` should prefer 2 to 4 evidence images rather than stopping at a single screenshot.
- Whole report: at least three images in total, including the header snapshot.
