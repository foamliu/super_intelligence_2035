# 深读：x2w2z — FineSim 多 corner 扫描 deck 拆分 + 并行提交

## 元信息
- session: 1793093197648_x2w2z
- user: yueliu @ hfeahpc501
- model: deepseek-v4-flash
- mc: 469 (kw: virtuoso:775 netlist:133 hspice:62 ...)
- title: "FineSim (R)"
- cwd: /home/yueliu
- 316 msgs，157 hspice tool 调用（agent 读/改 .sp deck + 跑 shell）

## 真实用户意图（逐字原文轮）
- U[0]（33KB）：贴 FineSim V-2023.12-1 启动 banner + 完整运行日志，问仿真退出原因
- U[19]：`/proj/dscqa/V0/workdir/yueliu/simulation/dscqa_yueliu_AF_Blown_Array_Block_sim_schematic_ALPS`（指出正确工作路径）
- **U[55]（提出需求轮，A档候选）**：`没有fqueue8权限，帮我操作看看怎么快速跑完五个corner`
- U[79]：`直接帮我创建，并提交仿真`
- U[167]：`有结果后分析结果，确认是否跑完仿真，如果有错或者退出，纠错并重新跑仿真直到出来结果`
- U[233]：`出结果了吗`

## 真实流程
yueliu 在跑 AF_Blown_Array_Block（反熔丝/eFuse blown array block）的 FineSim tran 表征，扫 rupe_res（熔丝电阻 10kΩ / 100MΩ / 300kΩ / MOS）× PVT corner。5 个 sweep deck：sweepR100M.sp / sweepR10k.sp / sweepR10k2.sp / sweepR300k.sp / sweepRMOS.sp。

**sweepR10k2.sp 结构**（核心）：
- header：FineSim options（`.option finesim_mode=prohd` 等）+ `.param ptemp=130` + `.OPTION finesim_spf="AF_Seg.spf.TYP_98_RCC"`
- `.inc 'netlist'` + `.inc 'Pattern_Power_fuse.sp'`（foundry 网表，permission denied 不可读）
- `.param pvcc=0.92v`（**早期 base pvcc，line 42**）+ `.param rupe_res=10000` + 时序 Tsel/Tlat/Tdone/tedge
- 激励：PWL 源 VFsYAdd<0>/VFsXAdd<0>（读/烧脉冲），VFsXAdd<1..31>=0，VFsZAdd<1..16>=pvwlp
- 网表段：`.SUBCKT AF_EfuseCell FzOut Lvfsbln XAdd inh_vss`（R0 AfInt Lvfsbln rupe_res + XMM0 ntn_fx MOS + cg1/cg2/cout1 电容）
- `.inc 'tran.sp'` → `.tran 10ps 2.5us`
- `.probe V(*) I(*) isub(*)`（**全节点 probe，输出巨大**）
- `.inc 'measure.sp'` → 大量 `.meas avg v(...)/i(...) from=1.7u to=1.8u` + PARAM 派生（V_XY=v_lvsblnX-v_Afint00 等）
- **base corner**：`.temp 130` + `.param pvcc=0.92v`（**corner 段又设一次 pvcc**）+ `.lib '...G5_CIP_Model_D5_v0d9.sp' SS` + bjt_ss/res_ss/nicap_ss/diode_ss
- `.alter 3`：`.temp -40` + `.param pvcc=1.23v` + `.lib ... FF` + bjt_ff/...
- `.alter 4`：`.temp 130` + `.param pvcc=1.23v` + `.lib ... FF` + ...
- `.END`

→ sweepR10k2 共 3 corner（base SS/130/0.92 + alter3 FF/-40/1.23 + alter4 FF/130/1.23）。

**失败根因**（agent 分析）：
- sweepR10k2 (SS/130°C) 在 DC 初始化阶段就超时（>2h），LSF `fqueue2h` 队列 2h 时限到期 → SIGTERM → FineSim 存 isnapshot 退出
- R10k 比 R100M 慢 100×+（大电流 → timestep 极小）+ SS/130°C DC 收敛困难
- **sweepR100M.sp 成功**（1.96h 跑完 5 corner）的关键：有 `.ic v(fsreadclamp)=0 v(samplefsaryn)=0`（DC 收敛辅助）+ TT/25°C 易收敛

**agent 解决方案**（U[55]/U[79] 后）：
1. 把多 `.alter` deck **拆成 N 个单 corner deck**（每个 corner 一个独立 .sp，去掉 `.alter`，把该 corner 的 `.temp`/`.param pvcc`/`.lib` 模型角烘焙进单 corner deck）
2. 加 `.ic` DC 收敛辅助（沿用 R100M 经验）
3. 缩窄 `.probe`（从 `V(*)` → 只 probe measure 用到的节点，减小输出）
4. 每个 corner 一个独立 LSF `bsub -q fqueue2h` 作业 → 并行跑（绕开 fqueue8 长队列权限）
5. 生成 gen_and_deploy.py + deploy_submit.sh，部署到 sim dir 提交

agent 用 editor 分步建 gen_and_deploy.py（拆分 + 部署 + 提交），跑 python-runner 生成 5 个 sweepR10k_<corner>.sp，再 shell-runner 跑 deploy_submit.sh 提交 bsub。踩坑：editor 多次追加产生重复段、`os.system` 被 code guard 拦截（改用独立 shell 脚本提交）。

## 可复现子技能（portable to .75）
真实流用 CXMT foundry 网表（`/proj/dscqa/...` permission denied）+ FineSim V-2023.12（GLIBCXX 不可移植 .75）+ LSF fqueue。取可复现子技能 = **多 `.alter` PVT corner 扫描 deck 拆分器 + 单 corner deck 烘焙 + 收敛辅助 + probe 缩窄 + per-corner 运行脚本 + 等价性验证（单 corner deck 的 `.measure` 结果 == 原多 alter deck 对应 alter 的结果）**。.75 有 HSPICE V-2023.12-SP1-1 真跑。用自包含 level-1 MOS eFuse cell DUT + `.param kp_n/kp_p/vto` 模拟 foundry model corner（结构同真实 `.lib SS/FF`）。

## 核心陷阱（烤进 case）
1. **`.alter` 覆盖语义**：`.alter` 块的 `.temp`/`.param pvcc`/`.lib` 只从该 alter 起生效；base corner = 首个 `.alter` 前的全部。naive 拆分（整个 deck 复制 N 份只改 `.temp`）会让 base 的 `.lib SS` 模型留进所有 deck → 非 base corner 模型错。
2. **双 `.param pvcc`**：早期 base pvcc（line 42，0.92v）+ corner 段 pvcc（line 233/242/251）。corner 段的 pvcc 才是该 corner 的真值。naive 拆分保留早期 0.92v 丢 corner 段 → 非 base corner pvcc 错（0.92 而非 1.23）。
3. **`.lib` 模型角 5 件套**：主 `.lib SS/FF` + bjt_ss/ff + res_ss/ff + nicap_ss/ff + diode_ss/ff 必须**一起翻**。naive 只翻主 `.lib` 留 bjt_ss → 模型混搭。便携版用 `.param kp_n/kp_p/vto` 一组（少一套但同构）。
4. **`.measure` 全保留**：measure.sp 的所有 `.meas` 必须进每个单 corner deck（测同节点，仅 corner 值不同）。漏一个 → 该 measure 缺结果 → 等价性 FAIL。
5. **`.probe` 缩窄不漏 measure 节点**：`V(*)`→只 probe measure 引用的 v()/i()/isub() 节点；漏一个被 measure 的节点 → 该 measure failed。
6. **`.ic` 收敛辅助只加存在的节点**：`.ic v(不存在的节点)=0` → HSPICE 报错 deck 跑不起来。必须对照网表实际节点验证。
7. **per-corner 运行脚本**：每个 corner 一个输出目录 + 正确 deck 文件引用。
8. **等价性闸门**：单 corner deck 的 `.measure` 结果必须 == 原多 alter deck 对应 alter 的结果（容差内）。这是判分核心——naive 拆分任一陷阱（错 corner 参数/漏 measure/错模型）都让等价性 FAIL。

## 交付计划
EDA-Eval-DesignFlow-AlterDeckSplit-001（spice_sim, B档 synthesized, L2, track faithful）。
- assets：多 alter deck_A（可见）+ deck_B（隐藏）+ measure.sp + dut.spc + tran.sp
- reference：alter_deck_split_ref.py（parser+splitter+baker+probe-narrower+ic-validator+runner+equivalence-checker）
- check.py：≥8 条断言（结构/无 .alter/corner 参数烘焙/probe 缩窄/.ic 节点有效/运行脚本/等价性 per-corner/跨输入守卫）
- negatives：empty_shell / naive_copy_base_only（只复制 base，所有 corner 同模型）/ naive_drop_corner_pvcc（保留早期 pvcc）/ naive_skip_measure / hardcode_A
