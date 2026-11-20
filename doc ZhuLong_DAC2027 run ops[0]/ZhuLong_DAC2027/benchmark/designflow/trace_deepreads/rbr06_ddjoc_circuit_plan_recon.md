# rbr06 — ddjoc 电路规划 reconnaissance (deepread)

**session**: `1794637486415_rbr06` · user `e0039516` @ `10.129.2.10` · mc=5 (floorplan:9/openroad:6/yosys:3/innovus:3/cadence:3/aether:3/virtuoso:2/synopsys:2 — eda_other 域)
**session json**: 61,629 B / 20 msgs · agent `lead` · model glm-5.3-flash / bobby · 2026-11-14 (status=completed)
**liveness**: r794 标 ALIVE (mc5-9 A-pure band) → r817 subdir-path 复测确认 ALIVE (subdir `/home/e0039516/.cline/data/sessions/1794637486415_rbr06/1794637486415_rbr06.messages.json` = 61,629 B, mtime Nov 14 14:34)。

## 真实用户意图（逐条原话）

- **U0** (ts 1794637486811): `你现在还是看不到我的ddjoc文件是吗`（先确认 agent 能否看到 ddjoc 工作区文件）
- **U9** (ts 1794637604402 估): `了解ddjoc这个项目吗？先为我介绍基本的电路规划` ← **核心任务：介绍 ddjoc 项目的电路规划**

## agent 工具链与产物

1. `list_allowed_files` `/home/e0039516/agentdir/ddjoc/V0` (depth 1) → 只看到 `diag_bridge.py` 一个文件
2. `get_agent_policy_status` → enforcing, 2 readable roots
3. `list_allowed_files` `/home/e0039516/agentdir/ddjoc` (depth 1) → 只含 `V0` 一个子目录
4. `read_files` `/home/e0039516/agentdir/ddjoc/V0/diag_bridge.py` (line 1-40) → 读到内容
5. `list_allowed_files` `/home/e0039516/agentdir/ddjoc/V0` (depth 3, includeHidden) → 深度递归确认仍只有 `diag_bridge.py`
6. `skills` `cimi-kb-search` + `run_approved_command` (python-runner, kb-search-cli.py retrieve "ddjoc 项目 电路规划") → **失败**：RAGFlow API Key 未配置
7. `skills` `ask-eda` + `run_approved_command` (python-runner, ask_eda.py ask --query "ddjoc 项目 电路规划") → **完成但无效**：`knowledge_base_used: false`，LLM 不认识 "ddjoc"
8. **最终汇报** (msg 19)：如实承认「不了解 ddjoc 项目，没找到相关资料」，列出 4 项检查表（工作区/cimi-kb-search/AskEDA），给出补充资料建议。

## ⚠️ agent 的关键误读（本 case 判分要纠正的点）

trace 中 agent 把 `diag_bridge.py` 描述为「**EDA Agent 菜单诊断脚本**，检查 `/apps/cad/bin/zl` 工具」——这是**错误**解读。实际 `diag_bridge.py` 是一个 **ddjoc 库单元 lineage（血缘反查）诊断脚本**：

```python
"""Find parents of nand2DQSQV4: grep OA files of DQS/WCK-related cells."""
LIBS = ["/proj/ddjoc/V0/libs/ddjoc_digital", "/proj/ddjoc/V0/libs/ddjoc_io"]
PAT = re.compile(r"dqs|wck|rdqs", re.I)
TARGET = b"nand2DQSQV4"
# 1) 遍历 LIBS，按 PAT 筛 cell，检查 schematic/sch.oa 是否存在 → candidates
# 2) 对每个 candidate 的 sch.oa 二进制读入，grep TARGET → 打印 HIT
```

用途 = 在 ddjoc 项目的 `ddjoc_digital` + `ddjoc_io` 两个 OA 库里，找出哪些 DQS/WCK 相关 cell 的 schematic 实例化了目标单元 `nand2DQSQV4`。跟"EDA Agent 菜单"/`/apps/cad/bin/zl` 毫无关系。本 case 的 check.py ⑦ 明确要求 SUT 把脚本描述为 parent/血缘/实例化反查 grep 诊断（而非菜单/license/工具检查），正是为了纠正这种误读。

## 关键产物字段（真实 diag_bridge.py，作为 input A，从 host 抓取）

- docstring: `Find parents of nand2DQSQV4: grep OA files of DQS/WCK-related cells.`
- LIBS: `/proj/ddjoc/V0/libs/ddjoc_digital`、`/proj/ddjoc/V0/libs/ddjoc_io`
- PAT: 正则 `dqs|wck|rdqs`（大小写不敏感）
- TARGET: 字节串 `b"nand2DQSQV4"`
- 操作文件: `schematic/sch.oa`（Cadence OA schematic 二进制）
- 两步流程: ① 筛 candidate cells (按 PAT + 检查 sch.oa 存在) → ② grep TARGET (二进制读 + 子串匹配 + 打印 HIT)
- 输出: `=== 1) DQS/WCK-related cell dirs ===` / `=== 2) grep for nand2DQSQV4 in their sch.oa ===` / `HIT: <lib>/<cell>` / `DONE`
- 46 行（含尾部空行），只读不改

## 合成决策

- **A 档 trace-faithful**：prompt 用 trace 原话（U0 + U9），资产 `diag_bridge.py` = 从 host 10.129.2.10 抓取的真实文件。无需 B 档。
- **判分范式** = S5 第二范式 analysis-Q&A + specificity oracle + refuse-to-hallucinate（沿用 PprRandomBankExplain-001 / VpsInterfaceSummaryQA-001，新增 refuse-to-hallucinate 维度，因为本 case 的核心诱惑是用户问"电路规划"而工作区只有一个不相关的诊断脚本 → agent 易编造）。
- **B (hidden)** = `diag_bridge_b.py`：同结构、不同域 specifics（ddjoc_analog + ddjoc_pll / `pll|vco|cp` / `pll_cp_unit_cell` / PLL-VCO-CP family），judge-only 防背题。
- **check.py 12 断言**：① 非空壳 ② markdown 结构 ③ 真实 TARGET `nand2DQSQV4` ④ 真实正则 tokens (dqs/wck/rdqs ≥2) ⑤ 两个真实库 ⑥ sch.oa ⑦ parent/血缘/grep 语义 (纠正误读) ⑧ refuse-to-hallucinate (承认无电路规划资料) ⑨ 不编造 (无 A 之外的 /proj/ddjoc/ 路径 + 无 ddjoc_X 纯编造 token + 无数值化指标) ⑩ B 独有签名不泄漏 ⑪ 两步流程 (candidate + grep/HIT) ⑫ 3-seed 随机化 (防硬编码)。

## 自验

- ref `ddjoc_circuit_plan_recon_ref.md` PASS 12/12
- 6 negatives 全 FAIL：neg_empty→①、neg_print_only→③、neg_core_deleted→①、neg_hallucinated→⑧(refuse-to-hallucinate)、neg_mischar→③(误读为菜单诊断)、neg_b_leak→⑩(B 独有签名泄漏)
- 命中 4 不同断言组（①③⑧⑩）证独立
- §4.9 (a)neg_empty (b)neg_print_only (c)neg_core_deleted 全 FAIL
- embedded test 字段独立运行 PASS
