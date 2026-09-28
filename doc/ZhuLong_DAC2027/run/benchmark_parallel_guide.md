# Benchmark 并发执行手册

## 1. 项目代码

```bash
/nasdata/app.e0031982/code/eda_fastmcp/
```

## 2. MCP 服务

### 2.1 启动 MCP 服务

```bash
# 启动 search api 工具服务
bash scripts/start_recall_api.sh

# 启动 mcp 服务（EDA_MCP_PORT=8090，已在 .env 中固定）
bash scripts/start.sh
```

以上 `start_recall_api.sh` 自动寻找可用端口，启动后需修改 `.env` 对应字段：

- `EDA_MCP_PORT` 固定为 8090（保持一致）

```bash
# RAG 知识库查询服务配置
# =======================================================
# RAG API 召回服务的完整 URL 地址
# 本地 chroma_db_v3_full 服务（8984 条 = 8463 主源 + 521 补丁，name:description 嵌入，
# 描述源自主源 API_INFO_MERGED_V3.json + api_patch.json，含 OOP 方法）
# 重建: cd kb && python build_v3_full_with_oop.py [--dry-run]
# 启动: ./scripts/start_recall_api.sh  停止: ./scripts/stop_recall_api.sh
RAG_RECALL_URL=http://localhost:9002/recall

# 远程召回服务（备用，需上游 ChromaDB 重建后可切回）
# RAG_RECALL_URL=http://10.252.32.15:9001/recall

# 本机通用向量检索服务（Memory Bank / query_memory_bank 用）
MEMORY_VECTOR_URL=http://localhost:9004
RAG_RECALL_URL_LOCAL=http://localhost:9004/recall
```

### 2.2 使用老版 MCP 服务

若使用老版 mcp 服务，直接设置好 `/home/app.e0031982/.cline/data/settings/cline_mcp_settings.json` 即可使用并发评测。

### 2.3 终止服务

```bash
bash scripts/stop.sh              # 停止 mcp 服务
bash scripts/stop_recall_api.sh   # 停止 search api 服务
```

### 2.4 消融时切换 MCP 工具开关（重启两个服务）

MCP 工具开关在 `eda_fastmcp/main.py` 的 `_TOOL_DEFAULTS` 字典 + `.env` 的
`EDA_MCP_TOOLS_ENABLED` 变量里控制，`main.py` 启动时读取。改完任一配置后
**必须重启两个服务**才会生效：

1. **召回服务**（`search_apis` 的 RAG 后端，跑在 `kb/` 的 chroma_db）
2. **主 MCP 服务**（`main.py`，承载全部工具）

> 关闭 `cimi_search` / `cimi_fetch` / `vqa` 三个 Web/图像扩展工具后，分数更高更稳
> （见 `experiments/09_15_mcp_ablation_benchmark.md`）。

```bash
cd /nasdata/app.e0031982/code/eda_fastmcp
source venv/bin/activate          # 务必先激活 venv（脚本内部也依赖 venv/bin/python）

# ① 重启召回服务（start_recall_api.sh 自动找空闲端口，端口每次可能变！）
bash scripts/stop_recall_api.sh
bash scripts/start_recall_api.sh
#   ↑ 脚本末尾打印 "更新 .env: RAG_RECALL_URL=http://localhost:<PORT>/recall"
#   → 必须照抄同步到 .env，否则 search_apis 会连错端口（当前实例跑在 9006，而 .env 还写 9002）

# ② 重启主 MCP 服务（读 .env 的 EDA_MCP_PORT=8090）
bash scripts/stop.sh
bash scripts/start.sh
```

**工具开关两种改法（改完按上面重启生效）：**

- 改 `main.py` 里 `_TOOL_DEFAULTS` 三个值（写死）：
  ```python
  "cimi_search": False,   # Web 搜索
  "cimi_fetch":  False,   # Web 页面抓取
  "vqa":         False,   # 图像问答
  ```
- 改 `.env` 的 `EDA_MCP_TOOLS_ENABLED`（不动代码，消融更推荐）：
  - `EDA_MCP_TOOLS_ENABLED=all` → 全开（含三个扩展工具）
  - `EDA_MCP_TOOLS_ENABLED=cimi_search,cimi_fetch,vqa` → 显式开这几个
  - 留空 → 按 `_TOOL_DEFAULTS` 默认（当前默认全关）
  - 核心 4 个 `get_api_details / search_apis / search_apis_by_keyword / run_code` 恒开，不受影响

> 当前 `main.py` 里这三个工具已是 `False`（关闭态）。所以「关闭 MCP」消融
> 直接跑即可；「开启 MCP」消融才需要上面任一种改法。

### 2.5 切换评测模型（cline auth）

`run_cli.sh` 每个 worker 都会从 `~/.cline/data/settings/` 拷贝 `models.json` +
`providers.json`，所以**切基座 = 跑对应那条 `cline auth`**（不是改 `.env` 的
`*_MODEL`）。5 个基座的切换命令：

```bash
# glm-5.2
cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23 -b http://agi-gateway.cxmt.com/cloud/v1 -m glm-5.2

# deepseek-v4-flash
cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_c43c1f4a-03c6-4148-b722-f4c8604c78d3 -b http://agi-gateway.cxmt.com/v1 -m deepseek-v4-flash

# kimi-k2.6-cloud
cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_80a707b0-4402-4c19-88d1-a3d4ebbf9a9f -b http://agi-gateway.cxmt.com/cloud/v1 -m kimi-k2.6-cloud

# deepseek-v4-pro-fp4（主基座）
cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_9eed3da1-b039-4d96-a18a-d0769b01baae -b http://agi-gateway.cxmt.com/v1 -m deepseek-v4-pro-fp4

# doubao-seed-2.0-pro-cloud
cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_3dd97aea-258e-4a53-a290-4f1425cdc15f -b http://agi-gateway.cxmt.com/cloud/v1 -m doubao-seed-2.0-pro-cloud
```

> 跑哪个基座，就切到对应那条 `cline auth` 再跑 `run_cline_script.sh`。
> 切换后无需重启 MCP 服务（`cline auth` 直接写 settings，`run_cli.sh` 每次跑会重新拷贝）。
> 当前 `models.json` 里只挂了单一 `openai-compatible` provider（`defaultModelId=deepseek-v4-flash`）。

## 3. 修改 `/nasdata/app.e0031982/eda_fastmcp/.env`

### 必须修改项

- 首先保证当前目录下存在 `EDA-Eval-Framework` 项目代码

```bash
EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework
```

将该字段内容修改成自己项目 `EDA-Eval-Framework` 绝对路径。

> 说明：`.env` 中配置的沙盒现均可以使用，无需更改。

### 可选修改项

- `CLI_AGENT`：可以分别设置为 `cline` 或者 `zhulong`，以唤起需要的 agent，默认为 `cline`
- `EDA_MCP_PORT`：mcp 服务端口号，固定 **8090**（如需更改，同步修改 `.env` 和 `~/.cline/data/settings/cline_mcp_settings.json` 两处）
- `RAG_RECALL_URL=http://localhost:9033/recall`：search api 工具 rag 服务，目前为优化后的，可改为自己的

> **注意**：`/home/app.t0002147/eda_fastmcp/pyAether-eval/config.yaml` 用于选择使用 `/home/app.t0002147/eda_fastmcp/pyAether-eval/original_dataset` 目录下哪个评测集
> （`pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl` 为默认使用 158 case 评测集）

## 具体操作

### 仅评测 158 case

```bash
# -p 8 代表 8 并发跑任务，禁用 Memory Bank 注入
bash scripts/run_cline_script.sh -p 8 -n
```

代码生成 + 评测一键执行，代码生成文件会存在 `/home/app.e0031982/eda_code_eval`。

下面指令执行评测（给生成的代码打分）
```bash
python scripts/run_eval.py -g /home/app.e0031982/eda_code_eval/code_generation_2026_0914_152253.jsonl
```

评测结果在命令行输出，类似如下：
```bash
  ✅ 020828: 147/157 pass (93.6%) | generated: 157 ok, 0 fail, 0 exec_err