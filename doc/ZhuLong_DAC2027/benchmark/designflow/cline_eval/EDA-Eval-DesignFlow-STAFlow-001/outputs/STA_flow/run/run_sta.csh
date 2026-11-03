#!/bin/csh -f
###############################################################################
# run_sta.csh -- PrimeTime STA flow 任务运行脚本(cshell)
#
# 用法:
#   ./run_sta.csh \
#       -design <top> -corner <corner> -mode <mode> \
#       [-lib "<libs>"] [-netlist <file>] [-sdc <file>] [-spef "<spefs>"] \
#       [-tool <version>] [-x "<extra tcl>"]
#
# 例:
#   ./run_sta.csh -design demo -corner ss0p72vm40c -mode func
#   ./run_demo.csh                                    (一键 demo)
###############################################################################

# ---- 定位 run/ 与 flow 根目录 ----
set self = $0
if ( $self !~ /* ) then
    set self = $cwd/$self
endif
set RUN_DIR  = `dirname $self`
set ROOT_DIR = `dirname $RUN_DIR`

# ---- 默认参数 ----
set DESIGN      = ""
set CORNER      = "tt0p8v25c"
set MODE        = "func"
set TOOL        = "U-2022.12-SP5"
set LIB_FILES   = ""
set NETLIST     = ""
set SDC_FILE    = ""
set SPEF_FILES  = ""
set XTRA        = ""

# ---- 解析命令行选项 ----
while ( $#argv > 0 )
    switch ( "$argv[1]" )
        case "-design":
        case "-top":
            shift; set DESIGN     = "$argv[1]"; shift; breaksw
        case "-corner":
            shift; set CORNER     = "$argv[1]"; shift; breaksw
        case "-mode":
            shift; set MODE       = "$argv[1]"; shift; breaksw
        case "-tool":
        case "-version":
            shift; set TOOL       = "$argv[1]"; shift; breaksw
        case "-lib":
        case "-libs":
            shift; set LIB_FILES  = "$argv[1]"; shift; breaksw
        case "-netlist":
            shift; set NETLIST    = "$argv[1]"; shift; breaksw
        case "-sdc":
            shift; set SDC_FILE   = "$argv[1]"; shift; breaksw
        case "-spef":
            shift; set SPEF_FILES = "$argv[1]"; shift; breaksw
        case "-x":
            shift; set XTRA       = "$XTRA $argv[1]"; shift; breaksw
        default:
            echo "run_sta: ERROR: unknown option: $argv[1]"
            exit 1
    endsw
end

if ( $DESIGN == "" ) then
    echo "run_sta: ERROR: -design <top> is required"
    exit 1
endif

# ---- 工具选型(默认安装根 /apps/synopsys/primetime) ----
set PT_INSTALL = /apps/synopsys/primetime
set PT_SHELL    = $PT_INSTALL/$TOOL/bin/pt_shell
if ( ! -x $PT_SHELL ) then
    set PT_SHELL = `which pt_shell`
endif
if ( $PT_SHELL == "" ) then
    echo "run_sta: ERROR: pt_shell not found for version $TOOL"
    echo "                  searched: $PT_INSTALL/$TOOL/bin/pt_shell"
    exit 1
endif

# ---- license: 优先 module load(Environment Modules 获取正确 license 环境) ----
set MODULE_INIT = ""
foreach cand ( /apps/cad/Modules/init/csh /usr/share/Modules/init/csh /apps/Modules/init/csh )
    if ( -r $cand ) then
        set MODULE_INIT = $cand
        break
    endif
end
if ( $MODULE_INIT != "" ) then
    source $MODULE_INIT
    # module 版本号去掉目录前缀(如 U-2022.12-SP5 -> 2022.12-SP5)
    set MODULE_VER = `echo $TOOL | sed 's/^[A-Za-z]-//'`
    module load ds/pt/$MODULE_VER >& /dev/null
endif

# ---- 预建输出件目录(log/rpt/sdc/session) ----
mkdir -p $ROOT_DIR/log $ROOT_DIR/rpt $ROOT_DIR/sdc $ROOT_DIR/session

# ---- 构造通过 -x 传递给 pt_shell 的变量 ----
set XARGS = "set ROOT_DIR $ROOT_DIR; set DESIGN $DESIGN; set DESIGN_NAME $DESIGN; set CORNER $CORNER; set PT_CORNER $CORNER; set MODE $MODE; set PT_VERSION $TOOL"
if ( $LIB_FILES != "" ) then
    set XARGS = "$XARGS; set ANALYSIS_LIBRARY_FILES {$LIB_FILES}"
endif
if ( $NETLIST != "" ) then
    set XARGS = "$XARGS; set NETLIST_FILES {$NETLIST}"
endif
if ( $SDC_FILE != "" ) then
    set XARGS = "$XARGS; set CONSTRAINT_FILES {$SDC_FILE}"
endif
if ( $SPEF_FILES != "" ) then
    set XARGS = "$XARGS; set PARASITIC_FILES {$SPEF_FILES}"
endif
if ( $XTRA != "" ) then
    set XARGS = "$XARGS; $XTRA"
endif

# ---- 在 run/ 目录执行，日志 tee 到 log/ ----
echo "===================================================================="
echo " PrimeTime STA flow"
echo "   design : $DESIGN"
echo "   corner : $CORNER"
echo "   mode   : $MODE"
echo "   tool   : $PT_SHELL"
echo "===================================================================="

cd $RUN_DIR
set LOG = $ROOT_DIR/log/${DESIGN}_${CORNER}_${MODE}.log
$PT_SHELL -f $ROOT_DIR/scr/sta_main.tcl -x "$XARGS" | tee $LOG