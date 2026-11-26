# Deepread: 1794472156729_uwq51 — LPDDR5 coverage-closure termit 修复

- **session**: `1794472156729_uwq51` (t0002470 @ hfeg0plg76, mc=441, domain=verification)
- **scan**: `ssh_eda_search_20261113_131349` (41408 rows / 6754 dedup sessions / mc10=3416)
- **model**: deepseek-v4-flash (desktop cline, 577 msgs, 3.3MB messages.json)

## 用户真实意图流（A 档，原话）

1. `/home/t0002470/workspace/lpddr5-coverage-closure.zip阅读这个skill` — 读 LPDDR5 覆盖率收敛 skill
2. `这是我的定向pattern .../directed_coverage.run 这是对应的仿真结果 .../log.1112.4` — 给 .run + sim log
3. `需要查看这些 pattern 的源码文件（.v 文件）`
4. `你可以自己去读取波形文件吗` → 给 `simvision.vcd`
5. `开始` — 触发修复
6. `你能否实现自己仿真，等待任务完成后自己查看覆盖率报告和波形自己debug`
7. `还算我来进行仿真吧，你目前更新了directed_coverage需要我进行仿真是吗` → 给 `log.1113.1`
8. `这才是对应波形路径 .../log.1113.1/directed_coverage.x16/simvision.vcd`
9. `帮我检查这轮仿真中新命中了哪些 legal_0cycle 覆盖率 bin`
10. `而是 cmdtcal.timingcal="auto" 在命令间插入 CAS_WS_FS 占用 1 tCK，这是 TB 本身的限制`
11. `如果你写了对应的定向pattern，你可以去波形里查看对应的序列中间是否新插入了CAS`
12. `T361 4 CAS_WS_WR→WRITE/WR32_AP` / `需要你去查看` / `你有写这些的定向pattern吗？`

## 根因（VCD 波形决定性证据）

`directed_coverage_patterns.v` / `patterns2.v` 里所有 READ 类操作（`Read`/`Read32`/`RDC`/`RFF`）的 `.termit` 参数 = 0（termination off）→ DUT 不驱动 DQ/RDQS（`TOP.Atop_dq = z` 全周期高阻）→ 读数据拿不到 → 124/199 pattern 失败 + legal_0cycle bin 空。WRITE 类 `.termit(0)` 是**正确**的。

## 真实 fix（fix_termit.py）

- READ_FAMILY = {Read, Read32, RDC, RFF} → `.termit(0)→(1)`
- WRITE_FAMILY = {Write, Write32, MaskWrite, WFF} → 保持 `.termit(0)`
- patterns.v: 17 处改（Read 8 + Read32 4 + RDC 3 + RFF 2），3 处 Write 保留
- patterns2.v: 5 处改（RDC 3 + RFF 2），15 处 Write 保留
- MRR.termit 在仿真中 0→1 @1097009ps（也属 READ，纳入 READ_FAMILY）

## 合成的 case

`EDA-Eval-DesignFlow-Lpddr5CovTermitFix-001`（verification, L1 离线 Python）
- 可见 A: `patterns_A.v`（read=10/write=8/fixed=9/read_already_1=1，含 WFF termit(1) 写陷阱）
- 隐藏 B: `patterns_B.v`（read=15/write=12/fixed=12/read_already_1=3，含 Read/RDC/MaskWrite/WFF 多重陷阱）
- check 20 条独立断言（k_check=k_rationale=20≥8）；3-seed 确定性；跨输入守卫击败 hardcoded_A
- 5 个 negative（naive_empty/print_only/hardcoded_A/blind_replace/core_removed）全 FAIL
- 自验：reference SELFTEST PASS（20/20）+ negative_selftest PASS（5/5 FAIL）

## 取舍

- 真 LPDDR5 irun 仿真不在 .75 sandbox（无 irun/xrun/vcs host），故做 L1 离线 Python（按 op family 改 .termit 值），与现有 A shard verification 案例风格一致。
- 未纳入 Phase 1 空 bin 提取 / Phase 5 飞书 diff（依赖内部 HTML 报告与飞书 API，无法自包含）；termit 修复是该 trace 最干净、最可自验的核心交付。
