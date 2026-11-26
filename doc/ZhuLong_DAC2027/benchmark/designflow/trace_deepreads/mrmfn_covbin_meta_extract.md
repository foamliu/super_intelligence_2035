# 深读 · mrmfn · ericw@hfhds201 · characterization · 2026-11-07 23:4x

## trace 源
- session: `1790042178493_mrmfn.messages.json`（dir-based: `/home/ericw/.cline/data/sessions/1790042178493_mrmfn/`）
- user: ericw · host: hfhds201 · mc=30 · size=1458317 · msgs=78
- 定位: spice-dominant local 池 unscouted（11-05 重扫令持续履行，hfhds201 fresh 0 + SSH 远程主机周六晚间 host-key/no-route → 复用 local unscouted）

## 选轮（A-档）
- **U#0（任务说明轮，逐字作 prompt）**:
  `/rundata/drcpa_sim/V0/simdir/finesim/workdir/ericw/verilog.ddr5.drcpa.aicov/coverage/DDR5_2026-09-11\n路径下有constraint_timing_coverage.sv 分析cg_t_PREsb_TO_MPC_ZQCal_Start_1nCK_Table_85这个bin`
  → 提出需求（"分析这个 bin"），无根因、无修复方向 → 符合 A-档选轮。
- U#32「哪里提到了start_cmd end_cmd，约束值=1个时钟周期这个在哪写了」/ U#34「帮我查找这个value是在哪里定义的」/ U#64「push_back(1 * tCK)这个就是对constraint_min的定义赋值是吗」→ 后续澄清/用户给猜测轮，**不入 prompt**。
- U#66/U#74「加载 skill / 如何启用」→ 跑题轮，不入 prompt。

## 金标准（assistant A#31，用户接受的分析）
assistant 用 search_codebase + run_commands(grep) + read_files 分段读取 `constraint_timing_coverage.sv`（约 22271 行），定位 `cg_t_PREsb_TO_MPC_ZQCal_Start_1nCK_Table_85` 在第 21635–21661 行，产出结构化分析：
1. **元数据注释头**（covergroup 上方的 `/*name:... event:{...} source:...*/` Python-dict 格式注释，21635–21639 行）:
   - name=`t_PREsb_TO_MPC_ZQCal_Start_1nCK_Table_85`
   - event={start_cmd:`PREsb`, end_cmd:`MPC_ZQCal_Start`, conditions:{}, value:`1 * tCK`, source:`Table_85`, consider_bank_situation:1, same_rank:1, same_ba:1}
   - source=`Table_85`
2. **采样事件**: `@(posedge vif.t_PREsb_TO_MPC_ZQCal_Start_1nCK_Table_85_sampled)`
3. **coverpoint**: `cp_delta_min_vs_constraint_min`（delta vs min 约束，nCK 单位，三元映射 + iff 约束≠0）
4. **bins**: `illegal`={[-100000000:-1]}, `meet_exactly`={0}, `safe_within_half`={1}, `safe_beyond_half`={2}
5. **兄弟 covergroup（诱饵）**: PREab(21577-21603, 无 bank 限制)/PREpb(21606-21632, same_bg=1,same_ba=1)/PREsb(21635-21661, same_rank=1,same_ba=1) —— 同 Table_85，按预充电类型区分。

## 可复用子流（通用化）
"在 constraint_timing_coverage.sv 中按名定位 covergroup，提取其上方 `/*name:... event:{...} source:...*/` 元数据注释头（Python-literal 解析 event dict）+ coverpoint 名 + bins 名 + 采样事件" → 通用化为 `extract_covergroup_meta.py <sv_file> <covergroup_name> -o out.json`，输出 {covergroup_name, metadata{name,event{...},source}, sampling_event, coverpoints[], bins[]}。

## 与既有 case 区分
- CgMeetExactlyMissWalk-001 (y91i6): **过滤+收集** —— 找所有 cg_t meet_exactly 未命中 covergroup → **list 输出**。
- CgtMeetExactlyFilter-001 (y91i6): 关键词过滤表。
- **本 case (mrmfn): 定位+抽取** —— 按名定位单个 covergroup，抽取其元数据注释头字段 → **单条结构化记录输出**。任务结构/输出形态不同。
- 多样性债务: ericw 已 3 case，本 case 为第 4（均 characterization coverage 主题）；下轮 SSH 主机恢复后优先选非-ericw。

## A / hidden B 设计
- A=constraint_timing_coverage_A.sv: 含目标 PREsb covergroup（真实元数据）+ 兄弟 PREab/PREpb 诱饵 + 2 个异构诱饵（无 event dict / max 约束）+ A_ONLY_MARKER 隐藏。
- hidden B=constraint_timing_coverage_B.sv: 目标 cg_t_ACT_TO_RD_tRL_Delay_Table_283（start_cmd=ACT,end_cmd=RD,conditions={same_rank:1},value=4*tCK,source=Table_283,consider_bank_situation=1,same_rank=1,same_ba=0）+ 2 coverpoints(min+max) + 不同诱饵 + 不同 bins。
