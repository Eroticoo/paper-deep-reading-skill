# paper-deep-reading

`paper-deep-reading` 是一个面向本地学术 PDF 的 Codex skill，用来做带截图证据的深度精读，并输出适合继续加工或发布的 Markdown 报告。

它目前特别适合控制、估计、滤波、观测器设计这类论文，尤其是需要同时处理：

- 标题与作者抬头截图
- 定理、引理、假设、性质、备注等技术链条截图
- 系统模型公式的 LaTeX 转写
- 仿真 / 实验部分的对比图、表格与简要说明
- 最终 `report.md + images/` 交付

## 中文介绍

这是一个专门为学术论文精读场景设计的 Codex skill。它的目标不是只做普通摘要，而是从论文原文 PDF 中直接提取技术证据，包括标题抬头、定理、引理、假设、性质、备注、系统模型、仿真图和结果表，并将这些内容组织成一份适合继续修改、发布或沉淀的 `report.md`。

对于控制方向论文，这个 skill 会特别关注系统公式链条、定理依赖关系、假设条件、仿真对比图以及最终的工程解释。输出结果默认保留 `report.md + images/`，并支持把图片链接重写成 GitHub CDN 或其他公网图床地址，方便后续粘贴到公众号、笔记系统或仓库文档中。

## English Overview

`paper-deep-reading` is a Codex skill for deep reading local academic PDFs and turning them into screenshot-backed Markdown reports. It is designed for users who need more than a plain summary: the skill extracts source-grounded technical evidence directly from the PDF, including the title header, theorem-like blocks, assumptions, properties, remarks, system-model equations, simulation figures, and result tables.

It is especially useful for control, estimation, filtering, and observer-design papers. The skill emphasizes theorem dependency chains, LaTeX transcription of core system equations, comparison-focused simulation analysis, and a final deliverable built around `report.md + images/`. It also supports rewriting image links into public GitHub CDN or other hosted URLs for publishing workflows.

## 仓库结构

```text
paper-deep-reading-skill/
├── README.md
└── paper-deep-reading/
    ├── SKILL.md
    ├── openai.yaml
    ├── agents/openai.yaml
    ├── references/
    └── scripts/
```

真正的 skill 本体是 `paper-deep-reading/` 这个目录。`README.md` 只是给仓库访问者看的安装和使用说明。

## 使用前提

- 建议在 macOS 环境下使用
  原因：截图脚本 `pdf_snapshot.swift` 依赖系统 PDF 渲染能力
- 已安装 `python3`
- 已安装 `bash`
- 可运行 `swift`
- 有一个可读写的输出目录用于保存 `report.md` 和 `images/`
- 如果要把图片放到公众号、GitHub CDN 或其他外链环境，最好准备一个公网图床前缀

## 安装方法

把仓库里的 `paper-deep-reading/` 整个目录复制到本地 Codex skill 目录下即可：

```bash
cp -R paper-deep-reading ~/.codex/skills/
```

如果你的 Codex 环境使用的是自定义 `CODEX_HOME`，就把它放到：

```bash
$CODEX_HOME/skills/
```

安装完成后，目录应当长这样：

```text
~/.codex/skills/paper-deep-reading/
├── SKILL.md
├── openai.yaml
├── agents/openai.yaml
├── references/
└── scripts/
```

## 别人怎么用这个 skill

在 Codex 里直接点名调用即可。最稳妥的写法是显式写出 skill 名称。

最小用法：

```text
Use $paper-deep-reading to read this local PDF and write a Chinese report.
```

更完整的用法：

```text
Use $paper-deep-reading to read this local PDF, capture the title-author header image,
explain the technical core with source-grounded screenshots, include comparison figures
from the simulation section, and save the final result as report.md plus images/.
```

如果你已经有固定输出目录，也可以在请求里直接说清楚：

```text
Use $paper-deep-reading to read /path/to/paper.pdf and save the output in /path/to/output-dir.
Keep report.md and the local images folder.
```

如果你希望最后的 Markdown 直接使用公网图片链接，也可以把图床前缀一并告诉 Codex：

```text
Use $paper-deep-reading to read /path/to/paper.pdf.
Rewrite all images in report.md with this public prefix:
https://fastly.jsdelivr.net/gh/<owner>/<repo>@<commit>/paper-name/images
```

## 输出内容

默认输出会保留：

- `report.md`
- `images/`

其中 `report.md` 会尽量满足这些特征：

- 一级标题使用论文标题的标准学术中文翻译
- 一级标题下紧跟论文抬头截图
- 关键词使用尽量自然的中文学术表达
- 技术核心部分会解释 theorem / lemma / assumption / property / remark 之间的关系
- 控制类论文会把系统公式转写为 LaTeX
- 仿真部分优先放多张互补的对比图，并配简洁说明
- 图片链接最终会改成公网 URL，而不是本地 `images/...`

## 适合什么论文

这个 skill 最适合：

- 控制理论
- 状态估计
- 区间估计
- 观测器设计
- 事件触发控制
- 含 theorem / lemma / assumption / property / remark 结构的论文

也可以处理没有定理块的论文，但那种情况下它会转去抓：

- 系统模型
- 算法块
- 目标函数
- 框架图
- 结果图或结果表

## 一个实用建议

如果论文仿真页是双栏排版，而且图很多，最好在请求里明确说：

```text
Please keep the simulation crops tight and include the main comparison figures plus brief comparative comments.
```

这样更容易得到你想要的“对比图 + 简要分析”风格。
