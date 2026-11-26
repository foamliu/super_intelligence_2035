# trace deepread — 1793941691690_z3tqe (reedchen @ hfeg0pkn002)

## 元数据
- sid: 1793941691690_z3tqe（ts 2026-11-09，mtime fresh ≥ 11-06）
- user: reedchen · host: hfeg0pkn002 (10.129.32.202) · msgs: 80（28 user turns）
- spice kw hits: 69（FineSim 多 PVT SP 生成）
- ledger: 11-05 重扫令 pkn001/002/005 fresh 扫描 → un-ledgered TOP → CLEAN

## U#0（逐字原文，A-faithful 任务说明）
```
/rundata/ddgoa/V0/simdir/finesim/workdir/reedchen/simulation/ReedChenWork_TB_DbusRcvWritePostSim/
我需要你在这个工作目录下构建多PVT 前仿后仿的环境，请你参考/rundata/ddgoa/V0/simdir/finesim/workdir/reedchen/simulation/ReedChenWork_TB_DbusRcvReadPostSim/scripts/SKILL.md
以及相关环境和脚本制定构建计划，和我讨论
```
- **A-faithful 判定**：✓ 提需求（构建多 PVT 前仿后仿环境）+ 表达目标（参考 SKILL.md 制定计划），🚫 未指出根因/未给修复方案 → 合规。

## 对话流（assistant 工具链 + 关键产物）
1. U#0 提需求 → assistant list_allowed_files 探 ReadPostSim 参考 + WritePostSim 目标目录
2. read_files SKILL.md/README.md/gen_sp_dbusrcv.py（Read 版生成器）+ WritePostSim template.sp/templateLF.sp
3. 对比 Read(读通路,9 PVT×5 RdFi=45 SP) vs Write(写通路,无 RdFi 脉冲块,量测落 v(Din0)/v(Q))
4. U#确认 36 SP(9 corner×{HF,LF}×{前仿,后仿})；HF→PVT_HighVolt，LF→PVT_LowVolt
5. assistant 在 /home/reedchen/script_dbus_rcv_write/ 创建 gen_sp_write.py（editor 分块写）+ run_oneclick.sh + run_all.sh + README/SKILL + deploy.py
6. deploy.py（python-runner）部署到 WritePostSim/scripts/ + 复制 PVT 表
7. run gen_sp_write.py 4 combo（HF post/pre + LF post/pre）→ 36 SP 生成
8. 验证：post TT(TT+tt_Array+bjt_tt,pvcc=0.8,.inc spf/subckt/XI 激活,.inc netlist 注释)/post SF(SF,tt_Array 注释,aux→ss,pvcc=0.85)/pre TT(反转) 全对
9. smoke_prep.py 短窗口(.tran 100p 400n,meas 0-200n/201n-400n) + TT smoke deck 生成
10. U#接受（msg[79] 环境已构建完成并验证通过）→ **金标准=该产物集**

## 金标准（gen_sp_write.py，233 行，已 fetch 到 .75 workdir + 本地 reference/）
核心变换 `transform_template(tpl_lines, corner, voltage, temp, mc, sim)`：
1. **.temp <temp>c** 替换
2. **.lib 'path' section**：
   - path 含 `model.sp`：section 含 array → 用 arr(tt/ss/ff_Array，SF/FS arr=None→注释行)；否则主段→model(TT/SS/FF/SF/FS)
   - path 含 `incFile_lp`：section `bjt_/res_/nicap_/diode_` + aux → aux(TT→tt,SF/FS→ss)
3. **.param pvcc = <voltage>v** 替换
4. **set_mc_block(mc)**：mc=True → 标称 `.tran`(无 monte/sweep)注释；`*.tran ... monte` 解注释；`*.param sigmaflag`/`*.param mis_flag` 解注释
5. **set_netlist_mode(sim)**：post → 激活 .inc(.spf/subckt)+XI_，注释 .inc netlist；pre → 反之。`_netlist_cat` 按模式匹配(.inc 路径含 .spf/subckt→post；含 netlist→pre；XI_ 开头→inst)，**非写死块名**

CORNER_LIB: TT{TT,tt_Array,tt} SS{SS,ss_Array,ss} FF{FF,ff_Array,ff} SF{SF,None,ss} FS{FS,None,ss}

## 真实资产（从 trace tool_result 提取，原文）
- template.sp（WritePostSim HF，128 行）：.temp 25c / .lib model.sp TT + tt_Array / .lib incFile_lp bjt_tt/res_tt/nicap_tt/diode_tt / .param pvcc=0.8v / .tran 200p 1u / *.tran sweep monte=10/1000 / *.param sigmaflag=6 / *.param mis_flag=1 / .inc netlist(presim 激活) / *.inc spf+*.inc subckt+*XI_(后仿注释)
- PVT_HighVolt.csv(9 行): TT,0.8,25 / SS,0.9,-40 / SS,0.85,130 / FF,0.82,-40 / FF,0.74,130 / SF,0.9,-40 / SF,0.85,130 / FS,0.9,-40 / FS,0.85,130
- PVT_LowVolt.csv(9 行): TT,0.68,25 / SS,0.83,-40 / ... 

## 案例设计（EDA-Eval-DesignFlow-MultiPvtSpGenBuild-001）
- domain spice_sim, track faithful(A), level L1, k=12
- 与 PostSimUncommentFix-001 互补：后者只测 netlist 注释切换(_netlist_cat)；本案测 **corner→库映射 + .temp + .param pvcc + mc 开关**（PostSimUncommentFix 未覆盖），netlist 切换仅作 1 条(k)汇总
- A 资产: template_A.sp(真实) + PVT_A.csv(真实 9 corner) + prompt.txt(U#0) + task_brief.md
- hidden B: template_B.sp(块名 wbufMuxPF_RdPath_length52_rev3) + PVT_B.csv(5 corner TT/SS/FF/SF/FS 异值)
- hidden C: template_C.sp(全新块名 rdqMuxPF_DqPath_length38_rev5) + PVT_C.csv(2 corner) 验泛化
- check.py 12 断言(a-l): ①zip含py ②py_compile ③B post 5 .sp ④.temp ⑤.lib model 主段 ⑥array 段(SF/FS 注释) ⑦incFile_lp aux ⑧.param pvcc ⑨mc 开关 ⑩非 mc 保持 ⑪pre netlist 切换 ⑫C 泛化
- 3 negative(naive_no_transform/hardcoded_A/always_identity) + §4.9 三假(empty/print_expected/del_core)
- 自验: ref PASS 12/12 ✓ + 3 neg 全 FAIL(d/e/f/g/h/i/l) ✓ + §4.9 三假全 FAIL ✓ + 闸门 12==12≥8 ✓ + sha dd59f0d8a9==disk ✓
