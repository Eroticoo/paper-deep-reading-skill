# Snapshot Playbook

Use the PDF itself as the screenshot source. Do not rely on manual screen captures unless the scripted route fails.

## Section-2 anchors

### Formal-result anchors

Search these keywords in order:

- `Theorem`
- `Lemma`
- `Proposition`
- `Corollary`
- `Assumption`
- `Property`
- `Remark`

Use the `theorem` preset when the anchor text is the start of a formal result block. The preset crops one column around the anchor and extends downward to include the body of the statement.
The expected output is the theorem block itself, not the following `Proof` block.

When a theorem depends on a nearby `Theorem`, `Lemma`, `Assumption`, `Property`, `Proposition`, or `Remark`, capture the smallest set of formal-result blocks that makes the dependency chain intelligible.
Do not screenshot a supporting block only because it appears earlier on the page; prefer the theorem, lemma, assumption, property, or remark that is explicitly cited by the later theorem or that explains a key model constraint, closure rule, parameter choice, or conservatism claim.
If the writeup explicitly names a `Lemma`, `Assumption`, `Property`, or `Remark`, that block should appear as its own screenshot in section `2`.
If a downstream theorem says it is derived by referring to or following an earlier theorem, include that earlier theorem screenshot as part of the chain even when the later theorem looks more sophisticated.

### Technical-core fallback anchors

If the paper does not rely on theorem-style statements, search these keywords in order:

- `Algorithm`
- `Objective`
- `Problem`
- `System Model`
- `Architecture`
- `Framework`
- `Loss`
- `Optimization`

For control-oriented papers, also search for model anchors such as:

- `System Model`
- `Observer`
- `Output`
- `error system`
- `triggered`
- `Dynamics`

Capture the system-model screenshot when it helps orientation, but do not stop there: the report should still rewrite the core model equations in LaTeX.

Use the `generic` preset when the anchor is a method block, equation group, pseudocode block, framework panel, or system-model paragraph. If the crop is close but still includes too much unrelated text, switch to `snapshot-rect --preset exact`.

## Section-3 anchors

Search these keywords in order:

- `Fig.`
- `Figure`
- `Table`
- `Tab.`

When the paper provides enough evidence, build a small comparison set rather than a single screenshot. Prefer:

- one main performance figure or interval-estimation plot
- one comparison, sensitivity, ablation, robustness, or communication-tradeoff figure
- one summary table when it adds evidence that the figures do not already show

For control, filtering, or event-triggered papers, pairing a state-interval figure with a communication or trigger-behavior figure is often more informative than keeping only the table.

Use the `figure` preset when the anchor is the caption line. The preset crops a broad region above the caption so the figure body is included.

If the paper uses a double-column layout and the wide crop pulls in the neighboring column, switch to:

- `figure-column`: keep the crop in the anchor column and stop before the previous or next neighboring figure block
- `table`: keep a titled table inside its column when the title sits above the table body
- `exact`: manually specify the final rectangle with `snapshot-rect`

For tables or mixed comparison panels, start with `table` or `exact`. Use `exact` when row labels, legends, or boundary lines are being cut off.

## Recropping rules

Recrop the image if any of these happen:

- The theorem or method image cuts off the first or last line of the block.
- The theorem image spills into `Proof` or into the next theorem-like block.
- The theorem image is present, but the referenced earlier theorem, lemma, assumption, property, or remark that makes the theorem understandable is missing.
- The report discusses a lemma, assumption, property, or remark, but there is no corresponding screenshot.
- The figure or table image includes too much unrelated neighboring text.
- The figure image contains only part of a multi-panel plot, or leaks into the next figure or table in the same column.
- The image is so small that symbols or axis labels cannot be read.
- The caption line or table title is missing and the evidence becomes hard to reference.

If the automatic preset is close but not sufficient, switch to `snapshot-rect --preset exact` and crop the region manually using the coordinates reported by `find`.

## Suggested naming

- `images/theorem_1.png`
- `images/lemma_1.png`
- `images/property_1.png`
- `images/remark_1.png`
- `images/proposition_1.png`
- `images/technical_core_1.png`
- `images/assumption_1.png`
- `images/figure_1.png`
- `images/table_1.png`
- `images/figure_2.png`

Name files by role, not by random timestamps.
