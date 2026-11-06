# 深读笔记 — 1793062149793_u8ovn (t0002616 @ 10.129.2.13, mc=126, schematic_netlist)

## 任务来源
- session: `1793062149793_u8ovn`（N=95 msgs，6 user turns）
- 用户：t0002616，主机 10.129.2.13
- 真实附件：netlist（`/home/t0002616/.cline/data/sessions/1793004252449_aet4o/uploads/netlist`，12504 行 SRAM 目标列测试台网表 `Mat_Testbench_revised`）

## 用户轮（逐字）
- **U#0 (msg0)**：「为我分析使用这个电路仿真计算 tCS（WL on → VSN 90%，D0） 和 WR_Time（BLa/b cross → VSN 95%）应该选取哪个cell」+ 附 netlist。**纯提需求 → A-faithful**。
- **U#1 (msg55)**：「需要选取最远cell，如何判断哪个cell最远」——目标细化（选"最远"cell），非根因/修复方案 → 仍可入 A 档。
- U#2 (msg78 后)：给激励 All0.sp，要求核对激励并给出最远 cell 正确结论（含修正方向）。
- U#3/U#4：补单元网表 / 给"最终仿真网表"。

## trace agent 工具链（msg1–94）
- `list_allowed_files` / `read_files` 读 12504 行网表 + uploads
- `run_approved_command` (shell-runner) 跑 `grep_netlist*.sh`（自己写 helper 脚本，因 `run_commands` 被 policy 禁、shell-runner 须 filePath）grep `.SUBCKT` / `Tar` / `CBL_Target` / `R_BL` / `LBL`
- `skills: aether-tool-qa` 查 SRAM 阵列混合信号仿真选 cell 方法
- 结论以 markdown 报告输出（msg54/62/78/88/94）

## 关键事实（agent 还原）
1. **网表层次**：顶层 `Mat_Testbench_revised`(2 个 Mat) → `Mat_SC_Mat_revised`/`One_mat_allmixed_revised`/`One_submat_LBL` → 列宏 `CBLx8_BLaBLb_Tar_BLSonBLa_Can_new` → 目标列 `XI_kcellx32mdl_{T,M,B}_Tar_*`(含 `kcellx1mdl_{T,M,B}` leaf) + RC 负载列 `kcellx32BGmdl_{T,M,B}_Load`/`kcellx16BGmdl_B_Dum`(只电容无真实 VSN) → `SA_unit`(灵敏放大器，接 `Mat0/Mat1_BLa_Tar<k>`)
2. **真实 VSN = 位单元存储节点 `CC`**（`CC00…CC73`，带 `.IC V(CCxx)=KCT..` 初值），**网表里没有叫 "VSN" 的节点**；SA 内部感应节点 `SaBla/SaBlb`。只有 `kcellx32mdl_*_Tar` 里的 `kcellx1mdl_*` 才有真实 CC/VSN。
3. **"最远 cell" 判据**（msg62/88/94）：按到 SA 的**位线/字线 R·C 累积电阻**定，不是"离 SA 最近的 cell"：
   - **BL 方向**：SA(`blsel_withcap`) 从**顶段 LBL1_T_R** 进 → 经穿透电容 `CTConLBL_Tar`(r131/r132, Rc/2) 耦合到 **LBL0_T_L**(LBL0 半边物理更远) → 每半再 `R_BL_T → R_BL_M → R_BL_B`(T→M→B)。**B 底段最远**。
   - **WL 方向**：WL 从驱动器 `SWD_unit`/`LWL*` 出发，离驱动器起点越远 `R_WL` 累积越大。
   - **远列**：列 16–23(`LWL0_R`，激励 `far_dvbl0_*`) vs 近列 0–7。
4. **最终结论**（msg94）：最远 cell = **`xi0.xi_mat0.xi_submatsldl_first.xi_kcellx32mdl_b_4.cc02`**（B 底段 / LBL0 半 / 远列 LWL0_R / BL0/WL2=D0），WL 触发 `lwl0_r_bottar<2>`。原激励测的 `_m_4`(中段 M) 选错层，应改 `_b_4`(`midtar→bottar`)。
5. `.meas` 修正：`trig v(...lwl0_r_bottar<2>)='0.5*(pvwlp-pvwln)+pvwln' cross=1` / `targ v(...kcellx32mdl_b_4.cc02)='VCS_90P' cross=1`。

## 合成（B-grade synthesized）
- 真实 /proj 网表 12504 行不可附加 + policy 不可写 → B-grade 合成。
- **建模**：SRAM 目标列测试台，SA_unit(端点=Bla) → `R_main` → fork → 近列链(`R_near_*`, tiers T/M/B) + 远列链(`R_far_*`, tiers T/M/B)；目标单元 `kcellx1mdl_{T,M,B}`(4 端口 Bl/Wl/CC/VSN，有真实 CC)；RC 负载 decoy `kcellx32BGmdl_Load`(1 端口，cap-only，无 VSN)；保留 `.IC`/`.param`/`.meas`/`.tran`/WL driver。
- **金标** `gen_farthest_cell_report_ref.py`(CLI `<netlist> --out <report>`)：跳过 .SUBCKT 内部，找 SA_unit 实例→SA 端点；建顶层 R 图 BFS 累积电阻；找 `kcellx1mdl_*` 目标单元(4 端口)，排除 `kcellx32BGmdl_Load`；最远=max cumulative BL R；报告 instance/tier/cumR/cc/WL/column/subckt + 全单元累积 R 表 + 推理。
- **A/B/B2 三轴反硬编码**：A=far 列 3 tier→最远 `Xfar_B`(R=35,B,far)；B=near 列 2 tier 大 R→最远 `Xnear_M`(R=46,M,near)；B2=far 列 1 tier 巨 R→最远 `Xfar_T`(R=44,T,far)。三者在 instance/tier/column/cumR 全不同 → 同时击败 hardcoded-A/hardcoded-B/hardcoded-B2。check 自含嵌入 A/B/B2 网表(repr 常量，不读 hidden)。
- **14 条件 a-n**：结构/compile/B-run/最远实例/cumR/subckt/cc/WL/column/排除 load/反硬编码 A/跨输入 B2/CLI/确定性。

## 自验
- ref PASS 14/14；12 negative 全 FAIL(distinct first-fail {b,c,d,g,k}=5)；§4.9 三假{empty→c, print_a→d, ref_core_deleted→d}全 FAIL；k_rationale=k_check=14≥8 GATE PASS；test==disk sha `0f94b15a` MATCH；D.jsonl 143→144；台账 mark u8ovn→case；schematic_netlist 64→65。

## 教训
1. SRAM bitline R-chain + 灵敏放大器端点 + tier/列维度是 schematic_netlist L1 拓扑分析可验好范式：BFS 累积电阻→max 即最远 cell，14 条件天然丰富(结构/run/6-字段/排除decoy/反硬编码双轴/跨输入/CLI/确定性)。
2. check 自含嵌入 A/B/B2 网表 repr 常量(非读 hidden 文件)是 design_flow test-string 隔离稳健模式(同 SpStimLoopAudit)。
3. 反硬编码三轴 = B 不同列/不同 tier/不同 cumR + B2 又不同 + 源码禁 A/B2 专属字面量(instance/cc/WL) → 击破硬编码任一档。
4. 报告含源文件路径会破坏确定性(每次 tempdir 不同)→ 金标用 basename + check 规范化 `<TMPDIR>` 替换。
5. py_compile 条件用 `compile(src,"<submit>","exec")` 而非 `py_compile.compile(bytes)`(后者不接受 str/bytes 源)。
