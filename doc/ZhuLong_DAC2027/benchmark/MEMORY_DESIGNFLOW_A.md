WAITING: 0（shard A 轮 30：按上轮 deepread 计划合成 EDA-Eval-DesignFlow-QualibTimingFix-001 ✓ 并落 A.jsonl 第 47 行。trace k3g96（lorikx@10.129.40.209,mc=9,verification 域）SRAM IP Qualib Verilog↔TMLib timing-constraint 一致性修复：4 用户轮纯需求(规则②✓)，助手仅 read/search 出中文分析报告无 write→B 档 synthesized。交付=单脚本 qualib_timing_fix.py <verilog> <lib> <html_dir> <out_dir>，解析 xcheck HTML 诊断 Tmlib-Only/Verilog-Only 弧，在 specify 块为 Tmlib-Only setup/hold 弧补 $setuphold，产 fix_report.json + <model>_fixed.v。A 可见=CXN4HCSPS512X8(45 Tmlib-Only 弧,44 setup/hold→补 $setuphold,33→122)；B 隐藏=TSMC R2R028SGA_W64B16M4B1_BCSW(0 Tmlib-Only,2 Verilog-Only removal 弧 CKA↔CKB,108 $setuphold 不变)——跨输入守卫击破硬编 A 44 弧/盲目加全 pin。资产从 10.129.40.209 scp 到 .75(hfhds201) session，本地 NAS 与 .75/源机三向无网络互通，经 tar.gz+base64 过 MCP 单次回传 8 文件(498KB→69KB gzip→92KB b64)，md5 全验过。check.py 12 条 a-l 独立断言，本地自验 ref **PASS 12/12** + 5 negatives 全 FAIL(NEG_RC=0：fake_empty→a / fake_print_expected→f,g,h,i,k,l / fake_core_deleted→g,k,l / naive_add_all→i / naive_hardcode_a→i)，§4.9 三假全 FAIL ✓。中途发现 naive_add_all 旧版 pin 正则在 B 的 bus 声明上失配→B 不加→泄漏(i)，已改用 timing_constraint arcs 提 pin 修复→(i) 正确击破。🧾 断言: k_rationale=k_check=12 ≥8 ✓。台账 k3g96 deepread→case，covered 45→46，verification 6→7，DEBT 清零。下一轮=候选池勘探新一轮。）

## 顶部快照
- **PHASE**: shard A 合成轮 30（A jsonl 47 行/covered=46）· covered=46 / target=696 (mc≥100) = 6.6% · domain: digital:12 · eda_other:7 · pnr_signoff:18 · verification:7
- 🎯 通过率: 最近20条无新增已跑 case（pi/cline 实跑 pending）；B 档目标 20–30%
- 📊 trace 覆盖率：covered=46 / target=696 = 6.6%（mc≥100 数字工具 trace 耗尽；mc≥10 二次筛剩余多为模拟/Q&A/templated；下轮重新勘探候选池）
- 📦 体积：TASK≈17KB / MEMORY_A≈小
- DEBT: 0（k3g96 已合成 QualibTimingFix-001，DEBT 清零）；rewrite_queue 全 done

## 迁移说明
- 本 MEMORY 为 shard A 独立文件（首次创建，此前仅有 MEMORY_A_archive.md 存旧轮次流水）
- 旧轮次流水见 MEMORY_A_archive.md（轮 24-27 cline+hook 重跑等）
