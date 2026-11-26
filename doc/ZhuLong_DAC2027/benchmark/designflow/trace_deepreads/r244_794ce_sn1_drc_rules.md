# 深读笔记 r244 — 1791963569790_794ce (lipingy, physical_verify)

- **trace**: 1791963569790_794ce · user lipingy · host hfeg0pkn003 (10.129.2.12) · mc=179
- **keywords**: drc:503 calibre:413 pyaether:24 transistor:16 lvs:16 pex:11 virtuoso:7 aether:7
- **tools**: 109 calibre 4 pyAether 1 schematic 1 "lang":"pyAether"
- **NEW user** lipingy（ledger 0 条；首个 case 候选）
- **agent**: lead (glm-5.3-flash / test20261014)
- **session**: 94 msgs, 855KB; scp 到 .75 workdir 解析
- **ledger**: r244 claim → status=claimed（case 合成留 r245）

## 工作区
- `/home/lipingy/AutoDRC/calibreDRC.rule` — 长鑫 DRAM Calibre DRC 规则文件，TVF 格式，~27,504 行
  - 头部 `#DEFINE`（TOP_METAL_IS_M5/M8、LPDRC_CHECK、CAD_RULE_CHECK、G4PLUS_FUSE_SPECIAL_RULES，带 `#IFDEF/#IFNDEF/#ELSE/#ENDIF`）
  - 第一 `tvf::VERBATIM`：`LAYER`+`MAP`（M0~M5/RDL、PG/PC/CT/V1…、mark/矩阵）
  - 第二 `tvf::VERBATIM`：检查逻辑（端口分类、CHIP/BULK/CORE/ARRAY/PERI 区域、well/active/diff、width/spacing/enclosure）
- SN1 定义：`LAYER SN1_drawing`(70:7) + `SN1_mark`/`SN1_ARRAY`/`SN1_reference`；行 2583 `SN1 = COPY SN1_drawing //70:7 cell vertical`
- 现成角度范例（行 2974-2975）：`BWL_ARRAY_H = BWL_ARRAY WITH EDGE (ANGLE WL_longEdge == 0)` / `... == 90`

## 用户真实意图（3 轮提出需求，未给根因/方案 → 均符合 A 档/B 档 seed）
1. **U#0**「写DRC」— 太开放，assistant ask_question 后用户选「在现有 deck 新增/修改具体 DRC 检查」
2. **U#30**「查SN1方向一致性，必须都为60度」— ★ 具体、可验
3. **U#84**「如何用DRC写一条rule，查矩形的短边与长边之比，必须小于0.8，如M1_drawing」— ★ 最具体、最可离线验
4. **U#92**「M1是"回形"pattern，如何show出M1的外轮廓」— ★ 具体 SVRF 概念

## gold（assistant 真实产物）
### U#30 SN1 60° 方向一致性（已插入 deck 行 14725-14741）
- 方案：60° 倾斜矩形的四边方向族 = {60, 150, -30, -120}（60° 主向 + 垂直向）
- 规则块 `SN1_F_dir_000_00 { @ Forbidden - SN1 direction not in 60deg family ... WITH EDGE (ANGLE ... == 60/150/-30/-120) ... }`，插入位置 `CELL_CELL_S_006_00` 之后、`GROUP CELL_CELL` 之前
- 沿用 deck `WITH EDGE (ANGLE X == Y)` 语法

### U#84 M1 短边/长边 < 0.8（A#91，SVRF 文字回答 + 规则草稿）
- 关系：W/L < 0.8 ⇔ L > 1.25×W
- 方法一（推荐，适配 deck 风格）：`INT`+`LENGTH` 阶梯逼近 —— `INT M1_drawing < X` 找宽度不足 X 的瘦条，`LENGTH M1_drawing > Y` 找长边，比值阈值用阶梯覆盖
- 方法二：新版本 `RATIO` 关键字（非标准）
- 规则草稿 `M1_ASPECT ... `（短边/长边 < 0.8 → 违规）

### U#92 M1 回形外轮廓（A#93，3 种 SVRF 方法）
- 方法一：`SIZE M1_drawing BY 5.0` 填洞 → `SIZE M1_filled BY -5.0` 回到外边界（X 须大于空腔跨距一半）
- 方法二：`HOLES M1_drawing INNER` 取内孔 → `OR M1_drawing M1_holes` 合并得实心外轮廓
- 方法三：描边（只画外边界线，不填区域）

## case 合成方向（r245）
**首选 U#84（矩形短边/长边 < 0.8 aspect-ratio 检查）** —— 最可离线验：
- **B-synthesized L1**：SUT 写 `aspect_check.py`（CLI `<rects.txt> --max-ratio 0.8 -o <violations.txt>`，stdlib only），解析矩形坐标（x1 y1 x2 y2），计算 short_edge/long_edge，flag >= 0.8 的矩形 + 报告
- A（可见）= trace-grounded（M1_drawing，ratio 阈值 0.8，一组矩形含违规/合规）；隐藏 B = 不同层名 + 不同阈值（如 0.6）+ 不同矩形集（杀硬编码）
- 断言方向：zip/py_compile/stdlib-only；B exit0+输出非空；B 违规矩形集合==golden_B（精确 id+ratio）；B 合规矩形不被误报；ratio 计算精度（边界 0.8/0.6 容差）；正方形(1:1)必报；极细长(1:100)必不报；退化(0 面积/线)处理；反硬编码 out_B==golden_B 且 !=golden_A；3-seed 确定性；缺失输入非零退出 → ≥12 条
- 备选 U#30（SN1 60° 方向族）—— 需多边形边方向计算，稍复杂；U#92（回形外轮廓 SIZE/HOLES）—— 需多边形 hole-filling，最复杂

## DEBT
- r244 选料轮：0 case 交付。DEBT:1（deepread 已完成，case 合成留 r245 第一件事）
- 已 park 候选（不入 ledger，仅记录）：mirbg yohannw（permission denied，home 不可读）；369rv mwxi（ops/devops，crontab 同步检查，非 EDA 工程）
- 本轮排查结论：shard C 高 mc(>=100) NEW-user layout 候选已基本枯竭（llns7/awgyg/nqgxe/f1fik/dq8bz/5m5ut/wp528/sakf0/791f6/k1af0 等均已入台账 case/parked）；mc 30-80 区间仍有 clean NEW-user physical_verify 候选（794ce lipingy[已claim]、9lbfz iceyma、giaze pdsong、1m39e e0042624），后续可逐步消化
