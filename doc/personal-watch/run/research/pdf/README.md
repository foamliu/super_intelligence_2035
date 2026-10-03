# research/pdf/ — PDF 落地目录（**默认不落地**）

> 由 **research agent** 按需写入（任务书 §4 铁律第 8 条）。

**政策**：
- **默认只存链接**（`research/<date>.md` / `papers.jsonl` 里的 `pdf_url`），**不下载 PDF**。
- 确需落地时才下载到本目录，且必须：
  1. 校验 `Content-Type: application/pdf` + 文件头 `%PDF`（否则判失败、删除）；
  2. **单轮限量 ≤ 10 篇**，控制仓库体积；
  3. 文件名用 `<arXiv_ID>.pdf`（如 `2609.12345.pdf`），便于与台账对应。
- ⚠️ 本目录**不参与每轮唤醒读取**；体积过大时应清理或改用外链。
