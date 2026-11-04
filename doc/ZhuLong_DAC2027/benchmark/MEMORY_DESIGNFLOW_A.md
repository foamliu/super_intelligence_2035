WAITING: 0（shard A 轮 60：**完成 VpsRegrErrorEngineer-001 落地**（verification, L2, A档 faithful）—— 发现该 case 已由轮 59 后的先前会话完整合成并提交 assets/reference（assets: verilogrun_A/*.sh + rtl_A/ddr5_* + libs_A/simlib_base.{sv,svp} + hidden/; reference: engineer.py + engineer_ref.py + check.py(12 条件 a-l) + negative/），但 A.jsonl 条目未提交、台账 le1s7 未 mark `case`。本轮**修正性收尾**：恢复被本轮误覆盖的 committed check.py/engineer_ref.py/naive_no_mod.py（git checkout HEAD），提交轮59遗留的 A.jsonl 第 68 行条目（task_id=VpsRegrErrorEngineer-001, 12 条断言, k_check=12 一致），台账 `mark --status case --case-id EDA-Eval-DesignFlow-VpsRegrErrorEngineer-001`。**DEBT:0 清零**。本轮另在 .75 vcs 烟测实证 L2 机制：vcs -full64 修复 libgcc_s 链接（默认 32-bit 导致 rmapats.so 链接失败）；svp 换用 → [UPIMI-E] Undefined port elaboration error (exit 255) = error1；strip -noerror 120343 → runtime $fatal "UVS_ERR_120343" (sim log) = error2；+define+NOERROR_120343 抑制 = pass。$fatal 在 vcs R-2020.12 sim 退出码仍 0 → engineer.py 按 log 内容("Fatal"/"UVS_ERR_"/"PASS_CASE_DONE")而非 exit code 分类。**教训**：选 trace 前先 `grep <case_id> A.jsonl` + `git log -- <case_id 路径>` 查重，避免重复合成（本轮前半程重复构建才发现）。covered=67（+1 verification）。
（轮 50–57 已归档至 `MEMORY_A_archive.md` 归档批次 56（2026-11-04）；轮 43–49 见归档批次 55；轮 33–42 见归档批次 50。）

## 顶部快照
- **PHASE**: shard A 轮 60（VpsRegrErrorEngineer-001 落地完成, DEBT=0）· covered=67 / target=1369 (mc≥30) = 4.9% · domain: digital:21 · eda_other:13 · pnr_signoff:21 · verification:12
- 🎯 通过率: 最近20条无新增已跑 case（pi/cline 实跑 pending）；B 档目标 20–30%
- 📊 trace 覆盖率：covered=66 / target=1369 = 4.8%（summary.tsv 10/28 stale；daily eda_trace_2026110{1-4}.log 45125 行已扫；纯数字工具 marker 0 命中=daily_eda_scan.sh step3 awk 缺数字工具词；所有 innovus-heavy 候选已入台账；fresh 仅剩 calibre/virtuoso-dominant 或 VPS netlist-heavy）
- 📦 体积：TASK≈17KB / MEMORY_A≈15KB
- DEBT: 0（le1s7 → VpsRegrErrorEngineer-001 已落地并 mark case）；BLOCKER: ① fresh 纯数字候选稀缺——daily log tool markers 缺 vcs/verdi/dc_shell/formality/primethe（**daily_eda_scan.sh step3 awk 需运维修加数字工具词**），summary.tsv tools 列亦无；所有 innovus-heavy 已 case；② **沙盒工具清单已查实**：.75 HAS vcs(/apps/synopsys/SRB/vcs/R-2020.12, 需 -full64 否则 libgcc_s 32-bit 链接失败)+vsim(/proj/shdc/sim/bin, 实为 DDR 专用 wrapper 非 UniVista)+dc_shell+primetime+pt_shell，MISSING verdi/formality/verilint/uvs/vps——⇒ verification L2 sim 可做（vcs -full64 烟测通过：svp-swap→UPIMI-E error1, strip-noerror→$fatal error2, $fatal sim exit 0 需按 log 分类）；③ 真实设计文件常 permission-denied → 多走 B 档；④ cline v3 session 路径=/home/<u>/.cline/data/sessions/<sid>/<sid>.messages.json；⑤ /nasdata 不在 .75 上挂载、本机不可直连 .75（port22 timeout）→ 文件过坝只能走 eda_flow write_file/base64，大文件传输成本高
- 🧾 断言: 今日 1/1 达标（VpsRegrErrorEngineer-001：k_rationale=12=k_check=12 ✓，存量断言清单进度 19/30）

## 迁移说明
- 轮 33-42 已归档至 `MEMORY_A_archive.md`（归档批次 50，2026-11-04）。
- 轮 43-49 已归档至 `MEMORY_A_archive.md`（归档批次 55，2026-11-04）。
- 轮 50-57 已归档至 `MEMORY_A_archive.md`（归档批次 56，2026-11-04）。
- 本 MEMORY 为 shard A 独立文件；旧轮次流水见 MEMORY_A_archive.md（轮 24-27 cline+hook 重跑等）

## 下一轮第一件事（DEBT=0）
DEBT 已清零。下轮按 `python3 designflow/trace_ledger.py --shard A next --n 5` 选新 trace → claim → 深读 → 合成新 case。**选料前必查重**：`grep <候选 case_id> EDA-Eval-DesignFlow_A.jsonl` + `git log -- benchmarks/EDA-Eval-DesignFlow/assets/<候选 case_id 路径>`，避免重复合成（轮60 教训）。优先覆盖 domain 尚无 case 的纯数字/verification 候选。
