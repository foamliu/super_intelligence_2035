# trace_deepread: pqeal — vtgm sim-result-directory per-file explanation

- **session**: `1791797079020_pqeal.messages.json` (subdir `1791797079020_pqeal/`)
- **user/host**: e0039122 @ hfeg0pkn003
- **mc**: 75 (characterization, reaudit 可造 #36)
- **size**: 1010KB, 84 msgs, ~5 substantive user turns
- **grabbed**: r654 via .75 open_session ssh hfeg0pkn003 scp (StrictHostKeyChecking=no)

## 用户真实意图（原话）

1. MSG0: 「阅读目录下的工程，给出代码架构」→ mpqa_V4/mpqa_V3 Qt 工程，助手产 MPQA 架构报告
2. MSG17: 「分析 /home/e0039122/ModelQA_1013092601/vtgm/result/ 下的每个文件分别是什么」→ HSPICE vtgm run 逐文件讲解
3. MSG28: 「同样分析」ModelQA_1013094111 → FineSim vtgm run
4. MSG35: 「同样分析」ModelQA_1013095103 → NanoSpice vtgm run (LSF)
5. MSG45: 「同样分析」ModelQA_1013100030 → FineSim (另一命名)

核心可造意图 = **解析 vtgm 仿真结果目录，逐文件结构化讲解报告**（反复 4+ 次，真实 characterization QA 工作流）。

## 关键事实（从助手 MSG27/34/44 讲解提取）

### Run 1 — HSPICE (ModelQA_1013092601)
- 仿真器: HSPICE U-2023.03-SP1-2, host hfednd077, local
- 测试: vtgm (最大跨导法 Vt 提取), DC 扫描
- 器件: ntn (NMOS) W=2.4µm L=0.19µm NF=1
- 条件: tt 角, Vd=0.05, Vg sweep(0,1.1,0.01) 111点, Vs=Vb=0, T=25°C
- 模型: nten.39 (BSIM6 Level 77)
- 测量: gm_max=1.28533e-4 @Vg=0.79, vt_gm_max=0.79, id_gm_max=2.878e-5, **vtgm=0.54107V**
- alter: 2 遍 (.ALTER)
- 文件: .lis(主日志), .ms0/.ms1(MEASFORM=2), logFile(PSF索引), .st0(状态), .pa0(plot unit), .su0/.su1(summary), .sw0/.sw1(波形BINPSF)

### Run 2 — FineSim (ModelQA_1013094111)
- 仿真器: FineSimPro T-2022.06, host hfeg0pgn023, parallel -np 4
- 同器件同条件同模型, vtgm=0.54107V (一致)
- 文件: .log, .md0/#1.md0, .sw0/#1.sw0, .sw.grp, .fp.log

### Run 3 — NanoSpice (ModelQA_1013095103)
- 仿真器: NanoSpice (Primarius) V4.26.2.2, host hfechds003, **LSF job 497285**
- 同器件同条件, vtgm=0.54107137072V (全精度, 一致)
- 文件: .log, .ms0/.ms1, **.measure (全精度汇总导出, 本run特有)**, .output/logFile, .output/.sw0/.sw1

三个 run 同测试同器件同条件 → vtgm 完全一致 = 多仿真器交叉验证样本。

## A 档可行性
真实 ModelQA_* 结果目录是 10 月临时产物，hfeg0pkn003 上 `ls` 已报 No such file or directory（已实测）⇒ A 档不可行，走 B 档 synthesized（从 MSG27 逐字重建 HSPICE run 关键文件，隐藏 B 合成 NanoSpice 结构不同 run）。

## 造题
→ EDA-Eval-DesignFlow-SimResultDirExplain-001 (characterization L1, B档)
- A doc/: 重建 HSPICE run (.lis/.ms0/.ms1/logFile/.st0/.pa0) + dir_meta.txt
- hidden B doc/: 合成 NanoSpice run (PMOS ptn W1.6/L0.13/NF2, ss, Vd0.1, Vg sweep(0,1.2,0.02) 61点, -40C, LSF hfechds003, model G5_CIP_Model_D6_v1d1_Rev02, vtgm=0.62341, gm_max=9.84210e-5@0.71) — .log/.ms0/.ms1/.measure/.output/logFile
- 23 顶层键 JSON, 24 断言 (a-x), cross-input guard + A-leak guard + 真跑候选 + 确定性
- ref PASS 24/24 + 4 negs 全 FAIL ✓; k_check==k_rationale==24 ✓
- 首例: 仿真结果目录逐文件结构化讲解（对象是仿真输出结果目录，非输入 deck，与 SpiceDeckExplain/PwrNoiseDeckExplain 非重叠）
