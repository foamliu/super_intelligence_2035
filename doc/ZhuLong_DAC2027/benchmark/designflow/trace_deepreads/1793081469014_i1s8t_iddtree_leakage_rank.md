# trace_deepread: 1793081469014_i1s8t

- **slug**: `1793081469014_i1s8t`
- **user**: chengk (in-ledger user via other session; this session is fresh-sid, not in any of A/B/C/D ledgers)
- **host**: hfeg0plg74
- **match_count**: 22 (netlist:134, hspice:58, waveview:8 — D-domain-dominant, analog_context)
- **claim**: shard D, round #533, topic iddtree_leakage_rank
- **source path (.75)**: `/home/chengk/.cline/data/sessions/1793081469014_i1s8t/1793081469014_i1s8t.messages.json`
- **NMSGS**: 20

## Original user goal (verbatim, USER[0])
```
从iddtree 导出表格，按照vdd2h电流排序，选出较大的instancs path，测量vcc和vss在时钟边沿的漏电流平均值，计算出占比，过滤掉异常值
生成流程图
```

## Domain / tooling context (from assistant tool calls)
- 工作区 root: `/home/chengk/work/code/wv_trig/port_catch/data_test1`
- 可见文件: `bufGFx1.netlist`, `cck_out`, `CktCheck.log`, `insi.list`, `netlistHeader`, `netlistFooter`
- 工具链: Tcl IDD 探针包 `cck_tcl_packages/iddprobe_port`, `cck_tcl_packages/idd/IddProbe_v2p2.tcl`, `task3_src/deck_v3p0.tcl`, `task3_src/PortCatchTest.tcl`
- policy engine `agent-policy-engine` enforcing → `run_commands` 被禁用（"Raw shell tool run_commands is disabled; use run_approved_command"），agent 转而用 `list_allowed_files` / `read_files` / `search_codebase` 反复探索，session 卡在探索阶段未产出最终脚本/表格。
- 关键词命中: iddtree / vdd2h / 漏电流 / 时钟边沿 / 占比 / 异常值过滤 / 流程图

## 实质工作意图（produce-task 抽取）
原始请求是一个**数据后处理流水线** produce-task（"生成流程图"为次要交付）：
1. 从 iddtree（IDD 漏电探针树）导出 per-instance 表格
2. 按 vdd2h 聚合电流排序，选出较大电流的 instance path
3. 对 vcc / vss 两条 rail 在各时钟边沿的漏电采样求均值
4. 计算 vcc_avg / vss_avg 占比
5. 过滤异常值（占比越界 / 除零 / 非有限）
6. 输出排名结果

session 因 policy engine 锁死 shell 未产出可运行脚本，但**领域语义、数据形态、计算口径**清晰可综合。

## B-grade 综合决策
- **case id**: `EDA-Eval-DesignFlow-IddLeakRank-001`
- **domain**: analog_context（D shard）
- **轨道**: B（自包含，无 EDA license / 二进制依赖）
- **数据形态综合**: 三 TSV — `vdd2h.idd.tsv`(per-instance 聚合电流) + `va.idd.tsv` / `vb.idd.tsv`(per-instance × per-clock-edge 采样)，纯文本 stdlib 可解析。va/vb 泛化原 vcc/vss 两条测量 rail。
- **A/B/C 参数 disjoint**:
  | variant | sort key | band [lo,hi] | corner | seed | 位置 |
  |---|---|---|---|---|---|
  | A (SUT 可见) | vdd2h_ua | [0.5, 2.0] | typ_0p9V_25C | 101 | assets/iddtree + example_report_A.json |
  | B (隐藏) | va_avg | [0.3, 3.0] | worst_0p72V_125C | 202 | assets/hidden/iddtree |
  | C (嵌入 check.py 反硬编码) | ratio | [0.4, 2.5] | best_0p95V_m40C | 303 | check.py C_FILES |
  - sort(mode) / band / corner / seed 四维全部 disjoint；sig = va/vb 共享（同 SetupHold 的 setup/hold 共享）。
- **outlier 构造**: i_mux/x1 → vb_avg==0（除零守卫）；i_buf/x1 → 高 ratio（越 tight band 上界）；i_inv/x2 → 低 ratio（越下界）。保证 n_filtered≥1 且 vb_avg==0 case 被过滤。
- **SUT**: 纯 stdlib（argparse/csv→改手写 TSV/json/math/os），无 subprocess/socket/eval/numpy。
- **check.py**: 独立 oracle 重算 va_avg/vb_avg/ratio/filter/rank，14 条独立断言（a-n），≥8 硬门槛满足。反硬编码 C 嵌入 + 3-seed sha256 确定性。
- **negatives**: empty / print_only / hardcode_a / core_deleted 四个全部 FAIL。

## 自验结果
- REF on A/B/C: **14/14 PASS**
- 4 negatives: **ALL FAIL**（empty 7/14, print_only 7/14, hardcode_a 11/14, core_deleted 7/14）
- example_report_A.json: 与 ref 输出**逐字节一致**
- 3-seed sha256: **set size 1**（确定性）
- negative_selftest.py: **ALL_NEG_FAIL: True**

## 备注
- chengk 作为 user 已在 D.jsonl 出现（经其他 session），本 session 为 fresh-sid（不在 4 shard ledger），符合 #532 同款 pivot 策略。
- 原始 session 的 policy-engine 锁死现象本身是真实 EDA 工程师日常痛点的折射（agent 在受限策略下难以完成 shell 任务），但本 case 不复现该限制（SUT 沙箱为纯 stdlib 脚本任务）。
