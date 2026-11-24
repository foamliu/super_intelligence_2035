# Deepread r1103 — mcnss (gracew@hfeg0pkn004, mc56, verification)

- session: `1795419751177_mcnss.messages.json` (452KB, 66 msgs)
- host IP: 10.129.2.13, user gracew
- keyword profile: verilog:172; pex:59; rtl:50; netlist:16; cmos:10; systemverilog:8 → A-domain verification (verilog+rtl dominant, pex secondary)
- 取法: scp messages.json → .75 workdir → python parse (claime `sessions/<sid>/<sid>.messages.json` 子目录路径陷阱复现 OK)

## 用户真实意图（trace 原话重构）
gracew 跑 LPDDR5 compress pattern 仿真（顶层 lpddr5_compress_tb，工程 /rundata/ddgoa/V0/simdir/verilog/gracew/verilog.lpddr5.ddgoa.net1116），拿到的 A_Compare.rpt 出现两类异常：
1. **"expdq 基本都错了"** — 每个 bank/sel 首笔读 DUT 的 DQ 是高阻 z，ExpDQ 已是有效数据，像期望窗口比 DUT 早半位。
2. **"dq 部分取反"** — 部分重排过的 sel，DQ 与 ExpDQ 呈取反关系。

用户问的核心：到底是 pattern/期望模型侧问题，还是 DUT 电路问题？且两方向不能互相掩盖（不能用好 pattern 迁就 DUT 缺陷）。

## 助手工具链 / 关键产物
- read_files: TM_Comp_Exp_function.v（seed_data_out() / data_sel 编码 case，刚做 8→16 重排，文件里大量 `// 改：原 data_sel=X → Y` 注释）
- read_files: TM_CompDataOut.v（Section 1 单 bank 读 Read_TM 缺 dqcomp_location；Section 2 多 bank 读有 dqcomp_location）
- read_files/list: A_Compare.rpt（24k 行，TM_CompDataOut 段逐笔 DQ vs ExpDQ）+ A_Summary.rpt（DQ_Err 计数 per sel）
- editor + run_approved_command: extract_dataout.py / extract_sel.py / grep_expdq.py / dump_bank0.py（在 A_Compare.rpt 里抽 bankN_selM 段、grep expdq 定义溯源）
- 结论：两类根因叠加 —— ① 封装侧 z 时序错位（Section 1 缺 dqcomp_location，期望窗口早半位）② 期望模型 8→16 重排后极性反转（seed_data_out 对 remapped sel 极性错）。verdict: model_side_fault + testbench_side_fault；非 DUT 电路问题。
- ⚠️ 助手关键警告：期望模型刚重写，是"模式侧自己把极性写反"最高发区；"是电路问题、不是 pattern 问题"这个结论不能靠 pattern 单方面下，需独立验证。
- 会话末尾用户误 `rm -rf` 删文件 → 助手给文件恢复步骤（停写盘 / 查符号链接备份 / mount ro）—— 属附带 ask，非主任务，不进 case。

## 合成决策
- 真实 /rundata/ddgoa / /proj/ddgoa 路径沙箱不可达（e0031982 ssh 仅免密 .75，目标机 gracew home 可读但工程树权限受限）→ B档 synthesized，按 trace-faithful 真实结构合成自含资产。
- A 资产: compare_A.rpt（[bankN_selM] 段 + sample K: DQ/ExpDQ/mismatch 类型）+ exp_function_A.v（seed_data_out/data_sel 8→16 重排 + gap 9~15）+ compdataout_A.v（Section 1 Read_TM 缺 dqcomp_location）。
- hidden-B: ddr5_phy_check_tb / chk_data_out / mux_sel / 6→14 重排 / gap 7~13 / bank2,bank3 — 与 A 判别 token 全不相交。
- 交付: diagnose_mismatch.py 通用根因诊断器（parse compare+exp_function+compdataout → universal_z / inverted_sel / encoding_table / remaps / section1_missing → verdict + JSON/MD 双输出）。
- check 14 断言（zip/py_compile/exit0/9 顶层键/mismatch oracle/universal_z/inverted_sel/encoding/model 标识符/wrapper 标识符/section1_missing/verdict/anti-hardcode/determinism）。
- 自验: ref PASS 14/14 + §4.9 三假(empty/print-only-A/core-deleted)全 FAIL + neg_selftest OK。
