# 技能 · 论文英译中并上传先论空间（EN → ZH Preprint Translation & Upload）

> **用途**：把一篇**英文 LaTeX／IEEEtran 双栏论文**译成**中文可读版 PDF**，再放到 **先论空间（`xianlun.cn`）** 上公开发布。
> **版本**：v1 ｜ **落地日**：2026-11-21 ｜ **首个实做**：`2611.19056v1`（DAC 2027，IEEEtran 双栏，译后 8 页）
> **服务器**：`106.54.228.191`（腾讯云 / Ubuntu 24.04）｜ **服务**：`wenyuan.service`（gunicorn @ `127.0.0.1:8501`，nginx 反代）
> **配套文档**：上传接口与字段白名单见 **`XIANLUN_AGENT_API.md`**（本文件只讲「翻译 → 排版 → 替换」这一段）。

---

## 0. 一句话流程

> **译（分节、逐节对译）→ 排（xelatex + xeCJK 双栏）→ 校（页数／行距／跨栏／图）→ 传（起新号 or 原地换 PDF）→ 验（MD5 + HTTP + 页数）**

5 个阶段，**每一阶段都有硬判据**，判据不过就不许往下一阶段走（§7 是全局验收集）。

| 阶段 | 产物 | 放行判据 |
|:--|:--|:--|
| ① 取源 + 分节 | `tex_src/` 原文快照 | 每节 `.tex` 可独立编译（`\input` 树完整） |
| ② 逐节对译 | `tex_zh/` 中文快照 | 图表／公式／`\cite`／`\ref` **一字不动** |
| ③ 排版调参 | `main.pdf` | `xelatex` ×3 零 `!` 错误；页数符合预期 |
| ④ 上传 | 站上条目 | 新号 `201` / 替换后 `200` |
| ⑤ 验证 | 校验记录 | MD5 一致 + 页数一致 + 页面 200 + 目视 3 页 |

---

## 1. 前置检查（开工前 5 分钟）

```powershell
# 1) 工具链（Windows 本机实测可用）
Get-Command python,xelatex,bibtex,pdftotext,zip
python -c "import requests; print('requests', requests.__version__)"

# 2) 中文字体（缺字体 = 整篇变豆腐块，务必先确认）
xelatex --version | Select-String MiKTeX          # 本次用 MiKTeX 25.12
fc-list :lang=zh family | Select-String 'Source Han|Noto.*CJK|SimSun|SimHei|Zen Hei'

# 3) 站点可达（⚠️ 必须先确认走 IP 还是域名，见 §5.0）
(Invoke-WebRequest http://106.54.228.191/api/v1/schema -UseBasicParsing).StatusCode   # 期望 200
```

**字体口径**（两条路都对，别混用）：

| 字体 | 适用 | 备注 |
|:--|:--|:--|
| `WenQuanYi Zen Hei` | 服务器／Linux 容器编译 | TTF 轮廓，弯引号与破折号齐全（Droid Sans Fallback 缺字） |
| `SimSun` / `Noto Serif CJK SC` / `Source Han Serif SC` | Windows 本机编译 | 宋体观感更接近正式出版物 |

> 🔴 **血泪 ①**：字体写错不会报错，只会**静默生成满篇方框**的 PDF。所以 §4 编译完**必须**目视第 1 页。

---

## 2. 取源与分节

**取源**：从 arXiv 取 e-print 源码包（`/e-print/` 而非 `/pdf/`），解出 `.tex` / `.cls` / `.bst` / `figures/`。
仓库里已存了一份可参考的完整快照：

```
doc/tex_src/            ← 英文原文快照（main.tex + DAC2027/*.tex + figures/system_arch.pdf + reference.bib）
doc/tex_zh/             ← 中文译版快照（同结构，图直接复用 pdf）
```

**分节即分任务**：一篇 IEEEtran 论文通常长这样，**按 `\input` 逐个译**，不要整篇一口气丢给模型：

```
main.tex
 └─ DAC2027/0_abstract.tex   ← 摘要 + IEEEkeywords
    1_intro.tex  2_background.tex  3_design.tex  4_grounding.tex
    5_bench.tex  6_exp.tex  7_discussion.tex  8_conclusion.tex
```

**分节译的三条理由**（不是风格问题）：

1. 单节 2–20 KB，模型不会「译到后面忘了前面的术语」；
2. 出错只回滚一节，不用整篇重来；
3. 图表计数器、`\ref` 天然按节归属，便于核对。

**翻译硬规则（每条都踩过坑）**：

| 类别 | 规则 |
|:--|:--|
| 🚫 **不动** | 所有 `\begin{...}` `\end{...}`、`\cite{}` `\ref{}` `\label{}` 的**键名**、`\textbf{}` 的包裹结构、数学环境、表格全部单元格、`\includegraphics` 路径 |
| 🚫 **不动** | 数字、百分比、单位、`Pass@1`、`pp`、RQ 编号 |
| ✅ **要译** | 正文叙述、图题／表题 `\caption{}`、表头文字、`\section{}` 标题、`\noindent\textbf{主要贡献。}` 这类引导词 |
| ✅ **术语一致** | 建一张术语表，全篇同一译法。本次口径见 §2.1 |
| ⚠️ **保留英文** | 专有名词／工具名／缩写：`PyAether` `SKILL` `Tcl` `MCP` `EDA` `LLM` `GRPO` `Pass@1` `L1–L4` |
| ⚠️ **中文排版** | 全角标点；中英文之间的薄空由 `CJKecglue` 自动加（§3.2），**不要手工敲空格** |

### 2.1 术语表（首个实做定下的口径，可继承）

| 英文 | 中文 | 备注 |
|:--|:--|:--|
| execution-grounded | 执行接地 | 全文统一，勿混「基于执行」 |
| grounding gap | 接地落差 | 与上一条同根 |
| observation fidelity | 观测保真度 | 标题关键词 |
| harness | 工具框架 | 不用「测试框架」（易与 test framework 混） |
| backbone | 骨干模型 | |
| read-back | 回读 | |
| self-exploration | 自探索 | |
| situated (L4) | 情境化 | |
| belief update | 信念更新 | |
| ablation | 消融（实验） | |
| Pass@1 | Pass@1 | 不译 |

> 📌 术语表要落到 `tex_zh/TERMS.md`（或 `main.tex` 注释头），下一篇复用 —— 否则同一概念两种译法，读者会当成两件事。

---

## 3. 排版：xelatex + xeCJK 双栏

### 3.1 `main.tex` 骨架（照抄即可）

```latex
\documentclass[conference]{IEEEtran}
% =====================================================================
%  中文译版：<英文原标题>
%  原文：arXiv:XXXX.XXXXXvN，第一作者 <Name>
%  中文版由原作者授权发布。本译版仅供学习与研究，非商业用途。
%  ⚠️ 授权说明只留在本注释里，不排进正文（见 §3.4）
%  构建：xelatex main && bibtex main && xelatex main && xelatex main
% =====================================================================
\usepackage{cite}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{algorithmic}
\usepackage{graphicx}
\usepackage{textcomp}
\usepackage{xcolor}
\usepackage{booktabs}
\usepackage{url}

% ---------------- 中文支持 ----------------
\usepackage{xeCJK}
\setCJKmainfont{WenQuanYi Zen Hei}   % Windows 可换 SimSun / Noto Serif CJK SC
\setCJKsansfont{WenQuanYi Zen Hei}
\setCJKmonofont{WenQuanYi Zen Hei}
\xeCJKsetup{CJKecglue={\hskip 0.08em plus 0.04em minus 0.02em}}
\setlength{\parindent}{2em}          % 中文段首缩进两字
\setlength{\parskip}{0pt}            % 取消英文段间距

\setlength{\textfloatsep}{8pt plus 2pt minus 2pt}
\setlength{\floatsep}{6pt plus 2pt minus 2pt}
\setlength{\intextsep}{6pt plus 2pt minus 2pt}
\setlength{\abovecaptionskip}{3pt}
\setlength{\belowcaptionskip}{0pt}

\begin{document}
\title{<中文标题>}
\author{\IEEEauthorblockN{<作者拼音，原样保留>}\\
\IEEEauthorblockA{\textit{<单位中文名>}，中国；\quad 邮箱：\{...\}@...}}
\maketitle

% >>> 行距开关放这里（关键！见 §3.3）<<<
\renewcommand{\baselinestretch}{1.35}\selectfont

\input{DAC2027/0_abstract}
...
\bibliographystyle{IEEEtran}
\bibliography{reference}
\end{document}
```

### 3.2 中文独有的三处必调

| 项 | 为什么 | 值 |
|:--|:--|:--|
| `xeCJK` + `\setCJK*font` | 没有它中文不进 PDF | 三档都要设，防 `\texttt` 里掉字 |
| `CJKecglue` | 中英混排（`PyAether` 挨着汉字）默认挤成一坨 | `≈0.08em`，自动加、别手敲 |
| `\parindent=2em` + `\parskip=0pt` | 中文习惯 = 段首缩进两字、段间不留空 | 照抄；**别保留英文的 `\parskip`** |

### 3.3 🔴 行距：唯一安全的做法

**症状**：中文方块字比英文密，直接编译出来**行贴行**，密到读不下去；一加行距又**页数暴涨 / 版面塌陷**。

**试过并且失败的方案（务必别再用）**：

| 方案 | 结果 |
|:--|:--|
| `\linespread{1.42}` 放导言区 | 正文松了，但**标题区也被撑开**，页数 7 → **9 页** |
| `\renewcommand{\normalsize}` 改字号 13.2–13.4pt | **9 页**，且 RQ1 列表**跨栏断裂**（左栏断句、右栏接尾） |
| `\setlength{\baselineskip}{13.2pt}` + `\normalbaselineskip` | 页数回到 7，但**两栏内容交错**，版面彻底坏掉 |

**原因**：IEEEtran 双栏的浮动体（`figure*`/`table*`）取样依赖 `\baselineskip`／`\normalsize` 的**原始值**；在导言区改它们，浮动体判断就错位 ⇒ 跨栏断句、栏目交错。

**✅ 正确做法：`\maketitle` 之后**，只改行距系数，只用一个命令：

```latex
\maketitle
\renewcommand{\baselinestretch}{1.35}\selectfont
```

- **位置**：必须在 `\maketitle` 后 —— 标题／作者块保持 IEEEtran 原样，只把正文拉开；
- **数值**：1.35 是本次实测的甜点（10pt 字 / 13.5pt 行）；1.28 更省页，1.42 起失控；
- `\selectfont` 不能省，否则当前段落的 `\baselineskip` 不刷新。

**页数换算（IEEEtran conference，10pt 双栏，7 页原文）**：

| `\baselinestretch` | 页数 | 备注 |
|:--:|:--:|:--|
| 1.00 | 7 | 原样，太密不可读 |
| 1.28 | ~7.5 | 只有必须压到 7 页才用 |
| **1.35** | **8** | ✅ 本次采用：松紧合适、无跨栏、无交错 |
| 1.42 | 9 | 标题区变形 |

> 📌 **页数不是 KPI，「能读 + 不漏图 + 不跨栏」才是。** 8 页是**可接受**的代价；只有投稿有时限才为省页牺牲行距。

### 3.4 译版声明：**不要排进正文**

早期版本在 `\maketitle` 后塞了一个 `\begin{center}\footnotesize…中文译版…以英文原文为准\end{center}` 灰字块。问题：

- 每篇都顶一行「授权／免责」，**版面污染** —— 读者第一眼看到的是声明而不是摘要；
- 信息**重复**：站点摘要页本就有「许可协议／提交人／备注」栏位（§5.4）。

**现行做法**：授权与出处**只写在 `main.tex` 顶部注释**（源码可查），版面从标题直接进摘要。

> ⚠️ **前提**：只有**确实拿到授权**才发中文版。站点《上传须知》明写「不得上传未经授权的他人作品译本」—— **这是硬门槛，不是格式建议**。

---

## 4. 校版（Grade-check）：5 项全过才算译完

```powershell
cd <work>\tex_zh
xelatex -interaction=nonstopmode main 2>&1 | Select-String '^!'
bibtex main
xelatex -interaction=nonstopmode main 2>&1 | Select-String '^!'
xelatex -interaction=nonstopmode main 2>&1 | Select-String '^!'
Select-String main.log 'Output written'          # 期望: (…) pages, … bytes
```

| # | 检查 | 判据 | 不达标怎么办 |
|:--:|:--|:--|:--|
| 1 | 编译 | 三轮 `grep '^!'` = **0** | 逐条修 `!` 行，**不许**吞错误重跑 |
| 2 | 页数 | 落在 §3.3 的预期区间 | 只调 `\baselinestretch`（**只准这招**） |
| 3 | **目视 3 页** | 第 1 页（标题+摘要）、第 2–3 页（正文+大图） | 🔴 **必做**，见下 |
| 4 | 字体 | 无方框／无豆腐块 | 换 §1 字体表里另一种 |
| 5 | 浮动体 | 图不越界、表不爆栏、**无跨栏断句** | 查有没有偷偷改 `\normalsize`／`\baselineskip` |

**目视怎么做**：把 PDF 渲成 PNG 再看（比开阅读器逐页翻快，也便于贴进评审记录）：

```powershell
pdftoppm -png -r 110 main.pdf page     # → page-1.png, page-2.png ...
```

> 🔴 **血泪 ②**：`log` 干净 ≠ 版面正确。本次前三版**编译零错误**，但分别出现「标题区被撑开」「RQ1 跨栏断裂」「两栏交错」—— **全是只有看图才发现的**。

**残留告警的容忍线**：`Underfull \vbox (badness 10000)` 出现在**分页／分栏处**、`Overfull \hbox` ≤ 2pt（浮动体宽度）属**正常**；正文里成片的 Underfull/Overfull 才是真问题。

---

## 5. 上传

### 5.0 🔴 先确认 URL 形态

**域名与 IP 的结论可能不同**（本次实测）：

| 入口 | 结果 |
|:--|:--|
| `http://106.54.228.191/...` | ✅ 200，API 正常 |
| `http://xianlun.cn/...` | ❌ 返回**腾讯云「备案」拦截页**（ICP 未备案 ⇒ 80 端口被拦） |

⇒ **未备案期间一律用 IP**；脚本里把基址做成变量，只改一处：

```python
BASE = "http://106.54.228.191"     # 备案后改回 http://xianlun.cn（并同步切 https）
```

### 5.1 哪条路？（决定用 A 还是 B）

| 情形 | 用哪条 | 入口 |
|:--|:--|:--|
| **首次发布**（站上还没有这篇） | **A. 新号上传** | `POST /api/v1/papers`（ZIP） |
| **同一篇改版**（已有条目，只想换 PDF） | **B. 原地替换** | 服务器端 `cp` + 重启服务 |
| 有新文件要重传、且愿意换编号 | A（`source_note` 注明「v2 替换旧号」） | 同上 |

> 📌 **B 是唯一能保住原编号与链接的路径**：`agent_api.py` **没有「更新 PDF」路由**；同一份内容重走 A 会因 SHA-256 撞车拿 `409`，换新内容走 A 会**生成新编号**（旧链接失效）。

### 5.2 A · 新号上传（ZIP）

ZIP 里**只放 PDF**（其他文件平台会忽略并提示「忽略 N 个文件」）：

```python
import io, zipfile, requests
from pathlib import Path

BASE = "http://106.54.228.191"
KEY  = "<WY_API_KEY：从服务器 /etc/systemd/system/wenyuan.service.d/api.conf 取，勿入库>"
PDF  = Path("main.pdf")

buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(PDF, "main.pdf")
buf.seek(0)

r = requests.post(
    f"{BASE}/api/v1/papers",
    headers={"X-API-Key": KEY},
    files={"file": ("paper.zip", buf, "application/zip")},
    data={
        "title":   "运行、回读、精炼：执行接地 EDA 智能体中的观测保真度",
        "authors": "Yang Liu, Shiwei Hou, ...",           # 逗号分隔，与原文一致
        "abstract": "<中文摘要，50–5000 字符>",
        "category": "cs.AI",                               # 白名单：XIANLUN_AGENT_API.md §3.4
        "license":  "arXiv 非独占许可",                     # 白名单：§3.5
        "submitter_name":  "Yang Liu",
        "submitter_email": "paul.liu@cxmt.com",
        "comments":   "中文译版，8 页；双栏排版优化版",       # → 摘要页「备注」栏
        "source_url":  "https://arxiv.org/abs/2611.19056",
        "source_note": "原文以 arXiv 非独占许可发布，中文译版经原作者授权",
        "keywords": ", ".join(["EDA 脚本", "LLM 智能体", "执行接地", "观测保真度", "基准测试"]),
    },
    timeout=180,
)
print(r.status_code, r.json())
# 201 → 成功：identifier / url / pdf_sha256 / page_count
# 409 → 已存在（SHA-256 撞车），响应里带 identifier，按成功处理
```

### 5.3 B · 原地替换 PDF（服务器端）

```bash
# 0) 本地：scp main.pdf <user>@106.54.228.191:/tmp/new.pdf
ssh <user>@106.54.228.191

# 1) 先备份（带时分秒，永远可回滚）
cp /home/liuyang/wenyuan/data/uploads/2611.19056v1.pdf \
   /home/liuyang/wenyuan/data/uploads/2611.19056v1.pdf.bak-$(date +%H%M%S)

# 2) 原子落位（不要直接覆盖正在被读的文件）
mv /tmp/new.pdf /home/liuyang/wenyuan/data/uploads/2611.19056v1.pdf
chmod 600 /home/liuyang/wenyuan/data/uploads/2611.19056v1.pdf

# 3) 重启服务，让页面缓存的页数／体积刷新
sudo systemctl restart wenyuan.service
systemctl is-active wenyuan.service          # 期望 active
```

> 🚫 **不要**试图用网页表单「编辑」来换 PDF —— 表单只做元数据；也**不要**走 `:8000`（那是另一个裸 `http.server`，无鉴权、返回 501）。

### 5.4 元数据同步（替换 PDF 时常被忘）

替换 PDF **不会**自动更新摘要页上的「页数／文件大小／备注」。若页数变了：

- **备注里写了页数** ⇒ 必须改（否则摘要页写「7 页」而 PDF 是 8 页）；
- 改法：提交人登录 `/login`（邮箱+密码）→ 编辑该条目；或改 `/home/liuyang/wenyuan/data/wenyuan.sqlite3` 的 `papers` 表（**改前先 `.backup`**）。

> 📌 本次遗留：`2611.19056v1` 备注仍是「中文译版，7 页」（实际 8 页），下次一并改。

---

## 6. 验证（传完立刻做，4 条）

```powershell
$BASE = "http://106.54.228.191"
$ID   = "2611.19056v1"

# ① PDF 直链 200 + 体积
$r = Invoke-WebRequest "$BASE/pdf/$ID" -UseBasicParsing
"$($r.StatusCode)  $($r.RawContentLength) bytes"
[IO.File]::WriteAllBytes("$env:TEMP\got.pdf", $r.Content)

# ② 摘要页 200
(Invoke-WebRequest "$BASE/abs/$ID" -UseBasicParsing).StatusCode

# ③ MD5 一致：服务器 md5sum /home/liuyang/wenyuan/data/uploads/$ID.pdf  vs  下载回来的
Get-FileHash "$env:TEMP\got.pdf" -Algorithm MD5

# ④ 页数一致：pdftoppm -png got.pdf p → 数 p-*.png；并与页面「页数」文案比对（§5.4）
```

**另加一条人工判据**：浏览器打开 `/pdf/$ID`，翻到**第 1、2、3 页**，确认是中文、无方框、无跨栏。

---

## 7. 全局验收清单（打印出来打勾）

- [ ] 原文件已备份（`.bak-HHMMSS`）
- [ ] 三轮 `xelatex` 后 `grep '^!' main.log` = 0
- [ ] `Output written … (N pages)` 与预期一致
- [ ] 已目视第 1/2/3 页：中文正常、无豆腐块、无跨栏断裂、图完整
- [ ] `\baselinestretch` 在 `\maketitle` **之后**，全篇只有一处
- [ ] 图表／公式／`\cite` 键名与原文逐一对应，无「译丢引用」
- [ ] 授权说明只在注释里，**版面没有声明块**
- [ ] 上传走 A 或 B 的**正确一条**（改版别误用 A）
- [ ] 服务器端 MD5 == 下载回来 MD5
- [ ] `/abs/<id>` 与 `/pdf/<id>` 均 200
- [ ] 备注里的页数／体积与新版一致
- [ ] API Key、SSH 口令**没有**出现在脚本、日志、提交里

---

## 8. 常见坑（血泪清单）

| # | 坑 | 症状 | 正解 |
|:--:|:--|:--|:--|
| 1 | 字体缺失／写错名 | 满篇方框，编译**不报错** | §1 先 `fc-list`；§4 目视 |
| 2 | 导言区调 `\baselineskip`／`\normalsize` | 跨栏断句、两栏交错 | §3.3，只改 `\maketitle` 后的 `\baselinestretch` |
| 3 | 行距拉太狠 | 9 页 + 标题区变形 | 1.35 是甜点，别超 1.42 |
| 4 | 把声明排进正文 | 每篇顶一行灰字 | §3.4，搬进注释 |
| 5 | 用域名访问 | 备案拦截页，像是站挂了 | §5.0，未备案用 IP |
| 6 | 想用 API「更新」PDF | 没这个路由；重发拿 409 或换新号 | §5.3，服务器端替换 |
| 7 | 直接覆盖 PDF | 可能读到半截文件 | 先 `cp` 到 `/tmp` 再 `mv` 原子落位 |
| 8 | 忘了重启服务 | 页面仍显示旧页数 | `systemctl restart wenyuan.service` |
| 9 | 备注页数没改 | 摘要页「7 页」而 PDF 8 页 | §5.4 |
| 10 | 中英混排手敲空格 | 空格宽窄不一、行末难看 | 交给 `CJKecglue` |
| 11 | 口令／Key 落盘 | 明文进脚本 / git | 从 systemd `EnvironmentFile` 取，脚本只在内存里用 |
| 12 | 一次改多处 | 出问题不知哪一步动的 | 一次只改**一个**变量，改完立刻看页数 + 看图 |

---

## 9. 可复用资产（首个实做的落点）

| 路径 | 内容 |
|:--|:--|
| `doc/tex_src/` | 英文原文快照（`main.tex` + `DAC2027/*.tex` + `figures/` + `reference.bib` + `IEEEtran.cls`） |
| `doc/tex_zh/` | 中文译版快照（同结构；`main.tex` = §3.1 骨架 + §3.3 行距开关） |
| `personal-watch/XIANLUN_AGENT_API.md` | 上传接口、字段/分类/许可白名单、错误码、运维路径 |
| `personal-watch/XIANLUN_TRANSLATE_SKILL.md` | **本文件**：翻译 → 排版 → 上传全流程 |

**下一篇要做的三件事**：① 把 §2.1 术语表落成 `tex_zh/TERMS.md`；② 把 §3.1 骨架占位符化成 `tex_zh/TEMPLATE/main.tex`；③ 编译命令固化为 `make_zh.ps1`（`bibtex` + `xelatex ×3`，末尾自带 `grep '^!'` 断言）。

