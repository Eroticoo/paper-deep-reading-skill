# paper-deep-reading

`paper-deep-reading` 是一个用于深度阅读本地学术 PDF 的 Codex skill。它的目标不是只输出一段普通摘要，而是生成**带截图证据、可继续加工和发布的 Markdown 报告**。

## 当前状态

**本仓库当前只面向 Windows 用户维护和发布。**

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

### 最推荐的安装方式：直接 clone 到 Codex skills 目录

**这是当前最推荐的安装方式。**

如果你使用默认 Codex skills 目录，请直接执行：

```powershell
git clone https://github.com/Eroticoo/paper-deep-reading-skill.git "%USERPROFILE%\.codex\skills\paper-deep-reading"
```

如果你使用的是自定义 `CODEX_HOME`，请执行：

```powershell
git clone https://github.com/Eroticoo/paper-deep-reading-skill.git "%CODEX_HOME%\skills\paper-deep-reading"
```

**执行完这一步，skill 文件本体就已经安装到位了。**

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
- 当前 README 明确按 Windows-first 发布

## 参考链接

- Codex CLI 官方仓库：https://github.com/openai/codex
