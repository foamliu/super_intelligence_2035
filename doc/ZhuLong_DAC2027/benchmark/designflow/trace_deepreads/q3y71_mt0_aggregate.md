# Deepread: q3y71 — HSPICE .mt0 测量文件汇总 (declanzh)

- **session**: `1793942940446_q3y71.messages.json` (declanzh @ hfeg0pkn005 / 10.129.2.14)
- **mc**: 96 · **domain**: spice_sim · **kws**: hspice:292 (ratio 0.50)
- **发现途径**: 11-05 重扫令 — 1109 新扫描 `ssh_eda_search_20261109_224902/summary.tsv` vs ledger_B diff ⇒ **545 fresh** shard-B 候选（mc≥10, spice kws）；q3y71 在 spice_count 排序中靠前且首条用户消息为真实 produce-task。
- **claim**: r417 ledger_B claimed

## 用户真实任务（trace 原话）
msg[2] user:
> `/rundata/drcoa/V0/simdir/hspice/declanzh/a51_VfsblnPumpCore_SIM/spf_result/core1103`
> 帮我把这个文件夹下后缀为.mt0的文件数据汇总到一个文档，并给出每个参数的最大/最小值

=msg[0]/msg[1] user 仅贴同一路径（铺垫）。=核心：解析目录下所有 `.mt0`（HSPICE/FineSimPro 测量输出），汇总成一个文档，给出每个参数的 max/min。

## .mt0 文件格式（msg[10] tool_result 原文，关键）
```
$DATA1 SOURCE='FineSimPro' VERSION='V-2023.12-1' PARAM_COUNT=0
.TITLE 'typ'
       i_vfsbln   i_vwlp_fsbln          ieff.         temper         alter#
     1.1058e-02    -3.5830e-02     3.0862e-01     8.5000e+01     1.0000e+00
```
- 列：`i_vfsbln`(A)、`i_vwlp_fsbln`(A, **负值**)、`ieff.`(无单位, 即比例 0.30~0.31)、`temper`(℃)、`alter#`(文件序号)
- 带后缀变体：`a51_AG_ThickVfsblnPumpCore_rerun#1.mt0` 的 `.TITLE 'typ'`、alter#=2、temper=-40
- 共 ~79 个 .mt0 引用（1.mt0…34.mt0 编号 + 命名 + `#N.mt0` 后缀）；agent 最终把全部文件重编号 1..N

## agent 的产出与迭代（msg[203]/msg[209]）
- **汇总文档**: `core1103_mt0_summary.txt`（同目录）
- **最终脚本**: `/home/declanzh/mt0_v4_final.py`
- 三轮迭代改动：① 小数位 4→2（`30.8620`→`30.86` mA）② 单位从数值后缀（`7.72mA`）改为独立"单位"列 ③ 去掉温度列
- **全局统计表**（最终）：
```
参数               单位      |min|     文件      |max|     文件
i_vfsbln         mA       7.72    #55      15.69    #68
i_vwlp_fsbln     mA      25.28    #55      50.69    #68
ieff              %      30.19    #59      31.19    #65
```
- 注意：`i_vwlp_fsbln` 原值为**负**，agent 取**绝对值**再算 min/max（`|iw|` 列）；ieff 用百分号（×100）。

## 价值取值范围（从样本 + 最终统计推得，用于忠实重建）
| 参数 | 范围(A) | min 文件 | max 文件 |
|---|---|---|---|
| i_vfsbln | 7.72e-3 ~ 1.569e-2 | #55 | #68 |
| i_vwlp_fsbln | -5.069e-2 ~ -2.528e-2 (abs 25.28~50.69 mA) | #55 | #68 |
| ieff | 0.3019 ~ 0.3119 | #59 | #65 |
| temper | -40, 25, 85 (多 corner) | — | — |

## 为何 B-synthesized（A 不可行）
- 11/12 重扫验证 `/rundata/drcoa/V0/simdir/hspice/declanzh/a51_VfsblnPumpCore_SIM/spf_result/core1103/*.mt0` ⇒ **count=0**（仿真产物已被清理/归档，sim 完即删）。
- 故 A 档（用真实 .mt0 文件）不可行；按 §3 用 **B-synthesized**：忠实复刻 .mt0 格式 + 真实取值范围（从 trace 样本 + agent 最终统计推得），生成 A(可见)/B(隐藏) 两套，规模/取值/文件数均不同。

## 合成计划（下轮首事交付，DEBT:1）
**case id**: `EDA-Eval-DesignFlow-Mt0Aggregate-001` (spice_sim / L2-adjacent / B-synthesized / k≥10)
- **资产 A**（可见）: `assets/.../A/core1103/` 下 ~12 个 .mt0（编号 01.mt0..12.mt0 + 1 个命名 `pump_rerun.mt0`），格式忠实，i_vfsbln 8~15 mA、i_vwlp_fsbln -26~-49 mA、ieff 0.301~0.312、3 corner temper。
- **隐藏 B**: `hidden/core1103_B/` 下 ~15 个 .mt0，**不同**文件数/取值/alter#（min/max 落在不同文件）。
- **reference**: `mt0_aggregate_ref.py` — 独立解析 B 的 .mt0：跳过 `$DATA1`/`.TITLE`，读列头，每文件一行数据，汇总；对 i_vwlp_fsbln 取 abs；输出汇总文档（参数|单位|min|文件|max|文件 + 明细表）。
- **check.py ≥10 断言**:
  1. zip 解压 + py_compile 通过
  2. 提交脚本在 B 上 exit 0 产 summary 文档
  3. summary 含全部 B 的 .mt0 文件名（计数匹配）
  4. i_vfsbln min 值正确（与 ref 独立计算一致，容差 1e-4 mA）
  5. i_vfsbln max 值正确
  6. i_vfsbln min/max **归属文件**正确
  7. i_vwlp_fsbln min(|iw|) 正确
  8. i_vwlp_fsbln max(|iw|) 正确 + 归属文件正确
  9. ieff min 正确（% 换算 ×100）
  10. ieff max 正确 + 归属文件
  11. 单位标注正确（电流 mA、ieff %）
  12. 跨输入 A 也运行 exit 0（泛化）
  13. 反空转：summary 非空且与单文件不同
  14. 反硬编码：B 的 min/max 不等于 A 的（B 值不同，硬编码 A 值会 FAIL）
- **negative**: naive_copy(A 的 summary) / only_count_files / hardcoded_A_values / only_print_header / ref_core_deleted（全 FAIL）
- **test_rationale**: `14 条断言：①…` (k_check==14≥8)

## 11-09 扫描重大发现（池未枯竭）
- `mc-matrix src=summary_1105.tsv` ⇒ mc10.fresh=0（pool 486 全 touched）—— **但这是 1105 旧快照**。
- **1109 新扫描** `ssh_eda_search_20261109_224902/summary.tsv`（38083 行 vs 1105 的 5823 行）shard-B kws 过滤 + mc≥10 + 去重 ⇒ **778 候选**，vs ledger_B(1295) diff ⇒ **545 fresh**（未动过）。
- ⇒ **"spice 池 98%+ ledgered / 池枯竭" 只在 1105 口径成立；1109 下 545 fresh，池远未枯竭**。
- A 尚未换池 1109（summary_stats.json.mc_matrix.src 仍 summary_1105.tsv）；本 shard 不自行换池，但按 11-05 重扫令用 1109 扫描取证找 fresh 候选合法。
- 候选清单存 `designflow/.cand_B_1109.tsv`（778 行）+ `designflow/.fresh_B_1109.tmp`（545 行）。
