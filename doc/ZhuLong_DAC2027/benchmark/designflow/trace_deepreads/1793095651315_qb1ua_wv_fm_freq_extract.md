# 深读笔记 — 1793095651315_qb1ua (WaveView ACE Tcl FM 瞬时频率提取)

- **session**: `1793095651315_qb1ua` · **user**: e0023936 · **host**: hfhds201（= .75 本机；session 文件本地存在 `/home/e0023936/.cline/data/sessions/1793095651315_qb1ua/`，summary 亦复制到 hfeg0plg52 等机）· **mc**: 103 · **n_msgs**: 123
- **tools hit**: `"lang": "tcl":49, schematic:6, virtuoso:4, netlist:4, cellview:4, hspice:3` —— 实际主体是 **WaveView ACE Tcl (SandBox_MCP_Server__run_code lang=tcl)**，schematic/virtuoso 仅 list_allowed_files 探查，hspice 偶发提及。
- **domain**: characterization（波形级信号表征——瞬时频率 vs 时间曲线提取）
- **shard**: B（spice_char）

## 真实对话流（逐轮）

| 轮 | 用户（逐字/近逐字） | agent 动作（真跑 / 仅读） |
|---|---|---|
| U0 | 「编写一个 Tcl ACE 脚本，计算一个 FM（调频）信号的瞬时频率随时间变化曲线，并在新的 WaveView 窗口中显示。要求：1.定义过程 f_vs_t(sig, v_thr) 2.创建新波形对象 "frequency" analog 3.对输入信号创建 RISE 扫描并设置电压阈值 4.遍历所有上升沿数据点，计算相邻两上升沿之间频率 f=1/(t2-t1) 5.将每个频率值及其对应时间 (t2,freq) 追加到新波形 6.主程序打开 ./wave.dat 获取信号 "wave" 调用 f_vs_t」 | RAG 检索 WaveView Tcl API（sx_create_signal/sx_create_scan/sx_set_threshold/sx_scan_first/next/sx_fetch_x/sx_append_data/sx_new_wv/sx_display_wave）→ **sandbox 真跑** 探查 `info commands sx_*` → 合成信号验证 RISE 遍历（上升沿 0.5/2.5/4.5 正确）→ editor 写 `fm_freq_vs_t.tcl` → 合成 FM 信号（VCO 方波 f=2+3t）端到端验证 f_vs_t → 调试 `sx_append_data` 回读伪影（DATA 扫描回读在 headless 下丢点，`sx_wave_to_list -out xy` 回读正确：freq={3.58166,4.34405} 匹配理论 3.58/4.34）→ 验证显示路径 sx_new_wv+sx_display_wave+sx_update_wv 全 OK |
| U55 | 「为什么这个打不开./wave.dat」 | 诊断：`./wave.dat` 不存在 + WaveView pwd=`/home/e0023936/devops`（非 `/home/e0031982`）→ 加 `open_wave_file` 健壮路径查找（$WV_WAVE_FILE / 多候选路径） |
| U69 | 重述 U0 + 新增第 7 点「把结果文件单独保存在一个顶层项目中」 | 用 `sx_write_open`+`sx_write_add_signal`+`sx_write_close` 写 `frequency_result.wdf`（437B）→ 重开 `sx_open_sim_file_read` 验证能定位 "frequency" 信号 ✓ → 加入脚本 |
| U83 | 「帮我执行 /home/e0031982/fm_freq_vs_t.tcl 代码查看结果」 | run_code 沙盒要求纯 ASCII（源文件中文注释被拒）+ 无 wave.dat → 用合成 FM 信号替代驱动完整流程 |
| U97 | 「唯一问题是当前环境没有 ./wave.dat 帮我找一个，copy过来」 | 搜全盘 .fsdb/.tr0/.dat/.wdf/.vcd 无可用 |
| U102 | 「你自己创建一个 ./wave.dat 波形文件」 | **sandbox 真跑** `sx_write_open` 生成真实 WDF `wave.dat`（FM 载波 2→5Hz，5001 点，58972B）→ `sx_open_sim_file_read` 验证能读信号 "wave"（analog，5001 点，x∈[0,1]）→ 用真 wave.dat 跑用户原版脚本：阈值 0.0V 恰压波形最低点（幅值 0~3V）→ 无上升沿 → 改中电平 1.5V → 正确恢复频率 |
| U112 | 「我在waveview上看不到你结果？帮我加载出俩」 | headless 环境新窗口不显示到远程 GUI → 写一键加载脚本 `load_result.tcl`（sx_open_sim_file_read wave.dat + frequency_result.wdf → sx_new_wv + sx_add_wave + sx_display_wave） |

## 关键产物（agent 真实生成，在 .75 上可复现）

1. **`fm_freq_vs_t.tcl`** — 交付脚本（editor 写到 `/home/e0031982/fm_freq_vs_t.tcl`）。结构：
   - `proc f_vs_t {sig v_thr}`：`sx_create_signal "frequency" analog` → `sx_create_scan $sig RISE` → `sx_set_threshold` → `sx_scan_first`/`sx_scan_next` 遍历 → 相邻上升沿 `f=1/(t2-t1)` → `sx_append_data $freq $t2 $f`
   - `proc open_wave_file`：健壮路径查找（$WV_WAVE_FILE / 候选路径列表）
   - main：open wave.dat → get signal "wave" → `f_vs_t $wave $v_thr` → `sx_write_open`+`sx_write_add_signal`+`sx_write_close` 存 frequency_result.wdf → `sx_new_wv`+`sx_add_wave`+`sx_display_wave` 显示
2. **`wave.dat`** — 真实 WDF 波形（agent 用 `sx_write_open` 合成，FM 载波 2→5Hz，5001 点）—— 可作为 A 输入资产
3. **`frequency_result.wdf`** — 频率结果文件（agent 验证可重开读 "frequency" 信号）

## .75 可移植性（强）

- WaveView ACE 经 `eda_flow run_code(lang=tcl, host=waveview)` 可用（= trace 原 SandBox_MCP_Server__run_code 同一后端）。
- `sx_*` 命令集已在 trace 中实证：`sx_create_signal/sx_create_scan/sx_set_threshold/sx_scan_first/sx_scan_next/sx_fetch_x/sx_fetch_real/sx_append_data/sx_wave_to_list/sx_open_sim_file_read/sx_write_open/sx_write_add_signal/sx_write_close/sx_new_wv/sx_add_wave/sx_display_wave/sx_update_wv/sx_version`。
- headless 限制：`sx_display_wave` 在无 DISPLAY 时不显示 GUI 但不报错；结果落 WDF 文件即可判分（不依赖 GUI）。
- ASCII 限制：run_code 沙盒要求纯 ASCII（中文注释被拒）→ 候选脚本与判分须纯 ASCII。

## A/B 档判定

- **A 档选轮合规性**：U0 是纯需求轮（6 点规整 spec，未给根因/修复）→ A 档可选。
- **但 A 档金标准不可用**：trace 末尾 U112 用户「在 waveview 上看不到你结果」→ 用户**未明确接受**最终结果（GUI 显示未达成）；agent 最终交付的是 headless 结果文件 + 一键加载脚本，非用户实际接受的可判定产物。
- **→ B 档 synthesized**（子技能忠实：保留「FM 瞬时频率提取 + RISE 扫描 + 边沿间周期倒数 + 写 WDF 结果」完整子技能，金标准由 .75 WaveView ACE 标定）。

## 子技能 / distinct

- **子技能**：WaveView ACE Tcl —— 从波形文件读模拟信号 → RISE 扫描 + 阈值 → 逐对上升沿求瞬时频率 f=1/(t2-t1) → 写 frequency 波形到 WDF 结果文件 + 显示。
- **distinct vs 已有 B characterization case**：GmidLut/NmosAgeChar/CTLEtranChar/VihTripTune/ButterflyCurve/DffSetupHoldChar/ThoxVthExtract/OtaAutoTune/TxRonSize/PVTvarSpecJudge/RcurrDirClassify/SizingSensDiag/NocalOffsetDeck/MeasExtractCornerTrace **全为 HSPICE/FineSim .measure/.lis/.mt0/.tr0 表征** —— 本条=**WaveView 波形级频率表征（RISE 扫描 + 边沿间周期倒数 + WDF 写回）**，shard B 首个「WaveView ACE 波形频率提取」case，distinct ✓。

## 候选 case 设计（next round 合成蓝图）

**case_id**: `EDA-Eval-DesignFlow-WvFmFreqExtract-001`（characterization, B档 synthesized, L2, track synthesized）

**交付**: `outputs/submit.zip` 含 `fm_freq_vs_t.tcl`（CLI：`wv -ace_no_gui -source fm_freq_vs_t.tcl` 或经 run_code lang=tcl 执行；接 `<wave_file> <sig_name> <v_thr> <out_wdf>`）。

**候选 ref** `wv_fm_freq_extract_ref.py`（CLI `<wave.dat> <spec.json> <out_dir>`：组装 Tcl 脚本（f_vs_t + open + write WDF）→ `subprocess` 调 `wv -ace_no_gui` 或 eda_flow run_code → 解析输出 WDF 回读 frequency 信号 → freq_report.json{t[], freq[], n_edges, carrier_start, carrier_end, v_thr, sig_name, wdf_path}）。

**A**（FM 载波 2→5Hz 线性扫频，5001 点，幅值 0~3V，v_thr=1.5，信号名 "wave"）→ 恢复 freq∈[2,5] Hz；
**B**（hidden：FM 载波 10→20Hz 对数扫频，8001 点，幅值 -1~+1V，v_thr=0.0，信号名 "fm_out"）→ 恢复 freq∈[10,20] Hz。
跨输入：载波范围/扫频类型/点数/幅值/阈值/信号名 全不同 → 防 hardcode。

**check.py 14 条 a-n（设计）**：
- (a) zip+fm_freq_vs_t.tcl
- (b) tcl 语法（沙盒 source 不报错 / 纯 ASCII）
- (c) subprocess 真跑 WaveView（run.log 含 sx_version / wv banner，反 naive_no_rerun/naive_print_expected）
- (d) B 输出 WDF 文件存在 + 可 sx_open_sim_file_read
- (e) B frequency 信号 n_points ≥ 5（≥5 个上升沿对，反 naive_empty）
- (f) B 恢复 freq 落 [carrier_start_B, carrier_end_B] ±15%（反 naive_fake_numbers）
- (g) B 首末 freq 匹配 GT ±10%（反 naive_partial）
- (h) B v_thr 从 spec_B 读（0.0）非硬编 A 的 1.5（反 naive_hardcode_a）
- (i) B 信号名从 spec_B 读（"fm_out"）非硬编 "wave"（反 naive_hardcode_a）
- (j) RISE 扫描 + 阈值逻辑（源码审查：含 sx_create_scan RISE + sx_set_threshold，反 naive_grep_only 只 grep 不跑）
- (k) f=1/(t2-t1) 周期倒数（源码审查：含 sx_fetch_x 相邻差 + 倒数，反 naive_no_inversion）
- (l) 跨输入守卫：rerun A 恢复 freq∈[2,5] + A 信号名 "wave" 出现
- (m) name-agnostic：B 名{fm_out, frequency} 出现 + A 名{wave} 不泄漏（反 naive_hardcode_a）
- (n) 确定性：rerun B freq 首值 2% 内一致

**6 neg**：naive_empty（空 tcl）/naive_print_expected（print 固定 freq 串不跑 WaveView）/naive_no_rerun（不调 subprocess）/naive_hardcode_a（硬编 A 的 wave/1.5/2-5Hz）/naive_grep_only（grep wave.dat 不做 RISE 扫描）/fake_core_deleted（删 f_vs_t 核心）。§4.9 三假齐备。

**GT 标定**：.75 WaveView ACE 生成 A/B WDF + 跑 ref + 回读 frequency 信号 → 写 hidden_manifest.json。

**风险**：① WaveView ACE 在 eda_flow run_code 是否可用（host=waveview）—— next round 第一步探查 `sx_version`；② `wv -ace_no_gui` CLI 是否可 subprocess 直接调；③ WDF 写回 + 重读保真度（trace 已验证 437B/58972B 文件可重开读信号，低风险）。

## 状态

- **本轮**：scouting + 深读（未合成、未进 jsonl、未 mark case）。本轮为 scouting+deepread 轮（上轮已交付 MeasExtractCornerTrace-001，非连续 deepread-only）。
- **DEBT:1**。next round 第一件事：探查 eda_flow run_code(lang=tcl, host=waveview) `sx_version` → 生成 A/B WDF（用 sx_write_open 合成 FM 信号）→ 标定 GT → 合成 WvFmFreqExtract-001（check.py 14 + 6 neg + selftest）→ 追加 EDA-Eval-DesignFlow_B.jsonl → mark case → 清 DEBT:1。
- ledger qb1ua claimed→deepread，covered 维持 68（deepread 不增 covered），已动 112→113。
