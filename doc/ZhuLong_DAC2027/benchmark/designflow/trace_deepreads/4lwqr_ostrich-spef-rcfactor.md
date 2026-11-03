# trace_deepread: 4lwqr — ostrich SPEF RC Factor Tcl (pnr_signoff, A-faithful)

- **session**: 1793088659672_4lwqr (e0047472 @ hfeg0pkn004 / 10.129.2.13)
- **source**: fresh scan `/home/t0002965/log/eda_trace_20261103.log` (10-28 summary.tsv stale; mc≥100 shard-A pool exhausted; mc≥30 + innovus-dominant on fresh 11-03 scan → 4lwqr top with 417 innovus, 303 msgs)
- **N_msgs**: 303 (rich; first ~83 msgs are NERDTree/vim env-debug — IGNORE for case; U#84 = the design-flow task)
- **domain**: pnr_signoff (Cadence Ostrich = SPEF compare / RC calibration; Innovus setRCFactor / create_rc_corner apply)
- **A-faithful prompt** = U#84 逐字原文: `写一个用ostrich比较两个spef 生成RC Factor的tcl脚本`
  - 用户给**目标**（写脚本做 SPEF 比较 + RC Factor 生成），未给根因/修复 → 规则②不命中 → **A-faithful ✓**
  - U#210: `将你最后比较spef的tcl 脚本保存在我的home目录下命名为 ostrich.tcl` = 交付确认（gold = 助手最终保存的 ostrich.tcl = ostrich_rc_factor.tcl）
- **gold** = 助手 A#85–A#208 真实工具链产物:
  1. find_ostrich.sh 探测 ostrich 在 Innovus bin 下
  2. 通过 stdin 重定向 `ostrich -64only < script.tcl` 执行 TCL；`info commands` 枚举命令集
  3. 关键命令语法: `read_spef -filename <f> -setname <s>` / `build_plot -plotname <p> -golden <g> -target <t> -datatype <d> -min_data <m> -max_perc_dev <x>` / `get_plot_statistics -plotname <p> -datatype <d>` / `export_sorted_list -plotname <p> -datatype <d> -sort_by perc_err -sort_dir decreasing -use_netnames [-cap_unit <u>|-sum_res] -filename <f>` / `get_scale_factor -plotname <p> -datatype <d> [-recommended|-applied]`
  4. 写 ostrich_rc_factor.tcl（read 2 SPEF → loop tcap/res/xcap → build_plot → stats → export → get_scale_factor → summary 含 Innovus setRCFactor/create_rc_corner apply hint）
  5. 跑通发现 bug: ①测试 SPEF 3 net 共用 driver `drv:Z` → Ostrich 按 driver pin 名匹配 → 0 match（真实 SPEF 每 net 唯一 driver）②build_plot 失败不抛 TCL 异常 → 加 if_plot_exists 检查
  6. 修 SPEF（每 net 唯一 driver+sink）+ 脚本健壮性 → 跑通 → 保存 ostrich.tcl

## 交付件 (next round submit.zip)
- `ostrich_rc_factor.tcl`（gold，全文见下方 GOLD_TCL）
- 可选 `rc_factor_summary.rpt`（样例输出，非必须）

## case 设计要点 (next round)
- **mode**: design_flow；**entry_point**: outputs/submit.zip；**test**: check(deliverable, workdir) 双参
- **L2 结构判分**: check.py 解 zip → 取 ostrich_rc_factor.tcl → **不跑真实 ostrich**（license/GUI 不可用），用 Tcl 结构断言 + 在 stub 沙盒里 source 脚本头部校验
- **A 输入 (assets/)**: prompt.txt + task_brief.md(≤3 行接口) + golden_quantus.spef + target_innovus.spef（A 版：3 net，driver 分别 drv_a/drv_b/drv_c:Z，**用修复后版本**，非 trace 原始 buggy 共用 drv:Z 版）
- **hidden B (reference/<id>/hidden/)**: 不同 SPEF 对（5 net，不同 net 名/不同 cap-res 值/不同 driver 名），hidden_manifest.json；check 只跑 B
- **anti-hardcode**: B 的 net 名/driver 名/cap-res 数值与 A 不同 → 断言脚本引用变量而非硬编码 A 值；脚本须对任意 SPEF 对工作
- **check.py ≥8 断言** 候选:
  (a) zip 恰含 1 文件 ostrich_rc_factor.tcl
  (b) 文件为合法 Tcl（无未闭合括号/引号；tclsh -nounknown 或语法扫描通过）
  (c) 含 `read_spef -filename ... -setname` 两次（golden + target）
  (d) 含 `build_plot` 带 -golden/-target/-datatype 三参
  (e) loop 覆盖 {tcap res xcap} 三 datatype（foreach 或显式三块）
  (f) 含 `get_scale_factor -recommended`（生成 RC factor，非仅描述）
  (g) 含 `export_sorted_list ... -filename`（per-net diff 输出）
  (h) summary 含 Innovus apply 提示 `setRCFactor` 且 `create_rc_corner`（single + MMMC 两路径）
  (i) 含错误处理 `catch` 包裹 read_spef/build_plot（健壮性 = trace 修复点）
  (j) 输出目录 $OUT_DIR / rc_factor_summary.rpt 写出
  (k) anti-hardcode: 脚本不得硬编码 A 的 net 名（net_a/net_b/net_c）或 driver 名（drv_a:Z）——用 Ostrich 命令动态枚举 net
  (l) anti-hardcode: 脚本不得硬编码 A 的 cap/res 数值（6.0/60.0/11.0...）
  (m) 在 stub 沙盒（mock ostrich commands）source 脚本 → 验证 read_spef 被调 2 次、build_plot 被调 ≥1 次、get_scale_factor 被调
  (n) stub 跑 B SPEF 对 → 脚本产出 rc_factor_summary.rpt 含 "RECOMMENDED RC factor"
  (o) 脚本 `exit 0` 正常终止
  (p) 脚本头部含 usage 注释（`ostrich -64only <` 执行方式）
  → k=16 ≥8 ✓
- **negatives**: fake_empty / fake_print_expected(只 print "RECOMMENDED RC factor tcap = 1.0") / fake_core_deleted(删 build_plot+get_scale_factor) / naive_stub(只 read_spef 无比较) → 全 FAIL
- **§4.9 三假**: (a)空壳 (b)只 print 期望串 (c)删核心(build_plot) 全 FAIL

## GOLD_TCL (ostrich_rc_factor.tcl — final, from trace A#168-A#180 edits, assembled)
```tcl
#==============================================================================
# Script : ostrich_rc_factor.tcl
# Purpose: Use Cadence Ostrich to compare two SPEF files
#          (golden = sign-off extraction e.g. Quantus/QRC
#           target = implementation extraction e.g. Innovus postRoute)
#          and generate RC factors (recommended scale factors) plus
#          per-net difference reports.
#
# Usage  : ostrich -64only < ostrich_rc_factor.tcl 2>&1 | tee ostrich_run.log
#
# Output : $OUT_DIR/rc_factor_summary.rpt      - RC factor summary
#          $OUT_DIR/tcap_diff_sorted.rpt       - per-net total-cap diff list
#          $OUT_DIR/res_diff_sorted.rpt        - per-net resistance diff list
#          $OUT_DIR/xcap_diff_sorted.rpt       - per-net coupling-cap diff list
#==============================================================================

# 0. User configuration
set GOLDEN_SPEF  "./golden_quantus.spef"
set TARGET_SPEF  "./target_innovus.spef"
set GOLDEN_SET   "golden"
set TARGET_SET   "target"
set PLOT_BASE    "rc_cmp"
set OUT_DIR      "./rc_factor_rpt"
set CAP_UNIT     "fF"
set MIN_TCAP     0.001
set MIN_RES      1.0
set MAX_PERC_DEV 200.0

# 1. Prepare output directory and log file
file mkdir $OUT_DIR
set logfh [open "$OUT_DIR/rc_factor_summary.rpt" w]
proc log {fh msg} { puts $msg; puts $fh $msg; flush $fh }

log $logfh "=============================================================="
log $logfh " Ostrich RC Factor Report"
log $logfh " golden : $GOLDEN_SPEF"
log $logfh " target : $TARGET_SPEF"
log $logfh " date   : [clock format [clock seconds] -format {%Y-%m-%d %H:%M:%S}]"
log $logfh "=============================================================="

# 2. Read the two SPEF files into separate datasets
if {[catch {read_spef -filename $GOLDEN_SPEF -setname $GOLDEN_SET} msg]} {
    log $logfh "ERROR: cannot read golden spef '$GOLDEN_SPEF': $msg"
    close $logfh
    exit 1
}
log $logfh "INFO: golden spef loaded into dataset '$GOLDEN_SET'"
if {[catch {read_spef -filename $TARGET_SPEF -setname $TARGET_SET} msg]} {
    log $logfh "ERROR: cannot read target spef '$TARGET_SPEF': $msg"
    close $logfh
    exit 1
}
log $logfh "INFO: target spef loaded into dataset '$TARGET_SET'"

# 3. For each datatype (tcap / res / xcap): build plot -> stats -> export -> factor
set factor_list {}
foreach dtype {tcap res xcap} {
    set plot "${PLOT_BASE}_${dtype}"
    log $logfh "--------------------------------------------------------------"
    log $logfh " Processing datatype: $dtype"
    set min_data $MIN_TCAP
    if {$dtype eq "res"} { set min_data $MIN_RES }
    if {[catch {build_plot -plotname $plot -golden $GOLDEN_SET -target $TARGET_SET -datatype $dtype -min_data $min_data -max_perc_dev $MAX_PERC_DEV} msg]} {
        log $logfh "WARN : build_plot($dtype) failed -> $msg"
        continue
    }
    if {[catch {get_plot_statistics -plotname $plot -datatype $dtype} stats]} {
        log $logfh "WARN : get_plot_statistics($dtype) -> $stats"
    } else {
        log $logfh "---- $dtype plot statistics ----"
        log $logfh $stats
        log $logfh "--------------------------------"
    }
    if {$dtype eq "res"} {
        set cmd [list export_sorted_list -plotname $plot -datatype $dtype -sort_by perc_err -sort_dir decreasing -use_netnames -sum_res -filename "$OUT_DIR/${dtype}_diff_sorted.rpt"]
    } else {
        set cmd [list export_sorted_list -plotname $plot -datatype $dtype -sort_by perc_err -sort_dir decreasing -use_netnames -cap_unit $CAP_UNIT -filename "$OUT_DIR/${dtype}_diff_sorted.rpt"]
    }
    if {[catch {eval $cmd} msg]} {
        log $logfh "WARN : export_sorted_list($dtype) -> $msg"
    } else {
        log $logfh "INFO : exported $OUT_DIR/${dtype}_diff_sorted.rpt"
    }
    if {[catch {set rec [get_scale_factor -plotname $plot -datatype $dtype -recommended]} msg]} {
        log $logfh "WARN : get_scale_factor($dtype -recommended) -> $msg"
    } else {
        log $logfh ">>> RECOMMENDED RC factor ($dtype) = $rec"
        lappend factor_list [list $dtype $rec]
    }
}

# 4. Summary: how to apply the factors in Innovus
log $logfh "=============================================================="
log $logfh " RC FACTOR SUMMARY"
log $logfh "--------------------------------------------------------------"
if {[llength $factor_list] == 0} {
    log $logfh " No RC factor generated (check warnings above)."
} else {
    foreach f $factor_list {
        set dtype [lindex $f 0]
        set rec   [lindex $f 1]
        if {$dtype eq "tcap"} {
            log $logfh " total-cap factor : $rec"
            log $logfh "   Innovus single-corner : setRCFactor -capacitance $rec"
            log $logfh "   Innovus MMMC          : create_rc_corner -cap_factor $rec ..."
        } elseif {$dtype eq "res"} {
            log $logfh " resistance factor: $rec"
            log $logfh "   Innovus single-corner : setRCFactor -resistance $rec"
            log $logfh "   Innovus MMMC          : create_rc_corner -res_factor $rec ..."
        } else {
            log $logfh " $dtype factor : $rec"
        }
    }
}
log $logfh "=============================================================="
log $logfh " Per-net detail lists: $OUT_DIR/*_diff_sorted.rpt"
log $logfh "=============================================================="
close $logfh
puts "DONE: RC factor reports written under $OUT_DIR/"
exit 0
```

## A-SPEF (修复后版本 — 每 net 唯一 driver+sink；trace 原始版共用 drv:Z 是 bug，A#196 修)
### golden_quantus.spef (A)
```
*SPEF "IEEE 1481-1998"
*DESIGN "top"
*DATE "2026-10-27:00:00:00"
*VENDOR "Cadence"
*PROGRAM "quantus"
*VERSION "23.1"
*DESIGN_FLOW "PIN_CAP NONE" "NAME_SCOPE LOCAL"
*DIVIDER /
*DELIMITER :
*BUS_DELIMITER [ ]
*T_UNIT 1 NS
*C_UNIT 1 PF
*R_UNIT 1 OHM
*L_UNIT 1 HENRY

*NAME_MAP
*1 net_a
*2 net_b
*3 net_c
*4 drv_a:Z
*5 drv_b:Z
*6 drv_c:Z
*7 sink_a:I
*8 sink_b:I
*9 sink_c:I

*D_NET *1 10.0
*CONN
*I *4 O
*I *7 I
*CAP
1 *1:1 6.0
2 *1:2 4.0
*RES
1 *4 *1:1 60.0
2 *1:1 *1:2 40.0
*END

*D_NET *2 20.0
*CONN
*I *5 O
*I *8 I
*CAP
1 *2:1 20.0
*RES
1 *5 *2:1 200.0
*END

*D_NET *3 5.0
*CONN
*I *6 O
*I *9 I
*CAP
1 *3:1 5.0
*RES
1 *6 *3:1 50.0
*END
```
### target_innovus.spef (A)
```
*SPEF "IEEE 1481-1998"
*DESIGN "top"
*DATE "2026-10-27:00:00:00"
*VENDOR "Cadence"
*PROGRAM "innovus"
*VERSION "23.1"
*DESIGN_FLOW "PIN_CAP NONE" "NAME_SCOPE LOCAL"
*DIVIDER /
*DELIMITER :
*BUS_DELIMITER [ ]
*T_UNIT 1 NS
*C_UNIT 1 PF
*R_UNIT 1 OHM
*L_UNIT 1 HENRY

*NAME_MAP
*1 net_a
*2 net_b
*3 net_c
*4 drv_a:Z
*5 drv_b:Z
*6 drv_c:Z
*7 sink_a:I
*8 sink_b:I
*9 sink_c:I

*D_NET *1 11.0
*CONN
*I *4 O
*I *7 I
*CAP
1 *1:1 6.6
2 *1:2 4.4
*RES
1 *4 *1:1 66.0
2 *1:1 *1:2 44.0
*END

*D_NET *2 19.0
*CONN
*I *5 O
*I *8 I
*CAP
1 *2:1 19.0
*RES
1 *5 *2:1 190.0
*END

*D_NET *3 5.5
*CONN
*I *6 O
*I *9 I
*CAP
1 *3:1 5.5
*RES
1 *6 *3:1 55.0
*END
```

## hidden B 设计 (next round)
- 5 net (而非 A 的 3): net_x/net_y/net_z/net_w/net_v
- 不同 driver 名: dx:Z/dy:Z/dz:Z/dw:Z/dv:Z；不同 sink
- 不同 cap/res 数值（golden vs target 偏差模式不同：A 是 target≈golden×1.1，B 用混合偏差如 ×0.9/×1.2/×1.05）
- B 的 net 数 5 ≠ A 的 3 → 守卫防硬编码 "3"
- B 的 net/driver 名与 A 完全不同 → 守卫防硬编码 A 名

## 状态
- **本轮 (r58)**: claimed ✓ + deepread ✓ + gold extracted ✓；**case 合成未完成**（预算 40min 用尽于发现+深读；pool 耗尽背景见 MEMORY）
- **next round (r59) 第一件事**: 用本笔记的 GOLD_TCL + A-SPEF + hidden B 设计合成 OstrichSpefRCFactor-001，自验，追加 jsonl
