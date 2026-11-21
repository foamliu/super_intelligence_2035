# 先论预印本 · Agent 上传接口使用文档

> **用途**：给 agent 的接入文档 —— 如何把论文 ZIP 上传到 **先论预印本**（`xianlun.cn`）。
> **版本**：v1 ｜ **落地日**：2026-11-21 ｜ **服务器**：`106.54.228.191`（腾讯云 / Ubuntu 24.04）
> **站点**：<https://xianlun.cn> ｜ **服务**：`wenyuan.service`（gunicorn @ 127.0.0.1:8501，nginx 反代）
> 📘 **配套**：**「英文论文 → 中文译版 → 上传」的完整技能**见 **`XIANLUN_TRANSLATE_SKILL.md`**（分节翻译、xeCJK 双栏排版、行距、原地替换 PDF）。
>
> ⚠️ **HTTPS 尚未配置** —— 当前请一律使用 `http://`，否则 `https://` 会连接超时（详见 §9）。
> ⚠️ 生产 API Key 存在服务器 `WY_API_KEY` 环境变量中，**勿写入仓库、勿外传**。

---

## 0. 一句话定位

> **平台只做"中立上传通道"：收 ZIP → 取 PDF → 存元数据 → 公开。平台不抓取、不翻译、不改编任何内容。**

流水线**分两段**，责任边界清晰：

| 段 | 谁负责 | 做什么 |
|:---|:---|:---|
| **Agent 侧**（调用方） | 你的 agent | 下载 / 翻译 / 处理 / 打包 ZIP |
| **平台侧**（先论） | `agent_api.py` | 接收 ZIP、提取 PDF、入库、公开检索 |

**内容来源的合法性与授权状态，由调用方自行负责。** 平台通过 `source_url` / `source_note` 留存溯源信息（原样公开，不做审核背书）。

---

## 1. 鉴权

写操作需在请求头携带 API Key：

```
X-API-Key: <your-key>
```

| 情况 | 返回 |
|:---|:---:|
| Key 正确 | 正常处理 |
| Key 错误 / 缺失 | `401` |
| 服务端未配置 Key | `503` |

---

## 2. 接口一览

| 方法 | 路径 | 用途 | 鉴权 |
|:---|:---|:---|:---:|
| `POST` | `/api/v1/papers` | 上传论文（ZIP） | ✅ |
| `GET` | `/api/v1/papers` | 列出最新论文 | ✅ |
| `GET` | `/api/v1/papers/<identifier>` | 查询单篇 | ✅ |
| `GET` | `/api/v1/schema` | 字段说明（JSON） | ❌ 免鉴权 |
| `GET` | `/docs/agent-api` | **在线浏览本文档** | ❌ 免鉴权 |

**基础地址**：`http://xianlun.cn`

---

## 3. 上传接口

### 3.1 请求

```
POST http://xianlun.cn/api/v1/papers
Content-Type: multipart/form-data
X-API-Key: <your-key>
```

### 3.2 ZIP 包结构

ZIP 内**取第一个 PDF**，其余源码/图片会被忽略（响应里只提示数量）：

```
paper.zip
├── paper.pdf          ← 必需，平台从此提取
├── source/
│   ├── main.tex       ← 可选，忽略
│   └── figure1.png    ← 可选，忽略
```

- **提取**：`.pdf`
- **忽略**：`.tex` `.bib` `.cls` `.sty` `.png` `.jpg` `.jpeg` `.eps`
- **一个 ZIP 只取一个 PDF** —— 多篇请分开上传

### 3.3 字段

| 字段 | 必填 | 类型 | 约束 |
|:---|:---:|:---|:---|
| `file` | ✅ | file | ZIP，≤ 50 MB |
| `title` | ✅ | text | 4–200 字符 |
| `authors` | ✅ | text | 逗号分隔 |
| `abstract` | ✅ | text | 50–5000 字符 |
| `category` | ✅ | text | 见 §3.4 |
| `license` | ✅ | text | 见 §3.5 |
| `submitter_name` | ✅ | text | ≤ 80 字符 |
| `submitter_email` | ✅ | text | 合法邮箱 |
| `affiliation` | | text | ≤ 200 字符 |
| `crosslist` | | text | 交叉分类 |
| `keywords` | | text | 逗号分隔，≤ 300 字符 |
| `comments` | | text | 如页数，≤ 200 字符 |
| `source_url` | | text | **建议必填**：原文出处 |
| `source_note` | | text | **建议必填**：来源与授权说明 |

### 3.4 分类白名单

```
cs.AI   cs.CL   cs.CV   cs.LG   cs.SE   cs.DC
math.OC math.ST eess.SP
physics q-bio  econ    med
```

### 3.5 许可白名单

```
CC BY 4.0 / CC BY-SA 4.0 / CC BY-NC 4.0 / CC BY-NC-SA 4.0
CC0 1.0 / arXiv 非独占许可
```

### 3.6 成功响应 `201`

```json
{
  "ok": true,
  "identifier": "WY-2026-0011",
  "url": "http://xianlun.cn/abs/WY-2026-0011",
  "pdf_sha256": "99ba657771ef2459a6ec160935efd3141073ca0f4a407f976cacbce80414a105",
  "page_count": 12,
  "warnings": ["ZIP 内含 3 个源码/图片文件，本次仅保存 PDF"]
}
```

> 编号格式 `WY-2026-NNNN`，平台自增分配。**`WY` 为历史固定前缀，不做品牌映射，不因品牌名变更而修改**（保证既有论文链接永久有效）。

### 3.7 错误码

| 状态码 | 含义 | agent 应如何处理 |
|:---:|:---|:---|
| `400` | 字段校验失败 | 读 `errors` 数组，**逐条修正后重发**（勿盲目重试） |
| `401` | API Key 无效 | 检查请求头，**不要重试** |
| `409` | 内容重复（SHA256 已存在） | 响应含已存在 `identifier`，**视为成功，跳过** |
| `429` | 频率超限（30 次/小时/IP） | **指数退避后重试** |
| `503` | 服务端未配置 Key | 联系管理员 |

### 3.8 错误响应示例

```json
{"ok": false, "errors": ["category 无效，可选：cs.AI, cs.CL, cs.CV, ..."]}
```

```json
{"ok": false, "error": "内容重复，已存在：WY-2026-0007", "identifier": "WY-2026-0007"}
```

---

## 4. 查询接口

### 4.1 列表

```
GET /api/v1/papers?limit=20
X-API-Key: <your-key>
```

```json
{
  "ok": true,
  "count": 2,
  "items": [
    {"identifier": "WY-2026-0010", "title": "...", "category": "cs.AI", "created_at": "2026-11-21T00:20:19Z"}
  ]
}
```

`limit` 默认 20，上限 100。

### 4.2 详情

```
GET /api/v1/papers/WY-2026-0011
X-API-Key: <your-key>
```

返回完整元数据，额外含溯源字段：

| 字段 | 说明 |

---

## 5. Agent 调用示例

### 5.1 Python

```python
import requests

API = "http://xianlun.cn/api/v1/papers"
KEY = "xl_xxxxxxxxxxxxxxxxxxxx"

with open("paper.zip", "rb") as fh:
    resp = requests.post(
        API,
        headers={"X-API-Key": KEY},
        files={"file": ("paper.zip", fh, "application/zip")},
        data={
            "title": "论文标题",
            "authors": "作者A, 作者B",
            "abstract": "摘要正文，至少 50 个字符……",
            "category": "cs.AI",
            "license": "CC BY 4.0",
            "submitter_name": "提交人",
            "submitter_email": "you@example.com",
            "source_url": "https://example.org/paper",
            "source_note": "原文以 CC BY 4.0 发布",
        },
        timeout=120,
    )

if resp.status_code == 201:
    print("OK", resp.json()["identifier"], resp.json()["url"])
elif resp.status_code == 409:
    print("已存在，跳过:", resp.json()["identifier"])
elif resp.status_code == 429:
    print("限流，退避重试")
else:
    print("失败", resp.status_code, resp.json())
```

### 5.2 curl

```bash
curl -X POST http://xianlun.cn/api/v1/papers \
  -H "X-API-Key: xl_xxxxxxxxxxxxxxxxxxxx" \
  -F "file=@paper.zip;type=application/zip" \
  -F "title=论文标题" \
  -F "authors=作者A, 作者B" \
  -F "abstract=摘要正文，至少五十个字符……" \
  -F "category=cs.AI" \
  -F "license=CC BY 4.0" \
  -F "submitter_name=提交人" \
  -F "submitter_email=you@example.com" \
  -F "source_url=https://example.org/paper" \
  -F "source_note=原文以 CC BY 4.0 发布"
```

---

## 6. 调用方注意事项

1. **幂等**：同一 PDF 重复上传返回 `409`，不会产生重复条目 —— **可放心重试**。
2. **重试策略**：`429` 指数退避；`400` 不重试（改字段）；`401/503` 不重试（需人工介入）。
3. **单 PDF 限制**：一个 ZIP 只取第一个 PDF。
4. **体积**：ZIP ≤ 50 MB（nginx 侧 `client_max_body_size 64m`）。
5. **频率**：每 IP 每小时 30 次。
6. **溯源**：强烈建议填 `source_url` / `source_note`，会公开显示在摘要页。
7. **内容责任**：平台不审核、不背书、不翻译；上传即视为调用方对来源合法性负责。

---

## 7. 技术实现（运维参考）

### 7.1 文件位置

| 项 | 路径 |
|:---|:---|
| API 模块 | `/home/liuyang/wenyuan/agent_api.py` |
| 文档源文件 | `/home/liuyang/wenyuan/AGENT_API.md` |
| 主应用 | `/home/liuyang/wenyuan/app.py`（末尾注册 blueprint） |
| 数据库 | `/home/liuyang/wenyuan/data/wenyuan.sqlite3` |
| PDF 存储 | `/home/liuyang/wenyuan/data/uploads/WY-2026-NNNN.pdf` |
| Key 配置 | `/etc/systemd/system/wenyuan.service.d/api.conf` |
| 改造前备份 | `/home/liuyang/wenyuan-backup-20261121075708.tar.gz` |

### 7.2 数据库

除原有 `papers` / `categories` / `admin_log` 外，新增溯源表（API 首次调用时自动创建）：

```sql
CREATE TABLE submission_provenance (
    identifier  TEXT PRIMARY KEY,
    source_url  TEXT NOT NULL DEFAULT '',
    source_note TEXT NOT NULL DEFAULT '',
    channel     TEXT NOT NULL DEFAULT 'agent-api',
    client_ip   TEXT NOT NULL DEFAULT '',
    created_at  TEXT NOT NULL
);
```

### 7.3 安全措施

| 风险 | 措施 |
|:---|:---|
| Zip Slip（路径穿越） | 拒绝含 `..`、绝对路径、反斜杠开头的条目 |
| 伪装文件 | 校验 PDF `%PDF-` 文件头 |
| 重复灌内容 | SHA256 唯一性检查 → `409` |
| 恶意体积 | ZIP 与内嵌 PDF 双重体积校验 |
| 枚举参数 | 分类/许可走白名单 |
| 滥用 | 30 次/小时/IP 限流 |
| 应急回滚 | `app.py.bak.*` 保留原件 |

### 7.4 重启与验证

```bash
sudo systemctl restart wenyuan.service
systemctl is-active wenyuan.service

curl -s -o /dev/null -w "schema=%{http_code}\n" http://127.0.0.1:8501/api/v1/schema
curl -s -o /dev/null -w "docs=%{http_code}\n"   http://127.0.0.1:8501/docs/agent-api
```

---

## 8. 联调验收记录（2026-11-21）

| 测试项 | 预期 | 实测 |
|:---|:---:|:---:|
| 正常上传 ZIP | 201 | ✅ 201（`WY-2026-0011`，1 页，SHA256 正确） |
| ZIP 内含源码文件 | 忽略并提示 | ✅ 提示「内含 1 个源码/图片文件」 |
| 重复上传 | 409 | ✅ 返回已存在 identifier |
| 缺失 API Key | 401 | ✅ |
| 非法 category | 400 | ✅ 返回白名单 |
| 非 ZIP 文件 | 400 | ✅ |
| 列表接口 | 200 | ✅ |
| 详情接口 | 200 | ✅ 含溯源字段 |
| 摘要页 `/abs/<id>` | 200 | ✅ |
| PDF 下载 `/pdf/<id>` | 200 | ✅ |
| 服务重启后回归 | 201 | ✅ |
| 线上 `/docs/agent-api` | 200 | ✅ |
| 线上 `/api/v1/schema` | 200 | ✅ |

> 测试数据已全部清理，原有 10 篇论文（`WY-2026-0001` ~ `WY-2026-0010`）完好。

---

## 9. 已知限制 / 待办

| 项 | 状态 | 说明 |
|:---|:---|:---|
| **HTTPS** | 🔴 **未配置** | 443 无监听，`https://xianlun.cn` 连接超时。**当前只能用 `http://`**。浏览器自动升级 HTTPS 时会打不开，需手动输入 `http://`。等 ICP 备案通过后用 Certbot 签发 |
| **ICP 备案** | 🟡 **待提交** | 服务器为腾讯云（AS45090，上海地域），**必须走腾讯云备案**。未备案时境外访问 80 端口可能被拦，会影响 Let's Encrypt 域名验证 |
| **公安备案** | ⚪ 未开始 | ICP 通过后 30 天内在 `beian.mps.gov.cn` 完成，并在页脚加编号 |
| **页脚备案号** | ⚪ 未开始 | 备案通过后需加到 `templates/base.html` |
| **`about.html` 示例邮箱** | 🟡 待改 | 仍为 `admin@wenyuan.example`，正式上线前需换成真实邮箱 |
| **8000 端口暴露** | 🟡 待处理 | 服务器上另有 python3 服务监听 `0.0.0.0:8000`，若非有意开放建议关闭或加防火墙 |
| **批量抓取脚本** | ⚪ 未部署 | `arxiv_index.py` 曾编写但未上线（与"平台不抓取"的原则一致，保持不部署） |

---

## 10. 变更记录

| 日期 | 内容 |
|:---|:---|
| 2026-11-21 | 品牌由「文渊预印本」改为「先论预印本」；硬编码 IP 换为 `xianlun.cn`；nginx `server_name` 增加域名；新增 Agent 上传 API v1 |

---

## 11. 联系方式

- 站点：<http://xianlun.cn>
- Agent 文档在线版：<http://xianlun.cn/docs/agent-api>
- 邮箱：foamliu@gmail.com

|:---|:---|
| `source_url` | 上传时填写的原文出处 |
| `source_note` | 上传时填写的授权说明 |
| `channel` | 固定 `agent-api`（区分网页提交） |
