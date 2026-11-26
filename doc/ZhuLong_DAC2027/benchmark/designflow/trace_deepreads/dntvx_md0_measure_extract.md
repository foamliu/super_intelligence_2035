# Deepread: 1789031505860_dntvx — rongjiez @ hfhds201 — ModelQA measure parser extension

- **session**: 1789031505860_dntvx (100 msgs, 1.0MB), rongjiez @ hfhds201 (=.75 local)
- **domain**: spice_sim / characterization QA (FineSimPro .md0 measure extraction)
- **spice tool count**: 39 hspice (mc=100); user rongjiez = characterization QA engineer (also did ctu99=ShrinkExtract-001)
- **real script**: `/home/rongjiez/jira_dev/mpqa/mp_1/scripts/runModelQA_new.pl` (Perl, refactored from runModelQA.pl)

## A-grade candidate轮 (USER#1 verbatim, idx 0) — CLEAN ✓
> @runModelQA_new.pl 现在我的summary_all_results需要考虑这六个结果vtgm vtsat vtlin idsat idlin ioff 其中vtgm已经写好了 `if ( $line =~ /\s+vtgm\s+=\s+(\S+)/ ) { _store_result(... 'vtgm', ... undef, $1 ); next; }` 对于vtsat和vtlin还需要匹配文件中的 `idlin =  6.5231e-07` 和 `idsat =  6.5231e-07` 这个数据替换原来代码中的$idlin_expr，在vtsat和vtlin的build_sim_condition时需要加上extract。输出报告时不要额外输出一个normalized报告，只需要total，但是需要把normalized数据对应增加一列，注意对于电压vtgm vtsat vtlin不需要normalized，只需要对电流 idsat idlin ioff计算normalized，计算公式为 `idsat_normalized = idsat/(w*nf)` 其中w和nf都可以在读取md0文件时获得，下面是idsat的文件格式…

**判 CLEAN A-grade ✓**：纯需求轮，给目标(6 measure types)+方法(regex/extract/normalized公式)+格式样例(md0)，未给根因/修复。

## .md0 文件格式 (FineSimPro V-2023.12 measure output)
```
* FineSimPro V-2023.12-1  (Compiled on Jan  4 2024 at 16:34:53 ...)
* Copyright(c) 2003-2024 Synopsys, Inc.
* Generated at Thu Sep 10 16:52:52 2026
* Hostname: hfeg0pgn021, Username: rongjiez
* Input File: ntn_w1.060u_l0.130u_nf1_c1.sp
* Title: "tt_1.2_1.2_0_0_-10"
          w =  1.0600e-06
          l =  1.3000e-07
         nf =  1.0000e+00
        vdd =  1.2000e+00
      idsat =  2.2917e-04
     temper =  -1.0000e+01
     alter# =  2.0000e+00
```
- devkey 从 `* Input File:` 提取 (basename 去 .sp): `ntn_w1.060u_l0.130u_nf1_c1`
- corner/temp/vdd 从 `* Title:` 提取: `"tt_1.2_1.2_0_0_-10"` → corner=tt, vdd=1.2, temp=-10 (格式 `corner_vdd1_vdd2_..._temp`)
- w/nf 从 `w =`/`nf =` 行
- measure value:
  - vtgm subdir → `vtgm = <val>` 行
  - idsat subdir → `idsat = <val>` 行
  - idlin subdir → `idlin = <val>` 行
  - ioff subdir → `ioff = <val>` 行 (ion 类似)
  - vtsat subdir → 用 `idsat =` 行的值 (extract)
  - vtlin subdir → 用 `idlin =` 行的值 (extract)

## assistant 解法 (21 处编辑，已验证)
1. `_parse_one_md0` 加 `$subdir_type` 参数；第一遍提 w/nf/idsat/idlin；vtsat 传 `$idsat_extract`，vtlin 传 `$idlin_extract`；加 idsat/idlin 独立解析(按 subdir 过滤)；传 `$w_val`/`$nf_val` 给所有 `_store_result`
2. `_store_result` 加 w/nf 参数；电流类型(idsat/idlin/ioff) normalized = value/(w*nf)；电压类型无 normalized
3. `_store_normalized` 修 pvt_key 加 vdd
4. `generate_report` 单报告 MPQA_total.report，total+normalized 列(电流两列/电压一列)
5. `_idlin_extract_display` 处理纯数字
6. `change_print_value`/`_unit_label`/`_type_prefix` 加 idsat/idlin
- USER#26 (idx 41): "vtgm vtlin vtsat不需要额外加一个normalized数据" → 修：电压类型只输出 total 列，电流类型 total+normalized 列
- USER#30 (idx 49): 报告列宽对齐 (Idsat_n(uA/um) 14 字符溢出 %-12s) → 动态列宽
- USER#32 (idx 57): 新需求 idvd/idvg → generate_csv_file + generateAllChart (新功能，本 case 不含)

## case 设计 (EDA-Eval-DesignFlow-Md0MeasureExtract-001, spice_sim A-faithful L1)
**交付**: 通用 `md0_measure_extract.py <md0_dir> <output_csv>` — 遍历 md0_dir 下 subdir(vtgm/vtsat/vtlin/idsat/idlin/ioff) 的 *.md0 → 解析 devkey/corner/temp/vdd/w/nf/measure_value → 按 type 算 normalized(电流=value/(w*nf)，电压=空) → 写 CSV (列: devkey,corner,temp,vdd,type,total,normalized)
**A 输入**: md0_A/ 6 subdir × 2 .md0 = 12 文件 (ntn/ptn 两个 devkey, tt/ss 两个 corner, 不同 w/nf/value)
**hidden B**: md0_B/ 6 subdir × 2 .md0 (不同 devkey ntk/ptk, ff corner, 不同 value/w/nf) A≠B
**reference**: md0_measure_extract_ref.py + check.py
**k=14 断言**: a-zip含py / b-py_compile / c-无参非零 / d-跑B exit0 / e-CSV存在有header / f-行数==.md0文件数 / g-vtgm行normalized为空(电压) / h-idsat行normalized==idsat/(w*nf)容差 / i-idlin行normalized==idlin/(w*nf) / j-ioff行normalized==ioff/(w*nf) / k-vtsat行total==idsat值(extract) / l-vtlin行total==idlin值(extract) / m-devkey从filename提取正确 / n-corner/temp/vdd从Title解析 / o-A!=B(不同值)
**negative**: naive_empty / print_only / hardcoded_A / wrong_norm_formula(用w*l) / skip_current_normalized(电流不算norm)

## 状态
- DEBT: 1 (deepread 完成，case 合成待下一轮 — 本轮 40min 硬预算耗尽)
- 下一轮第一件事：合成 Md0MeasureExtract-001 → 自验 → 追加 B jsonl → mark case → 清 DEBT
