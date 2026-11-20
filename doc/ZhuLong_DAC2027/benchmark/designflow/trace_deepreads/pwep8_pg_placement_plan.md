# Deepread: 1792563683776_pwep8 (jianhaiq @ hfeg0plg76 / 10.129.35.74)

**Session**: `1792563683776_pwep8` · user `jianhaiq` · host `10.129.35.74` (hfeg0plg76) · mc530
**Domain**: pg_layout (pyAether GDS placement, PG pin label, device connection)
**Keywords**: skipper:2564;pdk:1331;aether:940;pyaether:838;lvs:427;.gds:280;synopsys:192;calibre:169
**Ledger status prior**: parked 2026-11-05 (旧规则下 parked，11-15 task初心下 re-eval → case)
**NMSG**: 494 (very long, multi-turn pyAether API exploration + GDS generation)

## 用户真实意图（U#0 逐字原文）

> 帮忙写一个py脚本，脚本名称为：PG_check.py；脚本用法：PG_check.py list
> list文件是提供的一个文本文件，内容如下所示：
> mos: /home/pdk/jianhaiq/03_script/10_PG_split/07_zl_tool/gds_cdl_ori/test_ptn.cdl /home/pdk/jianhaiq/03_script/10_PG_split/07_zl_tool/gds_cdl_ori/test_ptn.gds
> res: /home/pdk/jianhaiq/03_script/10_PG_split/07_zl_tool/gds_cdl_ori/test_rnpo_2t_ckt.cdl /home/pdk/jianhaiq/03_script/10_PG_split/07_zl_tool/gds_cdl_ori/test_rnpo_2t_ckt.gds
> 上述文件中，提供了两行三列信息，由空格隔开：
> 第一步：首先抓取到mos开头的行，再获取此行中第三列的信息，调用该文件；
> 第二步：之后再抓取到res开头的行，获取此行中第三列的信息，调用该文件；
> 第三步：使用第一步和第二步调用的文件，生成 .../test_ptn_to_ptn.gds的文件，
> 生成的文件需要注意以下几点：
> 1.调用了两次mos文件，两颗mos的放置位置和如何排放的；
> 2.中间放置的res是如何放置的；
> 3.mos和res是使用什么layer将其连接在一起的；
> 4.使用了什么PG_pin打了label，label打在了什么地方；

## 助手行为

- 搜索大量 pyAether API（dbOpenLib / dbCrtInst / aeExportStream / aeCreateRect / geOpenLib 等）
- 探索目录 /home/pdk/jianhaiq/03_script/10_PG_split/07_zl_tool/
- 494 msgs 涉及多轮 pyAether GDS 创建 + instance 放置 + 连接 + PG pin label

## 真实交付物

- PG_check.py 脚本：读取 list 文件 → 加载 mos/res 的 cdl+gds → 用 pyAether 生成 test_ptn_to_ptn.gds（2×mos + 1×res 放置 + 连接 + PG pin label）
- 这是 L2 任务（真跑 pyAether 生成 GDS）

## Reframe（mock-behavioral · 11-15 task初心）

- 旧 parked 理由：需真跑 pyAether（L2），旧规则下判 teeth-fail。
- 11-15 re-eval：用户真实意图 = "parse list + plan placement (2 mos + 1 res, positions, connections, PG pins)"。plan 部分 IS checkable 不需真工具（承 r645-r698 mock-behavioral 家族）。
- **新子型 `pg-placement-plan-extract`**（pg_layout 首例 placement-plan 提取器）：fixture = list 文件 + placement spec JSON，candidate = parse list + combine spec → emit placement plan JSON (devices/instances/placement/connections/pg_pins/output)。
- distinct vs r697 PgDummyFillFlowOrganize=TVF deck 14-section structural extract / r698 ErcRulecheckStatsScan=erc.rep batch scan stats / 本例=PG device list parse + placement plan emit — distinct sub-family。
- teeth = B 全异（3 device types vs A's 2 / 6 instances vs 3 / different coords/rotation/mirror / different nets+layers M2/M1 vs M1 / different PG pins / different output path），反硬编 14 条件。

## 资产

- asset A (visible): list_A.txt (真实 list 格式，jianhaiq 真实路径) + placement_spec_A.json (2 mos + 1 res, M1, VDD/VSS)
- hidden B: list_B.txt (3 device types: mos/res/cap, 不同路径) + placement_spec_B.json (3 mos + 2 res + 1 cap = 6, M2/M1, NET_VDD/VSS/MID) — A∩B disjoint
- reference: pg_placement_planner.py (parse list + combine spec → plan JSON, 13 keys, deterministic sort_keys)
- check.py: 14 conditions (a-n), 独立可 FAIL, B-only
- negatives: naive (empty) / always_plan_a (hardcode A) / parse_empty (parse but empty plan) — all FAIL

## 自验

- py_compile ref ✓
- ref on B → PASS (3 devices, 6 instances, types [cap,mos,res], 6 placement, 3 connections, 3 pins)
- check(ref) → PASS ✓
- negative_selftest: ref PASS + 3 negatives FAIL ✓ (ALL GOOD)

## 泄漏隔离

- SUT 沙箱 = assets/PgPlacementPlan-001/{list_A.txt, placement_spec_A.json}（不含 check.py / reference / hidden / jsonl）
- hidden/ 不进 SUT（hidden_manifest.json 标注）
- check.py 在 reference/ 独立判分，不进 cline workdir
