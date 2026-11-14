# r553 trace deepread — dzbpb (weizhao@hfeg0pkn001)

- **session**: 1791460442634_dzbpb
- **user/host**: weizhao / hfeg0pkn001
- **mc**: 124 (pdk:124;calibre:124;drc:2)
- **size**: 844KB, 28 messages, 1 user turn
- **classification**: A档合格 produce-task author-new-script（提需求未给根因/方案）
- **domain**: physical_verify (Calibre PDK layer.map)
- **ACCEPT**: r553 → case LayerMapReleaseNote-001

## User turn (verbatim)

> U#0: 对比 /home/pdk/weizhao/sos/runsetRules/calibre/cxmtG5_CIP/current/common/layer.map_all/G5_CIP/layer.map_20260811_newnew /home/pdk/weizhao/sos/runsetRules/calibre/cxmtG5_CIP/current/common/layer.map_all/G5_CIP/layer.map_20261008_newnew 并输出一个releasenote

## Assistant 行为

1. **read_files** 两个 layer.map（各 1205 行，截断 368 行/次）→ 分块读 369-800, 320-370, 140-200, 1-40, 31-98, 446-455, 1030-1055, 60-75, 240-252, 220-240, 275-295, 415-448, 465-478, 1100-1135, 1060-1205 等 ~20 次 read_files
2. **run_commands** `diff` → 被 agent-policy-engine 禁止（"Raw shell tool run_commands is disabled; use run_approved_command"）
3. **get_agent_policy_status** → policy enforcing
4. 手动逐段对比两个文件，识别差异
5. 生成 markdown Release Note（msg[27] TEXT）

## layer.map 格式

```
############ user_defined ##########
LAYER_NAME    PURPOSE    GDS_LAYER    GDS_DATATYPE
```
空白分隔，`#` 注释行。同一 LAYER_NAME 多行（不同 PURPOSE）。

## Release Note 差异（assistant 识别）

### 一、新增层
- PASS (gds 99): TPV(35), KEY1(41), drawing(0)

### 二、移除层
- BAM (174): KEY1
- BPA (175): CMP, prohibit_cmp, SL, KEY1, drawing, pin
- BPZ (176): probe, bonding, KEY1, PROHIBIT_BOOLEAN, drawing
- TSV (140): KEY1, drawing
- C1FBZ (350): drawing

### 三、已有层属性新增
- AT4 (4): SRF (9)
- PG (30): SRF (9)
- SGD (19): PROHIBIT_BOOLEAN (261)
- DGX (20): PROHIBIT_BOOLEAN (261)
- TCP (78): PAD_drawing (402)
- M1 (88): voltage (31), switch_TSV (38), switch_NORMAL (39)
- M2 (91): MOM (376)
- M3 (93): MOM (376)
- M4 (95): MOM (376)
- M5 (103): slot (40)
- M0U (66): net (253)
- RLDEV (302): mark75 (525)
- prBoundary (235): drawing (0)

### 四、已有层属性移除
- SNT (74): ARRAY (7)

## Case 建模 (B档 synthesized mock-behavioral)

承 r545-r552 族：把"live Calibre layer.map 逐段对比→markdown Release Note"重构为纯 Python JSON fixture（核心 parse_layer_map + set-diff 算法不变）：

- **可见输入 A**: old_layer.map (6 行) + new_layer.map (7 行) + task_brief.md
- **hidden B**: B_old.map (13 行) + B_new.map (13 行) — diff: new=M3, removed=BAM, added=AT4/SRF+M1/voltage, removed=AR/ARRAY
- **hidden B2**: B2_old.map (9 行) + B2_new.map (8 行) — diff: new=PASS, removed=TSV, added=M2/MOM, removed=AT1/KEY1+PG/SRF
- **交付**: layer_map_releasenote.py (argparse --old/--new/--out + parse + compute_diff + json.dump sort_keys)
- **15 条件 a-o**: 结构2(a-b) + 运行2(c-d) + B内容8(e-l: 4键/新层/移层/增属/移属/移层属排除/gds来源new/gds来源old) + 防硬编2(m-n) + 确定性1(o)

## 自验

- GOLD 15/15 PASS ✓
- 4 neg (naive_empty/print_expected/core_deleted/naive_wrong_algo) all FAIL ✓
- §4.9 三假 (empty/print/core-deleted) all FAIL ✓
- E2E (check.py + reference_submit.zip + hidden workdir) 15/15 ✓
- k_rationale=15 = k_check=15 ≥ 8 ✓

## r527 动词法

dzbpb: U#0 "对比...并输出一个releasenote" = **produce-task author-new-script**（提需求未给根因/方案）→ ACCEPT ✓
