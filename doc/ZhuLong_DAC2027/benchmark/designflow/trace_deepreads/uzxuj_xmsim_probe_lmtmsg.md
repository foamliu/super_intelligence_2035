# deepread: 1792494745130_uzxuj — xmsim probe.tcl LMTMSG 优化

- **session**: 1792494745130_uzxuj (alanji @ 10.129.8.232, mc9, netlist:87/verilog:26/analog:21)
- **agent**: lead (r772 教训复用：lead 标签本身 NOT buildability disqualifier；本案 read_files/editor tool_results **含完整文件内容**)
- **liveness**: 目录式 session（`1792494745130_uzxuj/` 含 `1792494745130_uzxuj.messages.json` 306883B + `1792494745130_uzxuj.json`），3-host 检查 ALIVE @ 10.129.8.232 (ssh-keyscan 加 known_hosts)
- **msgs**: 23 (agent=lead), user turn0 + turn2 是真实意图，其余为 tool_result

## 用户真实意图（两轮原话）

- **turn0 (msg[0])**: 粘贴 5 条 `xmsim: *W,LMTMSG: packed array at "TOP.Chip.I_A_Top.I_Ary8G_E.I_Array1GBK1.I_Ary_m512Meg_U.Imblq24.{BLb,BLbfar,I0.BLa,I0.BLb,I0.BLafar}" of 4416 elements exceeds limit of 4096 - not probed`，问「出现这个的原因是什么」→ analysis-Q&A（agent msg[1] 解释了：xmsim 默认 packed array probe 上限 4096，4416 位 bitline 超限被跳过；解决 `probe -create -packed 4416` 或更大）
- **turn2 (msg[2])**: 给出一份 probe.tcl 草稿（`database -open -shm ncsim -incsize 10G` / `probe -create TOP -database ncsim -shm -all -dynamic -tasks -function -depth all -packed 100000` / 各 RTT 探针 / 显式 `I_Ary8G_W` `I_Ary8G_E` -depth all / `run`），说「优化这个解决上面的问题」→ **produce-task: 优化 probe.tcl 消除 LMTMSG 警告**（这是本 case 选用的意图）

## agent 工具链

list_allowed_files → read_files (vsim/top.sv/cpprog_proc.tcl/probe.tcl) → editor (改写 probe.tcl) → read_files 验证 → 中文总结 (msg[22])

## A 资产（SUT 看到）

- `probe.tcl` — 原始 39 行配置（从 msg[18] editor tool_use old_text 重建）：`-incsize 5G`、全局 `probe -create TOP` **未带** `-packed`（默认 4096，致 4416 位 bitline 全部超限被跳过）+ A/B 通道 RTT/timing/dutconfig/lpddr6 探针 + `run`/`drivers -active`/`exit`
- `lmtmsg_warn.log` — 5 条 LMTMSG 警告原文（4416 > 4096，含完整层次路径）
- `user_brief.md` + `prompt.txt` — 忠实还原 turn0 + turn2 原话

## ground-truth（从 A 输入推导，非硬编码）

- required_min_packed = 4416（从 warn log `of (\d+) elements exceeds limit` 取 max）
- target arrays = `I_Ary8G_E`（warn log）+ `I_Ary8G_W`（user brief）→ 显式 -depth all probe
- -incsize target = 10G（user brief）
- A 信号库存 = 5 条 bitline（从 warn log `at "PATH" of N elements` 解析）

## B 隐藏（specificity oracle，SUT 不可见）

`hidden/signal_inventory_B.json` — 16Gb LPDDR5-X 变体：`I_Ary16G_N`/`I_Ary16G_S`、`Imblq32`、`BLn`/`BLnfar` 8192 elements、`-incsize 20G`、`DQMS_RTT_B` 等 RTT。check.py 从 B 推导 b_only_identifiers，断言 SUT 提交不含任一（证明针对 A 的 8Gb/4416 修复，非背题/泛化）

## 判分范式 + check.py（k=15）

produce-task-config-edit + specificity oracle + **probe-limit 模拟器（真跑 subprocess）**
- check.py 把 `probe_emulator.py` 写到 temp，subprocess 执行于（SUT 提交的 probe.tcl + A 信号库存），模拟 xmsim packed-array probe-limit 逻辑，输出 JSON {signals_probed, signals_lmtmsg, lmtmsg_signals}
- 真跑条件 ⑧：lmtmsg_signals == []（0 LMTMSG）；⑨：5/5 bitline 均被 probe
- 退化提交（空壳/只 print 期望/原始未改/抄 B/伪选项）全部致模拟器报 LMTMSG 或漏 specificity oracle → FAIL

## 自验

- ref submit.zip → CHECK PASS 15/15
- 5 negatives 全 FAIL（neg1 noop→①⑧ / neg2 print→⑤⑬⑧ / neg3 原始未改→⑧⑨②③ / neg4 抄B→⑩⑥⑦ / neg5 伪选项-packedx→⑬⑧）
- §4.9 a/b/c（noop/print-expected/core-deleted）= neg1/neg2/neg3 全 FAIL ✓
- embedded test 字段 JSON round-trip OK（dumps→loads 字符串等值）

## 落库

- A.jsonl 391→392；ledger uzxuj claimed→case(EDA-Eval-DesignFlow-ProbeTclLmtmsgFix-001)
- domain = verification（xmsim = Xcelium 仿真，LPDDR5 DRAM testbench probe 配置）

## 与已有 case 区分

本 case = xmsim probe.tcl 配置优化 produce-task（消除 packed-array LMTMSG 警告），与 r765-r770 的 STA flow case（CXDP STA run/中断/评估/spec audit/recipe 改）完全不同域（simulation vs STA signoff）。
