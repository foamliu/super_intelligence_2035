# Deep-read: lp4xw — FineSim si.inp deck analysis report

**Trace**: `1789524301977_lp4xw` · clarawang @ hfeg0pgn045 (10.129.32.80) · mc77
**Keywords**: netlist:279;analog:84;synopsys:3;pyaether:3;aether:3;transistor:2;hspice:1
**Size**: 949251 bytes · 235 msgs · 6 user turns · editor 多次写入(受 policy writableRoots 限制)

## 用户原话（逐字）
- U#0: `please`
- U#1: `please help me analysis this file si.inp` (附 si.inp 7.8KB)
- U#2: `use chinese`
- U#3: `please help me create a file analysis.txt for up detail answer`
- U#4: `I cannot understand analysis.txt,please write in Chinese`
- U#5: `buxing,nizhehaishiluanmade,nihuanchengyingwenshuru,xieru analysis.txt wenjian`

## A-faithful 选轮判定
U#1 + U#3 = 提出需求/表达目标（分析 si.inp + 产出 analysis.txt），未给根因/修复 → **A-faithful 合规**。

## cline 工具链
- list_allowed_files / get_agent_policy_status（policy engine enforcing，writableRoots=/ai_sandbox,/home）
- read_files（si.inp + finesim.elog + crc_alert_chk.rpt + compare.rep 等 sim 输出，但 tool_result 内容未在 messages.json 中捕获，只读到 derived 分析文本）
- editor（多次写入 /home/clarawang/analysis.txt，受 6000 字符限制分批 + insert_line + 中文 old_text 匹配失败 + 重复内容清理）
- run_commands 被禁（需 run_approved_command profile）

## si.inp 内容重建（从 assistant 分析 MSG[14]/[16]）
FineSim (PrimeSim Pro) deck, DSIM 自动生成, DRCPA project, DDR5 X8, SS corner, 0.94V, -40°C.
Regression name: `Compress018_TDQ13_4TDQOut_Act32_Wr32_Rd4_BL7_CL3_Exp_EccOn_WPst_0P5_tCH_50_BL16_4b8g_B19BJ_TM_SS_NODLLK.x8`
- 18 字段名解码（Compress018/TDQ13/4TDQOut/Act32/Wr32/Rd4/BL7/CL3/Exp/EccOn/WPst_0P5/tCH_50/BL16_4b8g/B19BJ/TM_SS/NODLLK/x8）
- 混合模式 spicehd(高精度) + prohd(快速)
- 10nm G5 模型库, SS/-40°C
- 10 关键参数 (pvcc/tdqs2dq/pvwlp/...)
- ZQ 校准 PU=100111 PD=101011
- 28 个被忽略子电路 + B19 高风险（不忽略）
- switch_NORMAL + switch_TSV（3D 堆叠）
- 7 阶段测试序列
- 14/16 信号匹配, TDQ0/TDQ3 失配

## A-faithful 可行性
**不可行**：(1) sim 输出文件（finesim.elog/compare.rep/crc_alert_chk.rpt）在 /rundata/drcpa_sim/ 不可附加；(2) 中文乱码反复修正（U#2/4/5）非可移植判定点；(3) analysis.txt 完整 16 章节依赖 sim 输出，非纯 deck 解析。

→ **B 级合成**：取可移植 facet = FineSim .inp deck 结构解析器 → parsed.json + analysis.txt（章节 1-9 + 11 + 12 从 deck 可导出，章节 10/13/15/16 省略或泛化）。L1 离线可验。

## 合成方案
- **Generator**: `gen_finesim_deck_report.py --deck <si.inp> --outdir <dir>`
- **Asset A**: si_A.inp（DRCPA DDR5 X8 SS 0.94V -40C, 20 fields, 10 params, zq pu=100111/pd=101011, 27 ignored, switch_NORMAL+switch_TSV, 7 phases, 14/16 match [TDQ0,TDQ3], crc_alert+accurate）
- **Hidden B**: si_B.inp（LPDDR4X X16 FF 1.3V -40C, 20 fields, 10 params, zq pu=011010/pd=110101, 20 ignored, switch_NORMAL only, 6 phases, 12/16 match [TDQ2,TDQ4], crc_alert+accurate）
- **Hidden B2**: si_B2.inp（GDDR6 X16 TT 0.92V 25C, 15 fields, 6 params, zq pu=101010/pd=010101, 6 ignored, switch_NORMAL only, 4 phases, 8/8 match [], 无 crc_alert/accurate）
- **反硬编码轴**: A/B/B2 project/corner/volt/temp/zq/ignored/switch/phases/fields 全不同；B2 无 crc_alert+accurate(少字段)；源码禁 A 字面量(Compress018/DRCPA/0.94/100111/switch_TSV/T_0.L.L0/B19BJ/NODLLK/10nm_G5 等)；A GT 出 B 范围；3x sha256 确定性
- **check 16 条件 a-p**: zip 防泄漏/py_compile/B-run exit0+2文件/必需键/source_tool==FineSim/regression_name==B.title/n_fields==20/options mixed_mode+spicehd+prohd+crc_alert/corner FF+volt 1.3+temp -40/n_params==10+参数名集/zq pu=011010+pd=110101/n_ignored==20+集匹配/switch==[NORMAL]/n_phases==6/反硬编码源码无A字面量+A-run regression_name Compress018/跨输入B2(n_fields15+TT+crc False+n_phases4)+3x确定性sha256
- **自验**: ref PASS 16/16 + 6 negatives 全 FAIL(empty→c/hardcode_a→f/print→c/ref_deleted→d/naive→h/drop_b2→p, 5 distinct first_fail) + §4.9 三假全 FAIL + k_rationale=k_check=16 ✓

## 教训
1. **read_files tool_result 在 messages.json 中未被捕获**（len=0），只能从 assistant 的 derived 分析文本重建 si.inp 内容；附件 attachment 也只存元数据不存内容。
2. **FineSim deck 结构解析是 analog_context L1 可验好范式**：注释/.title/.option/.lib/.temp/.volt/.param/.include/.vec/.meas/signal compare 是 16 条件天然丰富来源（字段数/选项/工艺/参数/ZQ/忽略/开关/相位/测量/比对/反硬编码/跨输入/确定性）。
3. **policy writableRoots + editor 6000 字符限制 + 中文 old_text 匹配失败** 是 cline 写大文件的常见痛点（trace 中 assistant 反复失败），合成 case 应避开这些（用 --outdir 一次性写文件，非 editor 增量）。
4. **B-grade synthesized 取 portable facet**：trace 的完整 16 章节报告依赖 sim 输出（不可附加），但 deck 结构解析章节（1-9）完全可从 si.inp 导出 → B 级合成只取 deck 解析 facet。
5. **L1/L2 比例债未还**：本条 L1（原希望 L2 还债，但 fresh 池 clean L2 produce trace 稀缺，peek 14 候选仅 rscalc RTEXT 适合 L2 但属 shard C physical_verify 域，不强抢）。下轮继续优先 L2/L3。
