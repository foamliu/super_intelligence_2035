# Deepread — 1793268918911_brnqb (Sentaurus GAA_FET deck augment: sdevice AC CV + svisual)

- session: `1793268918911_brnqb.messages.json` (3.62 MB, 647 msgs: 367 user / 280 assistant)
- user: t0002805... NO — **e02141** | host: hfeg0pkn005 (10.129.2.14) | model: deepseek | match_count: 723
- domain: spice_sim (Sentaurus TCAD deck) | shard: B | track: reaudit revival #9
- 旧判定: parked "sentaurus deck study consultation" (r435 peeked) → 11-15 reaudit 复活为可造
- case: **EDA-Eval-DesignFlow-GaaFetDeckAugment-001** (round #627)

## 真实任务（U#6 + U#7 是与 cwq7f 区分的独立意图）
用户 e02141 在 GAA_FET 项目里学习/搭建 Sentaurus TCAD deck。**U#1**(study Applications_Library
common files) 与 cwq7f(r626) 重叠；但 brnqb 持续 55 轮向后扩展，**最 distinctive 可操作化
意图 = U#6 + U#7**：

- **U#6**: "添加sdevice工具，路径是 /home/e02141/devops/GAA_FET; then refer to the tool
  command file named AC_des.cmd (for capacitance simulation) in deck of
  Applications_Library/GettingStarted/sdevice/AC, copy and update the electrodes
  according to existing files in the deck of /home/e02141/devops/GAA_FET, update the
  gate sweep voltage range from -1.0V to 2.8V"
- **U#7**: "refer to the same deck 添加一个SVisual工具，提取CV curves"

即：以库 AC_des.cmd 为模板，**电极照搬现有 GAA_FET/IdVg_des.cmd**（gate:WorkFunction,
drain/source:Resist=375, substrate），**栅压扫频改 -1.0V→2.8V**，再加 SVisual 提取 CV
曲线(Cmax/Cmin)。

## trace 行为统计
- tool uses: 116 × editor (file create/patch), 95 × read_files, 91 × list_allowed_files,
  4 × SandBox_MCP_Server__run_code, 2 × search_codebase
- 助手产出 deck 文件（editor new_text 提取）:
  - `GAA_FET/AC_des.cmd` (3478B): sdevice AC 电容仿真，电极 gate/drain/source/substrate
    (WorkFunction=_WF_, Resist=375), Solve 两段 Quasistationary (ramp→-1.0V, sweep→2.8V
    带 ACCoupled 小信号 StartFrequency=1e6), 6 必备段 File/Electrode/Physics/Plot/Math/Solve
  - `GAA_FET/AC_des.prf` (87B): set WB_tool(sdevice,input,parameter,common) + parallel
  - `GAA_FET/Plot_CV_vis.tcl` (1807B): SVisual load ACExtract plt → create_curve
    (axisX v(g), axisY c(g,g)) → ExtractExtremum Cmax(max)/Cmin(min) → DOE puts
  - `GAA_FET/Plot_CV_vis.prf` (122B): svisual exec_mode=batch + strict + parallel
  - `GAA_FET/gtooldb.tcl` (577B): WB_binaries(tool,sprocess/sdevice) --xml
  - `GAA_FET/gvars.dat` (2619B): SWB DOE 变量表
- 另有 U#1/U#2/U#3 学习笔记 + U#12-U#48 GettingStarted 课程存档 + U#49 从零搭 DRAM GAA NMOS

## 选 trace 依据
- brnqb mc723 = 191 复活池中最高 mc 未造候选 (cwq7f mc698 已造 r626)
- 与 cwq7f(SentaurusDeckSetupSummary, study+summarize common files) 区分：cwq7f=学习总结,
  brnqb U#6/U#7=**deck 增强生产任务** (copy template + 改电极 + 改扫频 + 加 svisual)
- 复活池变现 #9 (承 r619-r626 #1-#8)

## 合成 case 设计 (B档 synthesized, trace-faithful 结构/命名)
- **形态**: L1 便携 produce-deck — agent 写 `augment_deck.py(workdir, out_dir)` 读
  template/AC_des.cmd + GAA_FET/IdVg_des.cmd(电极源) + task_spec.json(扫频) → 产出
  adapted AC_des.cmd + Plot_CV_vis.tcl + 两个 prf → 打包 submit.zip
- **A 档为何不可行**: 原始库 AC_des.cmd 模板与原始 GAA_FET/IdVg_des.cmd 在 trace 中未完整
  落盘 (助手只产出了 adapted 后版本)，无法 1:1 还原「模板+现有 deck」输入对；故按 trace
  产出的 adapted AC_des.cmd 结构反推合成模板(通用电极 + 默认扫频 0→2.0V)与现有 IdVg_des.cmd
  (gate WF / drain-source Resist=375 / substrate)。B档合成保留真实电极名/Resist 值/扫频值/
  6 段结构/SWB 占位符/SVisual Cmax-Cmin 提取，结构忠实于 trace。
- **Asset A**: template/AC_des.cmd(库模板 通用电极 gate/drain/source/body, 扫频 0→2.0V) +
  GAA_FET/IdVg_des.cmd(电极 gate[WF]/drain[Resist=375]/source[Resist=375]/substrate) +
  task_spec.json(sweep -1.0→2.8, extract Cmax+Cmin, curve v(g)/c(g,g))
- **Hidden B**: NanoFET 变体 — IdVg_des.cmd 电极 Gate/Drain/Source/Body, Resist=500,
  WF=_WF2_ ; task_spec sweep -0.5→3.3 ; 模板同 A
- **check.py** (13 断言 a-m, 自包含独立 oracle 解析器):
  a zip 含 5 文件 / b Device+File(Grid/Plot/Parameter/Current) / c 4 电极 /
  d 电极名==A 现有 IdVg(gate/drain/source/substrate) / e gate 带 WorkFunction /
  f drain+source Resist==375 / g 首段 Goal==-1.0(sweep_start) / h 次段 Goal==2.8(sweep_end) /
  i ACCoupled 小信号(StartFrequency/EndFrequency) / j vis create_curve(v(g)/c(g,g)) /
  k vis 提取 Cmax+Cmin(ExtractExtremum max+min) / l prf(sdevice parameter + svisual batch) /
  m **cross-input guard**: 重跑隐藏 B → B 电极==Gate/Drain/Source/Body + B 扫频==-0.5/3.3 +
  B Resist==500 且 A!=B(电极+扫频) 证非硬编 A
- **自验**: ref augment_deck_ref.py 13/13 PASS(A 全 PASS + hidden B 全 PASS) + 4 negs
  (naive_hardcode_a 仅 fail@m 证 cross-input guard 有牙 / always_empty fail@[b-m] /
  print_only fail@[b-m] / core_deleted fail@k 删 Cmax/Cmin 提取) 全 FAIL + §4.9 degenerate
  全 FAIL + negative_selftest ALL GREEN(含 ref positive control) · k=13 ✓ k_check==k_rationale

## 覆盖分子
spice_sim 域 + Sentaurus sdevice AC 电容仿真 deck 增强 + SVisual CV 提取 + SWB 工具集成。
新形态: reaudit「deck-template-adaptation 生产」操作化首例 + sdevice-AC-coupled 小信号块
解析首例 + SVisual-ExtractExtremum Cmax/Cmin 提取首例 + cross-electrode-adaptation guard 首例。
