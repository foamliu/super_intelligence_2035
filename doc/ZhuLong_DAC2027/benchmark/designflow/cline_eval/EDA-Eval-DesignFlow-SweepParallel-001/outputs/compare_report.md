# run_sweep.sh 修改对比报告（串行 → 每 corner 一个并行 LSF 任务）

## 1. 问题
原版 `run_sweep.sh` 只提交 **1 个** `bsub` 任务，在该任务内用一次 `finesim`
将网表中的 base/nominal 运行与所有 `.alter` PVT corner **串行**跑完。
corner 越多，单个任务墙钟时间越长，且始终只占用一个 LSF 队列槽位，成为瓶颈。

本版把每个 corner 拆成 **1 个独立 `bsub` 任务**，全部 corner 在 LSF 上并行执行。

## 2. 与原版的 diff

```diff
--- run_sweep.sh.orig         （原版：单任务、串行）
+++ run_sweep.sh              （本版：每 corner 一个任务、并行）
@@
 #!/bin/bash
 
-queue=fqueue3_analog
-cpu_core=4
-
-netlist=IsmOscTestSweep.sp
-run_dir=superon_sweep_$(date +%Y%m%d_%H%M%S)
-
-mkdir -p "$run_dir"
-
-module unload primesim
-module load prime/2023.12-SP4
-
-bsub -q "$queue" "cd $PWD/$run_dir && finesim ../$netlist -np $cpu_core > run.log 2>&1"
-
-echo "Output directory: $run_dir"
+set -u
+
+# 默认值与原版一致，可用环境变量覆盖
+queue=${QUEUE:-fqueue3_analog}
+cpu_core=${CPU_CORE:-4}
+netlist="${1:-${NETLIST:-IsmOscTestSweep.sp}}"
+
+SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
+# ...（网表绝对路径解析、自动发现 base + 各 .alter corner ...）
+
+run_dir="$SCRIPT_DIR/superon_sweep_$(date +%Y%m%d_%H%M%S)"
+mkdir -p "$run_dir"
+
+module unload primesim 2>/dev/null
+module load prime/2023.12-SP4
+
+# 对每个 corner 生成独立目录 + alter_select.inc，各提交一个 bsub 任务
+for ((i=0; i<total; i++)); do
+    sel=$((i+1))
+    corner_dir="$run_dir/${sel}_${name}"
+    mkdir -p "$corner_dir"
+    printf '.option alter_select="list %d"\n' "$sel" > "$corner_dir/alter_select.inc"
+    bsub -q "$queue" -J "sweep${sel}" \
+        "cd $corner_dir && finesim $netlist_abs -o ${name} -np $cpu_core \
+         -ifile $corner_dir/alter_select.inc > run.log 2>&1"
+done
```

## 3. 关键改动点与必要性

| # | 改动 | 必要性 |
| --- | --- | --- |
| 1 | 发现 corner：`awk` 扫描 `.alter <title>`，base 恒为第 1 个 corner | 每个 corner 需要一个独立任务，必须先知道 corner 列表；且对换「隐藏网表」同样适用（不硬编码 corner 名） |
| 2 | 每个 corner 一个 `bsub`（`-J sweep<N>`），各自 `cd` 到独立子目录再跑 finesim | 实现并行、输出互不覆盖 |
| 3 | 每任务注入 `.option alter_select="list N"`（经 `-ifile 文件`） | FineSim 原生只跑指定 run 的机制，1 基、含 base；用 `-ifile` 注入即可**不改原网表**（网表保持只读） |
| 4 | finesim 命令行加 `-o <corner名>` | 使用 `-ifile` 时必须给 `-o`，否则 finesim 外壳会把 `-ifile` 的值误当第二个输入网表，报 `two or more input file`；`-o` 同时让各 corner 输出前缀唯一 |
| 5 | 网表解析为绝对路径、`set -u`、`module unload ... 2>/dev/null` | 稳健性：脚本从任意目录/被 zip 解压目录调用都能定位网表；规避未定义变量；`primesim` 未加载时不报错 |
| 6 | 保留 `QUEUE`/`CPU_CORE` 默认值 `fqueue3_analog`/`4`，输出树目录名 `superon_sweep_YYYYmmdd_HHMMSS/` | 与原版行为/默认保持一致 |

## 4. corner 识别结果（IsmOscTestSweep.sp，共 4 个 corner）

| FineSim 运行序号 | alter_select | corner / PVT |
| --- | --- | --- |
| 1 | `list 1` | nominal base（FF 1.3V -40C） |
| 2 | `list 2` | `FF_1p3V_110`（FF 1.3V 110C） |
| 3 | `list 3` | `TT_1p1V_m10`（TT 1.1V -10C） |
| 4 | `list 4` | `TT_1p21V_98`（TT 1.21V 98C） |

## 5. 验证

用 FineSim `V-2023.12-1`（`prime/2023.12-SP4`）实测验证 `alter_select` 索引
语义与逐 corner 结果（4 个 corner 各跑一次，均 `exit=0`）：

```
list 1 -> vmax=1.30  TEMP= -40   alter# 1    (FF 1.3V  -40C)
list 2 -> vmax=1.30  TEMP= 110   alter# 2    (FF 1.3V  110C)
list 3 -> vmax=1.10  TEMP= -10   alter# 3    (TT 1.1V  -10C)
list 4 -> vmax=1.21  TEMP=  98   alter# 4    (TT 1.21V 98C)
```

每个 corner 只输出该 corner 的一行 measure（与整跑 `alter#` 一一对应），
证明拆分为 4 个并行任务后各任务选择正确、结果与原版逐 corner 等价。