#!/bin/bash
#===============================================================================
# run_sweep.sh  --  parallel, one-job-per-corner FineSim PVT sweep
#
#   原版：
#       单个 bsub 任务里跑一个 finesim，finesim 在同一个进程内把 base/nominal
#       与所有 ".alter" PVT corner 串行跑完 —— corner 越多，单个任务墙钟时间
#       越长，成为瓶颈。
#
#   本版：
#       自动发现 corner（base + 每一个 ".alter <title>"），每个 corner 提交
#       一个独立 bsub 任务，所有 corner 在 LSF 上并行执行。
#
# 单 corner 选择机制（FineSim 原生，不改网表）：
#   FineSim 的 ".option alter_select" 只运行指定的 run。索引从 1 开始，按顺序
#   枚举 base 与各 .alter 块：
#       list 1 -> base/nominal（第一个 .alter 之前的语句）
#       list 2 -> 第 1 个 ".alter" 块
#       list 3 -> 第 2 个 ".alter" 块
#       ...
#   该 option 通过 "-ifile" 注入，原始网表保持只读、不被修改。
#===============================================================================
set -u

# ---- 可用环境变量覆盖（默认值与原版一致） -------------------------------------
queue=${QUEUE:-fqueue3_analog}
cpu_core=${CPU_CORE:-4}
netlist="${1:-${NETLIST:-IsmOscTestSweep.sp}}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---- 将网表解析为绝对路径 ----------------------------------------------------
if [ -f "$netlist" ] && [[ "$netlist" == /* ]]; then
    netlist_abs="$netlist"
elif [ -f "$SCRIPT_DIR/$netlist" ]; then
    netlist_abs="$SCRIPT_DIR/$netlist"
else
    shopt -s nullglob
    sp_candidates=("$SCRIPT_DIR"/*.sp)
    shopt -u nullglob
    if [ "${#sp_candidates[@]}" -eq 1 ]; then
        netlist_abs="${sp_candidates[0]}"
        echo "NOTE: netlist not named '$netlist'; auto-detected: $netlist_abs"
    else
        echo "ERROR: netlist not found: '$netlist' (looked in: $SCRIPT_DIR)" >&2
        exit 1
    fi
fi

# ---- 输出目录（时间戳目录名与原版保持一致） -----------------------------------
run_dir="$SCRIPT_DIR/superon_sweep_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$run_dir"

module unload primesim 2>/dev/null
module load prime/2023.12-SP4

# ---- 发现 corner -------------------------------------------------------------
# 第 1 个 corner 恒为 base/nominal；其余来自网表中的 ".alter <title>"（不区分
# 大小写）。标题去注释、去首尾空白。
alter_names=$(awk 'tolower($1)==".alter" {
                      n++
                      $1=""
                      sub(/^[ \t]+/, "", $0)
                      sub(/[ \t]*\$.*$/, "", $0)
                      sub(/[ \t]+$/, "", $0)
                      if ($0=="") $0="alter" n
                      print $0
                  }' "$netlist_abs")

corner_names=("nominal")
if [ -n "$alter_names" ]; then
    while IFS= read -r line; do
        [ -n "$line" ] && corner_names+=("$line")
    done <<< "$alter_names"
fi

sanitize() {
    printf '%s' "$1" | tr -c '[:alnum:]_.-' '_' | tr -s '_' | sed 's/^_//;s/_$//'
}

total=${#corner_names[@]}
echo "Netlist : $netlist_abs"
echo "Corners : $total (1 base/nominal + $((total-1)) .alter)"
echo "Queue   : $queue   CPU core(s): $cpu_core"

for ((i=0; i<total; i++)); do
    sel=$((i+1))                      # FineSim alter_select 索引（1 基）
    raw="${corner_names[$i]}"
    name=$(sanitize "$raw")
    [ -z "$name" ] && name="corner${sel}"

    corner_dir="$run_dir/${sel}_${name}"
    mkdir -p "$corner_dir"

    # 控制文件：只选择这一个 corner（list N = 第 N 个 run）
    printf '.option alter_select="list %d"\n' "$sel" > "$corner_dir/alter_select.inc"

    # 注意："-ifile" 必须搭配 "-o"（否则 finesim 外壳会把 -ifile 的值误当成
    # 第二个输入网表而报 "two or more input file"）。"-o <name>" 同时让每个
    # corner 的输出前缀唯一、无冲突。
    bsub -q "$queue" -J "sweep${sel}" \
        "cd $corner_dir && finesim $netlist_abs -o ${name} -np $cpu_core -ifile $corner_dir/alter_select.inc > run.log 2>&1"

    printf '  [%d/%d] submitted %-24s alter_select="list %d" -> %s\n' \
        "$sel" "$total" "$name" "$sel" "$corner_dir"
done

echo "Output directory: $run_dir"
echo "Submitted $total independent corner jobs (parallel)."