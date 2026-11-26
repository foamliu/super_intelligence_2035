# Deepread — dckp0 (joeyl @ hfeg0pkn004, mc=69, hspice:175/waveview:121, 124 msgs, 1.07MB)

**trace_source**: user=joeyl, host=hfeg0pkn004, session_file=1791772987381_dckp0.messages.json, match_count=69, ip=10.129.2.10
**real_task_summary**: 从 612GB FineSim .tr0 二进制波形文件离线重测 jitter（TIE/period/RMS）→ CSV；agent 逆向 .tr0 二进制格式，发现 DUT 四相时钟根本未翻转（根因 ≠ measure 文件），用户最终叫停自 debug。

## 真实对话流（逐轮用户意图 + assistant 工具链）

- **U0（需求轮，A 档选轮评估）**：「这里是 testbench 3_RJ.sp，这里是 measure 文件 4phase8000.inc，这里是已经出来的结果（tt25 corner 跑完）RJ/。之前的 measure 文件 4phase.inc 有点问题导致 csv 全是 error，你可以帮我用新的 measure 文件重新算一遍并输出 csv 么？」
  - ⚠️ A 档选轮规则评估：用户**已指出根因方向**（"measure 文件有点问题"）+ 给出修复方向（"用新的 measure 文件重算"）→ **A 档不可用**（违反「凡用户已指出根因或给出修复方案的轮一律不得用作 A 档任务说明」）。→ B 档 synthesized。
- U114（叫停轮）：「不用继续了，我发现是仿真文件本身有问题，我先自己 debug，你清理下这次任务产生的文件吧」→ 用户**未接受**任何结果，主动叫停。**确认 B 档**（无金标准产物，子技能忠实 + .75 标定）。

### assistant 工具链（关键逆向工程过程）
1. `list_allowed_files` → 列 jitter/ 目录：0_fullpath_jitter.sp / 1_tran.sp / 2_ldo_dqs.sp / 3_RJ.sp / 4phase8000.inc / RJ/（结果目录）。
2. `read_files` 3_RJ.sp + 4phase8000.inc + RJ/3_RJ.log + RJ/3_RJ.mt0.csv。
3. **关键发现 1**：日志显示仿真仍用旧 `4phase.inc`，measure 全 `failed / targ not found`；旧周期 2.375G（T=421ps）vs 新 2G（T=500ps）。
4. `run_approved_command` (python-runner) 跑 `inspect_rj.py`：RJ/ 含 3_RJ.tr0=**47.5GB（首个 alter）** + 3_RJ#1.tr0 仍在增长（job 还活着）；3_RJ.mt0.csv 全 error。
5. **关键发现 2**：3_RJ.tr0 实际 **612GB**（= 300 次 Monte Carlo × ~2.04GB/次）→ **不需重跑仿真，可离线重新 measure**！
6. **16 个 parse_rj{1..16}.py 脚本逐步逆向 .tr0 二进制格式**：
   - 名字表：~5.98MB ASCII，定宽 16 字节，`v(signame)` 格式，60,629 个信号（含层次化名）。
   - 数据区：offset 6,226,896 起，每行 `[迭代号 1×f32][时间 1×f64][60629 信号 ×f32]`，行宽 W=60,630 floats；分隔符值 4 出现 65,376 次（f32 确认）。
   - 物理校验：`dqs_p`（输入激励）12.12ns 首次上升、摆幅 0.786–0.864V（= VIH/VIL）✓；`bc8_opt=0.0` 精确 ✓；时间轴 f64 单调 ✓。
7. **关键发现 3（根因）**：`dqs_buf_f0/r0≈0V`（死）、`dqs_buf_f1≈1.17V`（贴轨）、`dqs_buf_r1≈0.289V`（静态偏置）——**四相时钟节点全部不翻转**！全列扫描 60,629 信号，唯一翻转的只有 `scmosdqsib`（±5mV 小摆幅、66 次 ≈4GHz）。根因：`dqs4phstart≈0` / `cm1_fc_dqs4phstartn≈1.17`（active-low 未启动）→ **DUT 四相时钟发生器整块静止**，与 measure 文件无关。
8. 生成 `4phase8000_fix.inc`（count 100→90，T=0.5ns@2GHz，58ns tran 容 ~92 边）+ 写 `remeasure_tr0.py` / `remeasure2.py`（流式跨窗口解码，partial-row carry，时间列复位检测迭代边界）。
9. 验证：iter1 rows=4416 t=[0..35ns]，dqs_buf_* edges=0/90 → 全 error（符合根因）。
10. U114 叫停 → `cleanup_task.py` 删 23 个本任务文件（17 parse_rj + 2 remeasure + 1 gen_fix + 1 csv + 2 cleanup），不动 RJ/ 与跑着的 job。

## 4phase8000.inc measure 结构（从 agent 文本摘要还原）
- 4 相信号：`dqs_buf_f0/f1/r0/r1`（DQS 4-phase buffer 输出），vthr=0.55V。
- 每 k=1..90 边：`.measure tran tiedev_<sig>_<k> TRIG ... VAL=0.55 RISE=1 TARG ... VAL=0.55 RISE=2` → TIE（time interval error，边沿时间 vs 理想周期 T=0.5ns@2GHz）。
- 聚合：`.measure tran rms_tie_<sig> PARAM='rms(tiedev_*_*)'` 等 → RMS jitter。
- 8000 = Monte Carlo 迭代数；4phase = 4 相时钟。

## distinct vs 已有 B characterization/spice_sim case
- 7ycbz DutySkewAvg = **edge-dump CSV** → duty/skew 平均（无二进制解析、无 sim、无 .tr0）。
- 7rsed DivSelDuty = divider 选择 duty 测量。
- DffSetupHoldChar / RcurrDirClassify / ThoxVthExtract / PVTvarSpecJudge / TaperBufOpt = 全部 **parse .lis .measure**（ASCII），无二进制波形解析。
- FineSim 四 case (gvm3g/hk622/uky6c/cllpy) + FineSimWorkflowRunner = sim 修复器/运行器，无 .tr0 二进制逆向。
- NetlistLintHsp = 网表 lint。
→ **本条 = `.tr0` 二进制波形格式逆向 + 离线 jitter 重测（不重跑 sim，从 raw 波形重算 TIE/period/RMS → CSV）**，shard B 首个「二进制波形 forensics + offline re-measurement」case，distinct ✓。

## 便携 reframe（关键，下轮合成用）
- trace 走 FineSim 612GB .tr0 + 300 Monte + foundry DUT（不可移植 .75）→ 保留「**从二进制 .tr0 离线重测 jitter**」子技能。
- **.75 HSPICE V-2023.12-SP1-1 可产 .tr0**（binary transient waveform，HSPICE 标准 .tr0 格式）→ 用 level-1 Shichman-Hodges MOS 构造一个**4 相时钟发生器**（2 级反相器环振 + 4 抽头 / 或 4 级差分环振）作 DUT，HSPICE .tran 跑 → 产 .tr0（小规模，KB-MB 级）。
- 候选 **tr0_jitter_remeas_ref.py**（CLI `<netlist.sp> <cfg.json> <out_dir>`）：
  1. subprocess 跑 `hspice -i netlist.sp -o out` → 产 .tr0 + .lis。
  2. **解析 .tr0 二进制**：ASCII header（title/date/int+real flags）→ 名字表（`v(sig)` 定宽）→ 二进制数据行 `[time f64? 或 f32][sigs f32]`（HSPICE .tr0 实际格式须 .75 实测标定，与 FineSim 类似但不完全同）。
  3. 提取 cfg 指定的 clock 信号列（name-agnostic，从 header 名字表查）。
  4. 跨阈值 vthr 找上升/下降沿 → 每边 TIE = t_edge - k*T_ideal → period jitter / cycle-to-cycle / DCD / RMS_RJ / PP。
  5. 输出 jitter.csv（per-edge TIE + 聚合统计）+ remeasure_report.json。
- **A**（working）：4 相时钟正常翻转 → jitter.csv 有合理 TIE/RMS（level-1 RO 抖动 ps 级）→ PASS。
- **B**（hidden，trap 复刻 trace 根因）：clock-enable 信号关闭 / 环振使能断 → clock 节点静止 → 候选必须**检测无翻转**报 `no_edges / all-error`，不许伪造数值（反 naive_print_expected / naive_fake_numbers）。
- 跨输入：信号名 / T / vthr / 边数 / DUT 拓扑全不同；name-agnostic 从 .tr0 header 解析。
- **≥8 条 a-n check.py**：(a)zip+py (b)compile (c)subprocess hspice 真跑产 .tr0 (d).tr0 二进制解析（header/名字表/数据区，反 naive_skip_tr0 只读 .lis）(e)name-agnostic 从 header 查 clock 列（反 naive_hardcode_a）(f)A 有翻转→jitter.csv 含 N 条 TIE 数值 (g)B clock 静止→报 no_edges/all-error（反 naive_print_expected 伪造 B 数值）(h)TIE = t_edge - k*T_ideal 公式正确（反 naive_raw_period）(i)period jitter / cycle-cyc / DCD / RMS / PP 聚合齐全 (j)B 重跑确定性 (k)跨输入守卫 B≠A 名+T (l)rerun_log 含 'job concluded'+.tr0 存在 (m)B 输出无 A 信号名泄露 (n)rms 等数值匹配 judge 独立重算 ±5%。
- **三假**：空壳 / print-expected / 删核心（.tr0 解析核心删→(d)(f)(g) 击穿）。
- negatives：naive_empty / naive_print_expected / naive_skip_tr0（只读 .lis 不解析 .tr0）/ naive_hardcode_a / naive_fake_numbers（B 静止却伪造）/ naive_raw_period（不算 TIE 只报 period）/ fake_core_deleted。

## 环境坑预判（下轮 .75 标定）
- HSPICE .tr0 二进制格式须 .75 实测：`.option post=2` 或默认产 .tr0？须确认 header 结构（FineSim 是 [iter f32][time f64][sigs]，HSPICE 可能 [time f32/f64][sigs] 无 iter）。可能需 `.option probe` / `.option post`。
- .tr0 是 Fortran unformatted 记录（record marker 4 字节长度前缀）→ 解析须跳 record markers。
- name-agnostic：HSPICE .tr0 名字表格式（定宽 / 空格填充 / `v(sig)`）须实测。
- 备选：若 .tr0 解析过难，退一步用 HSPICE `.print` ASCII 输出 + 候选仍须从 raw 波形重算 jitter（非 .measure）——但会损失「二进制 forensics」distinct 价值，仅作 fallback。

## 教训（从 trace 提炼）
1. .tr0 二进制逆向须**多物理特征交叉校验**（电源轨精确值 + 已知激励翻转时间 + 时间轴单调）防名字→列映射偏移。
2. 跨窗口流式解码须 partial-row carry + 时间列复位检测迭代边界，不能按平均步长跳转（会漂移）。
3. **"全 error" 根因可能是 DUT 未工作而非 measure 文件错**——候选必须区分（B trap 烤入）。
4. 静态区大量 0.0 f64 会被误读为 t=0 锚点 → 须连续 4 行时间严格递增才算真锚点。

## 2026-11-04 13:2x–13:4x .75 HSPICE .tr0 二进制格式实测标定（本轮合成尝试，DEBT 顺延）

**HSPICE V-2023.12-SP1-1 post=1 .tr0 二进制格式（实测确认）**：
- 文件 = Fortran unformatted 顺序记录（每条记录前后各 4 字节长度 marker，值相等）。
- rec0 (4B) = int32 version = **49**
- rec1 (392B) = ASCII header：前 4 字符 = `nvars`（如 "0005"=5 = time + 4 sigs），其后 title + date + Copyright padding
- **无独立名字表记录** —— 信号名只在 .lis `.print` 表头（`time voltage voltage...` + 下一行 `n1 n2 n3 n4`）。候选须 parse .lis 拿列名 → name-agnostic。
- rec2 (4B) = int32 = **下一条数据块的 float 计数**（如 2049），**不是** per-row 维度！
- rec3 (data) = 2049×4 = 8196 字节数据
- rec4 (4B) = 下一条数据块 float 计数（2025）
- rec5 (data) = 8100 字节 … 交替 [count(4B)][data] 对
- **per-row 维度 = 2 + (nvars-1)**（f64 time = 2 slots + nsigs×f32）= 6（4 sigs 时），row_bytes = 24
- **关键坑（partial-row carry）**：每条数据块 float 数 **不是** row_dim 的整数倍（2049 = 6×341 + 3，余 3 floats = 12 字节 = 半行 [time f64 + 1 sig f32]）。下一条数据块续上剩下 3 sigs。**必须把所有 data 块 body 拼接（跳过 4B count 记录），再 floor(len/row_bytes) 提行**。按块 floor 解码会每块漏半行 + 下一块首行把 3 个 signal f32 误读为 f64 time → 时间非单调（出现 0.052s 垃圾值）。拼接后时间单调 0→10ns ✓。
- 数据行布局：`[time f64 LE @0][sigs f32 LE @8]`

**.75 端到端验证（reparse2.py 拼接版）**：
- A (5-stage odd ring + .ic v(n1)=0/n2=1.2/n3=0/n4=1.2/n5=0, post=1, .tran 5p 10n)：.tr0=165KB, nvars=5, row_dim=6, total_rows=6841, 时间单调 0→1e-8 ✓, clkp4 摆幅 -0.0014→1.12V, **但仅 2 条 rising edge @1.79ns/1.86ns（66ps 间隔）后衰减** → ring 起振后阻尼，DUT sizing 需调（robust 振荡，目标 ≥30 edges）。
- B (4-stage even ring + .ic, post=1, .tran 5p 8n)：.tr0=1288B, total_rows=27, clkb 静态 1.228e-8→1.229e-8（~12uV 抖动，不过 0.55 vthr）, **n_edges=0** ✓ dead-clock trap 工作。
- 列名 parse：A `['time','n1','n3','n5','clkp4']`, B `['time','phse1','phse2','phse4','clkb']` → name-agnostic lookup 工作。

**HSPICE 坑**：
1. level=1 `.model` **不可 gamma=0.0**（强制 nsub=0 → `**error** nsub <= ni` abort，不产 .tr0）。须 `nsub=1e16 u0=600 tpg=1`（gamma 由 nsub 派生）。
2. 环振 **必须 .ic** 打破对称（无 .ic → DC 解到 meta-stable 平衡点，tran 不起振，.tr0=1288B 静态）。
3. `.tran 5p 10n 0 5p` 第 4 参数 < tstop → HSPICE 警告并忽略 tmax（无害，仍产 .tr0）。
4. write_file MCP 对 JSON-looking content 反序列化 → cfg.json 须 run_commands heredoc 推。
5. candidate run_hspice 须 abspath(netlist) + abspath(out_dir) + cwd=out_abs（相对路径 cwd 错位 → rc=1 不产 .tr0）。

**本轮交付状态**：未进 jsonl、未 mark case。已完成：格式逆向（拼接版 parser 验证）、A/B 网表（nsub+.ic 修正）、cfg_A/B、prompt/task_brief、ref.py（tr0_jitter_remeas_ref.py，含拼接 parser + name-agnostic .lis 列名 lookup + edge/TIE/RMS/PP + no_edges 检测 + tr0_meta）。**DEBT 顺延 DEBT:1**。下轮第一件事：(1) 调 A DUT 使 robust 振荡（建议 3-stage odd ring + 大 W + 减 clkp4 负载 cl=2f + .ic 全错相，目标 ≥30 edges / period 稳定）→ 重跑 reparse2 确认；(2) 合成 check.py 14 条 a-n（judge 独立 reparse .tr0 比对，详见深读笔记 §≥8 条设计）；(3) 6 negatives + selftest；(4) reference_submit.zip + 追加 EDA-Eval-DesignFlow_B.jsonl + mark case。
