# Deepread: n7ot5 — cmlist → test.run + run_script 生成器 (produce-task, digital)

**session**: 1794482509558_n7ot5 · **user**: szcao · **host**: hfeg0pgn145 (10.129.35.244) · **mc**: 55 · **domain**: digital
**trace 源**: `10.129.35.244:/home/szcao/.cline/data/sessions/1794482509558_n7ot5/1794482509558_n7ot5.messages.json` (121KB, 44 msgs, 22 user / 22 assistant) — 已 scp 到 .75 workdir（本轮 sandbox），下轮可直接重 scp。
**audit 状态**: pool_reaudit_A.tsv 原标「待复审 BORDERLINE (old weak-deliverable)」→ **本轮重审定为 可造 (revived)**。旧 park 理由「dependent-on-existing-files weak verifiability」作废：所有依赖文件（cmlist/test.run/run_script/gen_pattern_files.pl/convert_signals.pl）均在 trace read_files tool_result 中逐字可取，self-contained 可造。

## 用户意图（3 个真实 user turn，逐字）

- **U#0** (ts=1794482510052): `/rundata/drcpa/V0/simdir/verilog/jkxu/TM_TEST` （切工作目录）
- **U#8** (ts=1794483373143): 「我这里有一个脚本 gen_pattern_files.pl，想要吃得文件是 cmlist，想要生成的文件内容如 test.run 所示，把 cmlist 中的每行信号与数值填到对应的 cm1/cm2/cm3 和 width 之后的括号中」
- **U#26** (ts=1794483509955): 「`if ($test$plusargs("cm13")) begin` 并把这个 "" 里的 cm13 等改成一致的信号」  → 即 `$test$plusargs` 的参数从 `cm<N>` 索引改为 cmlist 里的真实信号名
- **U#34** (ts=1794483690208): 「在参考 runscript，把提取出来的 cm 名称放入 -o+ 后面，并每个 cm 生成一行指令」  → 再生成一个 run_script，每个信号一行 vsim 命令，`-o +<信号名>`

## 交付目标（DoD）

一个脚本（agent 用 Python 写了两个：`gen_pattern_files.py` + `gen_run_script.py`；也可合成单一脚本两子命令），读 cmlist，产出：
1. **merged test.run**：固定 header（Config_Timing/PowerUp/initialize/compare_enable/model_compare_enable/begin:pattern_seq）+ 每个信号一个 `if ($test$plusargs("<SIGNAL>")) begin \t\ttmload(.tm("<SIGNAL>"), .width(<WIDTH>)); \tend` 块 + footer `end`。**关键：`$test$plusargs` 与 `tmload` 的名字必须用 cmlist 真实信号名，不得用 `cm1/cm2/cm<N>` 索引**（U#26 的核心修正）。
2. **run_script**：每个信号一行 vsim 命令，`-o +<SIGNAL>`，沿用 run_script 模板的固定前缀/后缀。

## A 档输入文件（全部 trace 逐字可取，已核对）

### `cmlist`（27 行，格式「信号名 宽度」）— 主输入
```
cm0_fc_PowerDownEn 1
cm0_io_CACSBIModeEn 1
cm0_io_NBTIMPSMCtrl 1
cm0_ts_PPRWRDRV 1
cm0_io_DLLCDLUpdateMon 2
cm0_ts_GeniusRepair 1
cm0_ts_MeasTaa 1
cm0_ts_ODLBData0En 1
cm0_ts_ODLBData1En 1
cm0_ts_ODLBRBSCLK 1
cm0_ts_ODLBResult 1
cm0_ts_ODLBDbuslat 1
cm0_ts_ODLBDbusDrv 1
cm1_ag_ReadSigSlaveOutEn 1
cm1_ag_ReadSigSlaveOut2MasterEn 1
cm1_ag_ReadSigSlaveOutMaster2DQEn 1
cm1_io_DLLCDLGATENBTI 1
cm1_fc_256T 1
cm1_fc_DLLGOff 1
cm1_io_DLLTDQSCKOption 3
cm1_io_DLLTDQSCKOption1Cap 3
cm1_io_DLLDCC1UpdSel 1
cm1_io_DLLDivRestore 1
cm1_ro_HPPRDisRef 1
cm1_io_DLLAntiHalfLock 1
cm1_ro_RefreshCompCtrl 4
cm1_fc_ContAgClk 2
```

### `test.run`（模板，用户期望的输出形态；注意 cm4/cm5 是原文件笔误，仅作结构参考）
```
Config_Timing(.ts_name("TS_3200"),.ck_mode(T_MIN),.t_mode(T_MIN),.duty_val(50));

PowerUp();
initialize();

compare_enable("all");
model_compare_enable("all");
begin:pattern_seq

	if ($test$plusargs("cm1"))begin
        tmload(.tm("cm1"), .width(1));
    end
	if ($test$plusargs("cm2"))begin
        tmload(.tm("cm2"), .width(1));
    end
	if ($test$plusargs("cm3"))begin
        tmload(.tm("cm3"), .width(1));
    end
	if ($test$plusargs("cm4"))begin
        tmload(.tm("cm5"), .width(1));
    end

end
```

### `run_script`（模板，3 行 vsim 命令，`-o +cm0/+cm1/+cm2`）
```
 /proj/drcpa/V0/sim/verilog/ddr5_tb/bin/vsim --msierun --local -sr test -q sverilog -l debugjkx -d "POST USESDFX   SHORTSIM USETF" -f 9200 -b "x16" -o +cm0 -g 171715944 & sleep 10s
/proj/drcpa/V0/sim/verilog/ddr5_tb/bin/vsim --msierun --local -sr test -q sverilog -l debugjkx -d "POST USESDFX   SHORTSIM USETF" -f 9200 -b "x16" -o +cm1 -g 171715944 & sleep 10s
/proj/drcpa/V0/sim/verilog/ddr5_tb/bin/vsim --msierun --local -sr test -q sverilog -l debugjkx -d "POST USESDFX   SHORTSIM USETF" -f 9200 -b "x16" -o +cm2 -g 171715944 & sleep 10s
```
固定前缀: `/proj/drcpa/V0/sim/verilog/ddr5_tb/bin/vsim --msierun --local -sr test -q sverilog -l debugjkx -d "POST USESDFX   SHORTSIM USETF" -f 9200 -b "x16" -o +` + `<SIGNAL>` + ` -g 171715944 & sleep 10s`

### `gen_pattern_files.pl`（原始脚本，生成每信号一个 .run，非合并 —— 用户要改造成合并版）
```perl
#!/usr/bin/perl
use strict;
use warnings;

while (<>) {
    chomp;
    s/^\s+|\s+$//g;
    next if $_ eq '';

    my ($signal_name, $width_num) = split(/\s+/, $_, 2);
    next unless defined $signal_name && defined $width_num;

    my $filename = "${signal_name}.run";
    open(my $fh, '>', $filename) or die "not create $filename: $!\n";

    print $fh qq(Config_Timing(.ts_name("TS_3200"),.ck_mode(T_MIN),.t_mode(T_MIN),.duty_val(50));\n);
    print $fh qq(\n);
    print $fh qq(PowerUp();\n);
    print $fh qq(initialize();\n);
    print $fh qq(\n);
    print $fh qq(compare_enable("all");\n);
    print $fh qq(model_compare_enable("all");\n);
    print $fh qq(begin:pattern_seq\n);
    print $fh qq(tmload(.tm("$signal_name"), .width($width_num));\n);
    print $fh qq(end\n);

    close($fh);
    print "DONE: $filename\n";
}
```

### `convert_signals.pl`（helper，可选：把带 `<N>` 后缀的展开信号折叠成「信号名 计数」；下轮 B 变体可用此逻辑反推）
```perl
#!/usr/bin/perl
use strict;
use warnings;

my %signal_count;
my @signal_order;

while (<>) {
    chomp;
    s/^\s+|\s+$//g;
    next if $_ eq '';

    my $base_name = $_;
    $base_name =~ s/<\d+>$//;

    if (!exists $signal_count{$base_name}) {
        push @signal_order, $base_name;
        $signal_count{$base_name} = 0;
    }
    $signal_count{$base_name}++;
}

foreach my $name (@signal_order) {
    printf "%s %d\n", $name, $signal_count{$name};
}
```

另：`cm.list`（36 行带 `<N>` 后缀的展开信号名，无 width）= convert_signals.pl 的输入侧；`cm_out`（27 行，与 cmlist 同内容）。两者非必需，A 档可只给 cmlist + 两模板 + 原始 .pl。

## 参考解（agent 在 trace 中已写出，逐字核对）

### `gen_pattern_files.py`（→ merged test.run）
```python
#!/usr/bin/env python3
"""gen_pattern_files.py - 读取 cmlist（每行 "信号名 宽度"），生成一个合并的 test.run 文件，
其中每个信号对应一个 if ($test$plusargs("信号名")) begin ... end 块。
用法: python3 gen_pattern_files.py <cmlist_path> [output_path]
默认 output_path = ./test.run
"""
import sys
import os

def generate(input_path, output_path):
    blocks = []
    with open(input_path, 'r', encoding='ascii') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(None, 1)
            if len(parts) < 2:
                continue
            signal_name, width_num = parts[0], parts[1]
            blocks.append((signal_name, width_num))

    if not blocks:
        print("ERROR: no valid entries found in input")
        sys.exit(1)

    with open(output_path, 'w', encoding='ascii') as out:
        out.write('Config_Timing(.ts_name("TS_3200"),.ck_mode(T_MIN),.t_mode(T_MIN),.duty_val(50));\n')
        out.write('\n')
        out.write('PowerUp();\n')
        out.write('initialize();\n')
        out.write('\n')
        out.write('compare_enable("all");\n')
        out.write('model_compare_enable("all");\n')
        out.write('begin:pattern_seq\n')
        out.write('\n')
        for name, width in blocks:
            out.write(f'\tif ($test$plusargs("{name}")) begin\n')
            out.write(f'\t\ttmload(.tm("{name}"), .width({width}));\n')
            out.write(f'\tend\n')
            out.write('\n')
        out.write('end\n')

    print(f"DONE: generated {output_path} with {len(blocks)} entries")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <cmlist_path> [output_path]")
        sys.exit(1)
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'test.run'
    generate(input_path, output_path)
```

### `gen_run_script.py`（→ run_script，每信号一行 vsim）
```python
#!/usr/bin/env python3
"""gen_run_script.py - 读取 cmlist，提取信号名，参考 run_script 模板，为每个信号生成一行 vsim 命令（-o +<信号名>）。
用法: python3 gen_run_script.py <cmlist_path> [output_path]
默认 output_path = ./run_script_gen
"""
import sys

TEMPLATE = (
    '/proj/drcpa/V0/sim/verilog/ddr5_tb/bin/vsim '
    '--msierun --local -sr test -q sverilog -l debugjkx '
    '-d "POST USESDFX   SHORTSIM USETF" -f 9200 -b "x16" '
    '-o +{name} '
    '-g 171715944 & sleep 10s'
)

def generate(input_path, output_path):
    names = []
    with open(input_path, 'r', encoding='ascii') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(None, 1)
            if len(parts) < 2:
                continue
            names.append(parts[0])
    if not names:
        print("ERROR: no valid entries found in input")
        sys.exit(1)
    with open(output_path, 'w', encoding='ascii') as out:
        for i, name in enumerate(names):
            if i > 0:
                out.write('\n')
            out.write(TEMPLATE.format(name=name))
        out.write('\n')
    print(f"DONE: generated {output_path} with {len(names)} commands")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <cmlist_path> [output_path]")
        sys.exit(1)
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'run_script_gen'
    generate(input_path, output_path)
```

### 参考 agent 实跑产物（msg[32] / msg[42]，对 A 档 cmlist）
- `test.run`：27 个 `if ($test$plusargs("<SIGNAL>")) begin` 块，每块 `tmload(.tm("<SIGNAL>"), .width(<W>))`，名字一致、width 取自 cmlist（1/2/3/4），footer `end`。
- `run_script_gen`：27 行 vsim，每行 `-o +<SIGNAL>`，信号名顺序与 cmlist 一致。

## 合成计划（下轮 fast-path，DEBT 1）

- **case_id**: `CmPatternRunGen-001`（C-A produce-task, digital）
- **A 档（trace-faithful）**: assets/<id>/ 下放 `cmlist`（上面 27 行原文）、`test.run`（模板）、`run_script`（模板）、`gen_pattern_files.pl`（原始）、`convert_signals.pl`。prompt 用 szcao 原话 U#8/U#26/U#34 拼接（不改写）。
- **交付物**: `submit.zip` 内含 `gen_pattern_files.py` + `gen_run_script.py`（或单一脚本两子命令）+ 在 B 上跑出的 `test.run` + `run_script_gen`。
- **B 隐藏变体**（hidden/，≥10 维全异于 A）: 另造一个 cmlist_B（不同信号名前缀如 `cm2_ts_*` / `cm3_io_*`、不同 width 分布含 5/6/8、不同行数如 18、含 `<N>` 折叠场景、空行/注释行干扰、信号名含下划线数字混合），加对应 test.run_B / run_script_B 期望结构。check 只跑 B。
- **check() ≥8 条（建议）**:
  1. submit.zip 解开含两个脚本（或单脚本）+ test.run + run_script_gen，可执行
  2. 在 B 上跑脚本 exit=0，生成 test.run
  3. test.run header 6 行齐全且顺序正确（Config_Timing/空/PowerUp/initialize/空/compare_enable/model_compare_enable/begin:pattern_seq）
  4. test.run 块数 == cmlist_B 有效行数 N
  5. 每块 `$test$plusargs("X")` 的 X 与同块 `tmload(.tm("X"), ...)` 的 X 完全一致（U#26 核心断言，反 hardcode cm<N>）
  6. 任一块都不出现 `cm<N>` 纯索引（即 X 必须来自 cmlist_B 信号名集合）—— 反 hardcode
  7. 每块 width == cmlist_B 该行的 width 值（解析对比，非子串）
  8. test.run 以 `end` 结尾 footer
  9. run_script_gen 行数 == N，每行含 `-o +<SIGNAL>`，SIGNAL 来自 cmlist_B 且顺序一致
  10. run_script_gen 每行含固定 vsim 前缀片段（`--msierun`/`-f 9200`/`-b "x16"`/`-g 171715944`）
  11. 3 个随机种子重跑结果一致（§4.5 确定性）
- **负样本**: (a) 空壳脚本；(b) 只 print A 档期望串的 stub；(c) 删 `tmload` 名字一致性逻辑的版本（让 `$test$plusargs("cm<N>")` 退回索引）—— 三个必须全 FAIL。
- **退化提交 §4.9**: 空壳/print-expected-A/core-deleted 全 FAIL。
- **anti-hardcode 关键**: B 的信号名/width/行数全异于 A，且 check 解析结构对比（非文本相似），索引退回版必挂在断言 5/6。

## 下轮操作清单
1. `python3 designflow/trace_ledger.py --shard A claim --session 1794482509558_n7ot5 --user szcao --host hfeg0pgn145 --match 55 --domain digital`（本轮已 claim 见 ledger）
2. scp trace（命令见顶部 trace 源行）→ 上述文件均已逐字记于本笔记，可直接落 assets，不必再 scp（除非要核对）。
3. 合成 assets/reference/hidden/negative → check.py → 自验（ref PASS + 3 neg + §4.9 + e2e）→ 追加 EDA-Eval-DesignFlow_A.jsonl。
4. `mark --session 1794482509558_n7ot5 --status case --case-id CmPatternRunGen-001`。
