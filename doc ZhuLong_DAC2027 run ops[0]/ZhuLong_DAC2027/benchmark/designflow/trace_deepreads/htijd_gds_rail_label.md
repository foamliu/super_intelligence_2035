# deepread — 1795049723270_htijd (e0047600 @ hfeg0pjn200, mc=285)

## trace
- 435 msgs / 2.84 MB / 19 real user_input turns (`<user_input mode=act>`).
- kw: .gds:1093; skipper:40; lvs:31; floorplan:20; drc:16; pex:15; pdk:13; rtl:6; pyaether:4; synthesis:3
- domain: **physical_verify** (GDS stream manipulation + LVS/PEX context, verilog=6 low).

## real task
e0047600 在 tiler 拼接生成的 GDS 上恢复 Metal4 电源/地 rail 的 VDD/VSS pin 标签"原始规律排布"。
迭代开发 `vdd_vss_replace/vdd_vss_rail_label.py`（gdstk，1234 行，最终落盘 58729 B）。
关键 user 轮：
- UI0: "拼接后的 gds 是从 gds_tiler_1022 的 1.py 等脚本生成的，怎么生成原始的那种规律 label 排布"
- UI3: "现在 label 成矩阵，是在怎么做的"
- UI8: "那我这次要重排 vdd、vss，添加 label 的任务呢"
- UI9: "vdd_vss_rail_label.py 也输出和 1.py 输出类似排布的 label + 补全空缺的位置"
- UI11: "现在的策略是什么，先全删再添加吗"
- UI13: "暂时不删除，注释标记一下，后续可能用到"（→ 4 种流程全保留）
- UI14/15: "更新文档和使用手册 + 清理临时文件；不需要处理 tiling 的代码"

## gold deliverable（on-disk, 直接读取，无需 patch 重建）
`/home/e0047600/project_wzf/vdd_vss_replace/vdd_vss_rail_label.py`（1234 行，Nov 19 19:00）
+ `_verify_canonical_metal.py` + `使用手册.md` + `VDD_VSS_label_技术方案.md`

### 关键契约（check.py hidden B）
- rail 图形：layer 95, datatype 353(VSS)/354(VDD) —— `RAIL_DEFAULT_TEXTS = {353:"VSS", 354:"VDD"}`
  （**实际 GDS 分层归属校验得出，非按字面 353→VDD**；§5.6）
- pin label：layer 95, texttype 251，文本 VDD/VSS
- AREF 感知：`get_polygons/get_labels(apply_repetitions=True)` + `_rep_offsets(repetition.get_offsets())`
  + 引用变换矩阵 `_mat/_gx/_mmul`（旋转/镜像/放大 + 平移）
- 旧标签清理：接触判定 —— label 全局坐标到 353/354 多边形边界距离 ≤ snap_tol(0.3um) 才删
  （`delete_pg_pins_contact` + `near_rail` + `dist_poly`），非盲删
- `--restore-original`：删除前快照 `snap_orig`（apply_repetitions）→ 删 → 原样恢复快照
  （保留同位成对 label 不去重塌缩）→ 碎片覆盖兜底（中心 0.35um 内无匹配文本 label 则补：
  Y 吸附最近原始行线 tol 0.04、吸附半径 0.35，X=碎片中心，落金属外则 `dist_poly` 吸到多边形）
  → 兜底点对快照去重 → polygon 总数前==后校验 → save
- 4 种流程：默认网格 / `--per-rail` / `--fill-blank` / `--restore-original`(推荐) / `--del-only`
- 通用：从 `--gds` 读几何，无项目路径/GDS 名硬编码

## case 落库
EDA-Eval-DesignFlow-GdsRailLabelRestore-001（physical_verify, L1, 档 B, k_check=15）
- track: A-faithful-seed-synthesized-reframe（deliverable-spec reframe）
- judge: **static source-analysis**（judge env 无 gdstk/gdspy，无法动态跑；按 TapPcellBot 范式静态验源）
- 15 teeth (a-o)：zip/imports/CLI/GDS-IO/AREF/双 datatype/353→VSS·354→VDD 映射/接触删除/
  restore 快照+re-add/碎片兜底/行线吸附+落金属/95:251 Label/polygon 校验/反硬编码/确定性
- self-verify: solve.py(gold 1234 行) PASS + compact base PASS + 6 neg FAIL distinct
  （empty_shell→b, wrong_textmap→g, blind_delete→h, no_aref→e, no_restore→i, hardcoded→n）
- 隐藏 B 嵌 check.py：353→VSS/354→VDD 反直觉映射 + 接触删除 + AREF + 反硬编码
