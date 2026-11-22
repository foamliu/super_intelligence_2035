# r1002 deep-read — 1795081266170_or2tj (SimRerunStatusAuditProduce-001)

## 选料

- scan: ssh_eda_search_20261122_172249 (r995 新扫, 沿用)
- A-pure filter (mc≥5, digA>ck/bk/dk, digA=verilog/rtl/systemverilog/synopsys/vcs/... 排除 netlist-only): 887 cands → fresh-diff vs 4-shard ledger (4130 sids): 98 fresh
- 排除 false-fresh (fjy8k=r993 ledger 缺记 / t61yg=r995 ledger 缺记) + intent-dup (3byhk=r990 dechaoc / bax7w=r969/r991 jkxu) + mixed-domain (oy9z9 waveview / qm71z cmos+schematic / ezpe5 netlist+cmos / unz6r cmos / dxxm5 drc 高 / 8y36x netlist+lvs / 2ajng aether+dbcreateinst GUI)
- top clean A-pure fresh: kjrai(t0002470 mc87 verilog:997 pure) / or2tj(ruisongs mc76 verilog:875 pure) / j3gn0(hao21l mc67 verilog:542 NEW) / ewijv(e0031668 mc95 rtl+synopsys)
- 选 `1795081266170_or2tj` (ruisongs@hfeg0pgn145, mc76, verilog:875 主导, ck=0 bk=0 dk=2 极纯 A-domain verification)
  - ruisongs 是高频用户但 or2tj session 未用过, 与历史 case 无 intent-dup (sim 农场 rerun 状态审计是新意图)
  - trace 524KB / 82 msgs / 4 干净 user 问 (act mode)
  - scp via `ssh e0031982@hfeg0pgn145 cat /home/ruisongs/.cline/data/sessions/<sid>/<sid>.messages.json` (e0031982 身份, 文件 group-readable rw-rw-r--)

## trace 要点

- U#0: 检测 run_odt / run_odtprac 下有哪些仿真在跑
- U#1: 和 odt.sh / odt_prac.sh 比较, 什么跑完/在跑/没真正跑完(log和波形没更新, 还是今天早上时间→视作失败)
- U#2: 和 1110net 路径比较确认真正没跑完的任务
- U#3: 直接帮我重跑这几个没跑完的任务

- agent 方法: 进程表检查(本机无 vsim/xrun, 仿真跑在 grid 共享存储) → 转文件系统扫描:
  - 检查每个任务目录的 xrun.log mtime + xcelium.dsn 波形 mtime + A_Summary.rpt 报告 mtime+内容
  - 两采样增长检测 (6s/45s/60s xrun.log size+mtime 增长 → running)
  - 读 odt.sh/odt_prac.sh 得期望 12 任务 (6 run_odt + 6 run_odtprac)
  - 分类: 波形停在早上 → stale_not_rerun(失败); 波形下午新写+完成标记+PASS → 跑完; 卡住+报告极小 → 没跑完
- 最终 M#65 分类表 (12 任务):
  - rerun_complete: run_odt/odt_eye.x4, odt_eye.x8, odt_1119.x4 + run_odtprac/odt_eye.x4, odt_eye.x8, odt_1119.x4 = 6
  - stale_not_rerun: run_odt/odt_1119.x8(波形 11:40 早上, Failed 26), run_odt/odt_ca_odt_toggle_1119.x8(波形 10:06 早上) = 2
  - rerun_failed: run_odtprac/odt_1119.x8(波形 18:41 下午, FAIL) = 1
  - incomplete: run_odt/odt_ca_odt_toggle_1119.x4(xmvlog 编译错, 报告 2590B), run_odtprac/odt_ca_odt_toggle_1119.x4(卡住 97min, 报告极小) = 2
  - (odt_measure_1118.x8 = 昨天旧目录, odt.sh 里已注释, 不算)
  - missing: run_odtprac/odt_ca_odt_toggle_1119.x8 (启动脚本列了但目录缺, 本 case fixture 补此分类)

## case 设计 (produce-task reframe)

- 把 agent 的「扫描活文件系统 + 两采样增长检测 running」抽象为「对 sim_farm tarball 快照的静态审计」
  (不依赖实时进程表/实时 mtime 增长, 而是用快照内文件 mtime + 内容做一次性分类)
- CID: EDA-Eval-DesignFlow-SimRerunStatusAuditProduce-001 (domain=verification)
- 交付件: audit_sim_rerun.py <sim_farm.tar.gz> <output.json>
- 分类规则 (忠实用户判据 "波形还是今天早上→没重跑完→失败"):
  1. missing: 任务目录不存在(启动脚本列了但快照里没有)
  2. stale_not_rerun: 波形缺失 OR 波形 mtime < rerun_cutoff (还停在早上)
  3. rerun_complete: 波形 mtime ≥ cutoff AND xrun.log 有完成标记 AND A_Summary.rpt VERDICT=PASS
  4. rerun_failed: 波形 mtime ≥ cutoff AND VERDICT=FAIL (重跑了但跑挂)
  5. incomplete: 波形 mtime ≥ cutoff 但无 PASS 无 FAIL (卡住/截断/编译错没产出报告)

## fixture 设计 (tarball + 保留 mtime)

- **关键**: harness 对 A 附件用 shutil.copy(仅文件) → 目录不可投递; 但 **tarball 是单个文件**, 可投递。
  脚本解压 tarball (tarfile.extractall 保留 mtime) → 文件 mtime 可用作判据 (tar 保留 mtime, 与 shutil.copy 重置 mtime 的目录附件不同)。
- A (可见): sim_farm_A.tar.gz (verilog.ddr5.drvqa.1116net, reference 2026-11-19 18:59, cutoff 12:00, odt.sh/odt_prac.sh 12 任务, 12 任务状态: complete=6 stale=2 failed=1 incomplete=2 missing=1, 忠实 trace)
- B (隐藏): sim_farm_B.tar.gz (verilog.ddr6.drvqa.1121net, reference 2026-11-21 20:30, cutoff 13:00, wr.sh/wr_prac.sh 12 任务, 状态: complete=4 stale=3 failed=2 incomplete=2 missing=1, **全 concrete 值异于 A**: wr vs odt / ddr6 vs ddr5 / 不同时间 / 不同失败数)
- A/B 任务名/项目/时间/verdict 全不相交 (反硬编码)

## check.py (17 断言, k=17 ≥ 8)

①zip 含 audit*.py ②py_compile ③B 运行 exit0+非空 output.json ④JSON 5 必需键 ⑤B total_tasks=12
⑥rerun_complete=4 ⑦rerun_failed=2 ⑧stale_not_rerun=3 ⑨incomplete=2 ⑩missing=1
⑪B reference_time='2026-11-21 20:30:00'(反硬编码 A 的 2026-11-19) ⑫run_wr/wr_ca_toggle_1121.x8_9200=rerun_failed(B特有) ⑬run_wrprac/wr_ca_toggle_1121.x8_9200=missing ⑭B 任务名不含 'odt_'(反 A 泄漏) ⑮stale 任务 waveform_mtime<cutoff(早上锚, 证真读 mtime) ⑯三次运行 JSON 一致(确定性) ⑰脚本含 def+import+tarfile/extractall+>300B(反空壳)

### 验证
- negative_selftest.py (in-place): ref PASS, 3 neg (empty/print_only/core_deleted) 全 FAIL ✓
- E2E (从 jsonl test 字段提取 check.py, 模拟 judge-temp 布局): ref PASS ✓
- §4.9 三假 (空壳/print-A值/core-deleted) 全 FAIL ✓

## ledger

- trace_ledger_A.tsv: 1795081266170_or2tj → status=case, case_id=EDA-Eval-DesignFlow-SimRerunStatusAuditProduce-001
- A.jsonl: 459 → 460 (verification +1)
- 覆盖率: 460/9542 ≈ 4.8%

## 选料注

- r1002 复用 r995 新扫 (9542 mc10 池), digA 过滤(排除 netlist-only 致 887 cands) × 4-shard ledger(4130 sids) 交叉得 98 fresh。
  排除 false-fresh(fjy8k r993 ledger 缺记 / t61yg r995 ledger 缺记, 提示 ledger 有少量未持久化条目) +
  intent-dup(3byhk/bax7w) + mixed-domain 后, or2tj(ruisongs mc76 verilog:875 pure, sim 农场 rerun 审计) 选中。
  r1001 的 21 fresh 中 ozvhc 已消费, 本轮独立重算 98 fresh 池(过滤更宽 digA)。
- pool 未枯竭 (98 fresh), stop-loss 不触发 (r1001/r1002 连续造题)。
- **发现**: r993 fjy8k / r995 t61yg 的 ledger 条目缺失 (case 已入 A.jsonl 但 trace_ledger_A.tsv 无对应行), 致 false-fresh。
  属历史 ledger 持久化 gap, 本轮在 fresh-diff 时人工排除, 不影响本轮造题正确性; 建议后续治理轮补记。
