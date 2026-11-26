# Deepread: ie8du — Mt0AggMinMax (FineSim .mt0 aggregation)

## Trace source
- session_file: `1793947529316_ie8du`
- user: `declanzh` @ host `hfeg0plg97`
- mc: 0 (un-ledgered, found via 11-11 06:1x fresh-window scan of 13 NEW spice-active hosts mtime≥11-10 00:00)
- file: `/home/declanzh/.cline/data/sessions/1793947529316_ie8du/1793947529316_ie8du.messages.json` (1.37MB, 498 msgs)
- scan evidence: `rescan_1111_0612.md` (29 un-ledgered from 11 hosts; 28 peeked, 1 CLEAN produce-task = ie8du)

## User intent (clean produce-task)
- U#0/U#1: `/rundata/drcoa/V0/simdir/hspice/declanzh/a51_VfsblnPumpCore_SIM/spf_result/core1103` (path only, twice — user pasting dir)
- **U#2 (主任务)**: "帮我把这个文件夹下后缀为.mt0的文件数据汇总到一个文档，并给出每个参数的最大/最小值"
- **U#24 (refinement, 方向性指示非根因)**: "按绝对值/换算成mA为单位"
- §A-② 判定: U#2 + U#24 均为「提出需求/表达目标」，未指出根因或修复方案 → A 档可用；但 conversation 后续演化成 SKILL.md 创建（498 msgs），核心交付仍为 .mt0 聚合脚本 → 采用 **B-synthesized with faithful prompt**，聚焦 U#2+U#24 核心任务。

## .mt0 file format (FineSimPro measurement output, from MSG #10 tool_result)
```
$DATA1 SOURCE='FineSimPro' VERSION='V-2023.12-1' PARAM_COUNT=0
.title 'typ'
       i_vfsbln   i_vwlp_fsbln          ieff.         temper         alter#
     1.1058e-02    -3.5830e-02     3.0862e-01     8.5000e+01     1.0000e+00
```
- Line 1: `$DATA1 SOURCE='FineSimPro' ...` (header, skip)
- Line 2: `.title '<corner>'` (corner name: '', 'typ', 'ff', 'ss', etc.)
- Line 3: column headers (i_vfsbln, i_vwlp_fsbln, ieff., temper, alter#)
- Line 4: one data line (5 floats): a, b, c, t, alter
  - i_vfsbln: Vfsbln 支路电流 (A, 通常正)
  - i_vwlp_fsbln: Vwlp_fsbln 支路电流 (A, 通常负)
  - ieff.: 电流效率 (无量纲, 0.30~0.31 → ×100 = 30~31%)
  - temper: 温度 (°C)
  - alter#: 仿真 run 编号

## Real data (77 files, MSG #20/#62 stdout)
- i_vfsbln: min=7.7241e-03 A (#54, 130°C), max=1.5693e-02 A (#67, -40°C)
- i_vwlp_fsbln: min=-5.0686e-02 A (#67, -40°C), max=-2.5280e-02 A (#54, 130°C)
- ieff.: min=3.0186e-01, max=3.1187e-01
- Temperatures: -40°C (44 files), 85°C (1), 130°C (32)
- abs(mA): i_vfsbln 7.7241~15.6930 mA; i_vwlp_fsbln 25.2800~50.6860 mA; ieff 301.86~311.87 mA

## Assistant tool chain
1. `list_allowed_files` core1103 dir → list .mt0 files
2. `read_files` 2 sample .mt0 → understand format (MSG #10)
3. `read_files` /home/declanzh/parse_mt0.py + parse_delay_mt0.py (existing parsers, MSG #16)
4. `editor` create `/home/declanzh/a51_mt0_summary.py` (MSG #17) — parse + min/max + write summary
5. `run_approved_command` python-runner → run script (MSG #19) → success, 77 files parsed (MSG #20)
6. `read_files` core1103_mt0_summary.txt → verify output (MSG #21/#22)
7. U#24 refinement → multiple editor attempts (corrupted edits, MSG #25-41) → create mt0_summary_v2.py (MSG #43) → fix corruption → run → success with mA+abs (MSG #62)
8. Later evolution: mt0_summary_v3.py with per-temp grouping, ieff%, short filenames (#NN); then SKILL.md creation; then FuseSense_SKILL.md rename to skill_sum/ (MSG #484-497)

## Final accepted deliverable (核心)
`mt0_summary_v2.py` / `mt0_summary_v3.py`:
- scan dir for *.mt0
- parse each: skip $/./header, find data line (5 floats)
- compute per-param: original (A) min/max, abs (mA = A*1000) min/max
- group by temperature
- write summary .txt to same dir

## Case design (B-synthesized, L1, spice_sim)
- case_id: EDA-Eval-DesignFlow-Mt0AggMinMax-001
- deliverable: `mt0_agg_minmax.py` CLI `<dir> <output.txt>` (stdlib only)
- assets A: 12 .mt0 files (3 temps × 4 files), config.json, example_output_A.txt, task_brief.md
- hidden B1: 15 .mt0 files (4 temps, different value ranges, different corner names)
- hidden B2: 10 .mt0 files (3 temps, reverse value distributions) — 反硬编码
- check.py: 12 assertions (a-l):
  a. zip 含 mt0_agg_minmax.py
  b. py_compile 通过
  c. B1 exit code 0
  d. 输出文件存在且非空
  e. 输出含 3 参数名 (i_vfsbln, i_vwlp_fsbln, ieff)
  f. 输出含 "mA" 单位标识
  g. 输出含 B1 正确文件数
  h. i_vfsbln abs mA min/max 在 B1 真值容差内
  i. i_vwlp_fsbln abs mA min/max 在 B1 真值容差内 (验证负值取 abs)
  j. ieff abs mA min/max 在 B1 真值容差内
  k. 输出含原始值 (A) 区段
  l. 反硬编码: B2 真值 ≠ B1 真值 (脚本在 B2 跑出 B2 真值)
- negative: 6 stubs (empty/only-print/hardcoded-a/no-parse/ref-core-deleted/naive) 全 FAIL
- §4.9 三假: empty_shell→c, only_print→c, ref_core_deleted→h 全 FAIL
- 真跑候选: subprocess 在 B1/B2 上执行脚本 (§4.2)
- 随机化: B1/B2 数值不同, 反硬编码

## 体积
- task_brief.md ≤3 行 (交付接口+文件位置, 不写「要做什么」)
- prompt 用真实场景 (declanzh/hfeg0plg97/core1103 真路径, FineSim .mt0 真格式)
