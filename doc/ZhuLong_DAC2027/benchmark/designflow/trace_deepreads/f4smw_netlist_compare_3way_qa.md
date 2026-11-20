# f4smw deepread — netlist 3-way compare Q&A (r887 选料)

**trace_source**: session `1794445820477_f4smw` / user `mhyu` / host `hfeg0plg52` (10.129.35.68) / mc=91 / domain=schematic_netlist
**ledger**: parked r638 (旧判 "netlist-compare Q&A") → r887 revival-from-parked per 2026-11-15 令§二 (Q&A 造-able)
**pool_reaudit**: 列 `可造(需源)` — netlist-grounded comparison tool (读两/三网表→结构化差异报告)

## 用户原话（逐字，A 档 trace-faithful 用 idx=37 三网表对比轮）

- **idx=0/5**（首轮，2 网表对比）：`/rundata/drvqa/V0/simdir/finesim/workdir/mhyu/simulation/04_256pattern/SM_256pattern_16BL_case21目录下的netlist_8TG_separate_PNdriver以及netlist_seperate_driver是两个网表，其中netlist_8TG_separate_PNdriver是通过M=250模拟了PCS、NCS电压域内SA的loading；netlist_seperate_driver只是将PCS、NCS单独对SA供电。这两个网表还有什么额外的区别吗，对比一下`
- **idx=37**（二轮，3 网表对比，**本 case A 档任务说明**）：`我重新生成了一份netlist_8TG_separate_PNdriver，现在netlist_8TG_separate_PNdriver、netlist_8TG_separate_PNdriver_bulk、netlist_seperate_driver有什么区别`

选 idx=37 作任务说明：用户**提出需求**（对比 3 网表找区别），未给出根因或修复方案 → 符合 A 档选轮规则。

## 真实工具链（assistant）

1. `list_allowed_files` 列目录 → `read_files` 读 3 网表
2. `run_approved_command` (shell-runner/python-runner) 跑 diff —— python-runner SIGABRT (locale/encodings) → 转 `editor` 写 `/ai_sandbox/drvqa/V0/agentdir/mhyu/compare_netlists.py`
3. `SandBox_MCP_Server__run_code` (pyAether) 跑 compare_netlists.py：unified diff / subcircuit 列表 / inh_vkb 计数 / PCS-NCS driver 计数 / CXSA_1x16x3 对比 / 3-way diff

## 金标准（assistant 末轮 idx=50，3 网表全面对比）

### 3 网表基本统计（真实，从 tool outputs 核实）

| 指标 | new_8TG `netlist_8TG_separate_PNdriver` | old_8TG_bulk `netlist_8TG_separate_PNdriver_bulk` | seperate_driver `netlist_seperate_driver` |
|:--|:--:|:--:|:--:|
| 总行数 | 13,424 | 14,517 | 14,267 |
| 子电路数 | 36 | 38 | 36 |
| Top Cell | `matleveltb_PLANC_PNdriver` | `matleveltb_PLANC_69_HB_0924` | `matleveltb_PLANC_69_HB_0924` |
| 生成日期 | Thu Nov 12 09:18:39 2026 | Thu Nov 5 20:42:26 2026 | Wed Oct 21 16:07:50 2026 |
| `inh_vkb` 引用数 | 334 | 543 | 0 |
| `m=250` 乘数实例 | 1 | 1 | 0 |
| `brknetBM1` 引用 | 23 | 23 | 0 |
| `brknetM0` 引用 | 2310 | 2310 | 2278 |
| `brknetM2` 引用 | 120 | 120 | 92 |
| `_org` 备份子电路 | 0 | 2 | (有) |
| CXSA_1x16x3 展开行数 | 12 | 332 | 144 |
| PCS/NCS 本地驱动管 XMMN | 108 | 108 | 204 |

### 核心差异（5 类，全 cited 到真实行/子电路名）

① **Iso/Oc/PreEq/Sa 管 Bulk 连接** `inh_vkb` vs `inh_vss`：new=334 refs/224 管，old_bulk=543/448，seperate=0/448（全 inh_vss）
② **PCS/NCS 驱动架构**：new+old_bulk 用 M=250 顶层模拟 + 108 本地管；seperate 用 204 显式本地驱动管（SanEn/SapEn 控制），无 M=250
③ **BL/CBCC 开关拓扑**：new+old_bulk 用 `brknetBM1` 子电路；seperate 用显式电阻 + `brknetM0`
④ **new vs old_bulk 独有**：Top cell 重命名（69_HB_0924→PNdriver）/ 寄生RC 重新抽取（~740 行 parasiticRC4）/ 晶体管减半（448→224）/ 移除 `_org` 备份 / CXSA_1x16x3 简化为 12 行
⑤ 独有子电路：new_8TG/old_bulk 有 `brknetBM1`、`kcellx16BGmdl_1`；seperate 无

## 可 falsify 交付物定义

- **真实交付形态**（trace 中 agent 实际产出）：`compare_netlists.py` 脚本（读网表→结构化差异报告）
- **本 case 契约**：`outputs/submit.zip` 含 `compare_netlists.py`，接受 3 个网表文件路径参数，stdout 输出结构化 JSON diff 报告
- **check() 策略**：独立解析 hidden B 的 3 个合成 mini-netlist 得 ground truth → 跑 SUT 脚本 on B → 比对 ≥8 事实（行数/子电路数/top cell/日期/inh_vkb 计数/M 乘数/brknetBM1/brknetM0/brknetM2/_org 备份）
- **反硬编码**：B 的事实与 A 不同（不同 top cell/日期/计数）+ B 文件名/路径与 A 不同 → 硬编码 A 数字或路径者必 FAIL

## 资产规划

- **A（真实，SUT 可见）**：user_question_A.txt（idx=37 逐字）+ 3 个真实网表 excerpt（从 trace tool outputs 提取真实行：header/brknetBM1 子电路/CXSA excerpt with inh_vkb+ntnlvio_iso/M=250 实例）+ task_brief.md（≤3 行接口说明）
- **B（hidden，合成平行场景，check() 跑）**：3 个合成 mini-netlist（~80-120 行），不同 top cell 名/日期/inh_vkb 计数/M 值/brknet 计数/子电路数/_org 存在性 + hidden_manifest.json

## 选料合规

- ✅ 真实 trace 溯源（trace_source 齐全）
- ✅ A 档 trace-faithful（用户原话逐字 idx=37，未脱敏，仅路径保持原值）
- ✅ Q&A 造-able per 2026-11-15 令§二（旧判 Q&A 不可造已作废）
- ✅ netlist-grounded comparison tool（套 #254 v2 output-grounded pattern + r880 manual-grounded 范式）
- ✅ D 域 schematic_netlist（kw: schematic:322;netlist:214;cmos:98）
- ✅ 非跨 shard dup（grep D.jsonl + 4 shard 台账：mhyu/hfeahpc502/f4smw 0 case）
