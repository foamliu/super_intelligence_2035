# 深读笔记 · scut3 (ronghu @ hfeg0pkn005 · mc=190)

- **session**: `/home/ronghu/.cline/data/sessions/1793928742719_scut3/1793928742719_scut3.messages.json` (dir-based, 7 msgs)
- **domain**: analog_context (SiliconSmart 功耗感知表征 inst 文件)
- **match_count**: 190 (netlist:46; schematic:14; hspice:3; calibre:1)
- **attachments** (全部可读, NFS):
  - `DbusRcvnew_DbusMg.cdl.spf` (2889B) — CDL/SPICE 网表 (invGF + invenPF 子电路 + 顶层 subckt DbusRcvnew_DbusMg, 17 MOS)
  - `deck.cir` (89305B) — HSPICE 仿真 deck
  - `deck.lis` (9583B) — listing (job concluded, 无语法/收敛报错, 121 arc data)
  - `deck.mt0` (16943B) — 测量结果 (arc delay__latr__lh__dbusl__hl__acq_1, tout__dbusl__hl_trig/targ 全 failed)

## 用户意图 (2 自然 user turn, 全 produce-task)

- **U0** (msg#0): 给出 DbusRcvnew_DbusMg 的完整 inst 描述 (power_meas_supplies {vbp vcc vccz} / grounds {vbn vss vssz} / back_bias_supplies / add_pin×8 / set_subckt_ports / add_function DbusL IQN|(RCPfrc&RCP) / add_latch IQ IQN !latRN&latR Dbus / add_switching_set {latR latRN} / add_forbidden_state×2 / create_parameter cut_netlist / set_config_opt state_partitions + timing arc RCP hl→DbusL)，附 4 文件，要求「分析原因以及如何修改」。
- **U1** (msg#5): 「inst 文件应该改成什么样」——要求给出修正后的 inst 文件。

## agent 工具链 (msg#1-6)

1. list_allowed_files + run_commands(被禁, raw shell disabled) → 读 uploads 目录
2. 解析网表/ deck.cir / deck.lis / deck.mt0
3. **电路级逻辑追踪** (msg#4): DbusL 驱动路径
   - 下拉 (→VSS): MMN10(Dbus)+MMN11(latR); MMN2(latRN)+MMN1(RCPN)
   - 上拉 (→vccz): MMP12(Dbus)+MMP13(latRN)+MMP0(latRNS); MMP10(Dbus)
   - 强驱动: XI_invenPF_7 (三态反相器, RCP=1 时 DbusL=RCPfrc)
   - 与 inst 一致: DbusL = IQN|(RCPfrc&RCP) (锁存反相输出 | 捕获值)
4. **根因**: 失败 arc `latR lh → DbusL hl` 在 acquire 模式 (RCP=1, DbusL=RCPfrc) 下逻辑上造不出来——驱动 latR 不会引起 DbusL 翻转；deck.lis 显示 job concluded (无语法错误)，纯测量失败。
5. **修正 inst** (msg#6): 给出完整修正 inst，关键改动在 latR/latRN 相关 timing arc / state_partitions。

## 资产可读性

- ✅ uploads 4 文件全部 NFS 可读 (scp 获原文)
- ✅ 网表 cdl.spf 含完整 subckt + MOS 实例 (可做拓扑追踪)
- → A-grade 可行：真实 inst + 真实网表 + 真实 deck.mt0/lis 直接可用

## case 合成 (B-grade synthesized, 防 DEBT④ + 加隐藏 B)

真实 trace 只有一组单元 (DbusRcvnew_DbusMg)，为做隐藏输入 B (结构不同) 与反硬编码，采 B-grade synthesized：
- **A (visible)** = 真实 inst (加一条显式 latR lh→DbusL state_partitions one 失败 arc 行) + 真实网表 + 真实 deck_A.mt0 (trimmed 45 行) + 真实 deck_A.lis
- **B (hidden)** = 合成单元 WlRdBufNew_WlMg (cell/pin/signal/instance 名全不同: WlQ/WlD/latW/latWN/latWS/RdEn/RdFrc; 上拉 MMP22/MMP30, 下拉 MMN24/MMN26, 三态 XI_invenPF_3; supplies vpb/vcc/vccx; forbidden_state 用 RdEn; deck_B.mt0 title delay__latw__lh__wlq__hl__acq_1 tout__wlq__hl failed) —— 每维度反硬编码
- **候选**: inst_arc_diag_fix.py (通用 --inst/--netlist/--mt0/--out CLI) 解析 inst+网表+mt0 → diagnosis.json (cell/output/function/latch/switching_set/forbidden_state/failed_arcs/root_cause/pullup_insts/pulldown_insts) + inst_fixed.txt (抑制不可造 arc)
- **15 条 a-o**: b py_compile / c subprocess B / d cell / e output_pin / f function / g failed_arc / h root_cause / i pullup / j pulldown / k arc 抑制 / l 必要段落 / m forbidden_state / n 反硬编码跨输入(A) / o 3-seed 确定性

## 自验

- ref PASS 15/15 (A/B 双端)
- §4.9 三假 (empty→c / print_only→c / core_deleted→i) 全 FAIL distinct
- 2 naive (hardcode_a→d / hardcode_b→n 跨输入) 全 FAIL
- negative_selftest ALL_NEG_FAIL=True, NEG_RC=0
- 3-seed 一致 (cond o)
- byte-sync: test field == disk check.py, sha 418272265a88642f806a6a7b92024b4c056e0805ac8f49dfd3679d34e16abd35 size 8436
