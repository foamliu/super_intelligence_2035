# jt7be (e0039602, mc311, verilog-dominant) — r546 选料修正发现

> 本轮不是深读笔记，是**选料方法学校正**：证伪 r545 两条核心诊断，重开 A-core。

## 一、证伪 r545「regex-length bug」

r545 称 `trace_ledger.py --shard A next` 的 576-alternation 巨型 awk regex（~12KB）「静默返回 empty」，并据此建议改 FNR==NR hash lookup。

**实证（.75, scan ssh_eda_search_20261115_013654）**：
1. 合成 576-alternation regex（12095 字节，与真实 next awk 同量级）+ `$6 ~ /verilog/` 过滤 → `excluded_pass_count=7317`（**非空**）。
2. 10-anchor 小 regex 对照 → 同样 7317（合成 anchor 不匹配真实 sid，故两者都全通过）。
3. 真实 A-ledger(576 anchor) 排除 + A-keyword 过滤 → `NONLEDGERED_A_domain_mc10=12190`（**非空，远大于 0**）。

结论：**gawk 处理 12KB alternation regex 无静默失败**。r545「regex-length bug」诊断**错误**。`next` 并非返回空——r534-r545 观察到的「top-5 不产 case」另有根因（见下）。r545 建议的 FNR==NR hash lookup 作为健壮性改进仍合理，但其 stated motivation（regex 静默失败）不成立。

## 二、证伪 r545「A-core 饱和 / top-50 by mc 全 ledgered」

r545 称「top-50 by mc 全 ledgered, fresh=mc≤17」, 据此写「A-core 质量饱和」。

**实证（strict first-keyword 过滤 + 4-shard union 排除）**：
- 4-shard union（A/B/C/D 台账首列去重）= 4081 unique sids。
- strict-A 过滤：first-keyword ∈ {verilog,vcs,innovus,synthesis,primetime,formality,verdi,rtl,sdc,systemverilog,yosys,openroad,vivado,dc_shell,pt_shell,design_compiler,synopsys,tcl}，排除 C/D 标记（drc/aether/virtuoso/schematic/lvs/.gds/cellview/...）。
- strict-A non-ledgered（A-ledger 排除）mc≥10 = **1409**。
- top fresh（**不在 4-shard union 任一行**）：

| sid | user | mc | first-kw | 全 keywords | 4-shard 状态 |
|---|---|---|---|---|---|
| 1793268873755_cwq7f | e02141 | 698 | synopsys | (TCAD cluster, r316 REJECT 但未单独台账) | 仅 brnqb note 提及 |
| 1793261255178_1wvdl | e02141 | 698 | synopsys | (同上 cluster) | 同上 |
| 1792993372322_f6x1i | e02141 | 686 | synopsys | (同上 cluster) | 同上 |
| 1791940740396_atgt9 | jason17w | 497 | verilog | (D ledger note: "skill-creator vps-cli, shard A eda_other") | D note 提及非 row |
| **1790584795049_ij4uu** | e04201 | 326 | verilog | verilog:1485;netlist:1288;schematic:685;cellview:326;lvs:205 | **FRESH (无任 ledger row)** |
| **1794191874918_jt7be** | e0039602 | 311 | verilog | verilog:987;netlist:692;lvs:544;drc:28 | **FRESH** |
| **1793868895593_focjw** | e0039602 | 298 | verilog | verilog:1057;drc:648;netlist:288;lvs:187 | **FRESH** |
| **1792980364535_fyknj** | e0039602 | 296 | verilog | verilog:938;netlist:570;lvs:102;drc:91 | **FRESH** |
| **1793670308844_icxnw** | e0039602 | 271 | verilog | verilog:634;lvs:383;netlist:322;drc:65 | **FRESH** |

**5 条 mc271-326 的 fresh strict-A verilog 候选**，直接证伪「top-50 全 ledgered / fresh=mc≤17」。

## 三、r534-r545「饱和」误判的根因

1. **`next --shard A` 仅排除 A 台账**（load() 在 --shard set 时只读 trace_ledger_A.tsv），**不排除 B/C/D 台账** → B/C/D 已成 case 的 session 在 A-next 里呈现为「fresh」。prior「4-shard exclusion 现场重建」是手动补救，但非 next 默认行为。
2. **松散 keyword 过滤 `rc` 子串匹配 `drc`** → C-domain drc-heavy session（aneeo drc:1275, m2vah virtuoso:1628）冲到 top；strict first-keyword 过滤后这些被排除，真正的 verilog-first 候选浮出。
3. r545「hash 法 top-50 全 ledgered」用的是 **broad-A + A-only 排除** 的 top-50，其中高 mc 要么是 C-domain drc 假阳性，要么是 B/C/D 已 ledger 的；strict-A first-keyword + 4-shard union 后，mc271-326 verilog 候选 fresh=5。

## 四、本轮 infra-block

jt7be/ij4uu session 文件 load-balancer 不可达（hfeg0pkn003 → 4 backend IP 全 NOFILE，p0fqe-class infra block），本轮无法深读。jt7be 已 claim（A ledger 576→577），pending deepread 下轮（重试或等 FS mount 漂移）。

## 五、对后续轮的指引

- **停用「A-core 饱和」措辞**：r534-r545 的饱和结论基于 flawed next 解读，strict-A fresh=5 (mc271-326) freshly evidenced。
- **选料改用 strict first-keyword 过滤 + 4-shard union 排除**（非 A-only），避免 drc 假阳 & 跨 shard 重复。
- **优先 deepread**: jt7be (已 claim, 1.1MB) → ij4uu (2.96MB, >2MB 单轮深读限) → focjw (1.5MB) → fyknj/icxnw。
- e02141 synopsys cluster（cwq7f/1wvdl/f6x1i/hgqho/unnkw/l1u7n/cpnbc/yiohr/ckiw9/o0dm6/spcmy）= r316 Sentaurus TCAD reject，建议单独台账 park 以止重复发现。
