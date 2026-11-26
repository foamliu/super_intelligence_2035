# Deep-read: 1793694775768_lw8dg (rongjiez / hfeg0pkn005, mc=11)

- session_file: `/home/rongjiez/.cline/data/sessions/1793694775768_lw8dg/1793694775768_lw8dg.messages.json`
- user: rongjiez, host: hfeg0pkn005 (10.129.2.14), 59 msgs, 1 real user turn
- domain: waveform (waveform comparison pipeline)
- keywords: netlist:21;synopsys:15;waveview:5;verilog:4;analog:2

## USER#0 (原话, 唯一真实用户轮)

> `@compare_wave_new.pl_supportOldConfig` 这个代码中
> `my ($vol_low, $vol_high, $cmp_time_file, $fsdb_files_ref, $vec_files_ref) = exportData($fsdb_file, $vec_file, $sigs, $simulator, $product_code);`
> 会输出文件到 debugode 中，现在有些 case，没有输入的 raw 下的 fsdb 文件，因为已经被清空了，但是 debugode 文件夹还在，现在我想对这些 case 执行我的 compare_wave_new.pl_supportOldConfig 脚本，请修改对应的代码，具体的 case 为 `/home/cad2/yanxvwei/compare_wave_case/drjpa/primesim.CRG003_Perbank_Core_timing_wl4_WPre_4_tCH_50_BL16_4b8g_B0_6400_FF.x8.FF1.06V-10C.X8`

**意图分类**: code-modification (modify existing Perl script to add a reuse/cache mode), NOT new-tool production. env-dep (Perl + FSDB binary + private case dir + waveview license) ⇒ **B-track 合成** (portable Python two-stage pipeline, text-CSV waveforms).

## 助手工具链 (59 msgs)

1. read_files compare_wave_new.pl_supportOldConfig (分段读 1-560, 556-1150, 1150-1478, 1686-1722)
2. run_commands ls case dir (被 shell-policy 拦) → list_allowed_files case dir (depth 2)
3. editor _explore_case.py 探 case 结构 → run_approved_command python-runner
4. 发现: raw/ + stimulus.list + vec.text 都是**指向 /rundata/... 的坏符号链接** (已删除); debugMode/ 完整保留上次导出 (vol_lower_value/vol_high_value/comp_end_time_temp + a2d 侧 lbdq.vec/ldqpad0-7.vec/ldqspad_t.vec/ldqspad_c.vec + exp 侧 LBDQ.vec/exp_LDQ0-7.vec/exp_LDQSPad_T/C.vec)
5. read_files exportData body + help() 区段
6. editor 改 compare_wave_new.pl_supportOldConfig (6 处):
   - 参数解析加 `-reuse` → `$reuse_debug`
   - `errorchk`: reuse 下 fsdb/vec not-exist 从 FATAL 降 WARN
   - `createDir`: reuse 下**不 rm -rf debugMode**, 改校验 debugMode 存在 (缺失则 die)
   - `exportData`: reuse 下跳过 3 个 wv 导出步骤; 校验 vol_lower_value/vol_high_value/comp_end_time_temp 必须存在 (缺失 die); 信号→.vec 路径映射不变; 个别信号 vec 缺失只 WARN (走 filterSkipSigs skip 流程)
   - `clearTmpFile`: reuse 下**永不删** debugMode + compare.rep_*
   - help() + 文件头注释补 -reuse 说明
7. perl -c 语法检查 (List::Util 环境问题, stub 后通过)
8. editor _reuse_test_run.py 端到端 smoke test (copy case 的 config_pincheck + debugMode 到 workspace, 故意不 copy raw/) → run_approved_command → **PASS**: compare.rep 正常生成, debugMode 保留, 结果与 old report 一致 (ldqs 40p-120p→80p zero-error, ldq 30p, pulse count ldqspad_t 61vs55 / ldqspad_c 56vs60)
9. 修 cosmetic header (reuse 下仍打 "exporting...") → 再跑 smoke test PASS
10. editor _cleanup.py 删临时文件

## 关键 gotcha (移植到合成 case)

1. **createDir 默认 rm -rf debugMode** — reuse 下若不屏蔽会删掉唯一数据源 (致命)
2. **errorchk 默认 raw-not-exist = FATAL** — reuse 下 raw 已删, 须降 WARN
3. **exportData 默认跑 wv 导出** — reuse 下须跳过; 改为校验 mandatory 中间文件 (vol_low/vol_high/comp_end_time) 存在, 缺失 die
4. **per-signal .vec 缺失 = WARN + skip** (非 fatal, 走 filterSkipSigs)
5. **clearTmpFile 默认 rm -rf debugMode** — reuse 下须屏蔽 (否则删掉 cache)
6. **比较窗口从 cache 读** (vol_low/vol_high/comp_end_time/comp_start_time) — reuse 下不能从 raw 重算 (raw 已删)
7. **normal mode 回归** — 加 -reuse 不能破坏正常模式 (raw 在时仍 export+compare+cleanup)
8. **比较正确性** — per-signal PASS/FAIL + mismatch count 须与 oracle 一致

## 合成方案 (B-track, portable text-CSV)

真实非便携因素: Perl + FSDB 二进制 + VEC + waveview license + 私有 case dir。
合成: Python 纯 stdlib 两阶段 pipeline `wave_compare.py`:
- normal mode: read `raw/sim.csv` (a2d) + `raw/exp.csv` (exp) + `config.ini` (vol_low/vol_high) → export per-signal `<sig>.a2d.vec`/`<sig>.exp.vec` + `vol_low`/`vol_high`/`comp_start_time`/`comp_end_time` 到 `debugMode/` → compare within window → `compare.rep` → cleanup (rm -rf debugMode)
- SUT 任务: 加 `-reuse` mode (skip export, compare from cached debugMode, 不删 cache, 放宽 raw 校验, 校验 mandatory 中间文件)

与 r637 GrDecPwr 同族 (waveform) 但 distinct: r637 = edge measurement (tr/tf/idle/stable); 本 case = add cache-reuse mode to export→compare pipeline (code-modification subtype, 非 measurement)。
与 WaveCmpWrap-001 (e0039602) distinct: WaveCmpWrap = wrap compare engine into CLI; 本 case = add reuse/cache-skip mode to existing pipeline。

## near-dup 审计

rongjiez 已有 4 case (OpenWaveFmt/SweepCfgParse/FFLatchExtract/ModelQaTbGen) — 全异 (wave fmt / cfg parse / latch extract / modelQA tbgen)。本 case = waveform pipeline reuse-mode code-mod, distinct ✓。
