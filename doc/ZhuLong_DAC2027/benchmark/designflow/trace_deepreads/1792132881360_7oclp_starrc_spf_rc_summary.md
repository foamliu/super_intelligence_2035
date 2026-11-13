# deepread: 1792132881360_7oclp (simplec StarRC flow + per-net RC CSV)

- **session**: `1792132881360_7oclp.messages.json` (directory format)
- **user / host**: simplec @ 10.129.2.11 (hfeg0pkn002 family)
- **size**: 325 KB, 79 msgs, 3 real user turns
- **keywords**: synopsys:88; netlist:50; calibre:6; lvs:2 → mc=10, domain **pnr_signoff**

## User turns (real)

- **U#1** 「跑一下starrc flow」
  - agent 探查 `to_simplechen_starrc/` 目录结构（skills/starrc_rc_flow/README+skill.md+run_starrc.sh, scripts/autorun_gxtr_v0d1.csh, work/cell.list=15 cells, work/extract_rc.py, work/extract_net_info.py）
  - 用 `run_approved_command` profile=shell-runner 调 `run_starrc.sh version` → StarRC `ds/star/2020.09-SP5-4`
  - `run_starrc.sh bg` 后台启动（PID 4002668），15 个 Sandwich_M1_M2_W0P055_S*_M3 cell 全部 SPF 提取成功，归档到 `rundata/261016144225/<cell>/<cell>.spf`，0 loss

- **U#2** 「重新生成每 net 的 RC 汇总 CSV」 ← **核心 produce-task（本 case 取此）**
  - agent 发现 `extract_rc.py` 与 `extract_net_info.py` 都**硬编码 `RUNDATA = .../rundata/20261014`**
  - 改造：`_RUNDATA_ROOT = .../rundata` + `resolve_rundata()`：argv[1] 显式（abs 或相对 _RUNDATA_ROOT），否则 `sorted(glob(_RUNDATA_ROOT/*))[-1]` 取最新
  - `parse_spf(filepath)` 逐行解析：
    - `*|NET <name> <cap>PF` → total_cap_pf（行头 pF，不重算）
    - `*|P (<port>` → 端口（`(` 紧接 port 名，无空格）
    - `R<num>_<sub> n1 n2 <val>` → total_r += val, r_count++（Ω）
    - `Cg<num>_<sub> n 0 <val>` → c_ground_count++（前缀 Cg + 第三字段 0）
    - `C<num>_<sub> n1 n2 <val>` → c_couple_count++（前缀 C，**不按节点判定**：`C1_1 n 0 v` 也算耦合）
    - 元件收集在下一个 `*|NET`/`.ENDS`/`.END` 停止（i-=1 让外层重读）
    - `cap_elements_sum_pf = sum(cap_values)` —— **原始法拉求和，不换算 pF**（列名 _pf 是历史遗留）
  - 跑 `extract_rc.py 261016144225` → 105 net / 15 cell → `work/all_nets_rc.csv`
  - CSV 列：`cell,net,total_cap_pf,total_r_ohm,r_count,c_couple_count,c_ground_count,cap_elements_sum_pf,ports`
  - 同步跑 `extract_net_info.py` 刷新 `net_info_summary.csv`

- **U#3** 「all_nets_rc.csv 这个文件要放到输出目录中 比如这次的 .../rundata/261016144225」
  - agent 写 `_copy_csv.py` 把 CSV 复制到 `rundata/261016144225/all_nets_rc.csv`（106 行 = 1 表头 + 105 net）

## A-faithful 判定

- 用户给任务（重新生成每 net RC CSV）+ 现成脚本（硬编码路径）+ 目标，**未给** SPF 解析算法 / Cg-vs-C 前缀分类规则 / 原始求和不换算 / 端口 '(' 紧接格式 / 自动取最新 rundata 逻辑 → A-faithful 合格
- deliverable 命中私有 `/home/simplec/to_simplechen_starrc/work/` → .75 Permission denied → **INFEASIBLE** → **B 档合成**

## 合成

**EDA-Eval-DesignFlow-SpfRcSummaryGen-001**（pnr_signoff L1-B，B 档，新 archetype = dspf-spf-per-net-rc-summary-csv-generator）：
- SUT 交 `spf_rc_summary.py`（纯 stdlib CLI `--rundata/--out`），解析 `<rundata>/*/*.spf` 生成 per-net RC CSV
- A 可见：`rundata_A/`（CellA1 2 net + CellA2 1 net，含 C-前缀到节点 0 诱饵、多端口 net、无接地电容 net）
- B 隐藏：`hidden/rundata_B/`（CellB1 2 net + CellB2 1 net + CellB3 2 net，零名重叠 A，含 C-前缀到节点 0 诱饵、无电容 net sense、多 R 链）
- check.py 16 条件（a-p），独立 string-based oracle（split 解析，非 regex，结构异于 ref）
- 核心 trap：⑦ total_cap 取自行头非元件和 ⑩ C-前缀到节点 0 算耦合（按前缀非节点） ⑫ cap_elements_sum 原始法拉和不换算 ⑮ 跨输入守卫 ⑯ 3-seed 确定性
- 自验 ref SELFTEST PASS 16/16；5 neg + 3 fake-submit 全 FAIL（NEG_RC=0）；断言闸门 k_rationale=k_check=16 ✓
- ledger mark 7oclp→case（coverage 263→264/917≈28.8%, pnr_signoff 36→37）
