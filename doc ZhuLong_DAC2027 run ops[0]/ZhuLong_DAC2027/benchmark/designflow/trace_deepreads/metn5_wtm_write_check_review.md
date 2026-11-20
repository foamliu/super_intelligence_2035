# deepread: metn5 — WTM006_write_check.v 新增基本读写块 code-review

- session: `1794365610027_metn5`
- user/host: tongfanl @ hfeg0plg98 (10.129.8.230)
- mc: 22, domain: waveform (shard D)
- 旧判定: weak/Q&A code-review（2026-11-14 因旧 "not produce" 规则 parked）
- 11-15 revival mandate: 重新激活为合法 code-review Q&A 用例
- 交付 case: `EDA-Eval-DesignFlow-WtmWriteCheckReviewQA-001` (r786)

## trace 逐字（U#0 + U#13）

> `/home/tongfanl/DDR6/DSCQA/analogsim/WTM 帮我看下WTM006_write_check.v写的有没有问题`
> `检查下我新增的基本读写有没有问题？`

## 素材可达性

- ssh 10.129.8.230 免密 ✓
- `WTM006_write_check.v` 787 行 / 49746 bytes，scp 到 .75 workdir
- 全附件内联在 session msg（立即可取，不需 /rundata）

## 文件结构 gold

- 顶层 task `WTM006_write_check`（begin label 与 task 同名，无 typo）
  - 参数: bg0/bk0/bg1/bk1/rowa/rowf/cola/colf
- 嵌套子任务 `gen_wtm_write_data_006`（生成 WTM 写数据 + 期望寄存器，~400 行 SV 语法）
- 末尾新增基本读写块，`//1)BGDATA` 起到 `endtask`：
  - BGDATA 段：4 Write (DATA_JF→colf, DATA_J→cola, DATA_H→cola, DATA_HF→colf) + 2 Read (cola, colf)
  - PW+AP 段：2 Active + Write DATA_A→cola(pw=1) + Read colf + Write DATA_DF→cola(pw=1,ap=1) + Write DATA_D→colf(pw=1) + Read colf

## 金标准（agent msg#12 + msg#14 focus on new block）

新增块 4 类问题：

1. **write/read column mismatch**（最关键）
   - `Write(.bg(bg0[0+:BG_BITS]), .ba(bk0), .col(cola), .dq(DATA_A), .pw(1))` (line 151)
   - `Read(.bg(bg0[0+:BG_BITS]), .ba(bk0), .col(colf), .ap(0))` (line 152)
   - 同 bg0/bk0，Write 到 cola，紧接 Read 从 colf → 读到旧数据而非刚写入的 DATA_A
2. **uncovered writes**（Write 后无同 (bg,ba,col) 的 Read 覆盖）
   - DATA_JF (colf, bg0/bk0) — 后续 Read bg0/bk0 读的是 cola 不是 colf
   - DATA_J (cola, bg1/bk1) — 后续 Read bg1/bk1 读的是 colf 不是 cola
   - DATA_A (cola, bg0/bk0) — 后续 Read bg0/bk0 读的是 colf 不是 cola
   - DATA_DF (cola, bg1/bk1) — 后续无 Read bg1/bk1 cola
   - DATA_D (colf, bg0/bk0) — 后续 Read bg0/bk0 colf 覆盖（唯一 covered）
   - gold 重点：DATA_J / DATA_A / DATA_DF 三条
3. **timing hazard**（同 bank Read→Write 之间夹不同 bank Write）
   - Read bg0/bk0 colf (line 152) → Write bg1/bk1 cola DATA_DF (line 153) → Write bg0/bk0 colf DATA_D (line 154)
   - 同 bg0/bk0 的 Read@152 与 Write@154 之间夹了 bg1/bk1 的 Write@153 → tWTR/tCCD 转身隐患
4. **SV-in-.v 语法**（整文件）
   - `bit [7:0]`、`int tmrr_wtm`、`foreach`、`wtm_wr_data[]` dynamic array、`.size()` → .v 后缀但纯 Verilog 编译会失败

## design_flow reframe

pattern #254 v2 code-grounded review（proven by 86g62 ScriptCompareMergeReviewQA-001 同族）：
- 候选工具 `wtm_write_check_review.py` 读 .v + question → 结构化 JSON
- 输出键: question / file_summary / bug_findings / uncovered_writes / timing_hazards / overall_assessment / cited_identifiers
- bug_findings type: write_read_col_mismatch / begin_label_typo / sv_syntax_in_v_file
- 候选在隐藏 B 上独立运行与 oracle 对账

## hidden B（同结构、不同标识符）

- task `WTM_B_write_check`，参数 bgp/bkq/bgq/bkr/rowp/rowq/colx/coly/colz
- 子任务 `gen_wtm_write_data_B`
- 同 bug 模式但标识符不同：
  - write_read_col_mismatch: Write DATA_T→colx (line 85) → Read colz (line 86) 同 bgp/bkq
  - uncovered writes: DATA_Q (colx, bgq/bkr) / DATA_T (colx, bgp/bkq) / DATA_U (colx, bgq/bkr)
  - timing hazard: Read bgp/bkq colz (86) → Write bgq/bkr colx DATA_U (87) → Write bgp/bkq colz DATA_V (88)
  - DATA_P/DATA_R/DATA_S/DATA_V 等
- B 内联在 check.py (B_V_FILE)，不进 SUT sandbox

## check.py 12 条件 a-l

a=zip含candidate / b=py_compile / c=7必需键 / d=bug_findings非空 / e=write_read_col_mismatch类型 / f=引B专属colx/colz/DATA_T / g=uncovered DATA_Q/DATA_T/DATA_U / h=timing_hazards非空 / i=anti-hardcode不泄A标识符 / j=anti-hardcode引B标识符 / k=cited grounded于B源码 / l=3-run确定性

## 自验

- REF 12/12 PASS
- 5 negatives FAIL distinct labels: fake_empty→[c], fake_print_only→[c], fake_print_expected→[f,g,i,j,k], fake_core_deleted→[d,e,f,g,h,j], naive_only_mismatch→[g,h,j]
- NEG_RC=0
- §4.9 三退化 (fake_empty/fake_print_only/fake_core_deleted) 全 FAIL ✓
- candidate on A: 2 bug_findings (write_read_col_mismatch + sv_syntax_in_v_file), uncovered_writes [DATA_J,DATA_A,DATA_DF], timing_hazards 1 — 匹配 gold
- embedded test == disk byte-sync ✓
- k_rationale == k_check == 12 ≥ 8 GATE PASS ✓
- D.jsonl 447→448

## ledger

- `trace_ledger.py --shard D mark --session 1794365610027_metn5 --status case --case-id EDA-Eval-DesignFlow-WtmWriteCheckReviewQA-001` → marked
