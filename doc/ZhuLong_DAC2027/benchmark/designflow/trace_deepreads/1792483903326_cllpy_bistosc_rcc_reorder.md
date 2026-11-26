# trace_deepread: 1792483903326_cllpy — BIST 振荡器 RCC 路径修复 + var_osc 扫描顺序重排

- **trace**: `1792483903326_cllpy.messages.json` — johnl @ hfeg0pfn119, mc=354, 298KB, 85 msgs, 354 hspice 命中
- **domain**: spice_sim（FineSim V-2023.12-1 真跑）
- **case**: EDA-Eval-DesignFlow-BistOscRccReorder-001（B档 synthesized, L2, k=16）

## 真实任务流（user turns + agent 工具链）

| msg | role | 内容要点 |
|---|---|---|
| T0 | user | 「这个文件夹跑失败了 你帮我看下原因 ...RCC文件路径是对的怎么gvim就是找不到呢」（纯诊断需求，A-档合规） |
| A1-A22 | agent | list_allowed_files → read_files T_BistOsc.sp/.log/elog/fp.log → 发现 .log 报 `.inc T_BistOscNew.spf.RCC` 不存在；list pex 目录确认 T_BistOscNew.spf.TYP_98_RCC 也不存在 |
| T25 | user | 「不对啊 我在这里都看到了 .../T_BistCtrlNew/lpe/T_BistCtrlNew/T_BistCtrlNew.spf_RCC」（用户指出正确 RCC 是 BistCtrl） |
| T31 | user | 「你帮我改一下我要跑bistctrlnew」 |
| A32-A45 | agent | 写 fix_rcc_to_ctrl.py 改 17 corner .sp + gen_osc_case.py 共 23 文件（NETLIST_PATH → T_BistCtrlNew.spf_RCC），run_approved_command 执行 |
| T48 | user | 「现在跑到顺序是从0到256 我要先跑前五个和后五个 再跑其他到 你看下怎么改gen文件 记得diff看变动前后文件是否必要」 |
| A49-A69 | agent | backup_gen.py → modify_gen_order.py 改 gen_var_osc() 从 `[range(5)+range(250,256)]` 11 行 → 256 行 `[0..4]+[251..255]+[5..250]` → diff_gen.py 验证只 var_osc 区变化 → regenerate_and_diff.py 重新生成 22 corner .sp → verify_order.py 验 256 行顺序正确 |
| T72 | user | 「肯定的」（接受终态） |
| A73-A85 | agent | cleanup 8 个临时脚本 |

## 真实产物（从 read_files tool_results 重建）

- **T_BistOsc.sp**（SF_0.94V_110 corner，111 行）：`.option finesim_mode=spicead` + `.inc ".../T_BistOscNew.spf.RCC"`（line 15，BUG）+ G4Plus power params + `.lib` G5_CIP 模型 + `.inc Pattern_Power.sp/stimulus.sp` + `.MEASURE TRAN tHALF_CK/tCK/Osc_Period_0` + `.data var_osc` 11 行 [0..4]+[250..255]（BUG，缺 5-249）+ `.tran 10p 300n sweep data=var_osc`
- **gen_osc_case.py**：`NETLIST_PATH = ".../T_BistOscNew.spf.RCC"`（BUG）+ `gen_var_osc(): for value in list(range(5))+list(range(250,256))`（11 行 BUG）+ `gen_case(corner, pvcc, temp)` 模板渲染 + 17 corner 表
- **T_BistOsc.log**（FineSim fail）：`cannot open include file T_BistOscNew.spf.RCC` → `fatal 1 include file could not be opened; aborting`
- **T_BistCtrlNew.spf_RCC**（正确 RCC，真实是 foundry PEX 网表，不可移植）

## 便携化（.75 L2 真跑）

- foundry G5_CIP 模型 + 全芯片 RCC 网表不可移植 .75 → 取便携 5-stage CMOS 环振（level-1 Shichman-Hodges MOS, kp=120u/40u, vto=0.4/-0.4）作 RCC surrogate
- .75 finesim V-2023.12-1 真跑 ro_probe.sp 3s 产 .mt0: tCK=9.8367e-09, Osc_Period_0=1.6395e-09=tCK/6 ✓, exit 0 "FineSim Successfully Completed"
- 隐藏 B 用 7-stage 环振（不同拓扑 + 不同 sizing）+ FF_1.04V_-40 corner + var_osc [0-9]+[246-255]+[10-245] 三重异构防硬编 A

## 核心子技能（distinct vs 已有 B case）

1. **RCC include 路径消去法诊断**：parse .log 找 wrong RCC name → 列 assets 找 *RCC* 且 ≠ wrong → 得 correct RCC（非 substring 匹配，是文件存在性消去）
2. **var_osc 扫描顺序边界优先重排**：`[0..4]+[250..255]` 11 行 → `[0..4]+[251..255]+[5..250]` 256 行（边界 5+5 先跑，中间 246 后跑，全 0..255 覆盖）
3. **批量 corner .sp 重新生成 + diff 验证**：gen 脚本生成 17/22 corner，diff 只 var_osc 区变化
4. **.75 FineSim 真跑闭环验证**：判分器独立真跑 FineSim 验候选 regenerated .sp，不信候选自报 .mt0

## 教训

- eda_flow write_file 对超长 base64(~17KB single content) 传输会腐蚀致 tar CRC fail — 大文件传输须拆分单文件 write 或 rsync
- .75 同时有 finesim V-2023.12-1 + hspice V-2023.12-SP1-1，FineSim spicead mode 跑 level-1 MOS 环振 3s 即出 .mt0，便携 L2 真跑可行
- FineSim .mt0 是 `$DATA1 SOURCE='FineSimPro'` 格式，列名小写化后取 tck/osc_period_0
- 跨输入守卫用「不同 corner + 不同 RCC 拓扑 + 不同扫描顺序 spec」三重异构防硬编 A
