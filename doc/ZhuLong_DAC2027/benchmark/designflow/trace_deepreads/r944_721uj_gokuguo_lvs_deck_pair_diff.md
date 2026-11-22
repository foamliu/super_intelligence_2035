# Deepread — 1793348781264_721uj (gokuguo @ hfeg0plg53)

- session: 1793348781264_721uj (started 2026-10-30 08:26, ended 08:42, completed, deepseek-v4-flash, cwd=/home/gokuguo)
- mc=58, kw: `lvs:340;calibre:22;netlist:14;pex:8;pdk:6;hspice:4;drc:4;gdsii:2`
- 46 msgs, 204886 bytes messages.json (parsed on .75 sandbox at /tmp/721uj.messages.json)
- domain: **physical_verify (C)** — Calibre LVS SVRF rule-file diff, no spice/char

## 用户意图（逐字摘录）

- U#0 (msg[0]): 「对比一下/home/gokuguo/Desktop/vir_setup_cant_remove/Batch_LVS/LVS_file路径下，Test07和Test08这两个文件的区别」
- U#26 (msg[26]): 「你是不是对比错了？我说的是 35H_1P18M_18F1xa1x1xb1ya6y2yy2yx2z_LVS_Cal_V0d1_Rev06_Test07.lvs 和 35H_1P18M_18F1xa1x1xb1ya6y2yy2yx2z_LVS_Cal_V0d1_Rev06_Test08.lvs 这两个」
- U#34 (msg[34]): 「哦我错了，是 35H_1P18M_18F1xa1x1xb1ya6y2yy2yx2z_LVS_Cal_V0d1_Rev06_Test08.lvs 和 35H_1P18M_18F1xa1x1xb1ya6y2yy2yx2z_LVS_Cal_V0d1_Rev13_S10.lvs 这两个」← **最终意图**
- U#40 (msg[40]): 「现在再对比一下呢」← 用户改完 Test08 后要求重跑 diff

## Assistant 工具链

1. list_allowed_files LVS_file 目录 → 列出 Test07/Test08/Rev13_S10 三个 .lvs 文件
2. read_files Test07.lvs + Test08.lvs（11k+ 行，截断）
3. editor 写 /home/gokuguo/diff_lvs.py（Python difflib 逐行 diff）
4. run_approved_command python-runner 执行 → 41 diff blocks 输出（中间 #DECRYPT 加密区截断）
5. editor 改 diff_lvs.py（缩短行 + 只 print block 16-25）
6. run_approved_command 重跑 → 拿到中间块
7. （用户改 Test08 vs Rev13_S10 后）editor 写 diff_lvs2.py
8. run_approved_command 重跑 → 11 plaintext diff blocks
9. read_files 第 155-162 / 482-483 行验证 ENABLE_WELL_TEXT 和 VIRTUAL CONNECT 修改生效
10. run_approved_command 再跑 → 9 diff blocks（差异减少）

## gold 输出（msg[25] / msg[39] / msg[45]）

差异维度（5 类）：

1. **版本/Header**：TITLE 文档版本（Rev13_S3→S11→S10）、命令文件版本号、日期、Change log 条数
2. **功能开关**：`#DEFINE ENABLE_WELL_TEXT TRUE|FALSE`、`#IFDEF ENABLE_PDSP` 包裹段
3. **虚拟连接**：`VIRTUAL CONNECT NAME "VPP"/"VDD"`（active）vs `//VIRTUAL CONNECT NAME "?"`（commented out）
4. **器件注释状态**：`rt_mom_2t_fs`、`ind_450ph_2t_fs`、`rbm1_fs` 的 `(not implement)` / `(not remove)` 标注
5. **新增 LAYER**：`LAYER NAME L4 IND_BODY (10852)`、`VMOD1_MK (10853)`、`VMOD2_MK (10854)`、`VMOD3_MK (10855)`

辅助指标：行数、字节数、加密区行数（#DECRYPT 块）、相似度 ratio（difflib SequenceMatcher.ratio()）、总 diff blocks、明文 diff blocks

## 跨 shard 串台检查

- 4-shard ledger: 721uj 仅 B shard parked（misfiled as spice_sim，B deepread 自己承认 "pure physical_verify C-domain, no spice/char"），C r944 `mark --status claimed --force` 复活
- 4-shard jsonl trace_source 无 721uj
- 同 domain 已落库 case 全正交（LvsRuntimeDiff=时序、RcDiffStarGloryReport=RC 报告、NetlistCellReplaceDiffAnalyzer=网表 cell 替换、SkillTreeDiffAudit=SKILL 树、GdsLvlStructDiff=GDS 层、ItfDirTreeDiffReport=ITF 目录树、DummyDeckStructDiff=dummy deck、DiffNetConnLayerSelect=net 连接层、CalibreLvsRulePtnFix=LVS rule 模式修复、RunsetPairCmpGen=layermap 对比、LayermapPairAudit=layermap 审计）—— 子型 "lvs_deck_pair_diff_svrf" 首例（对比两个 .lvs SVRF rule deck 的多维结构化 diff）

## 合成方向

档 B reframe fixture-driven：agent 写 `lvs_deck_pair_diff.py` 读两个 .lvs SVRF rule deck，emit JSON {file_a/file_b (path/size/lines/title/version/date), summary (total_diff_blocks/plaintext_diff_blocks/similarity_ratio/encrypted_lines_a/encrypted_lines_b), diff_blocks[], switches[], virtual_connects[], device_annotations[], added_layers_b[]}。env_A (Test08 vs Rev13_S10, 11-12k 行带 #DECRYPT 加密区, ENABLE_WELL_TEXT/VIRTUAL CONNECT/rt_mom/ind_450ph/rbm1/IND_BODY/VMOD1-3_MK) + hidden B (Rev14 系列不同 deck, ENABLE_HCELL/MOM_RES_BODY/MOM_CAP_BODY/COIL_MK/mom_res_3t/mom_cap_2t 不同具体值)。check() 真跑 B 上候选脚本，断言 JSON 结构 + 具体取值，≥10 独立条件。
