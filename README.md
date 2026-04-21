# paper-deep-reading

`paper-deep-reading` 是一个用于深度阅读本地学术 PDF 的 Codex skill。它的目标不是只输出一段普通摘要，而是生成**带截图证据、可继续加工和发布的 Markdown 报告**。

## 当前状态

**本仓库当前以 Windows 为正式支持平台。**

**mac 用户在安装好 Python 依赖后，通常也可以使用核心 Python 脚本，但目前仓库还没有把 mac 作为正式发布和完整验证的平台。**

默认工作环境：

- `Windows 10 / Windows 11`
- `Python 3.10+`
- `Codex CLI`

这套仓库现在已经整理成：**仓库根目录本身就是 skill 目录。**  
也就是说，别人不需要再额外执行安装脚本，**直接 clone 到 Codex 的 skills 目录里就能安装这个 skill。**

## 这个 skill 能做什么

安装后，Codex 可以通过 `$paper-deep-reading` 来：

- 逐页阅读本地学术 PDF
- 从 PDF 原文核对标题、作者和单位信息
- 截取标题抬头、定理链、算法块、系统模型、图和表
- 生成结构化中文 `report.md`
- 保留本地 `images/` 文件夹
- 把 `report.md` 中的图片链接改写成公网 URL
- 在交付前执行最终自我审查

它特别适合：

- 控制理论论文
- 状态估计、滤波与 observer 设计论文
- 有 theorem / lemma / assumption / property 链条的论文
- 既重视技术推导，也重视仿真对比图的论文

## 仓库结构

```text
paper-deep-reading/
+-- README.md
+-- SKILL.md
+-- openai.yaml
+-- agents/
+-- references/
\-- scripts/
```

## 下载安装

### 如果你本身就在用 Codex

**最简单粗暴的方式，就是直接让 Codex 帮你安装这个 skill。**

你可以直接对 Codex 说：

```text
请帮我安装这个 skill：
https://github.com/Eroticoo/paper-deep-reading-skill
把它安装到我的 Codex skills 目录里，并把需要的 Python 依赖也一起装好。
```

如果你希望说得更明确一点，也可以这样写：

```text
请帮我把这个 skill 安装到我的 Codex skills 目录：
https://github.com/Eroticoo/paper-deep-reading-skill
这是一个只面向 Windows 的 skill，请同时安装 pymupdf 和 pillow；
如果环境里需要处理扫描版 PDF，再补 pytesseract。
```

### 最推荐的安装方式：直接 clone 到 Codex skills 目录

**这是当前最推荐的安装方式。**

如果你是 Windows 用户，并且使用默认 Codex skills 目录，请直接执行：

```powershell
git clone https://github.com/Eroticoo/paper-deep-reading-skill.git "%USERPROFILE%\.codex\skills\paper-deep-reading"
```

如果你是 Windows 用户，并且使用的是自定义 `CODEX_HOME`，请执行：

```powershell
git clone https://github.com/Eroticoo/paper-deep-reading-skill.git "%CODEX_HOME%\skills\paper-deep-reading"
```

**执行完这一步，skill 文件本体就已经安装到位了。**

如果你是 mac 用户，对应思路也是一样的：把这个仓库直接 clone 到你的 Codex skills 目录，并把目录名命名为 `paper-deep-reading`。只是当前 README 的命令示例默认按 Windows 路径来写。

### 第二步：安装 Python 依赖

**安装完 skill 目录后，还需要安装 Python 依赖。**

必需依赖安装命令：

```powershell
python -m pip install --upgrade pymupdf pillow
```

如果你要处理扫描版 PDF，建议再安装：

```powershell
python -m pip install --upgrade pytesseract
```

### 不想用 git 也可以

如果你不想用 `git clone`，也可以：

1. 从 GitHub 下载 zip
2. 解压后把整个仓库根目录重命名为 `paper-deep-reading`
3. 放到：

```text
%USERPROFILE%\.codex\skills\
```

或者：

```text
%CODEX_HOME%\skills\
```

然后再执行上面的 `pip install` 依赖命令即可。

## 环境要求

### 1. 安装 Node.js 和 npm

**Codex CLI 通过 npm 分发，所以必须先安装 Node.js。**

建议版本：

- `Node.js 18+`
- 随 Node.js 自带的 `npm`

检查命令：

```powershell
node --version
npm --version
```

### 2. 安装 Codex CLI

**这是使用本 skill 的前提。**

官方安装命令：

```powershell
npm install -g @openai/codex
```

登录命令：

```powershell
codex --login
```

检查命令：

```powershell
codex --version
```

### 3. 安装 Python

**必须安装 `Python 3.10+`。**

下面两种方式至少有一种可用：

```powershell
python --version
```

或者：

```powershell
py -3 --version
```

### 4. Python 依赖说明

**必需依赖：**

- `pymupdf`
- `pillow`

**扫描版 PDF 可选但推荐：**

- `pytesseract`
- Windows 上单独安装的 `Tesseract OCR`

对于 mac 用户，如果你走的是核心 Python 路径，依赖仍然是同一套：

- `pymupdf`
- `pillow`
- 可选：`pytesseract`

也就是说，**mac 真正需要的是 Python 依赖，不是 Windows 专用脚本。**

## OCR 可选配置

对于自带文本层的 PDF，`PyMuPDF` 通常已经足够。

对于扫描版 PDF，建议额外安装：

1. Windows 版 `Tesseract OCR`
2. Python 包 `pytesseract`

这个 skill 把 OCR 当作兜底路径，而不是主路径。

## 安装后检查

**安装完成后，建议立刻做一次最小检查：**

```powershell
cd %USERPROFILE%\.codex\skills\paper-deep-reading
python .\scripts\pdf_tool.py
```

如果看到 usage 输出，而不是缺依赖报错，就说明基础安装基本成功。

如果你是 mac 用户，更推荐直接运行：

```bash
python3 ./scripts/pdf_tool.py
```

如果能看到 usage 输出，而不是缺依赖报错，就说明核心 Python 路径可以工作。

## 哪些脚本是 Windows 专用，哪些不是

当前仓库里：

- `scripts/pdf_tool.ps1` 是 **Windows / PowerShell 专用包装器**
- `scripts/pdf_snapshot.swift` 是 **Apple 平台 fallback**
- `scripts/pdf_tool.py`、`scripts/init_output_folder.py`、`scripts/render_wechat_paste.py`、`scripts/validate_report.py` 这些核心脚本本质上都是 **跨平台 Python 脚本**

所以更准确地说：

- **Windows 是当前正式支持平台**
- **mac 可以试验性使用核心 Python 路径**
- **仓库不是“只能在 Windows 上运行”，而是“当前只把 Windows 当作正式支持对象”**

## 在 Codex 中如何调用

最小调用：

```text
Use $paper-deep-reading to read this local PDF and write a Chinese report.
```

更完整的调用：

```text
Use $paper-deep-reading to read this local PDF, capture the title-author header image,
explain the technical core with source-grounded screenshots, emphasize the simulation
figures, and save the result as report.md plus images/.
```

如果你已经知道公网图片前缀，也可以这样指定：

```text
Use $paper-deep-reading to read this PDF and rewrite all images in report.md with:
https://cdn.jsdelivr.net/gh/<owner>/<repo>@<commit>/<slug>/images
```

## 输出形式

最终交付默认围绕下面两部分展开：

- `report.md`
- `images/`

生成出的报告会尽量满足：

- 标题使用标准学术中文翻译
- 在 `#` 标题下紧接标题-作者抬头截图
- 在 section `2` 解释 theorem / lemma / assumption 之间的关系
- 对控制类论文把核心系统模型公式转成 LaTeX
- 在论文支持时使用多张仿真 / 实验图形成证据链
- 最终把图片链接改为公网 URL
- 在交付前进行最终自我审查

## 给仓库访问者的说明

- 这是一个 **skill 仓库**，不是单一 prompt 文件
- `scripts/` 下的辅助脚本属于 skill 的一部分
- 当前 README 按 Windows-first 发布
- mac 用户可以优先尝试 `python3 ./scripts/pdf_tool.py` 这条核心 Python 路径

## 参考链接

- Codex CLI 官方仓库：https://github.com/openai/codex
