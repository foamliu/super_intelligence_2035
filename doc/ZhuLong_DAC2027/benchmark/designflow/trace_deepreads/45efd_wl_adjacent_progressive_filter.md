# 深读笔记 · 45efd · WL 相邻检测 4 级递推过滤

- session: `1795430404537_45efd.messages.json` (63 msgs, 6 user turns)
- user: ziyuny · host: hfeg0pnd001 · mc=60 · domain: physical_verify
- keywords: drc:248 / calibre:95 / .spi:69 / lvs:52 / .gds:43 / .cdl:33 / netlist:15

## 用户真实意图（U#1，唯一实质任务）

对 GDS `/proj/ddgoa/V0/ver/lvs_argus/BL_coupling_tpc_help_444matspace_rev7_modifyWL_1113bk/A_mblx744_e_wlo_WL/A_mblx744_e_wlo_WL.gds` 跑 `wl-adjacent-detect` skill 流程，产出 **4 级递进过滤的相邻 WL 对表（CSV 交付）**：

| 表 | 规则 | 数学条件（Δ = WL 编号差） |
|---|---|---|
| 1 (all) | wle↔wle、wlo↔wlo 同标记全部相邻对 | 同 marker |
| 2 (d2) | 表1 ∩ Δ%2==0 | Δ×2 mod 4 == 0 |
| 3 (d4) | 表2 ∩ Δ%4==0 | Δ×2 mod 8 == 0 |
| 4 (d8) | 表3 ∩ Δ%8==0 | Δ×2 mod 16 == 0 |

严格嵌套：d8 ⊆ d4 ⊆ d2 ⊆ all。缺省 space 阈值 0.182μm。

## assistant 工具链与关键产物

1. **S0 侦察**：确认 GDS 存在、顶层 cell=`A_mblx744_e_wlo_WL`、读 `.spi`/`.cdl` 网表确认 WL 网名格式 `H_WL[oe]<bit>`。
2. **S1 pattern 翻译**：解析 GDS TEXT 记录普查标签族 → 严格版 `^[A-Za-z_]*WL[oe][0-9A-Za-z_]*<[0-9]+>$`、宽松版 `?WL?<?>`。
3. **S2 Calibre**：rundrc.sh 提交 Job<3967760>，13 rulecheck 0 violation。
4. **S3 体检**：unattached=0、ERROR=0；m3a 三链全名前，其余链 empty-vector（已知现象）。
5. **S4 parser**：1705 对 / 1134 个 WL；multi-member=0、跨链 WARNING=0、one-sided=1184（子 cell 内部网 deck 抓不到）。
6. **S5/S6**：rep2csv + 4 级后处理 → 4 张 CSV（all=1705 / d2=232 / d4=109 / d8=91）。Δ 直方图主峰 31/33（WL strapping 跨 section）。

## 可交付意图抽取（合成 case 用）

抽「.rep 解析 → WL 名匹配严格正则 → Δ 计算 → 4 级 Δ%2^n 递进过滤 → 4 CSV」这一**纯计算后处理**意图。Calibre 运行环境相关，不进 case；交付件 = Python 脚本，输入 Calibre-style `.rep`，输出 4 CSV。

**判分要点（有牙）**：
- 严格正则过滤（trap 名 `WLstrap<N>`/`BusWL<N>` 等 WL 后非 o/e 须排除）
- 同 marker 过滤（e↔o 跨标记对排除）
- 2-member cluster 才配对（3-member cluster 不生成 pair）
- 去重（重复 cluster 1 行）
- Δ = |index 差|
- 4 级 Δ%2^n 严格嵌套
- 行序（delta, name）+ wl_a 小 index 在前
- RFC4180 CSV

## 自包含重建

- **visible A**：`wl_pairs.rep`（Calibre-style，o/e 两族 + trap + cross-marker + 3-member + 重复 cluster）
- **hidden B**：check.py 内嵌生成器构建（不同族名 `gut_WLo_m3a<N>`/`gut_WLe_m3a<N>`、不同 index 范围、不同 trap）
- **randomization C**：check.py 随机种子生成小 .rep，candidate 须与 reference 一致
- 与 A 在族名/index 规模/cluster 结构/trap 类型全不同

## 质量闸门

- k≥8 独立断言；3 neg（empty/print_only/delete_core）全 FAIL；§4.9 三假 FAIL；hidden B；随机化 3 种子；判分契约 return True/False。
