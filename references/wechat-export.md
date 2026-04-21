# WeChat Export

For WeChat-style Markdown export, two issues always need explicit handling:

1. Local filesystem image paths such as `images/foo.png`
2. Long formulas that should be visually broken into separate lines

## Why local image paths fail

When a Markdown file references `images/foo.png`, that path only exists on your computer. After paste, the公众号 editor cannot fetch your local disk, so the image disappears or becomes plain text.

Therefore, the WeChat-paste version must use public URLs such as:

```text
https://fastly.jsdelivr.net/gh/<owner>/<repo>@<branch>/<path>/<file>.png
```

or any other public image host URL.

If you overwrite an existing file in the repo and still reference `@main`, the CDN may temporarily serve the older cached image.
For final publishing, prefer an immutable URL such as:

```text
https://fastly.jsdelivr.net/gh/<owner>/<repo>@<commit-sha>/<path>/<file>.png
```

This forces the pasted article to request a fresh asset path instead of waiting for branch-level cache refresh.

## Formula policy

In the current target workflow, formulas should stay in LaTeX form rather than being rasterized into images.

To keep readability acceptable:

- preserve concise formulas in `$...$`
- move long formulas onto their own lines using `$$...$$`
- avoid turning ordinary formulas into images; screenshots should be reserved for theorem blocks, figures, tables, and other PDF-native content

## Export workflow

1. Finish `report.md`.
2. If possible, upload every screenshot in `images/` to a public host first.
3. Run one of these:

```bash
python scripts/render_wechat_paste.py report.md wechat_paste.md --image-url-prefix "<public-prefix>" --rewrite-report-images
```

or, if hosting is not ready yet:

```bash
python scripts/render_wechat_paste.py report.md wechat_paste.md --rewrite-report-images
```

4. Paste `wechat_paste.md` into your WeChat Markdown workflow.

If you omit `--image-url-prefix`, the exporter writes URLs like `__PUBLIC_IMAGE_PREFIX__/foo.png` and also creates `wechat_assets_manifest.txt`. With `--rewrite-report-images`, the same placeholder URLs will be written back into `report.md` as well. Replace the placeholder prefix after the assets are uploaded.

## Public URL prefix rule

The prefix should point to the folder that hosts the contents of local `images/`.

Example:

- Local file: `images/theorem_2_lp.png`
- Prefix: `https://fastly.jsdelivr.net/gh/bucketio/img19@7cc3ee1c371c5fe0bb2059f2096e6628a45f2075/2026/03/29`
- Final URL: `https://fastly.jsdelivr.net/gh/bucketio/img19@7cc3ee1c371c5fe0bb2059f2096e6628a45f2075/2026/03/29/theorem_2_lp.png`

If you are still waiting to upload assets, a placeholder prefix is acceptable for drafting and handoff, but not for final publishing.

## Formula rule

- Use `$...$` for inline math.
- Use `$$...$$` for display math.
- When a formula becomes too long for a sentence, place it on its own line with `$$...$$`.
- Use backticks only for identifiers, file names, code ids, and literal commands.
