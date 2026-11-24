# fm8au — TVF rule-deck variable usage audit (physical_verify)

- **session**: `1794898673878_fm8au` · ellawu @ hfeg0plg49 (10.129.8.86) · 48 msgs · mc=32 (drc:1192; calibre:71; gdsii:10) · pure physical_verify
- **attachments**: `G5_AA_PG_dummy_fill_for_Logic.rule` (2234L, G5 Logic block auto AA/PG dummy fill DRC deck) + `G5_CIP_AA_PG_dummy_fill_for_Stdcel.rule` (972L, G5 Stdcel companion deck)
- **真实任务**: ellawu 问「什么情况下底层生成的dummy会在顶层生成dummy的时候跑上来」→ 助手读 deck 解释 dummy 生成层级与变量传递(底层 AT4 dummy / 顶层 PG dummy 的 spacing 变量如何被引用); 同会话追问 `$AT4_PG_Dummy_Space` 和 `$AT4_Dummy2_PGLine_Space` 两个 spacing 变量在 deck 里的引用情况(每处 active 还是注释)。
- **reframe**: A 档 gold=free-text 中文解释, 无 ≥8 独立硬断言牙 → 抽离「逐行扫描 TVF deck + 定位变量引用 + active/注释分类 + usage_type 分类」为纯 stdlib 变量 usage 审计器 analyze_var_usage.py。
- **case**: EDA-Eval-DesignFlow-TvfVarUsageAudit-001 · k=14 · visible A=G5 Logic deck 前 300L(var AT4_PG_Dummy_Space def L224=0.078) · hidden B=G5 Stdcel deck 前 290L(var AT4_Dummy2_PGLine_Space def L144=0.156, 8/7/1) · hidden B2=合成 6L(var MY_VAR def L2=0.123, 5/3/2) 反硬编。
- **关键调试**: .75 SSH port 22 从本环境被防火墙挡 → 改用 eda_flow MCP(open_session/run_commands/write_file/read_file) 访问 .75 文件; write_file content_base64 会损坏内容只用 plain content。
- **状态**: r1055 已收口, ledger C fm8au marked case, covered 675→676/4529, cases/C 623→624。
