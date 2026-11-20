# trace_deepread — x8v81 (dsgao @ hfeg0pkn001, spice_sim, A-faithful)

**Session**: `1793945103405_x8v81.messages.json` (dsgao, pkn001=10.129.2.10, NFS dup pkn002)
**Size**: 596KB / 99 msgs / kw=11 (spice: hspice/netlist/ALPS)
**Tools**: read_files×15, list_allowed_files×9, editor×8, run_approved_command×7, search_codebase×6
**Scanned**: 11-09 fresh-window 15:51→16:18 (path(d) 续扫, 7 active 主机)

## 多任务对话流（同一 session 3 类任务）

### Task A (U#0→M#25) — netlist diff + delay diagnosis ★ 采用为 case
**U#0 逐字**: `@/proj/drcpa/.../drcpa_digital_R_trimEqOff_schematic_ALPS/drcpa_digital_R_trimEqOff_schematic.netlist和 /proj/drcoa/.../drcoa_digital_R_trimEqOff_schematic_ALPS/drcoa_digital_R_trimEqOff_schematic.netlist有区别吗，为什么后仿真 delay 有差异`

**选轮合规**: U#0 提需求（对比两 netlist + 解释 delay 差异），用户未给根因 → A-faithful 合格。

**Assistant 流**:
1. list_allowed_files 两 netlist 目录 → 发现 .netlist 是 symlink，真实路径在 `/rundata/{drcpa_sim,drcoa}/V0/simdir/finesim/workdir/dsgao/simulation/...`
2. read_files 两 netlist 1-60 行（开头一致）
3. editor 建 `/home/dsgao/Desktop/diff_netlists.py`（difflib.unified_diff）
4. run_approved_command(python-runner) 跑 diff → stdout: `drcpa lines: 459, drcoa lines: 462`，unified diff 显示 3 区域差异
5. read_files 两 netlist 360-459/462（顶层 R_trimEqOff 区段）+ search_codebase mx2LVSx2/invDS 定义
6. **M#25 结论**（用户接受的诊断）：
   - **功能性差异**：drcoa 在 trim 选通路径多插入一级 `invDSx1`（`XI13<2:0>`: trimN→trim）。drcpa 的 XI7<2:0> 直接产 cm1_ro_EqOffWlOnN，mux XI4/XI6/XI3 用 cm1_ro_EqOffWlOn/cm1_ro_EqOffWlOnN；drcoa 的 XI7<2:0> 产 trimN，XI13<2:0> 再把 trimN→trim，mux 用 trim/trimN。逻辑等价但选通边沿晚一级反相器延时 → mux 切换时刻变 → delay 差异。
   - **无害差异**：① header Top Design/Date（drcpa_digital vs drcoa_digital, 14:02 vs 14:04）② Library 名 ③ dlybiasn500ps 内 switch 实例**集合相同仅排序不同**。
   - 行数 +3 = 3 个 XI13<2:0>。

**Gold（trace-accepted 产物）**: diff_netlists.py 的 unified diff stdout + M#25 诊断。资产 /rundata 权限拒绝，从 trace M#11/M#24 tool_result 重建忠实缩减网表（A1/A2），保留全部 diff 相关结构（header + shared subckts + dlybiasn500ps switches + R_trimEqOff 顶层），diff 与金标准一致（+3 行、switch 集合相同、XI13 仅 A2）。

### Task B (U#26→M#44) — GIDL testbench 改 fnGidl 恒为 vwlp（L2，未采用）
U#26「fngidl 要恒为vwlp」→ editor 改 R_GidlAryCtrl_switch_sim_tb_v2.sp: `vfn fnGidl 0 PULSE(VHIB 0 5n TRF TRF TACT TPER)` → `vfn fnGidl 0 VWLP`。

### Task C (U#45→M#66) — fnGidlMode PWL + .tran 10p + 跑 FineSim 验波形（L2，未采用）
U#45「fngidlmode 前半程 vwlp 后半程 vss, 步长 10p」+ U#53「验证一下产生波形」→ editor 改 PWL(0 VWLP 50n VWLP 50.5n 0 100n 0) + .tran 10p 100n → run launch_v2.py (finesim) → wait_v2.py → 620 time points, gidlary_v2.pt0/fsdb 生成 → plot_v2_waveforms.py 解析 pt0 校验 fngidl=3.4 恒定 / fngidlmode 0-50n=3.4 50-100n=0 → v2_waveform.png。资产可读（tb 77 行 / DUT 11 行）但 L2 check.py 需跑 FineSim，本轮预算不足，留备选。

### Task D (U#69→M#81) — R_tOCTrim 两 netlist diff（未采用，与 Task A 同质但差异更大：dlyg 4-of-8→6-of-8 + L=176n→250n 单元族不同 + XI0 多一级 invLx2 生成 trimNN）

## 判定
Task A 交付为 **EDA-Eval-DesignFlow-NetlistSelectInvDiag-001**（spice_sim, A-faithful, L1, k=12）。
注：与 12:55 交付的 NetlistDiffBankLogic-001 同为 netlist-diff L1 类，但本 case 焦点是 **delay 根因诊断**（选通路径多一级反相器→选通边沿滞后），且金标准是具体结构事实（+3 XI13 / 选通网重命名 / switch 集合不变），非 bank-logic 结构重构。Task C (L2 GIDL FineSim) 留作下轮 L2 备选。
