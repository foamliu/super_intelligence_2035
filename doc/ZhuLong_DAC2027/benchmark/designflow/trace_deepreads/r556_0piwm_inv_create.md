# r556 deep-read — trace 1794384121107_0piwm (xdwang @ hfeg0plg94)

- **session**: `1794384121107_0piwm`, user `xdwang`, host `hfeg0plg94` (10.129.8.226)
- **size**: 729KB, 88 msgs, 3 user turns
- **domain**: layout_aether (pyaether:384 / aether:144 / dbcreateinst:74)
- **mc**: 176 (fresh, from ssh_eda_search_20261113_131349, src=summary_1113.tsv)
- **claim**: ledger_C claimed r556 → marked case `EDA-Eval-DesignFlow-InvCellCreate-001`

## 3 user turns
- **U#0** (Q&A analyze): `/proj/dscqa/V0/workdir/xdwang/00_DSCQA_SA/TimingCtrl` — "check this schematic ... how much inverters". assistant 用 pyAether `aeGetCurDesign()` 读 TimingCtrl schematic，遍历 `cv.instances`，按 cellName 含 "inv" 计数 → **3 个 invLVx1** (I92/I7/I9, stdcells_ac)。
- **U#1** (modify-existing): "add 1 inverter to the net Eqmsa". assistant `dbCrtInst` 放 invLVx1 I10@(12.0,4.5)，`dbMakeNet` 建 Eqmsa_n，`emyInstTermAddToNet` 连 A→Eqmsa/Y→Eqmsa_n/vcc→vcc!/vss→vss!/vbp/vbn；初始 read-only save 失败，`dbOpenCV(...,mode='edit')` 重开后 `cv.save()` 成功（saveTime 15:25:34→16:13:58）。
- **U#2** (produce-task author-new-cell) ← **本 case 任务源**: "create a new circuit INV in this lib and realize a inverter function" (lib=`00_DSCQA_SA`)。assistant 检索 `dbNewCV`/`dbCrtSymbolPin`/`dbCrtPinByNet`/`aeGenSymbolAndSchematicByVerilog`，规划用 dbNewCV 建 schematic+symbol、dbCrtInst 放 PMOS+NMOS、dbMakeNet+emyInstTermAddToNet 连 g/d/s/b、dbCrtPinByNet 建 pin、dbCrtSymbolPin 放 4 symbol pin。**但 Aether GUI 桥 (10.129.8.226:52163) 中途 connection refused**，cell 实际未建成，assistant 转而 `ask_question` 请用户重启桥 → **任务未完成**（INCOMPLETE produce-task）。

## case 合成决策
- U#2 是 A档合格 produce-task（author-new-cell，明确产件意图），但 trace 本身**未交付**（桥死）。
- 按 r539–r554 case_family：**B档 synthesized mock-behavioral** —— 把"新建 INV cell"抽成纯 Python 重建任务，端口 pyAether 创建逻辑为确定性 JSON 描述，mock 掉 OA/license/GUI 依赖。
- 核心算法保留：PMOS(上)+NMOS(下) 垂直堆叠放置、g/d/s/b 端子、IN/OUT/vdd/vss 四网（bulk 接对应 supply）、4 schematic pin（OUT=output）、symbol bbox+4 symbol pin（IN 左/OUT 右/vdd 上/vss 下）。
- 双隐藏 deck 防硬编：B (CORELIB/INVX1/pmos2v, pitch2.5, origin[1,1]) 与 B2 (IOLIB/INV2/pmos5v, pitch3.0, origin[0.5,0.5])，cell/lib/master/origin/W-L 全不同。
- 16 条断言（a–p），k_check==k_rationale==16 ≥8；GOLD PASS 16/16；7 fake（含 §4.9 三 fake）全 FAIL，NEG_RC=0。

## 交付
- EDA-Flow-Bench master: `EDA-Eval-DesignFlow_C.jsonl` (+1 → 339) + `assets/EDA-Eval-DesignFlow-InvCellCreate-001/` (A + hidden B/B2) + `reference/EDA-Eval-DesignFlow-InvCellCreate-001/` (check.py + build_inv_cell.py ref + reference_submit.zip + negative/negative_selftest.py)
- super_intelligence_2035 main: 本 deep-read + trace_ledger_C.tsv (claimed→case) + MEMORY_C + daily_C
