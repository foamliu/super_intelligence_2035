# trace_deepread: gp99g — APLMMX GEN-025 root-cause diagnosis

- **session**: `1794225494607_gp99g` (thomasz @ hfeg0pfn058 / 10.129.33.184, mc10[1115 scan] + 28[1116 scan], spice_sim)
- **trace**: 100KB, 34 msgs, 1 substantive user turn + agent diagnostic chain
- **scan**: ssh_eda_search_20261116_072610 (1116 scan); trace subdir `1794225494607_gp99g/1794225494607_gp99g.messages.json`
- **旧判**: parked "diagnostic aplmmx.err GEN-025 explain-only no-produce" (r375) → r693 reaudit 复活

## 用户真实意图（原话）
> 「读一下 /rundata/totem/drgqx/IR/20261105/WOWTOP_IDD5B_6400_X8_TT1.166v98c/adsRpt/aplmmx.err
> 为什么会报 ERROR(GEN-025): Failed to open file "/proj/drgqx/V0/simdir/finesim/workdir/weidong/simulation/tiashu_R_RowCtrl_spicesim_idd98C_ALPS_0904/netlist" to read.
> 我没有指定这个路径的文件啊」

意图 = 定位 GEN-025 报错里那个非用户配置的路径从哪儿来 / 为什么打不开 / 怎么修（debug-Q&A 根因诊断）。

## agent 工具链与发现
- read_files 读 aplmmx.err → GEN-025 + MMX-314(parse netlist@96915) + MMX-312(找不到 sim output) 连锁
- list_allowed_files 探 workdir 树 → finesim/idd5b2-6400.x8.TT1.166v98c.current/netlist + netlistHeader/Footer
- read_files 读 netlist 96900-96930 → 第 96915 行 `.inc "/proj/.../tiashu_R_RowCtrl_spicesim_idd98C_ALPS_0904/netlist"`，在 `.subckt R_RowCtrl ...` 与 `.ENDS` 之间
- editor+run_approved_command(python-runner) 诊断脚本 → 文件不存在、目录不存在、全表 .inc 共 2 条（另一条 573331 是正常的 Array_vcap_Param.sp）

## 关键事实（trace 真值，A 档）
| 项 | 值 |
|---|---|
| 工具 | APLMMX |
| 主错误码 | GEN-025 |
| 主错误动作 | Failed to open file |
| 缺失文件 | /proj/drgqx/V0/simdir/finesim/workdir/weidong/simulation/tiashu_R_RowCtrl_spicesim_idd98C_ALPS_0904/netlist |
| 文件存在 | False |
| 目录存在 | False |
| netlist 文件 | /rundata/totem/drgqx/IR/20261105/WOWTOP_IDD5B_6400_X8_TT1.166v98c/finesim/idd5b2-6400.x8.TT1.166v98c.current/netlist |
| .inc 行号 | 96915 |
| 子电路 | R_RowCtrl (library drgqa_cmos_digital, view spicesim_idd) |
| .inc 总数 | 2 |
| 另一 .inc | 573331 → /home/coverage/DDR5/DRGQX/sim_setup/Powervoltage/Array_vcap_Param.sp |
| 连锁错误码 | MMX-314, MMX-312 |
| Design cell / lib / view | WOWTOP / drgqx_top / config_IDD_trans_RevC |
| ALPS 运行标识 | ALPS_0904 |

## 合成决策
- **形态**: debug-Q&A 根因诊断 → 产 `aplmmx_gen025_diagnoser.py(workdir,out_dir)` 现场解析 3 个输入文件 → `aplmmx_gen025_diagnosis.json`（22 顶层键）
- **A 档 trace-faithful**: A=aplmmx.err(verbatim trace msg2) + netlist_inc_snippet.txt(verbatim trace msg14 96900-96917 + 收尾 .ENDS) + diag_probe.txt(verbatim trace msg26 诊断探针输出) + requirements.json + scenario.txt + task_brief.md
- **hidden B (cross-input guard)**: 不同 DDR5 平台 ZW/zaowu, 子电路 WckDqCalib, 网表行 184722, ALPS_0712, design ZWTOP/zaowu_top/config_WCK_trans_RevB, 另一 .inc Wck_vcap_Param.sp —— B 不进 SUT 沙箱
- **判分**: check.py 21 条独立断言 (a0-a21): 前置/真跑/确定性/JSON结构/键齐全 + 13 语义对账 vs B oracle + A-leak 12 token + B-grounding >=5 token + 4 假提交回归
- **自验**: ref 21/21 PASS + 4 negs(stub_empty/stub_print_only/stub_hardcode_a/stub_deleted_core)全 FAIL · k_rationale==k_check==21 ✓
- **首例**: APLMMX GEN-025 连锁错误根因诊断（GEN-025+MMX-314+MMX-312 三错误码对账 + .inc 引用溯源 + ALPS 运行标识提取），此前 B 域 debug-Q&A 多为 FineSim/NanoSpice 日志诊断，APLMMX 网表解析诊断首例
