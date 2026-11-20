# r689 — hfhds201 A-domain 候选池重审（最新 11-16 扫描快照）

**轮次**: r689 (0-case, 候选池可达性重审 + 2 复活线索登记)
**日期**: 2026-11-17
**扫描源**: `.75:/home/t0002965/log/ssh_eda_search_20261116_072610/summary.tsv`（37113 行，列 ip/host/user/session_file/match_count/keywords/tools）
**动机**: r688 下轮建议「trace_ledger next 内置排除 regex 在 .75 跑 fresh A-pure top-5, 优先 hfhds201 本机 readable」；本轮执行该选料并核实 mc≥5 11-15 令的止损判据（"mc≥5 候选里有无能忠实还原用户意图、且能写出可判分 check() 的任务"）。

## 一、hfhds201 A-domain mc≥10 候选（124 条）→ 0 truly fresh

`awk` 取 hfhds201 + mc≥10 + A 关键词（verdi/vcs/dc_shell/formality/innovus/primetime/pt_shell/synthesis/synopsys/tcl/verilog/systemverilog/rtl/sdc/vivado/yosys/openroad）→ 124 条，按 mc 降序。

**新鲜度交叉核对**（修复 r689 前的 `.messages.json` 后缀 bug）：用 4-shard 台账 `trace_ledger_{A,B,C,D}.tsv` 规范化 slug（strip `.messages.json`/`.messages.archive`，取 `_` 后缀）建 3514-unique slug 集，逐条核对 top-66 候选：

- **0 truly fresh**。top-66 全部 ledgered，跨 4 shard 分布（A/case、A/parked、B/case、C/parked、D/parked 等）。
- 例：wg5u2[B/parked]、bg39v[C/parked,A/case]、1s79t[B/case]、fl4rh[D/case,B/parked,A/case]、00p77[A/case]、ve67l[A/case]、sdtpg[A/case]、xd7ut[A/case]、m5mka[D/parked]、95kx2[D/parked,B/case]、5fpod[A/case]、wn9jo[A/case]、reo1p[A/case]、87wu6[A/case=WtmIs4PhaseMisuseCheck-001]、l8989[A/case]、q54e4[A/case]。
- r689 前 cross-check 误报 5 条 fresh（uky6c/0kgye/r6bcb/n5hh7/87wu6），根因 = 台账行首字段含 `.messages.json` 后缀而候选 slug 无后缀 → 比对失败。修正后 5/5 全 ledgered（uky6c[B/case]、0kgye[B/case]、r6bcb[A/case]、n5hh7[D/parked]、87wu6[A/case]）。
- **claim 实测复核**: `trace_ledger.py --shard A claim --session 1792654922770_87wu6` → REFUSED「已在台账 status=case case_id=EDA-Eval-DesignFlow-WtmIs4PhaseMisuseCheck-001 2026-11-16 23:31」，印证台账为新鲜度事实源。

**结论**: hfhds201（.75 本机 readable，唯一可达主机）A-domain mc≥10 池在本扫描快照下确证耗尽——与 r617/r619/r624/r678 的"可达池枯竭"结论一致，且现在用 11-16 最新快照（37113 行，较 11-15 的 39263 行无新增 A-domain fresh）重新举证。

## 二、mc 5-9 band（11-15 令 mc≥5 扩池新地带）→ 18 条，多为 C-domain-dominant / concept-Q&A / off-domain

`awk` 取 hfhds201 + 5≤mc<10 + A 关键词 → 18 条。逐条 peek 首条 user message + tool profile：

| slug | mc | user | 首条 user 意图 | 判定 |
|---|---|---|---|---|
| 9a7jm | 8 | t0002441 | "Finesim仿真报DC不收敛的错误, 可能的原因及解决方案有哪些?" (54 msgs, 1 user) | **不可造**：concept-Q&A，无 evidence anchor，§4.9 anti-hardcode 不可满足（承 r586/r595 concept-Q&A 判定） |
| y2mlp | 8 | t0002441 | aether/cadence/virtuoso dominant (pyaether/netlist) | C-domain 倾向，非 A-pure |
| l0x4z | 8 | yuankong | "AddressParameter.v中的COLA赋值给了谁" (36 msgs, 1 user, search_codebase×3) | **复活线索 A**：code-search Q&A，evidence-verifiable（assignment line token 可回溯 A .v）。形态同 Mr27ConfigLocate-001 (r667)。风险：单 user turn，≥8 独立断言可能偏薄。 |
| m273z | 7 | t0002987 | "怎么增加点log信息，当agent慢或卡的时候...当前zl agent" (186 msgs, 26 editor) | **不可造**：off-domain——调试 zl agent harness 自身（agent infra），非 EDA design-flow 用户任务 |
| ai203 | 5 | yuankong | "写个python脚本，在 /proj/.../MatrixRun 执行 bmatrix -f，解析 Fail 行" (14 msgs, 3 user) | **复活线索 B**：produce-task（parse bmatrix Fail 输出），evidence-verifiable（Fail 文本格式可结构化）。风险：trace 薄（assistant 用 ask_question，可能未完成）+ /proj 依赖（B-档自合成可绕开） |
| 7f29h/qhg0k/b2zwp/7cdxg/ogyui/ck74p | 5-7 | t0002987 | pyaether:aether:rtl dominant | C-domain 倾向（pyaether layout），非 A-pure |
| lxajs | 7 | mike | lvs:16+virtuoso:8 dominant | C-domain（LVS） |
| nlwn9 | 5 | t0002441 | waveview:21+synopsys:7 | waveview 倾向（C/D 域） |
| 其余 (6sh4c/0mx9i/shssw/qnm9e/uhrnk) | 5-7 | t0002441/mike | aether/virtuoso/pdk dominant | C-domain 倾向 |

**mc 5-9 band 小结**: 18 条中 **2 条为可造复活线索**（l0x4z code-search、ai203 bmatrix-parse），其余为 C-domain-dominant / concept-Q&A / off-domain。2 条可造线索均偏薄（单意图 / 短 trace），需下轮满预算深读后判定能否撑起 ≥8 独立断言。

## 三、mc≥5 11-15 令止损判据复核

11-15 令止损唯一判据 = "mc≥5 候选里，有没有能忠实还原用户意图、且能写出可判分 check() 的任务"。

- hfhds201 mc≥10 A-domain：0 fresh（全 ledgered）。
- hfhds201 mc 5-9 A-domain：18 条，2 条可造但薄（l0x4z/ai203），未本轮深读合成（40min fresh-agent 预算不足保质量闸门，承 r688 判据）。
- 远程 A-domain（hfeg0pkn*/pfn*/pgn* 等）：infra-block（SSH denied，e0031982 gid=555(guest) 无远端 ~/.cline 读权限，承 r647/r651/r654/r678）。

**本轮不触发 auto-stop 回退**：2 条可造线索（l0x4z/ai203）存在 ⇒ mc≥5 池在可达主机上"非完全枯竭"，但可造候选已稀薄至需逐条深读验证。**shard_mc.A 维持当前值**（不动配置）。连续 0-case 计数（mc≥5 口径）= 承 r688 状态，本轮 +1（非-选料-失败：可达主机 mc≥10 确证耗尽 + mc<10 可造线索已登记留待下轮满预算）。

## 四、下轮建议

1. **优先深读 l0x4z**（yuankong, AddressParameter.v COLA 赋值 code-search）→ 若 ≥8 独立断言可撑，按 Mr27ConfigLocate-001 (r667) C-A code-search Q&A v2 模板合成。trace 直接 hfhds201 本机可读。
2. **备选 ai203**（yuankong, bmatrix Fail 输出解析脚本 produce-task）→ B-档自合成 bmatrix 输出样本，按 produce-task 模板合成。trace hfhds201 本机可读。
3. 若 l0x4z/ai203 深读后均不可造（断言不足 / trace 未完成），则 hfhds201 mc≥5 A-domain 可达池方算"能忠实还原意图且可判分"口径下的真枯竭，届时在 MEMORY 记录数据依据并考虑转向（waveview 协作收尾 / 论文维护 / 跨 shard 卫生）。

## 五、纪律

- 🚫 未推 incomplete case 入 jsonl（尊重 §4.3 ≥8 独立断言 + §4.9 退化提交 + negative 硬闸门）。
- 🚫 不动 summary_stats.json / shard_mc 配置（本轮非选料重算轮，仅可达性重审）。
- ✅ 台账无新增 claim（l0x4z/ai203 仅登记为线索，下轮深读时再 claim，避免抢占）。
- ✅ eda_flow session 已 close（keep=false）。
