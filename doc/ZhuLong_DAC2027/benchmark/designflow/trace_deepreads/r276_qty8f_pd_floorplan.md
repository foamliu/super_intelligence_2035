# Deepread r276 — 1794032822083_qty8f (pd_floorplan)

- **trace**: 1794032822083_qty8f (xiwang @ hfeg0pkn002/10.129.2.11, mc=422, markers pyAether168 + cellview106 + dbGet30; xiwang 已覆盖用户但 qty8f 是 fresh session)
- **agent**: lead, 171 msgs, 8 user turns, 899KB messages.json
- **archive**: messages.json (非 .archive, 899KB)

## 选料路径
- r276 rescan (eda_trace_2026110{6-9}.log, sid 正则规范化 + 按 sid 聚合 max tot + lay>=15 ∧ sim<=lay*1.1, 排除 ledger_C 483 normalized sids) → 343 fresh candidates → fresh_pool_C_r276.tsv
- pg_layout 最低覆盖(36 cases) → 优先 pg_layout 域; 顶部 fresh 候选 peek 5 条, qty8f 最干净
- `trace_ledger.py --shard C claim --session 1794032822083_qty8f --user xiwang --host hfeg0pkn002 --match 422 --domain pg_layout` → claimed

## 真实用户意图 (U#0, 逐字原文, A-faithful-eligible)
> 帮我做一个Powerdomain的floorplan图，要求如下：（1）基于ddgoa_cmos_top/LP5TOP去做（2）不同的power domain用不同的颜色表示
- 用户陈述需求(未给 root cause) → A-faithful 合格; 但真实 OA/pyAether 不可沙盒复现 → 做 B 档离线重定义

## 真实 grounding (assistant 工具链 + 产物)
- agent 用 pyAether `dbOpenCVByType` 下钻 LP5TOP→Array16GTop→{Array8G_W, Array8G_E, SpineTop, Channel}
- per-block supply 分类: net.name word-boundary rail 正则 (vdd1/vdd2h/vddq/vintcore/vintbus/vintio + vss→infra)
- macro rail 映射: Array8G_*→vdd1/vdd2h, SpineTop→vintcore/vintbus mosaic, Channel→vintio+vdd2h, ESD_TOP→vdd2h/vddq
- 最终 sup dist {vdd1:19, vdd2h:24, vintcore:20, vintio:2, infra:15, None:6}
- U#2/U#3/U#4 给 vdd2h/vdd1/vintcore/vintbus/vintio 标签 / spine 精细多电压 / spine 下 2 层 hierarchy 的细化方向, 但 U#0 是干净 A-faithful 种子

## 为何 B 档离线重定义为 L2 inventory-结构分析
真实 OA lib `/proj/ddgoa/V0/libs` 不可从 .75 沙盒访问(权限拒) → 离线核心 = 给定 layout 层次 inventory JSON(die + blocks{inst,lib,cell,bbox,rails} + rail_supply_map + supply_domains_priority) → 块→电源域分类(rail 经 rail_supply_map 映射 + 按优先级选 dominant 非 infra domain, 仅 infra 块→null) → 输出结构化 power_domain_map.json + CSV + 上色 SVG。check.py 在 hidden B inventory 上 subprocess 真跑候选 (L2) 断言 JSON 结构与分类正确性 (15 条件 a-o)。

## B-track (hidden) 设计
- A inventory: TOP2 die, 10 块, 6 电源域(vdd1/vdd2h/vddq/vintcore/vintbus/vintio) + 1 unclassified, 源自 LP5TOP 真实层次(Array8G_W/E, SpineTop, Channel_N/S, ESD_TOP/BOT, Peri_W/E, Corner)但 bbox 合成
- B inventory: CHIP3D die, 14 块, 不同拓扑(CoreLogic/AnaCore_N/S/SerDes/PhyTop/DDR/PLL/IORing/Decap), 不同 rail 名(vintc→vintcore, vintb→vintbus, vssa→infra), **含 A 没有的 vdda 模拟域**, 不同优先级顺序(vdda 插在第 2), Decap_SE 仅 vss→null unclassified
- cross-input guards: die==CHIP3D(A 是 TOP2), AnaCore_N dominant==vdda(A 无此域), AnaCore_S dominant==vdd1(首 rail 是 vdda 但优先级 vdd1 更高, 挫败 naive first-rail), B rail 名不同(挫败硬编码 rail→domain)
- B 期望: total_blocks=14, unclassified=1, domains={vdd1,vdd2h,vdda,vintbus,vintcore,vintio}, AnaCore_N→vdda, AnaCore_S→vdd1, Decap_SE→null

## case 结构
- assets/A: prompt.txt + task_brief.md + inventory_A.json + hierarchy_note.md
- assets/hidden: inventory_B.json + hidden_manifest.json
- reference: pd_floorplan_gen.py(golden) + check.py(15 条件 a-o) + 5 negative{empty_shell→c, print_expected→e, core_deleted→f, naive_first_rail→i, wrong_supply_map→h} + negative_selftest.py + reference_submit.zip

## 自验
- golden 15/15 PASS on B ✓ (CHECK: PASS)
- golden on A sanity ✓ (10 blocks, 6 domains, 1 unclassified)
- 3-run sha256 一致 (power_domain_map.json: 1876538a15..., csv: e3349cfc..., svg: 3c5bbf6e...) ✓
- 5 negative 全 FAIL (NEG_SELFTEST_RC=0): empty→c, print_expected→e(len10≠14), core_deleted→f, naive_first_rail→i(AnaCore_S vdda≠vdd1), wrong_supply_map→h(AnaCore_N vdd1≠vdda) ✓
- §4.9 三假 (empty/print/core) 全 FAIL ✓
- test==disk check.py sha 30d3723a4176c9ace076de611e389961096afaa9a2687d7c8a349de6d99de1cf ✓
- 断言闸门 k_rationale=k_check=15(a-o)≥8 GATE PASS ✓

## DISTINCT from 现有 pg_layout / floorplan 系
r269 PpFlowSetupGen=script tree 生成 / r246 LefFromPinList=LEF 抽取 / r238 LayoutFloorplanGen=floorplan 几何(无电源域) / r185/r326 pg 分类器 —— 本案首次 ground on「layout 层次 inventory + rail net→supply-domain 映射 + 多电压块 dominant 优先级裁决 + 上色 floorplan 结构化输出」, 核心是 rail 分类+优先级裁决+三件套(json/csv/svg)生成, 非几何放置/LEF/脚本树。
