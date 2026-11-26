#!/bin/csh -f
###############################################################################
# run_demo.csh -- 一键 demo：自动发现 ../data 下的 demo design 并跑通 STA flow
#
# 用法:
#   ./run_demo.csh                             # 默认 corner/mode
#   ./run_demo.csh -corner ss0p72vm40c -mode func
###############################################################################

# 无匹配 glob 时按字面处理，避免 "No match" 报错
set nonomatch

set self = $0
if ( $self !~ /* ) then
    set self = $cwd/$self
endif
set RUN_DIR  = `dirname $self`
set ROOT_DIR = `dirname $RUN_DIR`
set DATA_DIR = $ROOT_DIR/data

# ---- 自动发现 demo design 名(data/ 下第一个真实存在的 .v/.vg) ----
set DESIGN = ""
foreach f ( $DATA_DIR/*.v $DATA_DIR/*.vg )
    if ( -f "$f" ) then
        set base   = `basename $f`
        set DESIGN = `echo $base | sed 's/\.v$//; s/\.vg$//'`
        break
    endif
end
if ( $DESIGN == "" ) then
    set DESIGN = "demo"
endif

echo "run_demo: discovered demo design = $DESIGN (data -> $DATA_DIR)"

# ---- 默认 corner/mode；额外命令行参数(如 -corner)透传并后置覆盖默认值 ----
set CORNER = "tt0p8v25c"
set MODE   = "func"

exec $RUN_DIR/run_sta.csh -design $DESIGN -corner $CORNER -mode $MODE $argv