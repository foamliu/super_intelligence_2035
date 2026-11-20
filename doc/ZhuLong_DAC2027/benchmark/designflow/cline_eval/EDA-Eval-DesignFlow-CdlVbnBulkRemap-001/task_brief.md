# EDA-Eval-DesignFlow-CdlVbnBulkRemap-001 — StarRCXT RCC bulk-pin CDL 修复

## 交付接口（仅此 3 行说明接口，不写"怎么做"）
交付 `outputs/submit.zip`，解压后须含 3 个文件：`fix_cdl.py`（通用 CDL
体偏置修复器）、`T_IsmTop_fixed.cdl`（对可见 A 修复后的结果）、`fix.diff`
（unified diff）。判分器把你的 `fix_cdl.py` 拷到独立临时目录，对**隐藏的 B
工程**的 CDL 运行它，校验修复是否对 B 正确——因此 `fix_cdl.py` **必须通用
地定位 buf 族实例**（按子电路名 `bufLx*` + 体偏置端接在 `vbn!`/`vbp!` 上
这一结构特征），不得硬编码实例名 `XI37` 或单元名 `bufLx4`。

## fix_cdl.py 行为规格（来自真实 trace，StarRCXT RCC 体偏置映射修复）
`fix_cdl.py` 命令行：`fix_cdl.py <in.cdl> <out.cdl> <out.diff>`
1. 读入 CDL，对每一个 `bufLx*` 子电路的实例行，若其体偏置 bulk 端（`A Y
   vbn vbp vcc vss` 签名中的第 3、4 位置）接在 `vbn!`/`vbp!` 上，则把这两
   端重映射为 `vss!`/`vcc!`（即 `vbn! vbp! vcc! vss!` → `vss! vcc! vcc!
   vss!`），仅改这两端，信号端 A/Y 与电源端 vcc!/vss! 不动。
2. 其余所有行（含所有 `.SUBCKT` 定义、其余实例、注释）原样保留。
3. 输出修复后的 CDL 到 `<out.cdl>`，输出 unified diff 到 `<out.diff>`。
4. 幂等：对已修复的 CDL 再跑应无改动并 exit 0；若 CDL 里根本没有 `bufLx*`
   实例则 exit 2（无可修）；成功修复 exit 0。

可见 A 工程上下文见 `ctx_A.txt`、待修 CDL 见 `T_IsmTop.cdl`（仅作开发参考；
判分只用隐藏 B）。
