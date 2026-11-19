# Deepread: szlie — vtarget.pl-style NxPx_RBL aggregator (U[41]+U[87])

**Session**: `1794532305061_szlie` (vincentz @ hfeg0plg58, mc=193, hspice:4986 关键词主导)
**Trace date**: 2026-11-16 (updated_at), 328 msgs / 169 user
**Selected task**: U[41] (msg 79) + U[87] (msg 168) — vtarget aggregator
**Case**: `EDA-Eval-DesignFlow-VtargetBisecAggregate-001` (r906, shard B, k=15)

## 为什么选这条 / 不选其他
该 session 含 7 个真实 user_input，多数是同一 param-sweep deck-gen 家族（U[0]/U[115]/U[138]/U[150]），与 vincentz 现有 3 case (SpiceParamSweepGen-001 / HspiceSwCurvExtract-001 / SpSweepDeckGen-001) 同形，会判 DUP。U[26] 是 runsim 批处理脚本生成（同 deck-gen 流派的下游 runner），便携化价值低。**U[41]+U[87] 是唯一不同形的任务**：不是生成 .sp deck，而是对**已跑完的仿真结果**做后处理聚合——扫 `result/NxPx_RBL/` 各 sim 目录、读 `SM.bisec_mt0`、取 vtarget 列、汇总成文档。这是 produce-action(后处理脚本) 形态，与 deck-gen 形态正交，与 xuelianf 的 BisecMt0SmCalc-001（Input_D0/D1.bisec_mt0 + SM 公式计算）也正交（此为 SM.bisec_mt0 vtarget 列聚合 + 矩阵，无公式计算）。

## 用户原始意图（逐字）
- U[41] (msg 79): `<user_input mode="act">请帮我根据vtarget.pl这个文件生成一下类似的文件，读取所有./result/NxPx_RBL/mixbest_V1_RBL_{RBL}_N{x}P{x}里的符合要求的文件并生成一个文档</user_input>`
- U[87] (msg 168): `<user_input mode="act">每个文件夹里需要读取的是SM.bisec_mt0文件的vtarget那一列的data</user_input>`

## 关键上下文（trace 中 agent 读到的真实文件）

### vtarget.pl（reference perl，agent 经 read_files 读到）
```perl
#!/usr/bin/perl
use strict; use warnings;
my $linenum = shift;
my $inputFile = `ls ./result/RBL_ZYT/*/SM.bisec_mt0`;
my @inputFile = split(/\n/,$inputFile);
foreach my $inputFile2 (@inputFile) {
    if(-e $inputFile2) {
        printf "$inputFile2\n";
        open IN, "< $inputFile2";
        while (my $line = <IN>) {
            if($line =~ /\d\.\d+e/) {
                my @line = split(/\s+/,$line);
                my $linenum = 1;
                print "$line[$linenum]\n";   # split 前导空白→idx1 = 第0数据列 = vtarget
            }
        }
        close IN;
    }
}
```
要点：glob `./result/RBL_ZYT/*/SM.bisec_mt0`，按 `\d\.\d+e` 匹配数据行，`split(/\s+/)`（前导空白→idx0 为空），取 `$line[1]` = 第 0 数据列 = vtarget。

### SM_a*.mt0 样本（per-alter 测量文件，agent 经 read_files 读到 SM_a0/a1/a14.mt0）
```
$DATA1 SOURCE='PrimeSim Pro' VERSION='U-2023.03-SP1' PARAM_COUNT=1
.TITLE ''
        vtarget         maxvbl         dvbl_4         vcom_4         temper         alter#
     0.0000e+00     4.7572e-04     8.9261e-02     3.9115e-01    -4.0000e+01     1.0000e+00
     9.5000e-01     8.9475e-01     9.8855e-02     4.8896e-01    -4.0000e+01     1.0000e+00
     4.7500e-01     4.7366e-04     4.7435e-03     4.3979e-01    -4.0000e+01     1.0000e+00
     ...（12-15 行 bisection 迭代，末行 = 收敛值）
```
6 列：`vtarget maxvbl dvbl_4 vcom_4 temper alter#`，科学计数法。

### SM.bisec_mt0（bisection 收敛汇总，每个 sim 一份）
与 SM_a*.mt0 同格式但仅含收敛汇总行。trace 中 agent 实际读到的 NxPx_RBL 树下 `SM/SM.bisec_mt0` 存在（msg 161-166 验证：240 个 sim dir，每个 16 个 mt0 = 3600 数据点；v2 脚本跑通）。

## Agent 工具链（msg 79-167，U[41]+U[87] 段）
1. read_files vtarget.pl → 理解 perl 范式
2. list_allowed_files result/V1_V0d9_1/mixbest_V1_RBL_95 / result/NxPx_RBL → 摸结果树结构
3. read_files SM_a0.mt0 / SM_a1.mt0 / SM_a14.mt0 → 确认 .mt0 列格式
4. editor 创建 `/home/vincentz/gen_vtarget_RBL_NxPx.py`（v1，读 SM_a*.mt0，**理解错**——U[87] 之前误以为要读 per-alter 文件）
5. run_approved_command python-runner 跑 v1 → 输出 16 mt0/sim（错）
6. U[87] 澄清后：list_allowed_files + read_files 确认 `SM.bisec_mt0` 文件存在
7. editor 创建 `/home/vincentz/gen_vtarget_RBL_NxPx_v2.py`（v2，读 SM/SM.bisec_mt0，**正确**）
8. run_approved_command python-runner 跑 v2 → 240 sim × 收敛 vtarget，输出 vtarget_converged_RBL_NxPx.txt + dvbl_RBL_NxPx.txt + vcm_RBL_NxPx.txt + CSV
9. read_files 验证输出文件内容 → msg 222「数据看起来非常合理！」

## v2 产出脚本要点（gen_vtarget_RBL_NxPx_v2.py）
- BASE 硬编码 `/rundata/.../00_V1_CBCC_Vcm/result/NxPx_RBL`
- RBL_LIST 硬编码 `[0,5,15,...,135]`，x ∈ range(16)（4 重 for 算 Sanadj1-4 组合）
- 读 `SM/SM.bisec_mt0`（无平铺退化）
- `re.search(r'\d\.\d+e', line)` 匹配数据行，`split()` 取 6 列 `['vtarget','maxvbl','dvbl_4','vcom_4','temper','alter#']`
- 输出 4 文件到 OUTDIR：vtarget_RBL_NxPx.csv（全数据行）+ vtarget_converged_RBL_NxPx.txt（末行 vtarget）+ vtarget_val/dvbl/vcm_RBL_NxPx.txt（R_BL×NxPx 矩阵，`matching[-1]` 为收敛值，缺 sim 标 N/A）

## 便携化重构（case 与 trace 的差异）
| 维度 | trace v2 | case gen_vtarget.py |
|---|---|---|
| base 路径 | 硬编码 `/rundata/.../00_V1_CBCC_Vcm/result/NxPx_RBL` | cwd-based `./NxPx_RBL`（可选 argv） |
| R_BL/x 发现 | 硬编码 RBL_LIST + range(16) | 从目录名正则 `mixbest_V1_RBL_(\d+)_N(\d+)P\2` 自动发现 |
| 文件布局 | 仅 `SM/SM.bisec_mt0` | `SM/SM.bisec_mt0` 退化到平铺 `SM.bisec_mt0` |
| 缺文件处理 | continue 跳过 | 跳过 + 矩阵标 N/A |
| 输出 | 4 文件（含 dvbl/vcm 矩阵） | 3 文件（CSV + converged + vtarget 矩阵，砍 dvbl/vcm 矩阵以收紧 check） |
| 输出目录 | OUTDIR=dirname(BASE) | cwd（可选 argv） |

## 合成资产保真度
- `.bisec_mt0` 格式逐字复刻真实 PrimeSim `.mt0`（`$DATA1 ...` + `.TITLE ''` + 列名行 + 科学计数法数据行）
- vtarget bisection 模式复刻真实：row0=0.0（低极端）→ row1=0.95（高极端）→ row2=target（收敛）
- 目录命名 `mixbest_V1_RBL_{RBL}_N{x}P{x}` 逐字复刻 trace
- B1 含 1 缺文件 sim + 1 平铺布局 sim（测双布局 + N/A 容错，trace v2 未显式测过）
- B2 用完全不同的 R_BL/x 取值（反硬编码，trace v2 因硬编码 RBL_LIST 在不同输入上会漏数据）

## 不重不漏校验
- vs vincentz 现有 3 case：均 param-sweep deck-gen 形态（生成 .sp），本 case 是 result 后处理聚合，不同形 ✓
- vs xuelianf BisecMt0SmCalc-001：Input_D0/D1.bisec_mt0 + SM 公式计算（directory,vtarget_D1,vtarget_D0,SM1,SM0），本 case 是 SM.bisec_mt0 vtarget 列聚合 + 矩阵（R_BL,NxPx,x,...），无公式，不同文件/不同输出/不同用户 ✓
- vs SpBisecDeckGen-001 / TspcTimingBisecTbGen-001：deck/tb 生成，不同形 ✓
- 台账 P-004 parking 基于 U[0]（param-sweep dup 判断正确），但 U[41]/U[87] 是同一 session 内的不同任务，r906 重新 claim + force-mark，note 已记录原因 ✓
