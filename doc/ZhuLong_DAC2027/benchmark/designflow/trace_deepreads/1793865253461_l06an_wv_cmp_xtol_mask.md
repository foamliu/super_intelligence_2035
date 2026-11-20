# 深读笔记 · 1793865253461_l06an · rongjiez @ 10.129.2.14 · mc=39 · waveform

> trace 来源：`/home/rongjiez/.cline/data/sessions/1793865253461_l06an/1793865253461_l06an.messages.json`（531KB）
> 选料轮：shard D #538（2026-11-12）。fresh-sid（不在 4-shard ledger）。

## 用户真实任务（逐字 U#0）

> @compare_wave_new.pl 这个脚本实现了对 fsdb 波形和理想的数字信号进行对比分析，输出报告，在
> /home/cad2/yanxvwei/compare_wave_case/dejoa/MatrixRun_Netlist_SpfBA_0805AM/.../voltage_s/ 的 case 中，
> pincheck 是执行脚本的命令，compare.rep 是输出结果，在结果中 dq0<7> 信号和 exp_DQ0<7> 平移后对比显示
> Matched，但是我在波形中发现时间为 5.092900E-07 时，dq0<7> 为 1，5.092900E-07 加上 Shift Time: 1.35n
> 为 5.1064E-07，此时 exp_DQ0<7> 为 0，应该是不匹配，为啥输出结果是匹配

**任务性质**：debug/Q&A（"why Matched"）。用户已定位到具体时刻 + 具体信号，要的是根因解释。
agent 写 check_wave.py / check_wave2.py 复现脚本逻辑，确认 error_count=0 → Matched 是脚本正确行为，
根因是 addToleranceForExpVecFile 的 X 区间容差扩展把 0/1 失配点扩成 X(don't-care)。

## 关键算法（compare_wave_new.pl 逐字还原）

### addToleranceForExpVecFile（X 区间容差扩展，核心）
```perl
sub addToleranceForExpVecFile {
    my ( $file, $tolerance ) = @_;
    foreach my $line (@infile) {
        $count++;
        my $pre = $count - 2;    ## 0-based index of the previous row
        if ( $line =~ /^\s*\d\S+\s+[01Z]/ && $pre >= 0
             && $infile[$pre] =~ /^\s*\d\S+\s+X/i ) {
            next;                ## this 0/1/Z row was already emitted by the previous X-segment
        }
        if ( $line =~ /^\s*(\d\S+)\s+X/i ) {
            my $Xbgn = $1;
            my $nextLine = $infile[$count];
            if ( defined $nextLine && $nextLine =~ /^\s*(\d\S+)\s+([01Z])/i ) {
                my ( $Xend, $type01 ) = ( $1, $2 );
                my $Xtol    = ( ( $Xend - $Xbgn ) / 0.15 ) * $tolerance;
                my $newXbgn = $Xbgn - $Xtol;   # sprintf %.9E
                my $newXend = $Xend + $Xtol;
                print OUT " $newXbgn X \n";
                print OUT " $newXend $type01 \n";
                next;
            }
        }
        print OUT $line;
    }
}
```
- tolerance 是分数（"35%" → 0.35，getConfig 里 `s/%//;/100`）。
- X 段后跟 0/1/Z：Xbgn=X 行时间，Xend=下一行时间，type01=下一行电平；
  Xtol=(Xend-Xbgn)/0.15*tolerance；emit (Xbgn-Xtol, X) + (Xend+Xtol, type01)。
- 紧接 X 之后的 0/1/Z 行被跳过（已被上一段 X 段 emit）。
- exp_tolerance 实测值 35%（config_pincheck：`*exp_tolerance = 32.5%` 注释掉，`exp_tolerance = 35%` 生效）。

### shift_signal
```perl
sub shift_signal { my ($signal_wave,$shift)=@_; $shifted_wave->{sprintf("%E",$time+$shift)}=$signal_wave->{$time}; }
```

### compare_signal（网格对比，X/Z don't-care）
- 合并 a2d 与 shifted_exp 的时间键；逐点：exp 为 X/Z → next（don't-care）；a2d 为 X/Z → next；
  否则 a2d ne exp → error_count++，记 mismatch point [time, a2d, exp]。
- whole-wave 模式：尾部（a2d 无样本）用 a2d 末值替代；explicit-window 模式不替代。

### record_segment_result（报告格式）
```
Signal Name: <sig>
Shift Time: <shift>
Compare Result: Matched      (overall_err==0)
   或
Compare Result: Mismatched
Error Count: <err>
Segment result (P=pass, X=fail):
<逐段 P/X>
```

### 复现结论（agent check_wave.py）
```
compare_end = 5.25099e-07
*** REPRODUCED for dq0<7>: error_count=0 (report says Matched/0) ***
a2d_grid(5.0929e-7)        = 1
exp_tol_grid(5.0929e-7)    = 1     ← 容差扩展后该点 = 1，与 a2d=1 一致 → 无失配
exp_tol_grid(5.0794e-7)    = X
shifted_exp(5.0929e-7)     = X     ← 原始平移后该点 = X（don't-care）
raw_exp(5.1064e-7)         = 0     ← 用户心智模型：原始 0 → 以为失配
```
用户混淆：把 raw_exp(0) 当成对比值，但脚本对比的是 tol_exp（X 扩展后），该点变 X/don't-care → 无失配 → Matched。

## 合成设计（B-grade，WvVecCmpXTolAudit-001）

放弃：FSDB 二进制读取（不可打包）/ Perl 脚本完整移植 / segment-window / parallel fork / pulse stats。
保留核心：vec 文本解析 + X 容差扩展 + shift + 均匀网格对比 + masked mismatch 检测（用户"why Matched"的审计角度）。

**判定语义**（合成自洽定义，受 trace 启发）：
- 均匀网格 step=1e-10s，hold-state 重采样（avoid transition-time aliasing；真实 compare_wave.pl 亦有 uniform resampling 子）。
- masked = 原始平移下真实失配(a2d≠raw_exp 且均 0/1) 且 容差扩展后该点 exp∈{X,Z}（容差把失配抹成 don't-care）。

**A/B/C 不相交**：
- A（task_A，给 SUT）：dq0_A，shift=1e-9，tol=0.30，ce=4.8e-7。a2d 1→0 转移对齐 X 段 relocated 0
  → **verdict=Matched, tol_err=0, raw_err=91, masked=91**（复现用户"why Matched"：raw 91 处失配全被容差掩盖）。
- B（hidden）：dqs_B，shift=2e-9，tol=0.20，ce=5.5e-7。X 段 type 1 落在 a2d=0 区
  → verdict=Mismatched, tol_err=863, raw_err=930, masked=67（容差掩盖 67 处，剩 863 处真实失配）。
- C（嵌入 check.py 反硬编码）：clk_C，shift=5e-9，tol=0.50，ce=3.8e-7
  → verdict=Mismatched, tol_err=233, raw_err=400, masked=167。
- A/B/C signal/shift/tol/compare_end/vec 内容全不相交；raw_err = tol_err + masked（三例均成立）。

**SUT**：wv_vec_cmp_xtol_audit.py 纯 stdlib（argparse/json/math/os/re/sys），禁 subprocess/socket/urllib/
ctypes/numpy/pandas/eval/exec，禁 B/C 字面量。

**check.py**：14 条件 a-n，独立 oracle（o_parse/o_add_tolerance/o_shift/o_grid_pass，不 import SUT），
subprocess 真跑 SUT on B + 嵌入 C，3-seed sha256 确定性。自验 ref 14/14 PASS + 3 neg（header_only/
static_hardcode/naive_no_tolerance）全 FAIL + §4.9 三假（empty/print_only/core_removed）全 FAIL +
example_report_A 逐字节 + 3-seed sha256 一致。

## 维度正交（非 dup）
vs 4qpyk ShiftIntervalReport-001（同 compare_wave_new.pl 家族但机制不同：4qpyk=best-shift 扫描的
shift interval Start/End/Tolerance 报告；本 case=addToleranceForExpVecFile 的 X 区间容差扩展 +
masked mismatch 审计，"tolerance"含义不同——前者是 shift 扫描容差，后者是 X 区间扩展容差）。
vs 3qe6x AutoDebug V3 WaveCompare CLI（顶层 CLI 封装，非 X 容差掩盖审计）。机制正交 ✓。

## difficulty
L1（诚实标：SUT 纯 stdlib vec 文本解析 + X 容差扩展 + shift + 网格对比 + masked 检测，无 EDA 工具运行时，
与 D 域近期 #518-#537 parse/transform 类一致；P-003 已确认 D 域 actual_tool_demand 99.7% parse）。
