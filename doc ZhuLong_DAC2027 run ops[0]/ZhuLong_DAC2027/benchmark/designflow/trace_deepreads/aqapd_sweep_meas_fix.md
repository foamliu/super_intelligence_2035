# 深读：aqapd — IsmOsc sweep 测量数据收集 + summarize_meas.sh 修复

**trace**: session `1792635809821_aqapd` (user `johnl` / host `hfeg0pfn119` / mc=54 / 67 msgs / 491KB)
**domain**: digital（数字仿真 sweep 角点测量数据收集）· **shard A**

## 用户意图（UI#0 逐字原文，A-faithful 候选）
```
/rundata/drcoa/V0/simdir/finesim/workdir/johnl/simulation/drcoa_digital_T_IsmTop_schematic_ALPS    submit_ismosc_corner_meas.sh   summarize_meas.sh     利用这两个脚本完成superon_sweep_20261021_133105/的数据收集   你只能进行微小改动 主要利用现有的脚本能力 改动后确认diff改动必要性
```
- 规则②判定：用户提出目标（用两脚本完成 sweep 数据收集，只许微小改动，确认 diff 必要性），**未给根因、未给修复方案** → A-faithful ✓。
- 真实工作目录 `/rundata/drcoa/V0/simdir/finesim/workdir/johnl/simulation/drcoa_digital_T_IsmTop_schematic_ALPS`（finesim/ALPS 数字仿真，drcoa_digital_T_IsmTop）。

## 助手工具链与关键发现（trace [1]–[66]）
1. [1]–[18] 探查目录、读 `submit_ismosc_corner_meas.sh` + `summarize_meas.sh`，列 `superon_sweep_20261021_133105/`。
2. [20]–[28] 写 `_probe_sweep.py` 普查：FSDB 文件命名 `IsmOscTestSweep_sN.fsdb`（**749 个，单 sweep，无 `#N` 角点副本**）；4 个 measure `.sp` deck 在；`bsub`/`fscript` 可用；已有结果目录 `meas_result_by_corner_1021/corner0,corner1` 空目录（先前半成品）。
3. [29]–[37] 单样本 `fscript` 跑通（s0→~5.9s 产 `.mt0`，pass_flag=0 即脚本标 FAIL 属预期）。确认 **753 样本（s0..s752）全单 sweep，corner1/2/3 各匹配 0 文件**。`fsdb_measure_corner0.sp` 741 行 stale。
4. [38]–[44] 备份原脚本；跑「原」submit → 实际跑的是**已修复版**（条件生成有 FSDB 的 corner、直接 fscript 不 bsub -I），被 120s runner SIGKILL，但 fscript 后台继续跑。
5. [48]–[57] 关键澄清：**on-disk `submit_ismosc_corner_meas.sh` 已是 fixed 版**（注释「20261021 sweep 目录只含 base (corner0) FSDB，corner1-3 skip」）。fscript 后台跑完 **753 个 .mt0** 全在 `meas_result_by_corner_1021/corner0/`。
6. [58]–[62] 跑 `summarize_meas.sh`：产 corner0 summary（753 行）+ corner1（空），**在 corner2 `find: .../corner2: No such file or directory` 处 `set -e` 触发 exit 1 中止**，从未写 combined `all_corners_summary`。
7. [64]–[66] **金标修复**：备份 `summarize_meas.sh`，写 `_patch_summarize.py` 做**最小改动**——`find "$result_dir" -maxdepth 1 -type f -name '*.mt0'` 加 `2>/dev/null`（容忍缺失 corner 结果目录），show diff。trace 在 [66] 跑 patch 后截断（无最终输出），但意图清晰。

## .mt0 格式（trace [51] tail）
```
             vp1=  1.000000e+00
             ...
      pass_flag=  0.000000e+00
   last_pls_pre0=      failed
 edge_is_0_or_17=  0.000000e+00
*** End of measure ... 2 error(s) 1 warning(s).
```
- `pass_flag=  1.000000e+00` = PASS；`0.000000e+00` = FAIL。
- `last_pls_pre0` 可为浮点或 `failed`。

## summarize_meas.sh 行为（trace [61]）
- 遍历 corner0..3；每 corner `find $result_dir -maxdepth 1 -type f -name '*.mt0' | sort_by_sample_number > $input_list`（**bug：缺失目录 + set -e/pipefail 中止**）。
- 解析每 .mt0 的 `pass_flag`；FAIL 打印 `[ALARM] cornerN sample=sN pass_flag=... file=...`。
- combined `all_corners_summary` 在循环后写；bug 中止在 corner1/2 → combined 永不写出。
- 任一 FAIL → exit 2（summary 已写后）。

## 金标（候选交付）
- **patched `summarize_meas.sh`**：最小改动——在 find 前加 `[ -d "$result_dir" ] || continue` 守卫（或等价：`find ... 2>/dev/null | sort || true`），使缺失 corner 目录不再中止；保留 `set -e`、保留 corner 循环、保留 [ALARM]/exit-2 语义。
- **`all_corners_summary.csv`**：在 fixture_A（corner0 8 样本，1 FAIL）上跑 patched 脚本产出。
- **`fix_report.md`**：diff + 必要性说明（find 遇缺失 corner 结果目录 + set -e/pipefail 中止 → combined summary 不写出）。

## fixture 方案（自包含 L1，不跑 fscript/ALPS）
- **fixture_A（assets，SUT 可见）**：`summarize_meas.sh`（original buggy，set -eu + pipefail + unguarded find）、`submit_ismosc_corner_meas.sh`（fixed 版，仅作上下文）、`meas_result_by_corner_1021/corner0/s0..s7.mt0`（7 PASS + 1 FAIL），corner1/2/3 目录缺失。
- **fixture_B（hidden，不进 SUT 沙箱）**：corner0 5 .mt0（4 PASS + 1 FAIL）+ corner1 3 .mt0（全 PASS），corner2/3 缺失。不同样本数 + corner1 在场 → cross-input + anti-hardcode。
- 判分 = subprocess 在 fixture_A/B 上跑候选 `summarize_meas.sh`，断言结构（all_corners_summary 存在/行数/FAIL 标记/cross-input corner1）+ 最小 diff + set -e 保留 + anti-stub（B 行数 ≠ A）。

## 候选发现路径（SUT 应走）
1. 读两脚本 + 列 `meas_result_by_corner_1021/` → 发现 corner0 有 .mt0（submit 已跑），corner1/2/3 缺。
2. 跑原 `summarize_meas.sh` → 在缺失 corner 处 set -e 中止，无 all_corners_summary。
3. 最小改动守卫 find → 跑通 → 产 all_corners_summary。
4. 写 fix_report（diff + 必要性）。
