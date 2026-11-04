WAITING: 0（shard A 轮 60：**完成 VpsRegrErrorEngineer-001 落地**（verification, L2, A档 faithful）—— 发现该 case 已由轮 59 后的先前会话完整合成并提交 assets/reference（assets: verilogrun_A/*.sh + rtl_A/ddr5_* + libs_A/simlib_base.{sv,svp} + hidden/; reference: engineer.py + engineer_ref.py + check.py(12 条件 a-l) + negative/），但 A.jsonl 条目未提交、台账 le1s7 未 mark `case`。**修正性收尾（两段）**：轮60首段误以为 `git checkout HEAD` 可恢复 reference，实则 committed check.py 为**陈旧版** cf92306c（硬编 `case_ddr5_drcoa_*` 旧名，与现 assets `ddr5_addr_dec` 等不符，反硬编 k 条件亦失效），且该陈旧版被写入 A.jsonl 第 68 行 `test` 字段。轮60次段（本会话）**实测纠偏**：从 .75 sandbox（session default_20261104-runA60-syn_VpsRegrErrorEngineer-001_0，仍存活）拉回**经 NEG_SELFTEST_OK 实证**的 check.py(md5 c752ef24, 12 条件 a-l, `_fail` 抛断言)/engineer_ref.py(79ca0dc5)/naive_no_mod.py(eb137916)，覆盖本地+commit e614782，A.jsonl 第 68 行 `test` 重写为 c752ef24 源；push EDA-Flow-Bench master（ls-remote HEAD=e614782）。台账 le1s7 已 mark `case`（covered=67, verification:12）。**DEBT:0 清零**。**实证 L2 机制**（vcs R-2020.12, /apps/synopsys/SRB/vcs/R-2020.12/bin/vcs，无需 -full64）：swap_svp（好库 simlib_base.sv → 损坏备份 simlib_base.svp，module header 缺 `;`）→ vcs `Error-[SE] Syntax error` exit 255 = error1；strip_noerror（移除 `+define+SUPPRESS_ERR120343`，RTL `\`else` 分支引用未定义 `simlib_missing_module_zzz`）→ vcs `Error-[URMI] Unresolved modules` exit 255 = error2；好库+define → exit 0 = pass。engineer.py `classify()` 扫描字面 `Error-[`...`]` 标签 + exit code 分类（非 log 内容关键字）。NEG_SELFTEST_OK：REF accept(rc==0) + 5 negative 全 reject(rc!=0)，含 §4.9 三假(fake_empty/fake_print_expected/fake_core_deleted)，43s。**教训**：选 trace 前先 `grep <case_id> A.jsonl` + `git log -- <case_id 路径>` 查重，避免重复合成（本轮前半程重复构建才发现）。covered=67（+1 verification）。
（轮 50–57 已归档至 `MEMORY_A_archive.md` 归档批次 56（2026-11-04）；轮 43–49 见归档批次 55；轮 33–42 见归档批次 50。）

## 顶部快照
- **PHASE**: shard A 轮 60（VpsRegrErrorEngineer-001 落地+纠偏完成, DEBT=0, commit e614782）· covered=67 / target=1369 (mc≥30) = 4.9% · domain: digital:21 · eda_other:13 · pnr_signoff:21 · verification:12
- 🎯 通过率: 最近20条无新增已跑 case（pi/cline 实跑 pending）；B 档目标 20–30%
- 📊 trace 覆盖率：covered=66 / target=1369 = 4.8%（summary.tsv 10/28 stale；daily eda_trace_2026110{1-4}.log 45125 行已扫；纯数字工具 marker 0 命中=daily_eda_scan.sh step3 awk 缺数字工具词；所有 innovus-heavy 候选已入台账；fresh 仅剩 calibre/virtuoso-dominant 或 VPS netlist-heavy）
- 📦 体积：TASK≈17KB / MEMORY_A≈15KB
- DEBT: 0（le1s7 → VpsRegrErrorEngineer-001 已落地并 mark case）；BLOCKER: ① fresh 纯数字候选稀缺——daily log tool markers 缺 vcs/verdi/dc_shell/formality/primethe（**daily_eda_scan.sh step3 awk 需运维修加数字工具词**），summary.tsv tools 列亦无；所有 innovus-heavy 已 case；② **沙盒工具清单已查实**：.75 HAS vcs(/apps/synopsys/SRB/vcs/R-2020.12/bin/vcs, 直接可用)+vsim(/proj/shdc/sim/bin, 实为 DDR 专用 wrapper 非 UniVista)+dc_shell+primetime+pt_shell，MISSING verdi/formality/verilint/uvs/vps——⇒ verification L2 sim 可做（vcs 烟测实证：swap_svp→`Error-[SE]` exit255=error1, strip_noerror→`Error-[URMI]` exit255=error2, 好库+define→exit0=pass；NEG_SELFTEST_OK 43s）；③ 真实设计文件常 permission-denied → 多走 B 档；④ cline v3 session 路径=/home/<u>/.cline/data/sessions/<sid>/<sid>.messages.json；⑤ /nasdata 不在 .75 上挂载、本机不可直连 .75（port22 timeout）→ 文件过坝只能走 eda_flow write_file/base64，大文件传输成本高
- 🧾 断言: 今日 1/1 达标（VpsRegrErrorEngineer-001：k_rationale=12=k_check=12 ✓，存量断言清单进度 19/30）

## 迁移说明
- 轮 33-42 已归档至 `MEMORY_A_archive.md`（归档批次 50，2026-11-04）。
- 轮 43-49 已归档至 `MEMORY_A_archive.md`（归档批次 55，2026-11-04）。
- 轮 50-57 已归档至 `MEMORY_A_archive.md`（归档批次 56，2026-11-04）。
- 本 MEMORY 为 shard A 独立文件；旧轮次流水见 MEMORY_A_archive.md（轮 24-27 cline+hook 重跑等）

## 下一轮第一件事（DEBT=0）
DEBT 已清零。下轮按 `python3 designflow/trace_ledger.py --shard A next --n 5` 选新 trace → claim → 深读 → 合成新 case。**选料前必查重**：`grep <候选 case_id> EDA-Eval-DesignFlow_A.jsonl` + `git log -- benchmarks/EDA-Eval-DesignFlow/assets/<候选 case_id 路径>`，避免重复合成（轮60 教训）。优先覆盖 domain 尚无 case 的纯数字/verification 候选。
