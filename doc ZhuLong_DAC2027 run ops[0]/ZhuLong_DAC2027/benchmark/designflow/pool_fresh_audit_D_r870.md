# r870 候选池 freshness 抽核 · D-dominant fresh 候选 cross-shard 复审

**背景**: r869 MEMORY plan ①「mc≥10 fresh=93 池继续挑 D-dominant fresh 候选造题」。r870 执行抽核：从 candidates_mc10.tsv (mc≥10, 2256 池) 减去 4-shard 全 ledger (7408 session 变体) 得 **103 truly-fresh**，按 D-domain keyword 占比排序得 **9 D-dominant (dr≥0.6)** 候选。逐个验证 trace 可达性 + 真实语义域。

## 9 D-dominant fresh 候选复审结果

| session | user@host | mc | D-kw | 真实语义域 | trace | 处置 |
|---|---|---|---|---|---|---|
| 1793253191536_9zxe2 | e0047600@10.129.2.11 | 31 | .gds:403 | C layout (GDS) | 未验 | skip-C |
| 1791945700586_w4ghz | xinpengc@10.129.33.230 | 26 | cmos:18932 | B spice_sim / 混合 | **71MB messages.json** (巨型) | skip-超大 |
| 1792320716721_4prf6 | thomasz@10.129.33.186 | 25 | cmos:81 pyaether:5 | **C pyAether/layout** | 存在 | skip-C |
| 1792841178220_2sexh | thomasz@10.129.33.186 | 18 | transistor:40 | **C pg_layout/IR-drop** | 存在(363KB) | **parked lean-C** (本轮深读) |
| 1791983835884_0pzfe | e0014566@10.129.2.10 | 13 | cellview:61 | D 但**重复用户** | 存在 | skip-冗余 |
| 1791983444226_u9tql | e0014566@10.129.2.10 | 12 | cellview:48 | D 但**重复用户** | 存在 | skip-冗余 |
| 1794200762174_uxc45 | e0023936@10.129.32.75 | 12 | waveview:32 | D waveview | **.75-local 已轮转删除** | skip-无trace |
| 1792062337914_8rk3f | e0023936@10.129.32.75 | 12 | cellview+schematic | D | **.75-local 已轮转** | skip-无trace |
| 1792027672199_u063h | e0044587@10.129.8.231 | 11 | transistor:43 mosfet:17 | D analog_context | **已删除** (仅余 65a53) | skip-无trace |

## 结论
- **9 D-dominant fresh 候选 → 0 可造 D-domain quality case**
  - 3 trace 已删除（uxc45/8rk3f .75-local 轮转 + u063h 用户清理）
  - 2 重复用户 e0014566（0pzfe/u9tql，与 r865/r866/r869 同用户同 top-cell-name 重复模式，11-15 审计 redundancy）
  - 3 跨 shard 误分类（9zxe2→C layout, 4prf6→C pyAether, 2sexh→C pg_layout/IR-drop）
  - 1 超大 trace（w4ghz 71MB，违 §3「单条 trace >2MB」+ cmos:18932 单文件主导）
- **印证 r864 发现**: D-confirm keyword-based D-classification 与真实语义域系统性偏差；truly-fresh D-dominant 池实质枯竭（mc≥10 fresh=93 中 D-dominant 仅 9，且 0 可造）

## 2sexh 深读价值
- 2sexh 是高质量 debug-Q&A trace（Totem-SC vss IR-drop 诊断，10 步工具链，明确诊断事实），**域属 C pg_layout**
- 已 claim + parked (lean-C)，深读笔记落 `trace_deepreads/2sexh_ir_drop_diag.md` 供 C 线造题参考
- 关键诊断: vss worst drop 1314.84mV, 仅 55 pads 全为 .extra 单边放置 → pad 覆盖不足

## 下轮 (r871) 建议
1. **扩大选料面**: D-dominant fresh 池枯竭，需 (a) 等待 shard A 换新快照池 (C r740 已换 2907→943 但 D 仍用 11/09 口径) 或 (b) 主动按 D-domain 关键词 (waveview/fsdb/cdl/spiros/netlist) 直接 grep summary 扫新 session 而非依赖 D-confirm 池
2. **优先波形域**: D 核心域 waveform/waveview 在 fresh 池中稀缺，下轮可定向扫 waveview/fsdb 关键词 high-mc 候选
3. **discuss mandatory**: r871 due（r869 后 +2 造题/审计轮，r871 = r867 due 后第 4 轮配额），下轮须发言
4. **不凑数**: 本轮 0 case 是 cross-shard 域审 + trace 可达性验证的合规产物，非枯竭摆烂（11-15 令「候选池重审优先于造题」+「质量非数量」+「🚫 不改别人 shard」三重合规）
