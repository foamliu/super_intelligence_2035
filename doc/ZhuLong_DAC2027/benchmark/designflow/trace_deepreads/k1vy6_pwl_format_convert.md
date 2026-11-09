# Deepread: k1vy6 — PWL Format Convert (hauserz, spectre)

## trace_source
- session: 1793705585219_k1vy6
- user: hauserz
- host: hfeg0pkn006 / hfeg0plg98 (dir-format sessions)
- mc: 131, spice_tools: 223 (spectre), ratio: 1.0 (pure spectre)
- msgs: 98, agent: lead
- file: 226858 bytes, mtime Nov 3 19:54

## User turns (A-faithful analysis)
- U#0: "/proj/drgqx/V0/simdir/spectre/workdir/hauserz/idd0_vintlp_current_TT_1p1v 阅读一下这个文件。" (read file)
- U#6: "复制一份，将复制后的文件命名为idd0_vintlp_current_TT_1p1v_pwl" (copy+rename)
- U#18: "idd0_vblhh_current_ipwl阅读一下这个文件。" (read target ref)
- U#22: "将idd0_vintlp_current_TT_1p1v_pwl转化成与idd0_vblhh_current_ipwl相同格式的文件。" ← **produce-task (A-compliant: goal, no root-cause/fix)**
- U#34: "要求时间从0开始。" ← refinement (A-compliant)
- U#46: "要求将电流方向反向。" ← refinement (A-compliant)
- U#54: "批量处理idd0_vblen_current_TT_1p1v，idd0_vblhh_current_TT_1p1v，...idd4w_vintlp_current_TT_1p1v" (batch 8 files)
- U#66: "将上面八个文件移动到.../drgqx_ipwl中" (move to dir)
- U#74: "批量处理proj/drgqx/V0/simdir/spectre/workdir/hauserz/路径下所有后缀为1p1v的文件，要求时间从零开始，电流方向反向。" ← **consolidated batch task**
- U#86: "把步骤1省去，再处理一次，另存为。" (variant: keep PWL format, skip step 1)

## Input format (Custom WaveView SPICE PWL EXPORT)
```
*** Custom WaveView SPICE PWL EXPORT (T-2022.06-SP1)
*** created at 2026-11-03 19:14:20
Ivintlp vintlp 0 PWL(
+ 1.00000E-08 -4.33451E-07
+ 1.00098E-08 -1.95966E-08
...
+)
```
- 3 header lines (*** comment, *** created, I<name> <node> 0 PWL()
- data lines: `+ <time> <current>` (uppercase E, 5 decimals)
- closing: `+)`
- ~260-380 data points per file, time offsets 1E-08 / 2.1E-08 / 4.5E-08

## Target format (pure data, idd0_vblhh_current_ipwl)
```
0.00000E+00 4.33451E-07
9.80000E-12 1.95966E-08
...
```
- No header, no `+` prefix, no PWL wrapper
- `<time> <current>` per line, uppercase E, 5 decimals, trailing space

## Gold standard = assistant A#79 batch_all_1p1v.py
Transformations (3 steps):
1. **Format conversion**: strip `***` headers, `I..PWL(` line, `+` prefix, `+)` closing → pure data
2. **Time shift**: subtract first time offset → first point = 0.00000E+00
3. **Current reverse**: multiply current by -1
- Output: `<src_name>_ipwl` files to `drgqx_ipwl/` subdirectory
- Format: `f"{val:.5e}".replace('e','E')` → uppercase E, 5 decimal places

## Real data values (from tool results)
- idd0_vintlp: 373 pts, offset 1.0E-08, first raw `-4.33451E-07` → after transform `0.00000E+00 4.33451E-07`
- idd0_vblen: 373 pts, offset 1.0E-08, first transform `0.00000E+00 7.09624E-10`, last `4.80000E-08 4.11369E-07`
- idd0_vblhh: 373 pts, first `0.00000E+00 2.69578E-08`, last `4.80000E-08 -3.47037E-06`
- idd0_vblhm: 373 pts, first `0.00000E+00 1.11300E-09`, last `4.80000E-08 5.78418E-07`
- idd0_viblh: 261 pts, offset 2.1E-08, first `0.00000E+00 -1.49594E-05`, last `4.80000E-08 3.27600E-05`
- idd4r_vblh: 354 pts, offset 4.5E-08, first `0.00000E+00 2.75790E-05`, last `5.00000E-09 3.60952E-05`
- idd4r_vintlp: 354 pts, first `0.00000E+00 2.66689E-05`, last `5.00000E-09 2.66728E-05`
- idd4w_vblh: 331 pts, first `0.00000E+00 2.33214E-05`, last `5.00000E-09 3.13939E-05`
- idd4w_vintlp: 331 pts

## Case design
- ID: EDA-Eval-DesignFlow-PwlFormatConvert-001
- domain: spice_sim, track: faithful, level: L1
- Assets A: simdir/ with 6 PWL source files + target ref (idd0_vblhh_current_ipwl)
- Hidden B1: 5 different PWL files (different values/offsets/counts)
- Hidden B2: 4 PWL files (anti-hardcoding, different magnitudes)
- reference: pwl_convert_ref.py (generalized from A#79)
- check.py: ≥8 assertions, 真跑候选 (subprocess on B1/B2)
