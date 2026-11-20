# deepread — sid 1794538392384_ueq86 (e0046686@10.129.2.14, mc13, schematic_netlist)

**trace**: 168 msgs / 4 clean user turns / 1.04MB messages.json (scp via .75 → 10.129.2.14 OK at 23:30; ssh/scp auth turned flaky afterward,但 messages.json 已抓全).

## 用户意图（U0 + 附件 TASK_HACK_SPF.md，逐字）
> 参考net_replace_for_large_spf.py脚本，做一个新的spf替换工具：
> 1. 源文件为形如 `HD1P_CXN4S1P8X16M1B1C1R1W1BW1RE1.dspf.TYPICAL_25_1` 的 spf 文件，生成 `..._hack.dspf.TYPICAL_25_1`（在文件名后新增 `_hack` 后缀，前缀和文件类型不变，**类型分隔符不是最后一个点**——即 `.dspf.` 处插入 `_hack`）。
> 2. 将 spf 中 `XXbitcell_crr_row` 开头的行，根据 MIPM0/MINM0 等不同管脚，将 solido.inc 中的 parm 追加到对应行；管脚与参数映射参考 725451~725456 行示例 case；**6 个管脚一组，parm 6 组**，所有 MIPM0 管脚追加的 parm 相同。
> 3. solido.inc 的 parm 分不同工况；一个 spf 只用一个工况下的 parm。
> 4. 工况需匹配：源工况 `tt_0p75v_25c` 标准形式，匹配 solido.inc 工况（rsnm/wm、process ssg/tt/fg、电压 0.54↔0p54v / 0.75↔0p75v、温度 125↔125c / 025↔25c）。
> 5. 大 instance spf 可能数 G~数十 G，要考虑性能（参考 net_replace_for_large_spf.py）。
> 6. 命令行 + import module 两种使用方式。

U2/U3 关键修正：**匹配行扩大为所有 `XXbitcell_` 开头的行**（不止 `XXbitcell_crr_row`，含 row1_crl/row1_l/row1_r 共 4 变体）；**追加的是 solido.inc 对应工况中参数的具体数值**（如 `sda_rnd_mis_0_local=1.4754085682340943`），**不是符号名**（`sda_rnd_mis_0_local=pd_t_0` ❌）。

## 助手工具链
list_allowed_files → read_files(net_replace_for_large_spf.py + README + runme.sh + solido.inc:1-150 + spf:725440-725480 + spf:1-30 + spf:725451-725457) → editor 写 _analyze_spf_tmp.py 统计 XXbitcell_ 变体/管脚分布（960 行 = 6 管脚×160，4 变体 crr_row/row1_crl/row1_l/row1_r）→ editor 分块写 parm_hack_for_large_spf.py（头部文档 → 常量/工况解析 → solido 解析/匹配 → 变换核心 → 主流程 → CLI）→ editor 写 _test_parm_hack_tmp.py 验证 → 多轮 editor 修数值追加/幂等剥离/corner 标准命名匹配 → _perf_test_tmp.py 500MB 性能 sanity → 更新 README。

## 关键格式（真实，从 trace tool_results 抓取）

### solido.inc（多工况段）
```
*rsnm_ssg_0.54_125_5sigma
.param pd_t_0 = 1.4754085682340943 pd_t_1 = 0.8690608341134444 ... pd_t_8 = 1.1031616683668493
.param pd_b_0 = 0.009067954225661527 ... pd_b_8 = 0.10985534328198218
.param pu_t_0 = 1.7515865517451896 ... pu_t_8 = -0.2138373237208962
.param pu_b_0 = 1.2638115644694317 ... pu_b_8 = -0.17037332526914684
.param pg_t_0 = 0.33389705608405457 ... pg_t_8 = -0.515715262655312
.param pg_b_0 = 1.0501942043686296 ... pg_b_8 = 0.7644555035908991

*wm_5fg_0.54_025_5sigma
.param ...
```
- 工况头：`*{type}_{process}_{voltage}_{temp}_{sigma}`（type ∈ rsnm/wm，voltage 形如 0.54，temp 形如 125/025）。
- 6 组 .param：pd_t / pd_b / pu_t / pu_b / pg_t / pg_b，每组 9 个值（index 0-8）。

### DSPF XXbitcell_ 行（725451-725456 示例 = 期望产物）
```
XXbitcell_crr_row1[0]g.XIbitcell_4x1[0].XICELL[0].MIPM0 Xbitcell_crr_row1[0]...:d Xbitcell_crr_row1[0]...:g VDD VDD hd_pu_fs l=6e-09 ... u0mult=1 sda_rnd_mis_0_local=pu_b_0 sda_rnd_mis_1_local=pu_b_1 ... sda_rnd_mis_8_local=pu_b_8
```
- 实例名首字段 `XXbitcell_<variant>[<i>]g.<path>.<pin>`，**管脚 = 首字段按 '.' 分割的最后一段**（如 MIPM0）。
- 示例行写的是符号名 `pu_b_0`，但 U3 明确要求**数值**。

### 管脚 → 参数组 映射（来自 725451-725456，**不规则**，不可由 model 名推断）
| 管脚 | model | 参数组 |
|---|---|---|
| MIPM0 | hd_pu_fs | pu_b |
| MIPM1 | hd_pu_fs | pu_t |
| MINM0 | hd_pd_fs | pd_b |
| MINM1 | hd_pd_fs | pd_t |
| MINM2 | hd_pg_fs | pg_t |
| MINM3 | hd_pg_fs | pg_b |
注：MIPM0/MIPM1 同 model（hd_pu_fs）但组不同（pu_b/pu_t）→ 必须用显式映射表，不可按 model 推断；MINM2→pg_t、MINM3→pg_b（数字-组对应不规则）是关键 gotcha。

### 工况匹配（四维）
标准入参 `{process}_{voltage}v_{temp}c`（如 `ssg_0p54v_125c`、`tt_0p75v_25c`、`fg_0p75v_025c`）+ `--mode rsnm|wm`。匹配 solido 工况段的 (type=mode, process, voltage, temp)，须唯一。
- 电压：`0p54v`→0.54、`0p75v`→0.75、`0p9v`→0.9。
- 温度：`125c`→125、`25c`→25、`025c`→25（去前导 0）、`0c`→0。

## 助手最终产物（接口）
`parm_hack_for_large_spf.py`：
- CLI：`--spf <dspf> --solido <inc> --corner <std> [--mode rsnm|wm] [-j N] [--dry-run] [--output <path>] [--copy-first]`
- module：`hack_spf(spf, solido, corner, mode=None, output=None, quiet=True) -> ret{path,stats,elapsed}`
- 输出文件名：在类型分隔符 `.dspf.`/`.spf.` 前插 `_hack`（非最后点）。
- 流式单遍 + 大文件可选并行分块；幂等（先剥离旧 `sda_rnd_mis_\d+_local=` 再追加）。
- 追加 9 个 ` sda_rnd_mis_{i}_local={数值}`（i=0..8），值取自匹配工况段的 `{group}_{i}`。

## 合成计划（case_id: EDA-Eval-DesignFlow-SpfBitcellParmHack-001）
- SUT 产通用 `parm_hack_spf.py`（纯 stdlib CLI `--spf --solido --corner [--mode] [--output]`）。
- 可移植化：真实 spf 数 G 私有 → 合成小 DSPF（XXbitcell_ 6 管脚 × 多变体 + decoy 非 bitcell 行 + 已 hack 旧行测幂等）；真实 solido.inc → 合成多工况 inc，各工况数值明显不同反硬编码。
- visible A：sample_A.dspf.TYPICAL_25_1 + solido_A.inc（3 工况）+ TASK_HACK_SPF.md（真实规格）。
- hidden B：sample_B.dspf.SS_0p54v_125c（不同 design/变体分布/含已 hack 旧行）+ solido_B.inc（4 工况，含同 process/voltage/temp 但 type 不同的干扰工况测 mode 区分）+ corner=ssg_0p54v_125c mode rsnm。
- hidden C（跨输入反硬编码）：sample_C.dspf.FG_0p75v_025c + solido_C.inc + corner=fg_0p75v_025c mode wm。
- check.py 18 cond a-r（内嵌独立 oracle 重解析 solido_B/C 自算期望数值，非文本相似）：zip合法仅1个.py / py_compile / 不硬编码A字面量 / B运行exit0 / B输出名正确(_hack插在.dspf.前) / B非XXbitcell行原样 / B每XXbitcell行追加9个sda_rnd_mis / B MIPM0值==oracle(pu_b) / MINM0==pd_b / MIPM1==pu_t / MINM1==pd_t / MINM2==pg_t / MINM3==pg_b / B值是数值非符号名 / B幂等(重跑同corner不变 + 重跑换corner值更新) / B工况type区分(值来自rsnm段非wm段) / C跨输入MIPM0==oracle(wm段pu_b 反硬编码A/B) / C非XXbitcell行原样。
- 4 neg（empty→d/e / print_only→e / hardcode_a→h / core_removed→g）ALL FAIL distinct labels。
- §4.9 三假（空壳/只print/删核心）全 FAIL。
- k_rationale=k_check=18≥8 ✓。
