# 深读笔记 — sid_1792660810859_l0qrf (DDGOA V0 device-usage audit)

## trace_source
- user: xiwang · host: hfeg0pkn003 (10.129.2.12) · session: 1792660810859_l0qrf
- mc=299 · domain: physical_verify (calibre 58 / schematic 1512 / netlist 553 / pyAether 256 / dbGet 46)
- msgs=265 · agent=zhulong (deepseek-v4-flash + glm-5.3-flash 混用) · 日期 2026-10-25
- 已 claim + mark deepread（shard C 台账）。**DEBT:1 → r73 必须合成 case**

## 项目背景
- DDGOA = LPDDR5 DRAM 项目，V0 版本，工艺 cxmtG4C
- 设计库：`/proj/ddgoa/V0/libs/ddgoa_cmos_top`，顶层 cell `LP5TOP/schematic`
- Aether 工程配置 `/home/xiwang/.cfg_prj` = `ddgoa V0 SE`（Schematic Editor）
- 已导出 CDL netlist 在 `workdir/ytian/*.cdl`（Channel / ChanEdgeL / CMDqL / DLDO_ChanLeft / GlbBiasGenAnalogIP / YsDecX1088_V_DDGOA / LvlShftVwlp2VfsblwnFsArygutIP / DqOutLeakCtrl + 标准单元 invGF/nand2PF/and2GFx1/invPFx2/dlyg2Ls1e/inv_DOU_eval2 等，共 21–28 份）
- pyAether 沙箱当时不可用（Connection refused @ 10.129.8.235:50640），agent 全程用 shell（run_approved_command 52 + editor 51）解析 CDL，未走 pyAether

## 用户意图（逐字原文 · A-档 seed 候选，均为「提出需求/表达目标」轮）
- **U#1/U#2**：『DDGOA项目 V0 版本schematic里面有没有用到ptk_sv这个device?』
- **U#93**：『DDGOA项目 V0 版本schematic里面有没有用到ptk这个device?』
- **U#103**：『DDGOA项目 V0 版本schematic里面有没有用到ntn_lv这个device?』
- **U#109**：『DDGOA V0 schematic中使用了哪些类型的device?』
- **U#171**：『请总结DDGOA项目V0中所有使用的晶体管，并总结每个晶体管使用的width和length的范围』
- **U#181**：『ptn这个晶体管，L=1908nm用在电路哪里？』
- **U#191**：『请总结DDGOA项目V0中所有使用的晶体管，并总结每个晶体管使用的width和length的值』
- **U#205**：『ptn这个晶体管width 12517200是用在哪个cell？』
- **U#215**：『帮忙列出上述cell使用的hierarchy』
- **U#247**：『ptn_lv W=120,000 用在哪个 cell？』

### 🚫 不得作 A-档 seed 的轮（用户已指出根因/给修复方向 → 只可作 hint）
- **U#161**：『前面我问你有没有用到ptk_sv, ptk, ntn_lv，你的回答好像都不对（你回答没有使用，实际是有使用的），请看看你的查找方式是不是需要修改』← 用户点出根因（查找方式错）→ hint，不进 prompt

## 关键错误与修正链（agent 自纠史）
1. **错误方法**（A#64–A#108）：只在设计库 `ddgoa_cmos_top` 的 `sch.oa` 二进制里 grep 器件名字符串 → 对 `ptk_sv`/`ptk`/`ntn_lv` 全报「没有使用」
   - 根因：PDK 原始器件（ptk_sv/ptk/ntn_lv）实例化在**被引用的 techlib/analog 库单元**的 schematic 里，设计库 `sch.oa` 只出现对那些**库单元**的引用（如 invGF），不直接写底层晶体管 model 名
2. **U#161 用户纠错** → A#162/A#170 agent 承认错，改方法
3. **正确方法**（A#170）：以**平铺 CDL netlist 的 element 器件 model 字段**为准（M 元素第 6 字段 = 器件类型），精确词边界匹配
4. **A#156 发现**：netlist 里**确实有** `ptk_sv`（6 instances），推翻之前「没有」
5. **A#256/A#260 自纠**：`ptn_lv` W=120000 **不存在**（agent 上一轮在截断处外推误填），实际 max=160000 @ VrAmpABM5IP

## gold（用户实际接受的结果 · 人工复核一次）

### G1. 三个器件确认使用（A#170，修正后）
| 器件 | 是否使用 | 证据 |
|---|---|---|
| `ptk_sv` | ✅ 使用 | Channel.cdl → 6（如 `MMP1 Y A vwlp! vwlp! ptk_sv W=500n L=140n nf=1`）|
| `ntn_lv` | ✅ 使用 | Channel.cdl→1974、ChanEdgeL.cdl→477、DLDO_ChanLeft.cdl→188、YsDecX1088→10、+ 标准单元 invGF/nand2PF/and2GFx1/invPFx2 |
| `ptk` | ✅ 使用 | Channel.cdl→2889、ChanEdgeL.cdl→1312、DLDO_ChanLeft.cdl→66、CMDqL.cdl→29、LvlShft→2 |

### G2. 晶体管类型 + W/L 范围（A#180，25 份 netlist，30 种类型）
PMOS：`ptn`(2384, W 200~12.5e6, L 36~1908) · `ptn_lv`(1595, W 200~160000, L 39~2000) · `ptn_lvio`(504) · `ptnlvio_sa`(15) · `ptk`(859, W 210~636000, L 124~2000) · `ptk_lv`(602) · `ptk_lvl`(44, W=954 L=318) · `ptk_s`(347) · `ptk_sv`(6, W=500 L=140)
NMOS 通用/LV/LVI：`ntn`(779) · `ntn_m`(2410, W 150~6.954e6) · `ntn_fs`(5) · `ntn_fx`(1) · `ntn_fx_a`(1) · `ntn_fx_asy`(4) · `ntn_lv`(1426) · `ntn_lvio`(488) · `ntnlvio_csl/iso/blen/sa/oc`(各3)
NMOS ntk 系/高压/ESD：`ntk`(875) · `ntk_lv`(314) · `ntk_hv`(1075) · `ntk_s`(216) · `ntk_sv1`(3) · `ntk_sv2`(3) · `ntk_esd`(4, W 444000~518000) · `ntk_esd_cap`(8, W=10000 L=1750)
核心用量：ntn_m(2410)/ptn(2384)/ptn_lv(1595)/ntn_lv(1426)/ntk_hv(1075)/ntk(875)/ptk(859)/ntn(779)

### G3. ptn L=1908nm 定位（A#190，12 处 / 4 单元，全在 Channel 块）
1. `VDD2LPDLeakCell`（VDD2 LPD 漏电控制，3 颗）：`MMP7/8/9 net8/7/6 OnN<1/2/3> net14 vbp! ptn W=878n L=1.908u nf=1`
2. 三个电压产生公共 IP（各 1 颗，结构相同）：`MMP0 vcc! BiasP vcc! vcc! ptn W=3.18u L=1.908u nf=2` @ `VncsgnComIP` / `VwlnComIP` / `VkbComIP`
- 父层实例：`XI_VDD2LPDLeakCell_1`、`XI44..VkbComIP`、`XI45..VwlnComIP`、`XI33..VncsgnComIP`，挂 `ddgoa_cmos_top/Channel/schematic`（+ ChanEdgeL）

### G4. ptn W=12,517,200nm 定位（A#210/A#214）
- cell：`SCmosDataDPCtrlNew_DDGOA_add`
- 器件行：`MMP0 svccz VPEnN vcc! vbp! ptn W=12.5172m L=50n nf=23.18K`（同 cell 还有 `MMN0 svssz VNEn vss! vbn! ntn_m W=6.954m L=50n nf=23.18K`）
- 父层实例（Channel.cdl）：`XI_SCmosDataDPCtrlNew_1_2 VNEn0 VPEnN0 vccz! vssz! vbn! vbp! vcc! vss! / SCmosDataDPCtrlNew_DDGOA_add`
- 角色：超大总宽(≈12.5mm) PMOS，nf=23.18K，单指≈540nm，Channel 数据通路 DPCtrl 大电源开关

### G5. hierarchy（A#246）
```
ddgoa_cmos_top/LP5TOP/schematic          ← 顶层
└─ ddgoa_cmos_top/Channel/schematic      ← Channel 通道块 (workdir/ytian/Channel.cdl, .SUBCKT Channel)
   └─ DPHalf                              ← 数据通路 half 子块
      └─ SCmosDataDPHalfAll_DDGOA
         └─ SCmosDataDPCtrlNew_DDGOA_add  ← 本 cell (2 元素)
            ├─ MMP0 : ptn   W=12.5172m L=50n nf=23.18K
            └─ MMN0 : ntn_m W=6.954m  L=50n nf=23.18K
```
- 实例链：`XI_SCmosDataDPCtrlNew_1_2`∈`SCmosDataDPHalfAll_DDGOA`；`XI_SCmosDataDPHalfAll`∈`DPHalf`；`DPHalf`定义于 Channel.cdl；Channel∈LP5TOP
- 诚信提示：`Channel→DPHalf` 直接 X 调用在 Channel.cdl 未搜到（DPHalf 定义存在且内部调用 SCmosDataDPHalfAll_DDGOA，但无 `X…/DPHalf` 行）→ 该级可能在更上层/需 schematic 确认

### G6. ptn_lv W=120000 纠正（A#260）
- `ptn_lv` **不存在** W=120000nm（agent 上轮截断外推误填）
- `ptn_lv` 实际大宽度：max=**160000nm** @ `VrAmpABM5IP`（Channel.cdl，`MMP5 pwr EnN vcc! vcc! ptn_lv W=160u L=250n nf=160`）；81408nm @ `Vad2NewStructureStbyAmpBiasIP`/`Vap2NewStructureStbyAmpBiasIP`/`VintlpStbyChBiasIP`（6 处）
- 120000nm 实际属 `ptn`（不是 ptn_lv）

### G7. CDL 器件行格式（解析口径）
- M 元素：`M<name> <drain> <gate> <source> <body> <model> W=… L=… nf=…`
- model = 第 6 字段（器件类型）；W/L 单位换算：n=nm, u=µm(×1000), m=mm(×1e6), K=×1000
- 部分实例 W/L 用单元参数（WN/WP/LN/LP）给定 → 不计入显式数值统计
- X 元素：`X<inst> <pins>… / <subckt>` → 层级/hierarchy

## 计划 case（r73 合成）
- **id**：`EDA-Eval-DesignFlow-DdgoaDeviceAudit-001`
- **domain**：physical_verify · **track**：A-档 faithful（用户逐字意图）· **level**：L1（离线 CDL netlist 解析，无 EDA 工具）
- **候选交付**：`ddgoa_device_audit.py`（stdlib re/json）— 读 `<netlist_dir>` + `<query_manifest.json>`，解析所有 `.cdl` 的 M 元素 → 输出 JSON：{device_types:[{model,inst_count,W_min,W_max,L_min,L_max}], locate:{<query>: {model,W,L,subckt,instance_line}}, hierarchy:{<cell>:[parent_chain]}, method_correction: bool(是否用 netlist element model 而非 sch.oa 字符串)}
- **A（可见）**：从 xiwang 机 `/proj/ddgoa/V0/.../workdir/ytian/` scp 一批真实 CDL（Channel.cdl + ChanEdgeL.cdl + 几个标准单元）+ `query_manifest_A.json`（query: ptk_sv 是否使用 / ptn L=1908 定位 / ptn W=12517200 定位 / hierarchy of SCmosDataDPCtrlNew_DDGOA_add）
- **hidden B**：另一批 CDL（CMDqL/DLDO_ChanLeft/GlbBiasGenAnalogIP）+ `query_manifest_B.json`（不同 query：ntn_lv 使用 / ntk_esd W 范围 / 定位 ntn_m W=6.954m 的 cell）— 击穿硬编码 A
- **B2（method-broken）**：候选用 sch.oa 字符串搜索（错误方法）→ method_correction=False + 漏报 ptk_sv → stage METHOD_SCH_OA_ONLY
- **B3（locate-broken）**：候选定位逻辑只返回 cell 名不带 instance_line / W/L 核对 → stage LOCATE_INCOMPLETE
- **check.py ≥8 条断言**（k≥8 GATE）：①zip+compile+多run rc0 ②A device_types 30 种齐全 + ptk_sv inst_count=6 ③A ptn W_min=200 W_max=12517200 L_min=36 L_max=1908 ④A locate ptn L=1908 → VDD2LPDLeakCell + 3 IP（VncsgnComIP/VwlnComIP/VkbComIP）+ instance_line 含 W=878n/3.18u ⑤A locate ptn W=12517200 → SCmosDataDPCtrlNew_DDGOA_add + instance_line 含 nf=23.18K + 同 cell MMN0 ntn_m W=6.954m ⑥A hierarchy LP5TOP→Channel→DPHalf→SCmosDataDPHalfAll_DDGOA→SCmosDataDPCtrlNew_DDGOA_add ⑦A method_correction=True（用 netlist element model，非 sch.oa grep）⑧跨输入 B ntn_lv inst_count>0 + ntk_esd W 范围 444000~518000 + 定位 ntn_m W=6.954m → 同 cell SCmosDataDPCtrlNew_DDGOA_add（击穿硬编码 A）⑨B2 method_correction=False + ptk_sv 漏报 → stage METHOD_SCH_OA_ONLY ⑩B3 locate 无 instance_line → stage LOCATE_INCOMPLETE ⑪确定性 B 3×md5 ⑫结构：候选解析 M 元素第 6 字段为 model + W/L 单位换算(n/u/m/K)真实。k=12 ≥8 ✓
- **negatives**：fake_empty→① / fake_print_expected→⑧(硬编码 A 的 ptk_sv=6 给 B) / fake_core_deleted→④(strip instance_line) / naive_sch_oa_only→⑨ / naive_hardcode_ptn_locate→⑤(硬编码 SCmosDataDPCtrlNew 给 B 的 ntn_m query) — NEG_RC=0
- **资产抓取**：r73 首件事 = ssh 10.129.2.12 scp `/proj/ddgoa/V0/.../workdir/ytian/*.cdl`（先 `find` 定位 ytian 目录）→ 取 6–8 份 CDL 作 A/B
- **与既有区别**：SpfstdBtn-001=netlist trigger GUI 按钮；本案=CDL netlist 器件统计/定位/hierarchy 审计，主题独立（shard D 已用同 j8f3i trace，本案用 l0qrf 不同 trace，无冲突）

## 备注
- agent 全程未成功用 pyAether（沙箱 refused），纯 shell 解析 CDL → 天然 L1（离线文本解析，不需 EDA 工具）✓
- gold 数据量大（30 类型 × W/L 值列表）→ check.py 只断言关键 type/count/range/locate/hierarchy，不要求全量值列表精确匹配（避免过脆）
- 用户两轮纠正（U#161 方法错 + U#247 W=120000 不存在）→ gold 含 method_correction 与 self_correction 两个诚信维度，可作断言对象
