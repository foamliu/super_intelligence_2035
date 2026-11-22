# trace_deepread — 1795164433311_o7ljl

- session: `1795164433311_o7ljl.messages.json`
- user / host: joeyl @ hfeg0pkn004
- match_count: 78 (hspice:205; pdk:190; netlist:130)
- domain: spice_sim (shard B)
- ledger status: claimed → case (`EDA-Eval-DesignFlow-C2cCornerAmplifierAudit-001`)
- round: r1038

## 真实任务

joeyl 在 `hfeg0pkn004` 上调一颗 C2C（capacitive-coupled inverting level-shifter
chain）放大器 `WCK_C2C_RFB`。电路是 4 级反相链
`divider_out -> vout1 -> vout2 -> vout3 -> OUT`，跑 FineSimPro 的 6-corner
transient sweep，产出 `1_TRAN.mt0.csv`。

工作目录 `/home/joeyl/c2c_iter/`，netlist 在
`/home/joeyl/ulvt_delvto/work/Divider_C2C_netlist_delvto-0.05`。

目标：让 5 个 fast corner（tt/ff）打出 rail-level OUT。SS corner 是
slew-limited 的本质 W/L frontier 冲突，留作已知限制。

## 诊断链（trace msg59 / msg191）

tt/ff 失败根因：X0（out↔vout1 耦合电阻）太强 → vout1 low 被钳高 →
XNM7 永远关不断 → vout2 high 被钳低 → vout3 卡 HIGH → OUT 死。

修复：`X0 l=20u→60u`（削弱 out↔vout1 耦合，让 vout1 low 真正拉低）+
`XNM7 w=4.8u→6u`（增强 vout1→vout2 pull-down）。

netlist 已确认 post-fix：`X0 out vout1 inh_vss rndif_3t l=60u w=100n`、
`XNM7 vout2 vout1 inh_vss inh_vss nlvt_ckt w=6e-6 l=50e-9`。

## 实跑 mt0（post-fix，6 corner）

`/home/joeyl/c2c_iter/tran/1_TRAN.mt0.csv`（FineSimPro V-2023.12-1，$DATA1
文本，30 列，6 行 = tt@45×2 / ff@-40 / ff@130 / ss@-40 / ss@130）。

关键列：
- `o1..o4`：最终 OUT peak-to-peak
- `i2_vout1/i2_vout2/i2_vout3`：instance2 各级 PP
- `i2_voutN_min/max`：各级节点 DC min/max（用于 bias 分类）
- `temper / alter#`：corner 温度 / alter 序号

post-fix 实测：
- tt@45 (alter 1,2)：o≈0.926 → PASS（rail）
- ff@-40 (alter 3)：o≈0.928 → PASS
- ff@130 (alter 4)：o≈0.514 → MARGINAL（半摆幅，无单级塌掉 → out_path_loss）
- ss@-40 (alter 5)：o≈9.6e-5 → FAIL，vout1 PP=0.257 塌掉、bias 0.33 → vout1_low_clamped
- ss@130 (alter 6)：o≈2.1e-3 → FAIL，vout1 PP=0.177 塌掉、bias 0.38 → vout1_low_clamped

## 案例合成（reframe）

FineSim 本身 e0031982 无 /proj PDK 读权限跑不了，故 reframe 成 L1 Python
per-corner CSV 分析任务：

- case_id: `EDA-Eval-DesignFlow-C2cCornerAmplifierAudit-001`
- SUT 产出 `c2c_corner_audit.py audit --mt0 <csv> --report <json>`
- A = 真实 o7ljl 6-corner mt0；隐藏 B = 合成 5-corner 1.2V-rail mt0，
  失败模式刻意不同（B 的 FAIL 是 vout2_high_clamped + vout3_stuck，区别于
  A 的 vout1_low_clamped），数值/corner/温度全不同，A-only magic 不得出现在 B。
- check.py：12 条独立断言（present / compile / A 实跑 / A 计数 / A verdict /
  A root_cause / B 实跑 / B verdict+counts+roots / 3-seed 确定性 / 反硬编码 /
  B≠A）。3 个 negative（empty / print-only / core-removed）全 FAIL。

## 选用理由

joeyl@hfeg0pkn004 真实 hspice/spice corner-sweep 调试 trace，mc78 远超
shard_mc.B=5 门槛；mt0 数据真实可取、诊断链清晰、天然适合 reframe 成
确定性 CSV→JSON 分析器，且失败模式可在 B 中做出与 A 不同的根因，支撑
反硬编码与隐藏-B 实跑断言。
