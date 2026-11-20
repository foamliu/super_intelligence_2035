# pool_domain_audit_D.md — shard D 可造候选池 domain 抽核报告 (r864, 2026-11-18)

> 触发：r863 发现 8n60f 跨 shard 域误分类（D ledger 标 analog_context，实为 B spice_sim @ hfeg0pkn002）。
> r863 MEMORY 明确：「下轮需抽核 domain 标注」「D pool_reaudit『218 可造』可能含其他 B/A 域误分类（8n60f 是首例）」。
> 本轮 = r864 plan ①「从 709 可造池挑经 domain 抽核确认 D-domain 的候选造题」的**抽核前置步骤**。

## 方法

- 输入：`pool_reaudit_D.tsv` 全部 709 条「可造*」候选（含可造/可造(待深peek定形态)/可造(需源…)/可造(prototype-proven) 等变体）。
- 域信号来源：scan summary 11/15 快照（`summary_1115_081559.tsv`，4543 sessions）的 keyword 分布。
- keyword→shard 映射（粗糙，承认重叠）：
  - **D** = netlist/schematic/.cdl/cellview/waveform/fsdb/waveview/analog/transistor/cmos/spice
  - **A** = verilog/rtl/primetime/tempus/synthesis/xcelium/irun/vcs/ncsim/systemverilog/formality
  - **B** = hspice/finesim/spectre/corner/monte/characterization/measure/dcop/ac/tran
  - **C** = drc/lvs/calibre/pex/gds/layout/virtuoso/aether/pdk/techfile/pcell/via/metal/pyaether
- 每条候选算 D/A/B/C 四分，按占比判 verdict：
  - `D-confirm` = D 占比 ≥40%（D 主导）
  - `D-confirm(weak)` = D 占比 30–40%
  - `cross-shard-suspect(lean-X)` = X 占比 ≥45% 且 D <25%（高置信误分类）
  - `lean-X` = X 占比 ≥40%（中置信偏 X）
  - `mixed` / `unclassifiable`

## 结果（709 可造* → 646 命中 summary，63 miss）

| verdict | count | 含义 |
|:--|--:|:--|
| D-confirm | 403 | 干净 D-domain，可直接造题 |
| D-confirm(weak) | 6 | D 弱主导，深读确认即可 |
| cross-shard-suspect(lean-C) | 102 | **高置信误标 C**（layout/drc/lvs/aether 主导） |
| lean-C | 58 | 中置信偏 C |
| lean-A | 25 | 偏 A（digital/verification） |
| cross-shard-suspect(lean-A) | 18 | **高置信误标 A** |
| lean-B | 18 | 偏 B（spice_sim） |
| cross-shard-suspect(lean-B) | 12 | **高置信误标 B（8n60f 同款）** |
| mixed | 4 | D/A/B/C 均势 |
| unclassifiable | 63 | summary 未命中（新会话/无 mapped kw） |

## 关键发现

1. **8n60f 自身被正确标记**：`1792135941514_8n60f` (adaml) verdict=`lean-B`（D=2 B=4 C=4，kw 太少被低估，但 lean-B 方向正确）—— 方法验证通过。
2. **8n60f 同款风险 = 12 条 cross-shard-suspect(lean-B)**，例：
   - `179327072926_ebmf3` (chapinc, analog_context/schematic_netlist/waveform) D=37 B=409 → 91% B，实为 spice_sim
   - `1793791169909_2ka5p` (e0030760) D=453 B=1728 → 79% B
   - `1793598804317_2swgt` (adaml) D=67 B=256 → 78% B
   - 这些若按 D ledger 域造题，会重蹈 8n60f 跨 shard 误分类覆辙。
3. **lean-B / lean-C 中 D+B 或 D+C 双高的混合候选**（如 e6xdf D=888 B=912、g89xb D=443 B=708）—— 按 11-15 令「D-purity 是筛选偏好不是初衷，跨域工作照样造」，**keyword 混合不等于误分类**；真实域归属需深读用户意图判定。本抽核只标 *keyword 嫌疑*，不下「不可造」结论。
4. **干净 D 池 = 409 条**（D-confirm 403 + weak 6），足够下一轮安全造题挑选。落 `pool_D_confirm_D.tsv`。

## 局限

- keyword→shard 映射粗糙（spice 归 D 但 hspice 归 B；drc 高频出现在 D 域 trace 里也算 C 信号）→ 跨域嫌疑会有假阳性，**深读才是终审**。
- 63 条 summary 未命中（session id 含 `.messages.json` 后缀或新会话），标 unclassifiable，需下次换池/补 summary 后重跑。
- 本抽核**不修改** pool_reaudit_D.tsv（只新增 audit 文件），不删候选、不下线——符合「🚫 不删数据」纪律。

## 产出文件

- `designflow/pool_domain_audit_D.py`（可复跑脚本）
- `designflow/pool_domain_audit_D.tsv`（709 行，全可造* 候选的域抽核）
- `designflow/pool_D_confirm_D.tsv`（410 行，D-confirm 短名单，下轮造题挑选源）

## 下轮 (r865) 建议

从 `pool_D_confirm_D.tsv` 挑 kw_D 高且 mc 可观的候选（如 otonl e0022089 waveform D=717、0vmow e0017052 schematic_netlist D=266、4auih pjli schematic_netlist D=322、f8g40 rongjiez schematic_netlist D=297、iqj11 shaoyou waveform D=190、voemm t0003117 waveform D=192），claim → 深读确认用户真实意图 → 合成造题。**优先 kw_D 占比 ≥60% 的最干净候选**，避开 lean-B/lean-C 嫌疑池。
