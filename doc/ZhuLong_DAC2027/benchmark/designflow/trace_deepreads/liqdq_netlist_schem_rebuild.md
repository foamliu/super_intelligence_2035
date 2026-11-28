# liqdq — ALPS/HSPICE netlist → schematic rebuild plan (xdwang@hfeg0pkn005, mc=1349, schematic_netlist)

## trace
- session 1794400108861_liqdq.messages.json, 152 msgs (4 子任务), agent=Aether schematic 流
- r587 曾 parked 标 "dup of eo84n"；本轮 revival-from-parked，deepread 确认 U#3 与 eo84n cases 三轴全不同。

### 子任务概览
- U#0 (idx 早期) — 数反相器（inverter count QA）→ eo84n SchInvCountQA 同源，不取
- U#1 — 加反相器 → 编辑操作，不取
- U#2 — 建 INV cell → 单元库 build，不取
- **U#3 (msgs 125-147) — 解析 ALPS/HSPICE 子电路网表 → 重建顶层原理图 build plan** ← 本轮取此

### U#3（可合成核心）
用户: 提供 `00_DSCQA_Array_xdw.sp`（ALPS/HSPICE 子电路网表），要求「从网表重建顶层原理图 / 给出 rebuild plan」。
助手: 读 `.sp` 网表，解析 `X..` subckt instance 行：
- 每行 `X<inst> <pin...> <master>` 形式
- 提取 master 名（剥 `X` 前缀的最后一个 token）
- 按 master 聚合实例列表
- 统计每 master 的 pincount（实例端口数）
- 规划 build plan：master first-seen 顺序，按依赖铺开
- 区分 globals / nets / inout

### 与 eo84n cases 的差异（去 dup 复核）
- eo84n **SchInvCountQA U#0**：只数反相器数量（计数 QA），GOLD=整数。本 U#3 GOLD=结构化 plan.json（master 聚合 + 顺序 + pincount）。
- eo84n **NetlistSchBuilder U#4-6**：网表→原理图全量 builder（输出完整 schematic 描述）。本 U#3 聚焦 **中间 build plan 规划层**（顺序 + 聚合 + 分类），非全量输出。
- intent / GOLD / check 三轴全不同 → revival 合理。

## case 合成 plan
- task_id = EDA-Eval-DesignFlow-NetlistSchemRebuildProduce-001
- reframe: spec-JSON 驱动纯 Python `netlist_schem_rebuild.py(spec) -> {plan.json, report.json}` netlist→schematic top rebuild planner
- LIVE-NA judge[L0,L1]（纯 SPICE 文本/网表解析，Aether/Virtuoso 不在 eval 沙盒）
- 16 conds a-p，独立 gold 复算 4 条不同代码路径：
  1. 正则提取 `X..` instance（vs reference line-tokenization）
  2. `_gold_master_pincount` Counter（vs reference dict.setdefault 循环）
  3. `_gold_master_insts` defaultdict(list)（vs reference append-loop）
  4. `_gold_plan_ordered` sorted by first-seen（vs reference OrderedDict 跟踪）
- A visible spec_A.json：TimingCtrl netlist，15 inst，6 masters，混合 pincount 2/6/7/8
- hidden spec_B.json：ClkGate netlist，12 inst，token-structurally 不相交
- 7 neg 全 FAIL 7-distinct {c,f,g,n,j,i,l}，§4.9 trio {c,f,g} 3-distinct
- REF PASS 16/16，sha b63c9c33 3-way sync，SKIP_RUN 框架接受

## 落库结论
ledger liqdq → case（covered 686→687），D jsonl 632→633，nonlite_D.tsv LIVE-NA 行（507→508, NA 501→502）。
