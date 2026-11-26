# p64wo — MRR enops delay (DDR6 Verilog TB)

- **session**: 1791526663956_p64wo.messages.json
- **user/host**: tongfanl / hfeg0plg53 (10.129.35.69)
- **mc**: 291 · **size**: 6.08MB · **msgs**: 253 (142 user)
- **domain**: waveform (DDR6 testbench timing) · **track**: A-faithful

## U#0 (提需求, 原文)
```
tbcontrol.timingcal="none";
      MRR(.ma(8'hDF));
      MRR(.ma(8'hE0));
      MRR(.ma(8'hE1));
      MRR(.ma(8'hE2));
tbcontrol.timingcal="auto";
帮我改一下，在MRR中加enops，使得MRR之间的delay时间为Max(5ns, 16nCK)
```
干净提出需求轮：用户给目标(加 enops + delay=Max(5ns,16nCK))，未给根因/修复实现 → A-faithful 合格。

## agent 行为 (U#0 → A#157)
- 66 read_files + 47 list_allowed_files + 9 search_codebase + 3 run_commands(grep) + 3 editor
- 大量搜索 MRR task 定义 / enops 用法 / timingcal 模式（Basic.v / ddr6_test.sv / Include）
- **U#0 最终以 TEXT 给出修改方案**（未 editor 写盘，3 个 editor 用于后续 U#158+ 的 WTM001/002 检查）
- A#157 gold answer:
```systemverilog
int mrr_delay_enops;
mrr_delay_enops = (5000 > 16 * timing.tCK) ? (5000 / timing.tCK) : 16;
tbcontrol.timingcal = "none";
  MRR(.ma(8'hDF), .enops(mrr_delay_enops));
  MRR(.ma(8'hE0), .enops(mrr_delay_enops));
  MRR(.ma(8'hE1), .enops(mrr_delay_enops));
  MRR(.ma(8'hE2), .enops(mrr_delay_enops));
tbcontrol.timingcal = "auto";
```
- enops = Max(5ns, 16nCK)：5ns=5000ps, 16nCK=16*tCK；tCK=1250ps → 16*1250=20000ps=20ns → Max=20ns → 20ns/1.25ns=16 cycles（nCK 分支胜出）
- 用户接受（转 U#158 检查 WTM001/002 pattern）→ 隐式接受

## 后续 user turns (不进本 case)
- U#158 检查 WTM001/WTM002_normal_check.v 有无问题
- U#175/187/201/203/205/209 Load_Mode task / MR 设置 / exp_data 方案讨论
- U#225 方案二省略默认参数
- U#243/249/251/252 反复检查 WTM pattern

## 合成 (A-faithful, L1-boundary waveform)
**EDA-Eval-DesignFlow-MrrEnopsDelay-001**：gen_mrr_enops.py 读 config.json → 参数化打印 Verilog 片段
- enops 三元式 `(delay_ns*1000 > delay_nck * tCK_PS) ? (delay_ns*1000 / tCK_PS) : delay_nck`
- localparam tCK_PS = tck_ps；MRR 调用 .ma(8'hXX)+.enops(mrr_delay_enops)，timingcal none/auto 包裹

### 资产
- A: config_A.json (delay_ns=5, delay_nck=16, tck=1250, ma=[DF,E0,E1,E2], out=mrr_enops.sv) + prompt.txt(U#0 原文) + task_brief.md
- hidden B: config_B.json (delay_ns=12, delay_nck=4, tck=625, ma=[A0,A1,B2,C3,D4], out=mrr_enops_B.sv) — **ns 分支胜出**：12000 > 4*625=2500 → 12000//625=19 cycles（与 A 的 nck 分支路径不同，测两条 ternary 路径）；ma 数 5≠4

### check.py 15 条件 a-o
a zip含gen · b py_compile · c 跑B退0出sv · d timingcal none 在 MRR 前 · e auto 在 MRR 后 · f 每 B ma 出现 · g 每 MRR 含 .enops() · h 三元式 B 操作数(12000>4*tCK_PS)?(12000/tCK_PS):4 · i enops=19(ns 分支) · j enops_param=enops · k ma_param=ma · l mrr_task=MRR · m 跨输入护栏(DF/E0/E1/E2+5000/1250/16 不泄漏, B 值齐) · n 3seed sha256 一致 · o 退化守卫(MRR==5, enops 非裸字面量, localparam tCK_PS=625)

### 自验
- ref PASS 15/15
- 4 negatives ALL-FAIL distinct: fake_empty→(d) / fake_print_fixed_A→(f) / fake_core_deleted→(h) / naive_no_max→(h)
- §4.9 三假 (d/f/h) 3-distinct ✓
- test==disk roundtrip EXACT (sha 457e783509)
- k_rationale=k_check=15 ✓
- D.jsonl 67→68 · mark p64wo case

教训：698 台 cline session 路径为 `<anchor>/<anchor>.messages.json`（目录级，非 flat）；peek 须用完整 `<ts>_<short>` anchor + hostname（非 IP）。本 case gold 为 text 答案（非文件写盘），靠参数化 gen 落地为可验交付。
