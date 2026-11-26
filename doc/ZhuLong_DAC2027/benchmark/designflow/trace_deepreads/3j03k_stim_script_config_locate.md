# Deep-read: 1794023372474_3j03k (tongfanl @ hfhds201)

**Case**: EDA-Eval-DesignFlow-StimScriptCfgLocate-001
**Domain**: spice_sim · **Track**: A-faithful · **Level**: L1
**Trace**: 26 msgs, 279KB, dir-based, 2026-11-07 11:50

## 选轮

**U#0** (任务说明轮，逐字作 prompt)：
> /proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen  在这个环境里帮我找下当时抽激励的脚本和配置文件。
> 之前跑的是Golden009_Multi4bank_bankskew pattern
> -l的位置是log_2026_Vcap/Designer/1017_bankskew
> 如果找不到就在/proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen_local里找找
> 重点找cfg_files和runsti文件夹

用户**提出需求**，无根因/修复方向 → 符合 A-档选轮规则。全 trace 仅此一个需求轮（后续全为 assistant 工具轮 + 总结），无澄清/猜测轮。

## 金标准 (assistant 实际产物)

assistant 用 list_allowed_files(10) + read_files(5) 遍历：

1. **主目录** `vecgen/runsti/gen_stimulus_bankskew`（已改过）：
   - 6 行并行 d6vecgen 调用，`-l log_2026_Vcap/Designer/1030_bankskew_fixnopissue`（**非 1017**）
   - `-f` 指向 `runcfg/run_bankskew_cfg_sc0_2p3` 等（绝对路径）
   - `-r` 指向 `vecgen_local`

2. **_local** `vecgen_local/runsti/gen_stimulus_bankskew`（原始版本）：
   - 1 行 d6vecgen：`-l log_2026_Vcap/Designer/1017_bankskew`（**匹配 1017**）
   - `-f cfg_files/run_bankskew_cfg`（相对路径）

3. **_local** `cfg_files/run_bankskew_cfg`（16 行配置 + 1 行注释）：
   - PatternName: Golden009_Multi4bank_bankskew
   - Speed: 11600, Width: X2P3, Port: SC0(8 banks) + SC1(8 banks)
   - Banks: 2b16g_BL0246/1357/8ace/9bdf/gikm/hjln/oqsu/prtv (8 个)
   - Corners: TT0.92V25C;SS0.92V-40C;SS0.92V130C;FF1.23V-40C;FF1.23V130C (5 个)
   - MR_Settings: WPre_4s4t_WPst_2p5;RPre_2s6t_RPst_0p5;RPs_0;CAParity_DIS;CMDBLK_DIS;MD_16b

4. **1017** log 目录文件（48 行）：SC0/SC1 × 8 bank × 3 corner(FF/SS/TT) = 48 个 pattern run dir

**结论**：1017 那次实际用的是 **_local 版本**（-l 匹配），主目录版本后来被改为 1030 rerun。

## 合成

通用化 `locate_stim_script_config.py <vecgen_root> <pattern_name> <log_location> -o out.json`：
- 扫描 `<root>/runsti/gen_stimulus_*` + `<root>_local/runsti/gen_stimulus_*`
- 提取各脚本 `-l`(log ref) 和 `-f`(config ref)
- 比对 `-l` 与给定 `log_location` → 判定 matched_version (main/_local)
- 解析匹配版本引用的 config 文件 → 输出 banks/corners/ports/speed/width 等

**A 资产**（真实内容）：A_vecgen/(主目录 runsti/runcfg/cfg_files/log) + A_vecgen_local/(local runsti/cfg_files)
**隐藏 B**（不同 pattern/结构）：vecgen_B/(Golden005_Singlebank_normalcheck, -l=1015_normalcheck → matched=main) + vecgen_B_local/(-l=1020_normalcheck_rerun → not matched)
- B 与 A 关键差异：matched_version 相反(main vs _local)、不同 pattern、不同 bank(2 vs 8)、不同 corner(3 vs 5)、不同 width(X1P6 vs X2P3)

## 判分 (17 断言 a-q)

a. submit.zip 含 script + out.json
b. py_compile 通过
c. 候选在 B 上 exit 0 + JSON dict
d. out_b 含 10 个必需顶层键
e. matched_version=="main" (B 正确, 非 _local)
f. main_log_ref=="log_2026_Vcap/Designer/1015_normalcheck"
g. local_log_ref=="log_2026_Vcap/Designer/1020_normalcheck_rerun"
h. main_log_ref ≠ local_log_ref
i. pattern_name=="Golden005_Singlebank_normalcheck"
j. pattern_verified==True
k. bank_count==2
l. corner_count==3
m. stim_script_content 含 "d6vecgen"
n. config_path basename=="run_normalcheck_cfg_sc0"
o. A-only 泄漏闸门 (14 个 A 标记不出现在 B 输出)
p. 幂等性 (3 次 sha256 一致)
q. 交叉输入守卫 (候选在 A 上 → matched_version=="_local" + bank_count==8)

## 自验

- ref PASS 17/17 ✓
- 5 negative (always_empty/core_deleted/naive_first_script/naive_hardcode_local/print_expected_a) 全 FAIL ✓
- §4.9 三假 (空壳 FAIL d / 打印期望 FAIL q / 删核心 FAIL q) 全 FAIL ✓
- 断言闸门 k_rationale=17 == k_check=17 ≥ 8 ✓
- jsonl test==disk check.py roundtrip sha 19c07759a94b ✓
