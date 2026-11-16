# trace_deepreads/1792649502711_qrr6j_idd_stim_howto.md

**Session**: 1792649502711_qrr6j (subdir-style trace file)
**User**: thqu @ hfeahpc501
**mc**: 14 (spice_sim domain)
**Trace source**: `.75:/home/thqu/.cline/data/sessions/1792649502711_qrr6j/1792649502711_qrr6j.messages.json`
**Real task summary**: 用户问「IDD仿真的激励要怎么写啊」，agent 探索 LPDDR5 R_NegVssIdd_opt_qyh 工作区后产出综合 how-to 指南。

## 用户原话（msg[0]）
- 「IDD仿真的激励要怎么写啊」

## Agent 探索路径
1. `list_allowed_files /home/thqu` — 列工作区文件
2. `skills cimi-kb-search "IDD仿真激励怎么写"` — 调 KB
3. `RAG_MCP_Server__search_apis` (skill + pyAether 双语) — 检索 API
4. `run_approved_command kb-search-cli.py retrieve "IDD仿真 激励 电源电流 测试方法"` — KB 检索
5. `read_files`:
   - `/home/thqu/stimulus_project/output/stimulus.sp` (compact-PWL: SanEn2G/SapEn2GP/PwrOnLsVwlp/GrEn/Ra16L<>/Ra16H<>)
   - `/home/thqu/stimulus_project/scripts/gen_stimulus_v2.py` (extract_pwl_data→simplify_pwl→format_compact_pwl 工作流)
   - `/home/thqu/stimulus_project/scripts/analyze_pwl.py`, `org_files.py`
   - `/home/thqu/analyze_power.py` (电源域枚举: vcc!/vss!/vdleq!/vwlp!/vssz_vic)
6. `search_codebase` 多次 (IDD/idd/`.meas.*i(vdd`/`pwl.*pvcc`) — 项目内代码检索
7. `read_files /home/thqu/TECHLIB_ALL_power_voltage_table.md` — 30 行电压表
8. `run_approved_command kb-search-cli.py retrieve "LPDDR DDR IDD 测试项 IDD2N IDD3N IDD4R IDD4W IDD5 IDD6 IDD7 条件"` — JEDEC 标准

## Agent 最终产出 (msg[33])
结构化 how-to 指南，覆盖 9 个章节：
1. IDD 定义 (DRAM 工作态电源电流, mA 级, 直流测试项)
2. 激励三要素 (电源 / 控制信号 / 测量语句)
3. PWL 两种写法 (紧凑式 + 多行式 + DC+.tran)
4. 项目信号含义 (SanEn2G→IDD2N, SapEn2GP→IDD3N, PwrOnLsVwlp=2.71V, GrEn→IDD4R/4W, Ra16L<>/Ra16H<>→行选)
5. JEDEC 标准 IDD 测试项 (IDD2N/3N/4R/4W/5/6/7 + 激励条件)
6. 完整 testbench 模板 (.param + 电源 + 控制信号 + .tran + .meas AVG/MAX/FIND + .option + .end)
7. WaveView→PWL 工作流 (gen_stimulus_v2.py: extract→simplify→format→write)
8. 关键技巧 (simplify_pwl min_change_pct=3.0 / 多电源域分别测 / 初始状态稳定 30ns)
9. 项目改进建议 (缺 .meas / .option / 部分电源定义)

## 案例合成（A 档 trace-faithful + 产出生成式 how-to 指南）
- **case_id**: `EDA-Eval-DesignFlow-IddStimHowtoGuide-001`
- **domain**: spice_sim
- **archetype**: howto-guide-produce (revival #66 from pool_reaudit_B)
- **A 输入** (SUT 可见): 4 个真实项目文件 (stimulus.sp / gen_stimulus_v2.py / analyze_power.py / TECHLIB_ALL_power_voltage_table.md) + requirements.json + scenario.txt + hidden_manifest.json
- **B 输入** (hidden cross-input guard): DDR4 项目 (DDR4_BankActive_Idd_opt) — 不同 DRAM family / 不同信号名 (CKE/CS_n/RAS_n/CAS_n/WE_n/DQ<>/DQS_p/DQS_n) / 不同 helper (gen_dc_source/gen_pwl_step/gen_command_pulse/gen_idd_test_pattern) / 不同电压表 (VDD 1.2V/VPP 2.5V/VTT 0.6V) / 不同 JEDEC 项集 (11 项含 IDD0/1/2P/3P/7)
- **任务**: 写 `idd_stim_guide.py(workdir, out_dir)` 读 `doc/` 下输入产出 `idd_stim_guide_report.json` 结构化指南
- **check.py**: 55 条独立断言 (k_check==k_rationale==55, ≥8 硬闸门)
  - a0-a4c (7 条): 交付件存在 / zip 含脚本 / 可解 / py_compile / B 输入齐全 / B family=DDR4 / B project=DDR4_BankActive_Idd_opt
  - a5_run1-3 + a5_file1-3 + a5_det (7 条): 3 次重跑 exit 0 + 产报告 + sha256 一致 (确定性)
  - a6-a7 (2 条): JSON dict / 14 顶层键齐全
  - a8_idd/current/ma/dram (4 条): idd_definition 关键词覆盖
  - a9_voltage_sources/control_signals/measurement_statements (3 条): stimulus_components 三子键
  - a10_list/pwl/dc (3 条): pwl_writing_styles ≥2 项且含 pwl/dc
  - a11_list/b_items (2 条): jedec_idd_items ≥7 且覆盖 B 要求的 11 项
  - a12_tran/meas/vsrc (3 条): testbench_template 含 .tran/.meas/Vxxx...dc
  - a13_gen_dc_source/gen_pwl_step/gen_command_pulse/gen_idd_test_pattern (4 条): waveview_workflow 含 B 全部 4 个 helper
  - a14_thresh (1 条): pwl_simplification 阈值 ≥ B 最小 1.0%
  - a15_list/AVG/MAX/FIND/RMS/meas_syntax (6 条): measurement_methods 含 4 方法 + .meas 语法
  - a16_list/nets (2 条): project_power_domains ≥3 项且引用 ≥3 个 B 电源网络
  - a17_list/rows (2 条): voltage_table_ref ≥5 行且非空 net+voltage
  - a18_no_a_leak (1 条): 报告不含 A 专属 token (R_NegVssIdd_opt_qyh/SanEn2G/.../LPDDR5/extract_pwl_data/simplify_pwl/format_compact_pwl)
  - a19_b_grounded (1 条): 报告提及全部 B 专属 token (DDR4/CKE/CS_n/RAS_n/.../gen_dc_source/...)
  - a20_list (1 条): caveats ≥2 项
  - a21_nonempty/idd (2 条): conclusion 长度 >30 且提 idd
  - a22_proj/family (2 条): report_overview 提到 B project / family
  - a23_sources (1 条): methodology 引用 stimulus.sp + gen_stimulus_v2.py
- **negative samples**: 4 个 (stub_empty / stub_print_a_constants [A-leak + non-determinism] / stub_delete_core_logic [空 JEDEC/methods/helpers] / stub_minimal_b_print [最小 B 但缺项])
- **自验**: ref 55/55 PASS + 4 negatives 全 FAIL ✓
- **cross-input guard**: A=LPDDR5+WaveView-PWL, B=DDR4+JEDEC-timing-driven；A-leak 16 token / B-grounding 16 token，互斥

## 关键 quirk / 注意事项
- trace 文件在子目录 `1792649502711_qrr6j/` 下（非根 .messages.json），scp 直路径会失败，需 `find` 子目录
- B 输入故意选了 DDR4 而非 LPDDR5 — JEDEC 项集合不同 (B 有 11 项含 IDD0/1/2P/3P/7，A 有 7 项) — 测试 SUT 是否真的从 requirements.json 读 JEDEC 列表而非硬编码
- B 的 helper 是 JEDEC-timing-driven (gen_dc_source/gen_pwl_step/...) 而非 A 的 WaveView-PWL converter (extract_pwl_data/simplify_pwl/format_compact_pwl) — 测试 SUT 是否真的从 gen_stimulus_v2.py 读 helper 名而非硬编码
- B 的电压表 12 行 (VDD/VDDQ/VSS/VSSQ/VPP/VTT/VREF_CA/VREF_DQ/ZQ/VDDSPD/VPP_DLS/VSS_DLS) 而非 A 的 30 行 — 测试 SUT 是否真的从 TECHLIB md 解析而非硬编码
- pwl_simplification section 在 B 输入下不能 mention `simplify_pwl` (A-leak)，ref solution 用 `drop_minor_transitions` 替代名
