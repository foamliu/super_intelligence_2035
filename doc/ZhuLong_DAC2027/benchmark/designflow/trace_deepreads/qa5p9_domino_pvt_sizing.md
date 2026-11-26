# qa5p9 — Domino 接收器 PVT 尺寸扫描（reedchen / hfeg0plg93, mc=197）

**session**: 1793172510005_qa5p9 (733KB, 259 msgs)
**user**: reedchen · **host**: hfeg0plg93 · **domain**: analog_context (schematic_netlist 邻域)

## 提需求轮（A-faithful，U#1, msg 0，逐字原文）
> 我现在希望你在这个目录下/proj/ddgoa/V0/workdir/reedchen/simulation/ddgoa_cmos_work_TB_domino_Receiver_rst0_2/帮我跑多个PVT的尺寸仿真，并且收集Vm数据评估达标成果，你可以参考这个skill ddgoa_cmos_work_TB_domino_Receiver_rst0_1/skill/skill.md来加快理解需求 输入件：template vm_target.csv netlist 构建的尺寸分为P_width和P_length两个尺度 P_width 100n-1u 步进100n P_length 42n - 80n 步进4n 先产出mos_size.csv 先构建计划，和我确认后开始执行

## 真实 agent 工作流（深读 259 msgs / 87 user turns 提取）
1. 读 skill.md + template.sp + vm_target.csv + netlist（symlink → 共享 stephens netlist.presim）
2. 发现 netlist 中 `XMMP7 AbusDnN ABusDn net13 vdd! psvt w=P_width l=42e-9 nf=1` —— **width 已参数化、length 硬编码 42e-9，无 P_length 旋钮**
3. 生成 `mos_size.csv`（10×10=100 行：P_width 100n-1u×10 × P_length 42n-78n×10）
4. 参数化 netlist → `netlist_pwl.presim`：把 XMMP7 改成 `w=P_width l=P_length`
5. 建 `template_pwl.sp`：`.inc ../netlist_pwl.presim` + `.param P_length=42n` + `.tran 100p 6u` + `.measure VMLH/VMHL`（v(AbusDn) gating v(net13)）+ `.data data_scan P_width P_length`
6. `gen_sp_domino.py` + mos_size.csv + vm_target.csv → 9 张 SP 卡（每 corner 一张：.lib corner + 100 行 data_scan）+ runscript（bsub -q fqueue2h finesim）
7. 提交 9 job → 命中 `LD_PRELOAD` libstdc++ 缺 GLIBCXX_3.4.26 → 修：unset LD_PRELOAD + LD_LIBRARY_PATH 指向 finesim 自带 gcc-9.5.0 lib64
8. 轮询 .mt0.csv（每 corner 100 行 = VMLH/VMHL）→ `parse_and_optimize.py` 评 Vm vs vm_target → PASS/FAIL 报告
9. **U#42** 用户改 P_width 起点 150n（150n-1050n/100n，10 点）→ 重新生成 mos_size.csv + SP 卡 + 重提
10. **U#86** 用户又改 vm_target 回 3 corner → 重新跑（v3）

## 降级（L1-boundary）
真实 finesim 不可在评测沙箱执行 → 降级为确定性 Python 生成器 `gen_pvt_sizing.py`，保留全核心逻辑：
- 读 config.json（P_width/P_length 网格 + corners + netlist device line + template + queue/simulator）
- 产出 mos_size.csv（全因子网格）/ netlist_pwl.presim（device 行替换为 w=P_width l=P_length）/ template_pwl.sp（.inc+.param+.tran+.measure VMLH/VMHL+.data）/ sp_cards/<corner>.sp（.lib+100 行 data_scan）/ runscript.sh（bsub+queue+unset LD_PRELOAD）/ evaluate.py（独立 Vm 评估器）/ vm_eval_report.md（--mt0-dir 给定时）
- 真实 .mt0.csv 测量数据 → 合成确定性 mt0_B CSV（VMLH/VMHL per size combo）作为隐藏输入

## gold
`reference/EDA-Eval-DesignFlow-DominoPVTsweep-001/gen_pvt_sizing.py`（参数化生成器， faithful 于 trace 的网格/参数化/SP 卡/runscript/评估全链路）

## check
15 条件 a-o：a zip 含 gen b py_compile c 跑 B 出 7 件 d mos_size 网格==B 全因子 e netlist 参数化无硬编码 f template 六要素 g sp_cards 每 corner .lib+100 data_scan h runscript bsub+queue+job 数+unset LD_PRELOAD i 报告 corner 覆盖 j PASS 计数==重算 min(VMLH,VMHL)>=target k best_combo==重算 max-Vm l 跨输入护栏 A 缺 B 现 m 3 跑 sha 一致 n 退化三假全 FAIL o Vm 公式 min 独占
ref PASS 15/15 · 4 negatives ALL-FAIL distinct{empty→c / print_fixed_A→d / core_deleted→g / vmlh_only→j} · §4.9 三假(c/d/g) 3-distinct ✓ · test==disk sha c612cdc425 · k_rationale=k_check=15 ✓

## 资产
A: config_A.json(P_width 100n-1100/100, P_length 42-82/4, 9 corners cxmt10G4plus, device_orig w=100e-9 l=42e-9) + prompt.txt(U#1 逐字) + task_brief.md
hidden B: config_B.json(P_width 150n-1100/100, P_length 42-80/4, 3 corners /proj/pdk/b06, device_orig w=150e-9 l=42e-9, 不同 cap/inv) + mt0_B/(3 文件，合成 VMLH/VMHL，PASS 计数 41/16/16) + hidden_manifest.json

## 教训
(1) .75 /proj/train NAS 100% 满（22T/64K avail），无法在沙箱 workdir 写资产 → 全流程在本机 36.15 repo 构建（资产/reference/check.py 均落 EDA-Flow-Bench 本地，无需 .75）；仅 ssh 远程读 trace 用 run_commands（不写盘）。
(2) ssh 远程 python heredoc 在 eda_flow 会 hang（stdin 不通）→ 改用 base64 编码 python payload + `ssh host "python3 -c 'import base64;exec(base64.b64decode(\"...\"))'"` 绕过 stdin/quoting。
(3) 高 mc 候选首轮多为 skill-paste/analysis/根因/debugging；qa5p9 靠 PVT sizing 提需求轮（具体交付 mos_size.csv + 评估）入选，gold 降级为读 config 的确定性生成器保留全链路。
(4) 合成 .mt0.csv 替代真实 finesim 输出是 L2→L1-boundary 降级的关键抽象：测量数据变隐藏输入，评估逻辑保持 faithful。
