# trace_deepread: 546be — compare_wave.pl vs compare_wave_ddr5.pl 合并对比

## trace 来源
- session: `1792394160673_546be` (directory on host)
- user: rongjiez @ hfeg0plg98 (10.129.8.230)
- mc: 17, domain: waveform
- messages: 23 msgs, 2 substantive user turns

## 用户逐字原话

**U#1 (idx=0)**:
> @compare_wave_ddr5.pl @compare_wave.pl 这两个脚本适用于不同的项目，请仔细分析这两个脚本的区别和相同，方便我后续进行合并

**U#9 (idx=15)**:
> @compare_wave_new.pl 这个是我已经写好的合并后脚本，帮我分析一下有没有什么问题，不要修改我的任何文件

（本 case 取 U#1 为任务说明——A-faithful「提出需求」轮；U#9 是后续「审合并稿」轮，不进 prompt。）

## 真实脚本（on-disk 取得）

路径：`/home/rongjiez/jira_dev/compare_wave/scripts/`
- `compare_wave_ddr5.pl` — 1794 行，DDR5 项目，38 个 sub
- `compare_wave.pl` — 2126 行，non-DDR5 项目，51 个 sub
- `compare_wave_new.pl` — 1965 行，用户已写好的合并版（含 `grouping`/`_ddr5_groups`/`_nonddr5_groups` 分派）

两脚本同源（同一作者 Leozhao 的 Revision History v1.1a 2019/05/23 起），随项目演进分叉。

## 关键异同（代码证据）

### 相同（shared）
- 共享 Revision History 头（Leozhao v1.1a→v2.2a）
- 7 个共享 sub：`compareSignal` / `parse_result` / `addToleranceForExpVecFile` / `readFile` / `divideTimeRange` / `parse_floating` / `getFirstSignal`

### 不同（differences）
- **项目标记**：ddr5 `our $PROJECT="DDR5"` vs wave `our $PROJECT="nonDDR5"`
- **ddr5 独有 sub (5)**：`Compare_with_rangeShiftTime` / `chkXtypeFromVec` / `compareZtypeSig` / `getShiftedRange` / `extraChkDqs_c`
- **wave 独有 sub (7)**：`main` / `clearTmpFile` / `chkZXtypeFromVec`（合并 Z+X 检测，vs ddr5 拆分 `chkXtypeFromVec`+`compareZtypeSig`）/ `findNewDq0` / `getVolatge` / `exportDataFromFsdb` / `getCompareTime`
- **共享 sub 签名分叉**（arg count）：
  - `compareSignal`: ddr5 6 args vs wave 13 args（wave 多 dq_flag/dqs_shift/dq0shift/dq_shift/shift_tol/dqst/dq0）
  - `parse_result`: ddr5 4 args vs wave 11 args
  - `addToleranceForExpVecFile`: ddr5 1 arg vs wave 2 args（wave 多 tolerance）
  - `divideTimeRange`: ddr5 1 arg vs wave 2 args（wave 多 inc_step）
  - `readFile`: ddr5 1 arg vs wave 2 args
  - `parse_floating`: wave 多 `return "NA" if !defined` 守卫
- **main 入口**：wave 有 `sub main{...}` 显式入口，ddr5 无 main sub（顶层执行）

## case 设计

- **套 #254 v2 code-grounded answer-extraction reframe**（同族 636qr refactoring-summary / 7sgr2 mechanism-explanation / 9imo1 code-debug）
- 用户意图=对比异同为合并准备，design_flow 契约需在隐藏 B 上跑候选 → reframe 成 code-grounded script-compare+review tool
- 候选写 `script_compare.py` 读两 Perl 脚本 + 问题 → 结构化 JSON（shared_subs/unique_to_a/unique_to_b/differences/similarities/merge_review/cited_identifiers），cited_identifiers 必须 grounded 于真实源码
- **data-driven 2×2+degenerate**：A(ddr5 vs wave) / B1(ALPHA vs BETA 中性命名不同 sub 集) / B2(GAMMA vs DELTA 第三组 sub 集) / B3(两同脚本→优雅降级)
- **反硬编码**：B 用中性命名（range_shift_cmp/cmp_signal/parse_res 等），A 专属标识符（Compare_with_rangeShiftTime/findNewDq0/DDR5/Leozhao 等）不泄入 B 输出
- **check.py 15 cond a-o**：REF PASS 15/15 + 6 negatives 全 FAIL + §4.9 三退化全 FAIL + k_rationale==k_check==15≥8

## 交付
- case_id: EDA-Eval-DesignFlow-ScriptCompareMergeReviewQA-001
- D.jsonl 421→422(+1)
- ledger_D 546be → case
