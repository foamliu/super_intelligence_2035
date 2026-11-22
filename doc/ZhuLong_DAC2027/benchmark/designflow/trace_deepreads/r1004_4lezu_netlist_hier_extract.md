# r1004 deepread — 4lezu · netlist hierarchy extraction

- **round**: r1004 (shard A, 1-case轮)
- **case_id**: EDA-Eval-DesignFlow-NetlistHierExtractProduce-001
- **domain**: digital (A-pure, verilog:518 dominant)
- **trace**: `1795164483425_4lezu.messages.json` (204KB / 47 msgs)
- **user**: wenfeiz @ hfeg0pkn004 (NEW — no prior ledgered case, no dedup concern)
- **mc**: 53
- **scan**: ssh_eda_search_20261122_172249 (复用 r1001-r1003 同一 .75 scan)

## 心跳三数
- mc≥5 pool: 817 dedup candidates (digA filter: verilog/rtl/synopsys/dc_shell/innovus 等, 排 netlist/drc/lvs)
- fresh-diff vs 4-shard ledger (4165 normalized sids): **82 fresh**
- 本轮 peek: 3 A-fresh + 0 跨域 (46vx0 / 4lezu / qs9e9)
- 产出: 1 case → A.jsonl 461 → 462
- auto_stop consecutive_zero_case_rounds: 0 (r1003 产1 → r1004 产1, 维持 0)
- stop-loss: 0/3 未触发

## 选料决策
3 fresh 候选 scp 深读:

| sid | user@host | mc | kw | verdict |
|---|---|---|---|---|
| 46vx0 | (mixed) | — | 跨域 mixed | REJECT — 非 A-pure |
| **4lezu** | wenfeiz@hfeg0pkn004 | 53 | verilog:518 | **SELECT** — cleanest A-pure produce-task, 用户原话逐字可reframe |
| qs9e9 | — | — | — | REJECT — analysis-Q&A 需多 fixture, 难 hidden-B 化 |

4lezu 选中理由: trace-faithful 度高 (gold 脚本 `analyse_muxsref.py` 在 editor tool_use msgs[22,28,36,42] 完整捕获), produce-task 形态清晰 (输入网表 + target → 结构化 JSON), 易泛化为通用脚本, 易构造 hidden-B (任何同构门级网表即可)。

## trace 主线
session 主线: LPDDR5 gate-level (post-PnR) 网表分析。多子任务:
- 波形查看
- 网表裁剪 (从 full netlist 切出 module ... endmodule 节)
- Verdi 信号追踪
- **模块层次提取** ← 本 case 取此子任务

用户原话 (逐字):

> MuxAdjSrefRate 这个module的层次结构

意图拆解:
1. 目标模块定义所在行范围 + 端口列表
2. 被谁例化 (父模块 / 实例名 / 行号)
3. 从顶层到目标的完整调用链 (parent chain)
4. 内部例化的子模块/标准单元 (child instances: celltype + instname + line)

## trace gold (agent 实际产出)
agent 写 `analyse_muxsref.py`:
- 正则切 `module <Name> ... endmodule` 块, 记每个模块定义起止行
- 解析模块体内例化行 `<CellType> <inst_name> (`, 跳过 module/endmodule/assign/wire/input/output/inout/parameter 等非例化行
- 反向查父模块链: 谁例化了当前模块 → 递归上溯直到无父 (防环)
- 对 `MuxAdjSrefRate` 输出:
  - parent_chain: `WOWTOP → LP5TOP → Channel → ChanEdgeL → MuxAdjSrefRate` (5 节点)
  - child_instances: 6 个 (INV×3 / BUF×2 / AOI21×1)
  - 叶子模块 (无子模块例化)

## 本 case 泛化
通用脚本 `extract_netlist_hierarchy.py <netlist_file> <target_module> <output_json>`:

行为:
1. 解析网表, 识别所有 `module <Name> ... endmodule` 块, 记定义起止行
2. 解析每个模块体内例化行 (跳过 module/endmodule/assign/wire/input/output/inout/parameter/specify/endspecify/initial/always), 记 celltype/instname/line
3. 从 input/output/inout 声明行提目标模块端口名
4. 对 target_module 给出:
   - `definition` = {start_line, end_line, port_list}
   - `child_instances` = 目标模块体内所有例化
   - `instantiations` = 网表中所有例化了 target 的位置 (parent_module/instance_name/line)
   - `parent_chain` = 从顶层根模块到 target 的完整调用链 (根在前, target 在尾, 防环)
5. 写 JSON `<output_json>` + stdout 简短汇总

仅依赖 Python 标准库 (re/sys/json/collections), 不得硬编码任何模块名/行号。

## fixture
### A (供 SUT 测试, 可见)
- `netlist_A.v`: LPDDR5 WOWTOP 网表裁剪 (保留 module ... endmodule 扁平门级结构 + 例化关系, 只裁 stdcell 内部连线体)
  - target = `MuxAdjSrefRate`
  - 顶层 = `WOWTOP`
  - parent_chain = `WOWTOP → LP5TOP → Channel → ChanEdgeL → MuxAdjSrefRate` (5 节点)
  - 叶子模块, child = INV×3 / BUF×2 / AOI21×1 (6 个)
- `task_brief.md`: 用户原话 + 交付要求 + A 网表元信息

### hidden B (判分器用, SUT 不可见)
- `netlist_B.v`: DDR controller CHIP_TOP 网表 (与 A 完全不同的设计/命名/结构)
  - target = `ZqCalMst`
  - 顶层 = `CHIP_TOP`
  - parent_chain = `CHIP_TOP → DDR_CTRL → CmdCtrl → ZqCalMst` (4 节点)
  - **非叶子**, child = ZqTrim + ZqRange (子模块) + INV + NAND2 + BUF (5 个)
  - 端口 = {ZqCalStart, zq_trim_code, ZqCalDone, zq_range_sel}
  - 父模块 = `CmdCtrl`

B 与 A 全 concrete 值异:
- 模块名: ZqCalMst vs MuxAdjSrefRate
- 顶层: CHIP_TOP vs WOWTOP
- chain 长度: 4 vs 5
- chain 节点: CHIP_TOP/DDR_CTRL/CmdCtrl vs WOWTOP/LP5TOP/Channel/ChanEdgeL
- target 是否叶子: 非叶子 (含子模块) vs 叶子
- 端口: 4 个全异 (ZqCalStart 等 vs CmMdAdjSrefLTRate/sel/SrefRateOut)
- child celltypes: {ZqTrim,ZqRange,INV,NAND2,BUF} vs {INV,BUF,AOI21}
- 父模块: CmdCtrl vs ChanEdgeL

## check.py (k=17 ≥ 8)
17 条独立断言:

| # | gate | anti-hardcode? |
|---|---|---|
| ① | submit.zip 含 extract*.py 脚本 | |
| ② | py_compile 编译通过 | |
| ③ | B 运行 exit0 + 非空可解析 JSON | |
| ④ | JSON 含 5 必需 key | |
| ⑤ | target_module == ZqCalMst | ✓ 反硬编码 A target (MuxAdjSrefRate) |
| ⑥ | definition.start_line/end_line 正整数, start<end | |
| ⑦ | port_list 含 B 4 端口 | ✓ 反硬编码 A 端口 |
| ⑧ | parent_chain 根 == CHIP_TOP | ✓ 反硬编码 A 顶层 (WOWTOP) |
| ⑨ | parent_chain 精确 [CHIP_TOP,DDR_CTRL,CmdCtrl,ZqCalMst] | ✓ |
| ⑩ | child celltypes == {ZqTrim,ZqRange,INV,NAND2,BUF} | ✓ 反硬编码 A 的 {INV,BUF,AOI21} |
| ⑪ | child 含 B 子模块 {ZqTrim,ZqRange} | ✓ 证明 B 非叶子 (A 是叶子) |
| ⑫ | instantiations parent_module 含 CmdCtrl | ✓ B 特有父模块 |
| ⑬ | A-only 名 [WOWTOP/LP5TOP/Channel/ChanEdgeL/ChanMid/MuxAdjSrefRate/SrefTempDecoder/ModeRegMrrDSF_New/ErrorCounter/MrrDecoder] 不泄漏进 B JSON 任意位置 | ✓ |
| ⑭ | 三次运行 md5 一致 (确定性) | |
| ⑮ | §4.9 空壳: 脚本 >200B + 含 def + import | |
| ⑯ | §4.9 print-only: JSON 文件被写入 + 含 parent_chain/child_instances 结构键 | |
| ⑰ | §4.9 core-deleted: parent_chain 长度 ≥3 且非 [target] 单元素 | |

## §4.9 三假 (negative_selftest 验证)
| neg | 行为 | FAIL at |
|---|---|---|
| neg_empty | 空壳 stub (无 def/import/无 JSON 产出) | ③ (无 JSON 文件) |
| neg_print_only | 只 stdout 打印 B 摘要不写 JSON 文件 | ③ (无 JSON 文件) |
| neg_core_deleted | 解析逻辑删除 + 硬编码 A MuxAdjSrefRate/WOWTOP 链 | ⑤ (target_module=MuxAdjSrefRate ≠ ZqCalMst) |

三假全 FAIL ✓

## E2E 验证
1. 从 jsonl entry 的 `test` 字段提取 check.py 源码 → 写入 temp check.py
2. 模拟 harness: temp workdir + `hidden/` 拷贝 B fixture (netlist_B.v + hidden_manifest.json)
3. ref solution (`extract_netlist_hierarchy.py`) zip 为 submit.zip → run check() → **PASS** ✓
4. 3 negs 各自 zip 为 submit.zip → run check() → 全 **FAIL** ✓

ref solution 实测:
- A: chain 5 节点 / 6 child / 1 inst
- B: chain 4 节点 / 5 child (含 2 子模块 ZqTrim/ZqRange) / 1 inst

## bookkeeping
- ledger: `4lezu` claimed → case (EDA-Eval-DesignFlow-NetlistHierExtractProduce-001)
- A.jsonl: 461 → 462
- eda_flow session: r1004 declare_done + close
- 📊 462/9542 ≈ 4.8% (+1, digital +1)
- 🎯 观察值 (1 新 case 未跑 pi)

## 选料注
- r1003 后 fresh pool 仍有 41 余量, r1004 选 4lezu (wenfeiz NEW 用户, mc53 verilog:518 A-pure digital) 打破 dedup 顾虑
- 与 r1003 PtCellExtractProduce (同 digital 域) 无 intent-dup (不同子任务: gate-level 网表模块层次提取 vs PrimeTime timing 报告 cell 提取)
- 4lezu 是 r1004 选料前 82 fresh 中 top-2 候选, trace-faithful 度高 (gold 脚本 analyse_muxsref.py 在 editor tool_use msgs[22,28,36,42] 完整捕获)
- flat-file A 附件约束 (r1001 发现的 harness 限制) 本轮遵守: A fixture 全扁平文件 (netlist_A.v + task_brief.md), hidden B 同样扁平 (netlist_B.v + hidden_manifest.json)
