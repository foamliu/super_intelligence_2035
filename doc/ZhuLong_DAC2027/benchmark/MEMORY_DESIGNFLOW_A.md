WAITING: 0（shard A 轮 33：合成 EDA-Eval-DesignFlow-ItfCompare-001 ✓ 并落 A.jsonl。trace 1792133398859_0t5o9（claire1l@hfeg0pkn004,mc=143,eda_other 域）StarRC LPE QA：用户轮 0 逐字「读取并分析对比这五份itf，将他们的共同点和差异点总结成表格」给出 5 份 CXMT TSI 工艺 ITF 路径——**clean 提需求，未给根因/方案 → 符 A 档规则②，归 A 档 faithful**。深读 636KB/98 msgs 定位：助手 read_files 并行读 5 份 ITF，逐块解析 TECHNOLOGY/DIELECTRIC/CONDUCTOR/VIA/TSV（TSV 跨多行 `{...}`）产共同点+差异点 markdown 表，用户后续追问 TSV/star_cmd/starrc_mapping/qrc.ccl。本 case 聚焦首轮流可判定子任务=通用 ITF 比较生成器。交付=submit.zip 含 compare_itf.py(通用 ITF 比较器,CLI `compare_itf.py <dir>`,产 comparison.json+comparison.md)+对可见 A 的 comparison.json/md。A 可见=5 份 TYP（TSI1.0 OL/NL Rev06 cxmttsi1.0、TSI2.0a staircase、TSI2.0b isc OL/NL；TSV RHO=0.02825/AREA=113/ILD1=0.7100|0.65|1.8800）；B 隐藏=5 份异构 ITF（TSI1.0 rev05 CMAX/CMIN corner、singleDTC typ/cmax、doubleDTC typ；TSV RHO=0.01695|0.02373|0.02034、b5 AREA=113.09、ILD1=0.639|0.781|0.079|0.0711|0.985、b3/b4 多 DTC_TP/DTC_BP 导体+CT_BP/CT_TP 通孔）——跨输入守卫击破硬编 A。check.py **14 条 a-n** 独立断言（结构键/TECHNOLOGY/GLOBAL_TEMP/TSV 7 参数/ILD1/M5.RPSQ/V1.RPV/commonalities≥5/differences≥5/DTC 层存在性/跨输入守卫禁 A 值），独立 oracle 解析器校验。本地自验 ref **PASS 14/14** + 4 negatives 全 FAIL（fake_empty→c / fake_print_expected→e / naive_hardcode_a→e / fake_delete_core→e）+ §4.9 三假(空壳/只print/删核心)全 FAIL ✓ + inline-exec(exec(test,ns) 无 __file__)路径 PASS 14/14。🧾 断言: k_rationale=k_check=14 ≥8 ✓。台账 0t5o9 claim→case，covered 48→49，eda_other 7→8，DEBT=0。候选池：mc≥100 shard-A 工具候选已耗尽，本轮用关键词信号(sig_re:primetime|synopsys|innovus|...)在 summary.tsv mc≥30 fresh 候选里选——多属 synopsys-keyword 噪声/analog-dominant；0t5o9 因 calibre+gdsii+primetime+netlist 重且 ITF 文件小可解析入选。下一轮=继续 mc≥30 fresh 候选选 verification/digital（覆盖仍偏低）。）

## 顶部快照
- **PHASE**: shard A 合成轮 33（A jsonl 50 行/covered=49）· covered=49 / target=696 (mc≥100) = 7.0% · domain: digital:12 · eda_other:8 · pnr_signoff:20 · verification:7
- 🎯 通过率: 最近20条无新增已跑 case（pi/cline 实跑 pending）；B 档目标 20–30%
- 📊 trace 覆盖率：covered=49 / target=696 = 7.0%（mc≥100 shard-A 工具候选耗尽；用关键词信号在 mc≥30 fresh 候选里选；每日扫描 eda_trace_2026110*.log 备用）
- 📦 体积：TASK≈17KB / MEMORY_A≈小
- DEBT: 0（0t5o9 已合成 ItfCompare-001）；rewrite_queue 全 done
- 🧾 断言: k_rationale=k_check=14 ≥8 ✓（今日 1/30 达标，存量断言清单进度仍 1/30）

## 迁移说明
- 本 MEMORY 为 shard A 独立文件（首次创建，此前仅有 MEMORY_A_archive.md 存旧轮次流水）
- 旧轮次流水见 MEMORY_A_archive.md（轮 24-27 cline+hook 重跑等）
