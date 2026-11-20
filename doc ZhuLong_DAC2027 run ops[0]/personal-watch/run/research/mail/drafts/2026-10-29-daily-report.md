# 论文日报草稿 · 2026-10-29（当日 5/5 收口）

- 类型：论文日报（内部 · 中文 · 免审直发）
- 收件人：`paul.liu@cxmt.com`（固定，不加第三方）
- 主题：`[论文日报] 10-29 精选 5 篇（BaiZe/ZhuLong 相关）· 当日 5/5 收口（批次未刷新 kept 0 已如实标注）`
- 正文：`research/mail/2026-10-29-body.txt`
- 附件（5 个 PDF，合计 13,703,732 B ≈ 13.07 MB ≤ 20 MB ⇒ 单封直发）：
  1. `2610.37647.pdf`（MuonGS，21 页，2,682,396 B）
  2. `2610.37609.pdf`（EnvSched，27 页，2,953,308 B）
  3. `2610.36114.pdf`（Context Is a Pipeline，5 页，217,638 B）
  4. `2610.36195.pdf`（Learning to Read Braille，22 页，6,027,201 B）
  5. `2610.37619.pdf`（Egocentric Tennis Video，8 页，1,823,189 B）

## 正文要点（四段式）

1. **口径**：「借鉴」= 对 BaiZe / ZhuLong 有迁移价值；「科普」= 大众看得懂 + 有传播力，两口径不混用；早 3 篇一字未改。
2. **取数如实**：AM / PM 两轮探针均为 `totalResults=124009`、广度 `639590` ⇒ **批次仍 `2026-10-27`，PM 未刷新**；两轮 `--fetch --seen` 15/15 200、`kept 0` / `dropped 600`（557 SEEN + 43 stale），5 篇取自 r118 候选池并做 `id_list` AM 3/3 + PM 2/2 复核；HF `Errno 101` 记 FAIL。
3. **早 3「借鉴」**：MuonGS（累积有效学习率 + GS 去径向 / 等 loss 估计 token 等效加速 ≈15%）· EnvSched（按「环境–任务对」调度 rollout / 8B 40 步 48.81）· Context Is a Pipeline（1/3 工具结果被前缀截断成坏 JSON / 调用 +43%）。
4. **晚 2「科普」**：盲文（合成 96.00% → 真实一级 3.26%，**本日科普 TOP-1**，分镜 `video/SCENES/10_29.html`）· 第一人称网球（1.10 s 后球误差 0.91 m；加长历史无收益；扩散策略 100 Hz）。

## 发送前自查

- [x] 收件人仅 `paul.liu@cxmt.com`（未加第三方）
- [x] 附件合计 13.07 MB ≤ 20 MB
- [x] PDF 头部 `%PDF-` + `%%EOF` + `pdfinfo` / `pdftotext` 全通过（PM 两篇 sha256 与 CDN `etag` 未对齐 ⇒ 正文已明示只声称结构校验）
- [x] 正文数字均可回查当日 `research/daily/2026-10-29.html` 与 PDF
- [x] 未承诺合作 / 署名 / 资助；未透露未公开内部信息；未夸大
