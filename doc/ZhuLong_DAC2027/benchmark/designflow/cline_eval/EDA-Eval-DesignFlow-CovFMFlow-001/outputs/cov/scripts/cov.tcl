##########################################################################################
# cov.tcl - CFREQ_CTRL VCS 代码覆盖率驱动脚本 (由 Makefile 通过 tclsh 调用)
#
# 参考: lagat FEINT 流程的 Makefile + 脚本接口风格 (变量透传)
# 流程: VCS 编译(-cm 覆盖率) -> simv 仿真 -> URG 汇总报告
# 说明: 纯 tclsh 可运行 (stub/dry-run), 工具不存在时自动跳过, 便于 lint 与结构断言。
##########################################################################################

set FLOW_HOME [file normalize [file join [file dirname [info script]] ..]]

# ---- 参数默认值 ----
set DESIGN   "cfreq_ctrl"
set RTL      ""
set TB       ""
set METRICS  "line+cond+tgl+fsm+branch"
set WORKDIR  ""
set TAG      "Au22"

# ---- 解析 argv (tclsh cov.tcl -design X -rtl f -tb t -metrics m -workdir w) ----
for {set i 0} {$i < [llength $argv]} {incr i} {
    set k [lindex $argv $i]
    switch -- $k {
        -design  { set DESIGN   [lindex $argv [incr i]] }
        -rtl     { set RTL      [lindex $argv [incr i]] }
        -tb      { set TB       [lindex $argv [incr i]] }
        -metrics { set METRICS  [lindex $argv [incr i]] }
        -workdir { set WORKDIR  [lindex $argv [incr i]] }
        -tag     { set TAG      [lindex $argv [incr i]] }
        default  { puts "WARN: unknown option $k" }
    }
}

# 读取 setup 变量, 保证与 fm/syn 流程变量口径一致
source [file join $FLOW_HOME "setup" "common_setup.tcl"]
if {$RTL     eq ""} { set RTL     $RTL_SOURCE_FILES }
if {$TB      eq ""} { set TB      "$FLOW_HOME/data/tb_${DESIGN}.sv" }
if {$WORKDIR eq ""} { set WORKDIR "$FLOW_HOME/flow_${DESIGN}" }

set COMPILE_LOG "$WORKDIR/logs/vcs_compile.log"
set SIM_LOG     "$WORKDIR/logs/vcs_sim.log"
set URG_LOG     "$WORKDIR/logs/urg.log"
set VDB_DIR     "$WORKDIR/vdb/simv.vdb"
set RPT_DIR     "$WORKDIR/reports"

# ---- 工具执行: 工具缺失时跳过 (dry-run 保底), 不中断脚本 ----
proc sh {cmd} {
    set bin [lindex $cmd 0]
    puts "+ [join $cmd { }]"
    if {[auto_execok $bin] eq ""} {
        puts "  (skip: $bin not found - dry-run)"
        return
    }
    catch {exec -ignorestderr {*}$cmd} msg
    if {$msg ne ""} { puts $msg }
}

# 1) VCS 编译 (覆盖率编译)
sh [list vcs -full64 -sverilog -cm $METRICS -f $RTL $TB -l $COMPILE_LOG -o $WORKDIR/simv]

# 2) 仿真 (生成 simv.vdb)
sh [list $WORKDIR/simv -cm $METRICS -l $SIM_LOG]

# 3) URG 汇总 (HTML + text)
sh [list urg -dir $VDB_DIR -report $RPT_DIR/${DESIGN}.urgReport -format both]

puts "RM-Info: VCS coverage flow finished (design=$DESIGN, metrics=$METRICS)"