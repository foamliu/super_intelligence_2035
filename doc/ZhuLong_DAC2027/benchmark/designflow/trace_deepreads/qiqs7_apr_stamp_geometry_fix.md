# deepread: 1793706326923_qiqs7 — Innovus APR stamp-mechanism + PM-band geometry fix (L3)

## trace_source
- user: alan3zh · host: hfeg0pkn001 · session: 1793706326923_qiqs7
- match_count 470 (innovus 470 / netlist 245 / synthesis 40 / dbGet 650) · 82 msgs · 936KB
- domain: pnr_signoff (shard A)
- daily log source: eda_trace_20261103.log + eda_trace_20261104.log (fresh 11/03 session; NOT in 10/28 summary.tsv)
- workspace: `/home/alan3zh/workspace/test_chip/test_chip_v1/apr/` (e0031982 ssh hfeg0pkn001 可读，非 owner-only)
- 真实 fixed 文件已落地并重跑成功：`.inv_fp_hl22_porting_test_chip_v1.stamp` + `.inv_route_hl22_porting_test_chip_v1.stamp` 存在（success stamps）→ verified-accepted L3 build

## A档规则②判定
- 用户轮 1（首个真实输入）逐字：「此次报错>>> innovus floorplan FAILED -- see /home/alan3zh/workspace/test_chip/test_chip_v1/apr/logs/inv_fp.log，而且无route的log」
- = debug 报错（根因-指向型，指出 fp FAILED + 无 route log 这一症状）→ **A档规则②禁用** → 取 **B档 synthesized**
- 用户轮 27 = `/continue`（meta）。

## 真实意图与助手交付（trace 末态接受）
诊断 + 修复 Innovus APR flow 的 3 个 bug：
1. **make 误判 fp FAILED**（日志可见性竞态）：LSF `-o` 日志异步 flush（实测 9s）+ NFS 客户端目录属性缓存（实测 >30s，`make clean` 删 logs/ 后 30s grep 窗口拿到过期 ENOENT 视图）→ 日志里明明有 `INNOVUS FP DONE`、LSF Job 成功，make 却判 FAILED。
2. **PM band 被跳过**（行几何查询失败）：`dbGet top.fPlan.rows.origin_y` / `top.fPlan.coreBox` 在该 Innovus 版本拼写不被识别（IMPDBTCL-204/206 on `cellMaster`/`masterCell`）→ `WARN: PM band: cannot query row/core geometry -- skipping` → sroute IMPSR-1253、VDD_PM 0 leaf pin。
3. **placeInstance 探测**：电池扩展加 `placeInst` 拼写复用。

助手用 editor 改 `innovus_fp.tcl`（10 处）+ `innovus_pr.tcl`（8 处）+ `Makefile`（6 处）+ `README.md`（2 处），跑 3 个校验脚本（tcl 括号平衡 / make recipe / apr setup validate）+ `tclsh info complete` 全 COMPLETE-OK + make -n OK，全部通过。

## 真实 fixed 文件关键语义（已 ssh 读出，作 reference gold 依据）
### stamp_write proc（fp.tcl 19–52，pr.tcl 同形）
```tcl
proc stamp_write {suffix} {
    if {[info exists ::env(INV_FP_STAMP)] && $::env(INV_FP_STAMP) ne ""} {
        if {[catch {close [open "$::env(INV_FP_STAMP)$suffix" w]} err]} {
            puts "WARN: cannot write stamp $::env(INV_FP_STAMP)$suffix : $err"
        }
    }
}
```
- 5 处 fp FAILED 出口 + 7 处 pr FAILED 出口补 `stamp_write .fail`（在 `puts "INNOVUS ... FAILED"; exit` 前）
- DONE 横幅前 `stamp_write ""`（success stamp）

### 几何块重写（fp.tcl 260–360+）
- dbGet **电池**：row 路径 `top.fPlan.rows` / `top.rows` 两选；属性 `origin_y`/`y` → 兜底 `origin`{x y} pair → `bbox`{x1 y1 x2 y2}；orientation `orient`/`orientation`
- core box：`coreBox.lx/ly/ux/uy` scalar → `coreBox` 4-list
- **DBU→µm 归一化**：`dbGet head.dbUperUU`（默认 2000.0）；坐标 >500 判为 DBU → `/$_dbu_per_um`
- **LEF SITE 兜底**（确定性派生）：floorPlan 参数 + LEF SIZE/SYMMETRY
- 方向逃生阀：`INV_PM_ROW0_ORIENT` env；方向查不到 → 整个 band 安全跳过（避免 VDD_PM↔VSS short）

### Makefile retry loop（fixed，140–200）
```makefile
S1 := $(CURDIR)/.inv_fp_$(TOP).stamp
TSTAMP1 := $(WORK_DIR)/.inv_fp_$(TOP).tclstamp
INV_FP_STAMP := $(TSTAMP1)
# export ... INV_FP_STAMP INV_PR_STAMP
$(S1): innovus_fp.tcl ...
	@rm -f $(S1) $(TSTAMP1) $(TSTAMP1).fail
	@cd $(WORK_DIR) && $(BSUB) ... -o $(LOG1) "..."
	@for i in 1 2 ... 60; do \
	  if [ -f "$(TSTAMP1)" ]; then touch $@ && echo "done (tcl stamp)"; exit 0; fi; \
	  if grep -q "INNOVUS FP DONE" $(LOG1) 2>/dev/null; then touch $@; exit 0; fi; \
	  if [ -f "$(TSTAMP1).fail" ] || grep -q "INNOVUS FP FAILED" $(LOG1) 2>/dev/null; then break; fi; \
	  touch $(WORK_DIR)/.nfsprobe $(LOG_DIR)/.nfsprobe 2>/dev/null; \
	  rm -f $(WORK_DIR)/.nfsprobe $(LOG_DIR)/.nfsprobe 2>/dev/null; \
	  sleep 2; \
	done; \
	echo "FAILED"; exit 1
```
- 60×2s = **120s 窗口**（覆盖 60s NFS acdirmax 上限）
- **stamp-priority**：先查 Tcl stamp `$(TSTAMP1)`，log-grep 后备
- **NFS refresh**：每轮 `touch+rm .nfsprobe` 强制目录属性重验
- `.fail` stamp + grep FAILED break

## B档合成计划（下一轮合成）
**case_id**: EDA-Eval-DesignFlow-AprStampFix-001（pnr_signoff，L3 multi-file fix + regression verify）
**与已有 APR case 区分**：
- AprLogAudit-001 (z5wxj, r40) = 审计 Innovus 运行**日志**（post-run，产 report）
- AprSetupAudit-001 (97tse, r41) = 审计 Innovus setup **输入文件**（pre-flight，产 report）
- AprStampFix-001 (qiqs7, 本轮) = **修复** Innovus APR flow 3 bug（产 fixed Tcl/Makefile + 通用 patcher）—— verb 全异

**交付** = submit.zip{fix_apr_stamp.py（通用 patcher，CLI `<bundle_root>[-o out_dir]`）+ fixed/innovus_fp.tcl + fixed/innovus_pr.tcl + fixed/Makefile}
- patcher 必须**自适应**：从 bundle 读 TOP/PM-cell/SITE（test_chip_power.md 或 Tcl `set TOP`），对 buggy Tcl/Makefile 做程序化 patch（加 stamp_write proc + FAILED 出口 stamp + 几何块重写 + Makefile retry loop 重写），输出引用 bundle 自身 TOP/cell 的 fixed 文件。

**A 可见 bundle**（assets/<id>/，minimal 60-line Tcl + 50-line Makefile + test_chip_power.md，buggy 语义忠实复刻 qiqs7 真 bug）：
- `innovus_fp.tcl`（buggy）：env_or + `set TOP` + required-file FAILED 出口（无 stamp）+ buggy 几何块（仅 `dbGet top.fPlan.rows.origin_y`，无电池无 LEF fallback，`cannot query row/core geometry -- skipping`）+ DONE banner（无 stamp）
- `innovus_pr.tcl`（buggy）：FAILED 出口（无 stamp）+ DONE banner（无 stamp）
- `Makefile`（buggy）：`S1=$(CURDIR)/.inv_fp_$(TOP).stamp` + buggy retry loop（15×2s=30s，仅 grep log，无 stamp check，无 NFS refresh）
- `test_chip_power.md`：TOP=hl22_porting_test_chip_v1 / PM cell=INVD8BWP40P140LVT / SITE=coreSite

**B 隐藏**（assets/<id>/hidden/，结构全异）：TOP=hl22_porting_test_chip_v2 / PM cell=INVD16BWP40P140LVT / SITE=coreSite_v2 / log dir=run_logs/ → cross-input guard 击破硬编 A

**check.py（≥8 条，L2 真跑 tclsh + make -n + subprocess）** 候选 15 条 a–o：
- a zip 含 fix_apr_stamp.py + fixed/{fp.tcl, pr.tcl, Makefile}
- b py_compile fix_apr_stamp.py
- c subprocess 跑 patcher 于 A bundle → exit0 + 产 fixed 文件
- d `tclsh` `info complete [read fixed/innovus_fp.tcl]` → COMPLETE-OK（真跑 tclsh）
- e `tclsh info complete` on fixed/innovus_pr.tcl → COMPLETE-OK
- f fixed/innovus_fp.tcl 含 `proc stamp_write` 定义 + ≥5 `stamp_write .fail` 调用
- g fixed/innovus_fp.tcl 几何块含 dbGet 电池（`top.fPlan.rows` + `top.rows` 两路径）+ LEF SITE fallback（regex SITE/SYMMETRY/lefGet）+ DBU 归一化（`dbUperUU` / `/$_dbu_per_um`）
- h fixed/innovus_pr.tcl 含 stamp_write proc + ≥7 `stamp_write .fail`
- i fixed/Makefile retry loop：stamp-priority（`TSTAMP1` 先查）+ 窗口≥120s（60×2 或 sleep ≥120）+ NFS refresh（`touch`+`rm` `.nfsprobe`）+ `.fail` break
- j `make -n` dry-run on fixed/Makefile（stub vars）→ 无语法错（真跑 make）
- k cross-input guard：跑 patcher 于 hidden B → exit0；fixed B 的 innovus_fp.tcl 引用 B 的 TOP（hl22_porting_test_chip_v2），**不**含 A 的 TOP
- l cross-input guard：fixed B 的 Makefile 引用 B 的 stamp/log 路径（不 含 A 的 `.inv_fp_hl22_porting_test_chip_v1`）
- m anti-hardcode：fixed A 的 Tcl **不**含 B 的 TOP（反之亦然）—— 击破 copy-paste
- n fixed/innovus_fp.tcl DONE banner 处有 `stamp_write`（success stamp）
- o patcher 自适应：fixed A 的几何块引用 A 的 SITE/cell，fixed B 的引用 B 的 SITE/cell（两份不同）

**negatives**（reference/<id>/negative/）：
- fake_empty（空 zip）→ a
- fake_print_expected（硬编 A 的 fixed 文件，不读 bundle）→ k（B run 仍输出 A 的 TOP）
- fake_core_deleted（patcher 加 stamp 但不重写几何块）→ g
- naive_hardcode_a（直接 cat A 的 fixed 文件）→ k
- naive_no_stamp（patcher 只重写几何块不加 stamp）→ f

**自验**：ref PASS 15/15 + negatives 全 FAIL + §4.9(a)(b)(c) 三假全 FAIL。

**判分环境**：纯 stdlib + tclsh + make（.75 均有），无需 Innovus license。L2 = 真跑 tclsh info complete + make -n + subprocess 于 A+B。

## 选此 trace 的理由
- fresh 11/03 真实 pnr build（10/28 summary.tsv 已 stale，daily log 是唯一新鲜源；shard-A 数字候选在 summary.tsv 已耗尽，本轮改扫 daily eda_trace log）
- verified-accepted（success stamps 已落地，flow 重跑通过）→ 金标准可靠
- L3（多文件 fix + 3 校验脚本回归 + tclsh info complete）— 符 §5「新建 case 只做 L2/L3」
- 与 2 条已有 APR case verb 互斥（audit-log / audit-setup / fix-flow）

## blocker 性质 / 下一轮
- 本轮 genuine scoping blocker：qiqs7 是 viable L3 但合成需自适应 Tcl/Makefile patcher + 15 条 check + 5 negatives，工作量超本轮剩余预算；强写易过不了断言闸门 → rewrite_queue（更差）。故本轮 deepread + park，下一轮第一件事合成 AprStampFix-001。
- daily_eda_scan.sh step3 awk 缺数字工具词（dc_shell/primetime/pt_shell/genus/tempus/icc2/formality/vcs/verdi/verilint/design_compiler）→ 纯数字 session 在 daily log 被丢弃。**agent 不能写 .75（红线 #4），需运维修**：在 daily_eda_scan.sh 的 `e=(t ~ /virtuoso|innovus|calibre|spectre|hspice|synthesis/)` 正则加 `|dc_shell|primetime|pt_shell|genus|tempus|icc2|formality|vcs|verdi|verilint|design_compiler`。修后 11/05 起 daily log 可捞纯数字 build session。
- shard-A summary.tsv mc≥100 数字候选已耗尽（11 条全 analog-dominant，靠 innovus 噪声命中）；daily log 是唯一新鲜源，其中 innovus-heavy pnr 候选（qiqs7/fbuip/ggmdz）是当前可做 pool。
