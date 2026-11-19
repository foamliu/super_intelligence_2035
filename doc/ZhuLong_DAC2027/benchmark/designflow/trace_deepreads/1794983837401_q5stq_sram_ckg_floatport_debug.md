# Deepread · q5stq · t0002607 · SRAM HCSP CKP 电路调试 (spice_sim)

- **sid**: 1794983837401_q5stq
- **user**: t0002607 @ hfeg0pkn004 (10.129.2.13)
- **match_count**: 159 ; **model**: lead (deepseek-v4-pro-cloud)
- **msgs**: 215 (user 112 / assistant 103) ; **tool_use**: read_files×11, list_allowed_files×6, editor×43, run_approved_command×42, get_agent_policy_status×1
- **trace verbatim 取回**: eda_flow open_session → scp 10.129.2.13:/home/t0002607/.cline/data/sessions/1794983837401_q5stq/1794983837401_q5stq.messages.json (1.30MB, 215 msgs, READABLE)

## 用户真实意图（原话）
1. `[msg0]` 「/proj/lacaa/TV1_FS/workdir/t0002607/circuit reading/HCSP_CKG.png 看看我这个CKP的产生有问题吗，是不是有CEB和CLK就应该有CKP」+ 详细网表路径 `HCSP_AA_CXN4HCSPS1024X8M4B2C1R1W1BW1RE1_FS_Qinyu.netlist`
2. `[msg91/92]` 「presim.fsdb 这个仿真应该是比较成功的，你可以对比一下」（参考仿真）
3. `[msg178]` 「HCSP_LEAF_TRKTOP.png 这个电路今天被改过了，看看这么改可以吗」
4. `[msg183]` 「这个是新网表」（11/18 17:22 导出）
- 全程「继续思考 / 好好思考」推动 agent 深挖

## 真任务形态
**电路调试 Q&A / 根因诊断**：HCSP SRAM（1024×8M4B2C1R1W1BW1RE1_FS）CKP（时钟脉冲）从未产生，用户怀疑 CKG 电路。给 schematic PNG + netlist + fsdb 波形 + 参考仿真，要 agent 判断「电路对不对 / 改动行不行 / 为什么 CKP 不来」。零脚本交付物（43 个 editor 写的都是临时分析脚本，非交付）。

## agent 诊断链（关键转折）
1. 读 netlist 抽 HCSP_CKG/TRKTOP 子电路端口与顶层例化（XI119/XI47/XI0）
2. 追 CKP 脉冲环路：`CKP → TRKTOP 产 tracking 脉冲(TRKWBL/TRKRBL) → WT/RT 延迟链 → CKP_BCK → RSC=INV(CKP_BCK) → 回 CKG 结束脉冲`
3. 波形确认：CLK 持续跑、CEB 恒 0、Q[0..7] 全平 → 读操作未生效，CKP 未产生；measure 全 error
4. **根因 1 (Bug1)**：DC 初始工作点（presim.ic）显示 `ckpb=1.8e-5(≈0) → CKP=1 恒高 → 传输门 clk_en=0 关断`，CKPB 是**双稳态节点**，DC 收敛到坏态无法自恢复。参考仿真 `ckpb=0.75(=1) → 传输门导通`。同一 CKG 单元、同空闲输入，DC 收敛到相反态 ⇒ 证明 CKPB 双稳态无确定上电态。**修复**：`array.sp` 加 `.nodeset v(xi0.xi_timer.xi_ckg.ckpb)='pwr'`
5. **根因 2 (Bug2，决定性)**：顶层 `XI119 (HCSP_LEAF_TRKTOP)` 的 `TRKWL_BCK` 引脚接在顶层独立网络 `TRKWL_BCK` 上 → **悬空**。
   - 参考设计：`XITRK ... TRKWL TRKWL_ARY TRKWL ...` —— TRKWL_BCK 与 TRKWL **短接**（TRKWL=CKP buffer 输出，driven），脉冲期 TRKWL_BCK=1 → TRKWWL/TRKRWL 导通 → tracking 脉冲 → CKP_BCK↑ → RSC↓ → CKP 正常结束
   - 用户设计：`XI119 ... TRKWLD TRKWL_ARY TRKWL_BCK ...` —— TRKWL_BCK 是独立网络，唯一能短接的 `HCSP_LEAF_TIEHL_CORNER`（内部 `vi_cds_thru_0 TRKWL TRKWL_BCK DC=0` = 0V 短路）虽例化 XI262/XI263 两个，但接的是别的网络（net68/net73、net2/net6），短不到主环路 TRKWLD–TRKWL_BCK ⇒ TRKWL_BCK≈0V → tracking 环断
6. 对「今天对 TRKTOP 的修改」（新增 XNM3/XNM4/XNM5 三个 NMOS + 2 反相器）：与原 PMOS（XPM1/XPM0/XPM2）**同相同条件并联**，功能冗余加强驱动，**逻辑等价、不坏事**；但新网表仿真 `ckp_rise1=1.046ns ✓ / ckp_fall1=error ✗`（起振但首脉冲结束不了）→ 证明修改没改到点子上，TRKWL_BCK 仍悬空
7. 终验：新网表 + TRKWL_BCK 接 TRKWLD → `ckp_rise1=1.046ns / ckp_fall1=1.159ns / rise3=5.046n / 每 2ns 一个 113ps 脉冲`，全部正常

## 交付
**分析结论报告**（msg177/214）：两根因 + 修复（.nodeset + TRKWL_BCK 短接）+ 仿真验证数字。**无持久脚本交付**。

## reframe（harness-for-teeth · Q&A→produce 可复用脚本，第八实证）
- 诊断核心可移植子技能 = **「SPICE 顶层例化悬空引脚检测」**：给定 netlist + 子电路名 + 端口名，找该子电路所有顶层例化，判该端口所接网络是否「悬空」（仅本引脚一接，无 driver / 无 0V 短接到 driven 网络）；可选 --reference-netlist 报告参考设计是否短接了该端口（修复提示）
- 全程纯 python netlist token 解析（subckt 端口表 + X* 例化端口对齐 + 顶层 mos/inverter/vdc 驱动计数），**无 EDA 二进制依赖** → layer=L1
- 真实 trace 痛点（XI119 TRKWL_BCK 悬空 + TIEHL_CORNER decoy 短到别的网络）→ asset A 设计：subckt HCSP_LEAF_TRKTOP 含 TRKWL_BCK 端口 + 顶层 XI119 TRKWL_BCK→独立网络 + decoy TIEHL_CORNER 例化在 net68/net73/net2/net6（测「短接到 driven 才算修复，decoy 短到 floating 不算」）
- hidden B 结构性差异 6 维度：subckt HCSP_LEAF_TRKWRAP / 端口 TRKWR_BCK / 例化 XI207+XI208(2 例化：1 悬空+1 短接) / 悬空网络 netTRKWR_bck / driven 网络 TRKWRD / decoy subckt HCSP_LEAF_TIEHL_DECOY(vdc_short A B DC=0)
- B2 anti-stub：同 B 但 XI207 的 TRKWR_BCK 经 TIEHL_DECOY 短接到 driven → 0 悬空；stub 常量必 FAIL

## 判分设计（k_check=k_rationale=14 a-n）
a zip顶层含detect_floating_port.py无泄漏 b py_compile c argparse(--netlist/--subckt/--port/--outdir/--reference-netlist)exit0 d 跑B产report.json e JSON结构(subckt/port/instances/verdict) f B 2例化齐(XI207/XI208) g XI207=floating h XI208=shorted/driven i verdict.floating_count=1 j reference.shorted=True+fix_hint k 非hardcode-A(B用TRKWR_BCK/HCSP_LEAF_TRKWRAP/XI207非A token) l anti-stub B2 floating_count=0且XI207≠floating m 代码实质≥25行+argparse+--reference+无A token硬编 n 确定性3次逐位一致

## §4.9 negatives(5)
empty_shell / print_expected / hardcoded_a / core_deleted / no_reference — 全 FAIL；ref 14/14 PASS

## ledger
trace_ledger_B: 1794983837401_q5stq claim @ r864 → mark case EDA-Eval-DesignFlow-SpiceFloatPortDetect-001
