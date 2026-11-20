# Deepread: 1794296966966_l4tfv (shushengz @ hfeg0plg93, mc183)

- session: `1794296966966_l4tfv.messages.json` (1.55MB, 127 msgs), waveform domain
- host IP: 10.129.8.225, path: `/home/shushengz/.cline/data/sessions/1794296966966_l4tfv/`

## User intent (3 user_input turns, verbatim)
- U#0: 「你可以帮我找一下LP6 的波形么」
- U#8: 「找一下DEJOA/DECQA/DEGNT 的仿真波形」
- U#76: 「想看DEJOA/DEGNT finesim 的数据读写波形，wck leveling 相关波形」 ← A-faithful 锚轮

## Agent tool chain
- list_allowed_files / read_files 浏览 `/rundata/dejoa/V0/simdir/{finesim,verilog,hspice}`、`/proj/degnt/V0_ARRAY/simdir`、`/rundata/degnt/V0_ARRAY/simdir`
- read compare.rep / irun.log / .vec 波形文本
- 最终产出一个 markdown 报告 (A#126)

## Key findings (real)
- DEGNT: finesim/hspice/verilog simdir 全空，无波形
- DEJOA finesim: `MatrixRun_Netlist_SpfBA_*/finesim.*.voltage_s/` 目录
  - 数据读写: `debugMode/dq00.vec..dq011.vec` + `rdqs0_t.vec`/`rdqs0_c.vec` (WaveView .vec 文本时间-电压表) + `shift_debug_EXP_signals.wdf` (WDF 二进制波形) + `compare.rep` (PASS 0 errors)
  - WCK leveling: run 名含 `WCKPSTL6d5`，多 PVT corner (SS/FF 0.88v -40c)
- DEJOA verilog: irun logs + ncsim.trn/.dsn (非 finesim，排除)
- DEJOA hspice: idd 测试 (非 finesim，排除)

## Synthesized-reframe rationale
真实目录树不可入沙盒（/rundata,/proj NFS 海量）。reframe 为清单 JSON:
`{"projects": {<proj>: {"tools": {<tool>: [run]}}}}`，每个 run = `{matrix,run,corner,files,compare_rep}`。
任务 = 写脚本扫清单找 finesim run，分类 wck_leveling(run 名含 WCKPSTL)/data_rw(有 dq*/rdqs*.vec)，解析 compare.rep PASS/FAIL+errors，收集信号名+ wdf 是否存在，输出 JSON inventory。
A=dejoa/degnt (5 finesim run)，hidden B=drjoa/drgnt (8 finesim run，命名/信号/corner 完全不相交)。

## Case
- case_id: EDA-Eval-DesignFlow-WaveformInvSearchProduce-001
- 15 assertions a-o, k_check=k_rationale=15, ref PASS + 3 neg FAIL + §4.9 a/b/c
- revival: B 台账 11-11 parked (file-search consultation, 旧规则 weak) → 11-15 reaudit retrieval/QA 合法 → D --force mark

## 旧规则为什么 parked
11-11 B 标 "find LP6 waveform file-search consultation"，旧规则把 file-search/retrieval Q&A 判为 weak/不可造。
新标准（2026-11-15 用户令）：retrieval/search/Q&A 是真实用户意图，全部恢复可造。本 case 即为该类 revival。
