#!/bin/csh -f
#===============================================================================
# FILE    : run_sta.csh
# PURPOSE : PrimeTime STA flow top-level run script (executed inside run/)
#
# This cshell wrapper:
#   * configures the runtime environment and selects the PrimeTime tool
#     (module load is required on this farm so that the license is picked up)
#   * creates the output directory hierarchy (log/ rpt/ sdc/ session/)
#   * launches pt_shell with scr/sta_main.tcl, passing design/corner/mode so the
#     flow can adapt to different PVT corners (tt/ss/ff) and functional/test modes
#
# USAGE:
#   run_sta.csh [-corner <corner>]  [-mode <mode>]
#               [-corners "c1 c2 ..."] [-modes "m1 m2 ..."]
#               [-design <top>] [-clean] [-help]
#
#   corner examples : tt0p8v25c  ss0p72vm40c  ff0p88v125c
#   mode   examples : func  test  hold
#
# Reference flow (modelled after):
#   /apps/imctf/cad/script/digital_flow/feint  (synopsys pt reference flow)
#===============================================================================

#--- resolve absolute location of this script, then the project root -----------
set ARGV0   = "$0"
if ( "$ARGV0" == "$ARGV0:t" ) then
    set ARGV0 = "$cwd/$ARGV0"
endif
cd `dirname "$ARGV0"`
set RUN_DIR  = `pwd`
cd ..
set ROOT_DIR = `pwd`
cd $RUN_DIR
set SCR_DIR  = "$ROOT_DIR/scr"

#--- defaults ------------------------------------------------------------------
set DESIGN   = "design"
set CORNER   = "tt0p8v25c"
set MODE     = "func"
set CORNERS  = ""          ;# optional multi-corner list; empty => single -corner
set MODES    = ""          ;# optional multi-mode list;   empty => single -mode
set CLEAN    = 0
set HELP     = 0

#--- tool selection (PrimeTime) ------------------------------------------------
# Prompt tool root : /apps/synopsys/primetime
# A module must be loaded on this farm so the license is correctly obtained.
set PT_MODULE = "pt/2022.12-SP5_os7"
set PT_SHELL  = "pt_shell"

#--- command line parsing ------------------------------------------------------
set i = 1
while ( $i <= $#argv )
    switch ( "$argv[$i]" )
        case "-corner":
            @ i++
            set CORNER = "$argv[$i]"
            breaksw
        case "-mode":
            @ i++
            set MODE = "$argv[$i]"
            breaksw
        case "-corners":
            @ i++
            set CORNERS = "$argv[$i]"
            breaksw
        case "-modes":
            @ i++
            set MODES = "$argv[$i]"
            breaksw
        case "-design":
            @ i++
            set DESIGN = "$argv[$i]"
            breaksw
        case "-clean":
            set CLEAN = 1
            breaksw
        case "-h":
        case "-help":
            set HELP = 1
            breaksw
        default:
            echo "ERROR: unknown option '$argv[$i]'"
            exit 1
    endsw
    @ i++
end

if ( $HELP == 1 ) then
    echo "usage: $ARGV0:t [-corner <corner>] [-mode <mode>] [-corners \"c1 c2\"] [-modes \"m1 m2\"] [-design <top>] [-clean]"
    echo "  corners : tt0p8v25c ss0p72vm40c ff0p88v125c"
    echo "  modes   : func test hold"
    exit 0
endif

#--- environment configuration & output directories ---------------------------
set LOG_DIR = "$ROOT_DIR/log"
set RPT_DIR = "$ROOT_DIR/rpt"
set SDC_DIR = "$ROOT_DIR/sdc"
set SES_DIR = "$ROOT_DIR/session"

if ( $CLEAN == 1 ) then
    echo "RM-Info: cleaning output dirs"
    rm -rf $LOG_DIR $RPT_DIR $SDC_DIR $SES_DIR
endif
mkdir -p $LOG_DIR $RPT_DIR $SDC_DIR $SES_DIR

#--- load the PrimeTime module (tool selection + license setup) ----------------
if ( "$PT_MODULE" != "" ) then
    which module >& /dev/null
    if ( $status == 0 ) then
        echo "RM-Info: module load $PT_MODULE"
        module load $PT_MODULE
    else
        echo "RM-Warning: 'module' not found; assuming $PT_SHELL is on PATH"
    endif
endif

#--- derive the corner/mode run lists ------------------------------------------
if ( "$CORNERS" == "" ) set CORNERS = "$CORNER"
if ( "$MODES"   == "" ) set MODES   = "$MODE"

#--- launch PrimeTime ----------------------------------------------------------
cd $RUN_DIR
set RUNCORNER = ""
foreach RUNCORNER ( $CORNERS )
    set RUNMODE = ""
    foreach RUNMODE ( $MODES )
        set TAG = "${DESIGN}_${RUNCORNER}_${RUNMODE}"
        echo "==================================================================="
        echo " RM-Info: STA run -> design=$DESIGN corner=$RUNCORNER mode=$RUNMODE"
        echo "==================================================================="

        set PT_X = "set ROOT_DIR $ROOT_DIR; set RUN_DIR $RUN_DIR; set SCR_DIR $SCR_DIR; set LOG_DIR $LOG_DIR; set RPT_DIR $RPT_DIR; set SDC_DIR $SDC_DIR; set SES_DIR $SES_DIR; set DESIGN_NAME $DESIGN; set PT_CORNER $RUNCORNER; set PT_MODE $RUNMODE"

        $PT_SHELL -f $SCR_DIR/sta_main.tcl -x "$PT_X" |& tee $LOG_DIR/sta_${TAG}.log
        if ( $status != 0 ) then
            echo "ERROR: PrimeTime returned non-zero for $TAG"
            exit 1
        endif
    end
end

echo "RM-Info: STA flow finished."
echo "  logs    -> $LOG_DIR"
echo "  reports -> $RPT_DIR"
echo "  sdc     -> $SDC_DIR"
echo "  session -> $SES_DIR"
exit 0