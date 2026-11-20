# 深读：um5we — xuebaok @ hfhds201 — 确定性 seed by pattern name

- session: `1791463574990_um5we.messages.json` (xuebaok @ hfhds201, 361 msgs / 2.66 MB)
- shard B (spice_sim) · A-档 trace-faithful · L1
- match_count ≈ 50 (finesim/primesim MatrixRun 上下文；本机 hfhds201 local session，不在 11-05 summary.tsv 中)

## USER 轮（意图）
- **USER#0**（逐字，A-档任务说明）：`/proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen/run_compres分析这个命令，每次生成的pattern都用不同的seed，我想要相同名字开头的pattern共用一个seed`
- USER#39（细化 spec + 例子）：`...run_compress...我想要相同名字开头的pattern共用一个seed，比如 Compress031_FT_2P6_MultiAct_PRAC_Normal2Compress_MCI_MCI_CAParity_DIS_tCH50_sc0sc1_2b16g_BL0_TM_TT_FSMSHORT_DUALSC_COMPRESS.X2P6_TM`（同一 pattern 跨 PVT corner 共用 seed）
- USER#123-127（子任务：tran 10ps 来源分析，agent 未答 "？"，incomplete，与主任务无关）
- USER#288/289（子任务：unlink_netlist_033.sh）
- USER#339（子任务：relink_pincheck_032_033.sh）

→ **主任务 = USER#0**：纯需求轮（给目标「相同名字开头 pattern 共用 seed」+ 方法「改 run_compress/vsim 的 seed 来源」），未给根因/修复 ⇒ **CLEAN A-档 ✓**。后续子任务与主任务无关，不进 prompt。

## assistant 工具链（主任务部分）
- read_files×97 / list_allowed_files×43 / search_codebase×13 / editor×22 / run_commands×5
- 关键发现（assistant 推理）：
  - `bin/vsim` line 678：`if($gsusr) { $gseed = $gsusr; } else { $gseed = int(rand(2**31)); }` —— 每次 vsim 调用若未传 `-g` 则用 `rand(2**31)` 随机 seed
  - `bin/vsim` line 1279：`print RUNFILE ("set ...")` 把 seed 写入 runfile
  - 框架中 `$patName`（pattern 基名）与 `$corner`（SS/TT/FF/SF/FS PVT）是**分离字段**
- 修复（editor [48][66][82]）：新增 Perl sub `computeSeedFromName($name)`，把 `runRegression(...)` 调用里的 seed 来源从随机改为 `computeSeedFromName($patName)`：
  ```perl
  sub computeSeedFromName {
      my $name = shift;
      my $seed = 0;
      foreach my $c (split //, $name) {
          $seed = ($seed * 31 + ord($c)) % (2**31);
      }
      $seed = -$seed if $seed < 0;   # mod 2**31 后恒非负，no-op
      return $seed;
  }
  ```
  调用点 [88][92][96]：`runRegression(..., $corner, $queue, $mrSet, computeSeedFromName($patName))`
  vsim 命令 [86]：`... -g $seed` 把确定性 seed 传给 vsim
- 算法 = 经典多项式散列（Horner，base 31，mod 2^31），seed 仅由 pattern 名决定 ⇒ 同名 pattern 跨 corner 共用 seed

## 金标准（trace-faithful）
USER#0 spec 的正确实现：seed = pattern_name 的多项式散列（base 31, mod 2^31），与 corner 无关；同名 ⇒ 同 seed。
便携 L1 Python 脚本：读 manifest（`pattern_name<TAB>corner`），对每行输出 `pattern_name<TAB>corner<TAB>seed`，seed 仅依赖 pattern_name。

## case 合成
- ID: `EDA-Eval-DesignFlow-DetermSeedByName-001` · spice_sim · A-faithful · L1
- 交付 = 通用 `seed_from_name.py <manifest> <output>`，输出 `name<TAB>corner<TAB>seed`
- A = manifest_A（可见，2 patterns × corners，anti-hardcode）
- B = manifest_B（隐藏，4 patterns × corners，含 1 个单-corner pattern 测 distinct）
- reference = seed_from_name_ref.py（多项式散列 base 31 mod 2^31）+ check.py k=12 + 5 negative + selftest
- 断言 a-l：zip/compile/无参非零/跑B exit0+输出/行数对齐/seed∈[0,2^31)/同名跨corner同seed/异名异seed/匹配参考散列/重跑字节一致/corner无关/anti-hardcode(A≠B)
