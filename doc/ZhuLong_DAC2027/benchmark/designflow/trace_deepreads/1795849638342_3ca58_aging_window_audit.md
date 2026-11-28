# trace_deepread: 1795849638342_3ca58 — DDR6 Aging001 老化窗口跨 corner 差异诊断

- **session**: `1795849638342_3ca58` (tongfanl @ hfeg0pkn005, mc28, 37 msgs)
- **domain**: digital / verification (DDR6 dscqa 验证, xrun/Xcelium 数字仿真)
- **keywords**: verilog:262; analog:71; netlist:9; aether:2 (verilog 主导, analog 来自 "Aging" 词面)
- **trace 源**: `/home/tongfanl/.cline/data/sessions/1795849638342_3ca58/` (.75 hfhds201 本机, 经 fullscan 160229 发现)

## 用户真实意图 (msg[0] 原话)
> /proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen_local/log/stimulus_tongfanl/Aging_1127_Aging001_bls 三个corner抽出来的激励时间（xrun.log中的aging_start   aging_stop）不一样是咋回事儿？？？

诊断型追问：为何 3 个 corner (FF/TT/SS) 的 xrun.log 里 aging_start/aging_stop 激励时间不一致。

## assistant 调查链 (policy-engine enforced, python-runner/shell-runner)
1. `aging_probe.py` → grep 3 corner xrun.log 的 aging_start/aging_stop
2. `aging_grep.py` (SIGKILL 超时) → `aging_sym.py` 解析软链 → 定位真源 `bakup/bakup1106/`
3. `aging_target.py` → grep pattern 源, 找到 aging_start/aging_stop 是 `Aging001_Perbank_Normal.v` 的 `$display("aging_start=%0t", $time)` / `$display("aging_stop=%0t", $time)` 窗口标记
4. `aging_timing.py` → 对比 3 corner 的 timing_table (tCK_min/tCK_max/tCK2DQI 等)

## 关键实测数据 (msg[13] / msg[36])
| corner | aging_start | aging_stop | 老化窗口 (stop-start) |
|---|---|---|---|
| FF | 361063 | 2081751 | 1720688 |
| TT | 361063 | 2081751 | 1720688 |
| SS | 361063 | **2127503** | **1766440** |

- aging_start 三 corner 完全一致 (361063 ps)
- 只有 **SS corner 的 aging_stop 偏长** (~45.75ns / 45752ps)
- 根因: aging_start/aging_stop 是 per-bank aging body 的 $display 窗口标记; 各 corner 的 timing_table 不同 → per-bank aging body 消耗的 wall-clock sim 时间不同 → SS 的 aging_stop 落点偏后

## xrun.log 格式 (从 trace tool_result msg[12]/msg[35] 复原)
```
xmvlog: *W,VARIST (...) Local static variable ...
	+xmlibdirpath+/tmp/tongfanl_<ts>Aging001_Perbank_Normal_..._<corner>_...
	+define+AGING
		Simulation timescale:        1ps
aging_start=<int ps>
aging_stop=<int ps>
Job:tongfanl_<ts>..._<corner>_... is done @<date>
```

## case 取材 (A 档 trace-faithful)
- **交付物形态**: `aging_window_audit.py` 脚本, 输入 `--root <corners 目录>` (每 corner 子目录含 xrun.log), 输出结构化 JSON 老化窗口审计报告
- **A (可见)**: 3 corner xrun.log, 用 trace 实测真实值 (FF/TT=2081751, SS=2127503, outlier=SS)
- **隐藏 B**: 2 组不同 corner 集 (B1: TT 离群 / B2: 无离群全等), 不同 aging 值 + 不同离群 corner, 防 A 硬编码
- **判分**: 12 断言 (subprocess 真跑候选脚本 on B, 断言 JSON 结构 + 逐 corner aging_start/stop + window=stop-start + outlier_corners + window_mode + window_spread)
- **negatives**: fake_empty / fake_print_expected(硬编码 A) / fake_core_deleted(只 parse start 不算 window) 全 FAIL
- **自验**: ref check PASS + neg_selftest OK (ref PASS + 3 neg FAIL) + SKIP_RUN=1 结构合法 (4 attachments 全部署, workdir clean)
- **case id**: EDA-Eval-DesignFlow-AgingWindowAudit-001 (domain=digital, judge_layers=[L0,L1])

## 备注
- 源 log 目录 `/proj/dscqa/.../Aging_1127_Aging001_bls/` 在 .75 上 Permission denied (同 r1541 vsim.pl 先例), xrun.log 内容从 trace tool_results 复原, 真实值保留 (不脱敏铁律)
- fullscan 160229 (r1567) 的 3 个 shard_A_new 中, 8lcjv/rg6di 为 D 域 drift (netlist/hspice 主导, synopsys:14 偶命 A 放宽词), 仅 3ca58 为 genuine A 域
