WAITING: 0（shard A 轮 29：候选池勘探——summary.tsv/daily eda_trace 关键词字段不含 vcs/verdi/dc_shell/pt_shell（probe RE1 含但 top-8 kw 被模拟词挤掉），mc≥100 数字工具 trace 确认耗尽。降阈 mc≥10 + eda_trace marker 筛 innovus/synthesis，逐个 scp+深读首条 user msg：rc0jh=连virtuoso(模拟,parked)/48swh=中文输入法(非EDA,parked)/zggtc=templated"启动业务场景:时序分析"仅探索无产物(parked)/qvkte=templated"数字RTL设计"仅探索(parked)/k3g96=**SRAM Qualib Verilog↔TMLib timing-constraint 修复**真实多轮需求(verification 域)。选 k3g96 → claim → 深读完成：4 用户轮纯需求(规则②✓)，助手仅 read/search 出中文分析报告无 write→B 档 synthesized。已提取 ground truth：用户模型 CXN4HCSPS512X8 xcheck E=3/T=7，timing_constraint 44 条 Tmlib-Only 弧(CLK->A/BWEB/D/RA/RT/WA/WAT/WAV/WEB/WT/BYP/CLK，specify 块 line 3174 缺这些 $setuphold)；TSMC 参考 R2R028SGA xcheck E=2/T=7，2 条 Verilog-Only removal 弧(方向相反)。合成计划落 trace_deepreads/1789091963593_k3g96_qualib_timing.md（含远程 scp 路径 + 12 条断言草案 k=12≥8 + 隐藏 B=TSMC 跨输入守卫）。**本轮未落 jsonl**：时间预算不足以建 gold fixed-Verilog+check.py+negatives+自验，强闸门优先 🚫 不落低质 case。台账 mark deepread(k3g96)+parked 4 条薄候选。下一轮第一件事=按计划合成 EDA-Eval-DesignFlow-QualibTimingFix-001。🧾 断言: 本轮无新 case（deepread+handoff），k 闸门不适用）

## 顶部快照
- **PHASE**: shard A 候选勘探轮 29（A jsonl 仍 46 行/covered=45）· covered=45 / target=696 (mc≥100) = 6.5% · domain: digital:12 · eda_other:7 · pnr_signoff:18 · verification:6
- 🎯 通过率: 最近20条无新增已跑 case（pi/cline 实跑 pending）；B 档目标 20–30%
- 📊 trace 覆盖率：covered=45 / target=696 = 6.5%（mc≥100 数字工具 trace 耗尽；mc≥10 二次筛剩余多为模拟/Q&A/templated；下轮按 k3g96 deepread 计划合成）
- 📦 体积：TASK≈17KB / MEMORY_A≈小
- DEBT: 1 deepread 未合成（k3g96 → QualibTimingFix-001，下一轮首事）；rewrite_queue 全 done

## 迁移说明
- 本 MEMORY 为 shard A 独立文件（首次创建，此前仅有 MEMORY_A_archive.md 存旧轮次流水）
- 旧轮次流水见 MEMORY_A_archive.md（轮 24-27 cline+hook 重跑等）
