# Deepread — 1795595688030_1wuoc (FineSim dlybias post-trim .mt0 后处理)

- **trace_source**: user=jasonxu, host=hfeg0plg93, session=1795595688030_1wuoc.messages.json, mc=296, domain=characterization
- **scan**: ssh_eda_search_20261128_192356/summary.tsv, B-strong (hspice:1035;analog:450;netlist:300;schematic:24;pyaether:24), FRESH (B 台账无)
- **trace size**: 1.13MB, 222 msgs (9 real user inputs / 173 assistant), agent=lead
- **真实上下文**: jasonxu 做 dlybias post-trim FineSim characterization。`n40.mt0` 是 27 组 (3 电压条件 LV/NV/HV × 9 corner [TT,FF,FS,SF,SS,FT,TF,ST,TS]) 的测量表，每组 `i_dlybias` 按原生步长 (5u→8u @50nA = 61 点) 扫，列含 `i_dlybias, voltage, dlybias2000p_rdelay_nomap, dlybias2000p_fdelay_nomap, alter#`。

## 用户真实意图（9 个 user_input 逐条）

1. **U#1 (msg0)**: 核心——按 `alter#` 分 27 组 (3 电压 LV/NV/HV × 9 corner)，过滤保留 `i_dlybias, voltage, dlybias2000p_rdelay_nomap, dlybias2000p_fdelay_nomap` + 电压/corner 标注；按 50nA 和 100nA 步进分别输出 rdelay/fdelay 最接近 2e-09 的 i_dlybias 点（4 个文件）。
2. **U#2 (msg28)**: 用步骤3 输出的 i_dlybias 值过滤 `p98.mt0`（次文件），保留对应行，输出 4 个文件。
3. **U#3-U#5 (msg40-91)**: 误触发 skill-creator → 纠正：把数据处理流程做成可复用 skill `process_dlybias`。
4. **U#5 (msg91)**: 支持任意电流范围（不再写死 5u→8u/61 行）+ 一次指令两文件 `process_dlybias, 文件1, 文件2`（位置区分 n40/p98，不要求文件名固定）。
5. **U#6-U#9 (msg131-218)**: 步长可自定义 `step=50n,100n,200n`；最后用 `step=300n,400n` 跑 sim1125_2 新数据（5u→9u/81 点）验证。

## 核心脚本语义（mt0_dlybias_process.py，判分要点来源）

- **alter→(cond,corner)**: 依据源网表 `1_dlybias_post_trim.sp` + `corner_sweep_finesim.sp`：3 电压 `.alter` 块 × 每块 9 corner `.alter` → alter 1-9=LV, 10-18=NV, 19-27=HV；corner [TT,FF,FS,SF,SS,FT,TF,ST,TS] 每电压内重复。
- **stride 子采样**: `stride = round(目标步长 / 原生步长)`，原生 50n 时 50n→stride1（全用）、100n→stride2（每第2点）、200n→stride4。
- **pick_closest**: 子采样里找 `*_nomap` 最接近 `TARGET=2e-09` 的 i_dlybias + 对应 voltage，输出 `abs_diff_to_2e-9 = |metric - 2e-09|`。
- **secondary 过滤**: 用 primary 各 step 选出的 i_dlybias 点（按 (voltage_cond, corner) 对应）过滤次文件，`abs_diff` 按次文件 metric 重算。
- **任意范围自适应**: 自动检测 i_dlybias 起止/原生步长（不再写死 5u→8u/61 行）。

## case 合成（已交付 EDA-Eval-DesignFlow-DlybiasMt0PostTrim-001，L1 judge-run LIVE-NA judge=[L0,L1]）

**reframe**: FineSim .mt0 二进制/项目网表依赖不可便携 → reframe 为 spec-JSON 驱动纯 Python `.mt0` 文本表格后处理器 `dlybias_post_trim.py <primary.mt0> <secondary.mt0> <spec.json> <out_dir>`。判分用独立 gold 复算（不同代码路径）。

**A (visible)**: 电压条件 LV/NV/HV，corner [TT,FF,FS,SF,SS,FT,TF,ST,TS]，target 2e-9，steps [50,100]，i_dlybias 5u→8u（原生 50n，61 点/组），rdelay 列 `dlybias2000p_rdelay_nomap`。
**hidden B (token-structurally 不相交)**: 电压条件 LO/MID/HI，corner [TT,SS,FF,FS,SF,ST,TF,TS,FT]（不同顺序），target 1.5e-9，steps [50,200]，i_dlybias 4u→9u（101 点/组），rdelay 列 `clkbuf_rdelay`。A 硬编器在 B 全错。

**check.py 17 断言** (a,b,sa 静态 + c..p L1.judge-run): a zip 入口 / b py_compile / sa 源码 alter+stride+abs 结构 / c B 跑出 report+4 step 文件 / d B report schema (n_groups==27+conds[LO,MID,HI]+B corner_order+target) / e B rdelay 50n gold 复算 / f B fdelay 50n / g B rdelay 200n (stride4 自适应) / h B fdelay 200n / i abs_diff 计算 / j B cond 映射 LO/MID/HI [neg] / k B corner 映射 (alter2->SS) [neg] / l B secondary 用 primary 点过滤+abs_diff 重算 / m cross-input A rdelay 50n / n A secondary abs_diff / o 确定性 B2 md5 / p anti-hardcode 源码无 A-only 字面量 [neg]。

**negatives (4, §4.9 trio distinct + hardcode_a)**: naive_empty→c / naive_print_expected→e / naive_core_deleted→g (stride 删, 200n 错) / naive_hardcode_a→c (硬编 A steps, 缺 B 200n 文件)。trio {c,e,g} 3-distinct。

**自验**: ref reference_solution.py → check.py 17/17 PASS；negative_selftest ALL_FAIL + TRIO_DISTINCT(c/e/g) + HARDCODE_FAIL；SKIP_RUN=1 deploy workdir clean no-leak + 4 attachments copied。

**trace_source**: user=jasonxu, host=hfeg0plg93, session_file=1795595688030_1wuoc.messages.json, match_count=296, real_task_summary="从 FineSim dlybias post-trim .mt0 测量表 (27 组 = 3 电压条件 × 9 corner) 按 alter# 分组, 过滤列 + 标注 voltage_cond/corner, 对 50nA/100nA 步进子采样找 rdelay/fdelay 最接近 2e-9 的 i_dlybias, 再用主文件电流点过滤次文件 p98.mt0; 后续要求任意电流范围自适应 + 自定义步长 + 一次指令两文件"。

r1400 按 plan 合成 DlybiasMt0PostTrim-001 交付。
