# 论文日报草稿 · 2026-10-31（当日 5/5 收口）

- 类型：论文日报（内部 · 中文 · 免审直发）
- 收件人：`paul.liu@cxmt.com`（固定，不加第三方）
- 主题（分包 2 封）：
  - `[论文日报] 10-31 精选 5 篇（BaiZe/ZhuLong 相关）(1/2)`
  - `[论文日报] 10-31 精选 5 篇（BaiZe/ZhuLong 相关）(2/2)`
- 正文：`research/mail/2026-10-31-body-1of2.txt` / `research/mail/2026-10-31-body-2of2.txt`
- 分包理由：当日 5 篇 PDF 合计 **44,904,331 B ≈ 42.83 MiB > 20 MB**（10-12 运维指令 ④）

## 1/2 封（早 3 篇「借鉴」· 3 个 PDF · 5,988,962 B ≈ 5.71 MB）

1. `2610.38095.pdf` —— Nemotron 3.5 Super & Lightning（NVIDIA · 79 页 · 3,628,821 B）
2. `2610.40305.pdf` —— Rimuru（中山大学（珠海）+ 独立研究者 · 14 页 · 1,924,458 B）
3. `2610.40574.pdf` —— MTA-OPSD（TUM / MCML / relAI + Kyoto / NII / ELLIS / Aalto · 19 页 · 435,683 B）

## 2/2 封（晚 2 篇「科普」· 1 个 PDF · 14,658,374 B ≈ 13.98 MB）

4. `2610.40530.pdf` —— PhysCount（南京大学 + NVIDIA · 38 页 · 14,658,374 B）**本日科普 TOP-1**
5. `2610.38957` —— MIMO-Bench（IIIT Hyderabad + MSR India + IIT Hyderabad · 52 页 · 24,250,619 B）
   ⇒ **PDF ≈ 23.13 MB 超 20 MB 附件上限 ⇒ 不附，正文给链接 + 摘要**（符合 10-12 运维指令 ④）
   （本地 `research/pdf/2026-10-31/2610.38957.pdf`，`pdf/` 不入 git）

- 选文口径：早 3 =「借鉴」（BaiZe / ZhuLong 相关性）；晚 2 =「科普」（大众可懂 + 传播力），两口径不混用。
- 数据核验：5 篇 PDF 全部 `%PDF-` 头 + 尾部 `%%EOF` + `pdfinfo` 页数可解析（79 / 14 / 19 / 38 / 52 页）；
  ⚠️ 5 篇 `sha256` 与 CDN `etag` 均不一致 ⇒ 完整性只声称「结构校验 + 字节数 == `Content-Range` total」。
- 配套交付：`research/daily/2026-10-31.html`（5/5 收口）· `research/video/SCENES/10_31.html`（分镜 5 镜 / 120s / 口播 386 字）。
