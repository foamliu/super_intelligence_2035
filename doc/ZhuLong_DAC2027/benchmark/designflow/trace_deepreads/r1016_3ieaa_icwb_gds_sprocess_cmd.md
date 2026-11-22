# r1016 deepread — 3ieaa (rayfeng@hfeg0pkn003) — IcwbGdsSprocessCmdProduce

## trace
- SID: 1795162765195_3ieaa.messages.json (rayfeng @ hfeg0pkn003=10.129.2.12, mc=89, ac379/cc24/bc15 A-pure eda_other/TCAD)
- 116 msgs, 2 user_input (U#0 task, U#9 "继续任务")
- scan: ssh_eda_search_20261122_172249, digA2 narrow-C_KW filter (ac>cc&&ac>bc&&ac>=5&&mc>=5) → 647 unique → 18 fresh (4216 4-shard ledger sids)
- NEW user rayfeng (no prior cases), 3ieaa fresh (verified absent from all 4 shard ledgers)

## user intent (U#0 verbatim)
> 帮我检查当前环境下是否有TCAD里面IC workbench工具和license，并提供通过icwb导入gds生成.mac在sprocess中建模的全套SOP

## session主线
- agent 探测 Sentaurus W-2024.09-SP1 安装（独立 icwb 可执行文件不存在，但 ICWB 引擎完整内置于 sprocess：ELF 含 IcwbCommand/icwbReader/.mac 解析器）
- license 实测（12000@dc21/dc22，SILICON_WORKBENCH + sprocess_all 可用，v2030.12 有效期 2030-12-30）
- 写 icwb_smoke.cmd（sprocess .cmd deck）跑通 GDS→icwb→mask→etch→struct 全链路 smoke test
- 交付 ICWB_GDS_sprocess_SOP.md（13.8KB 完整 SOP）+ icwb_smoke.cmd

## trace gold (.cmd deck, editor a66/a75)
icwb gds.file= "BICMOSinverter.gds" cell= Inverter layer.numbers= {1:0...9:0} layer.names= {NWELL NPDIFF PPDIFF NPLUG POLY PBASE EMIT METAL CONT} sim2d= {1000.0 4100.0 1000.0 6200.0} scale= 1e-3
→ icwb list domains/layerNames/layerIDs/dimension/bbox 查询 + LogFile
→ icwb.create.all.masks + icwb.create.mask layer.name= "NPDIFF PPDIFF NPLUG PBASE" name= STI_n polarity= negative
→ line x/y, region silicon, init silicon field= Boron concentration= 1e14, deposit Photoresist, etch Photoresist mask= NWELL_n, struct tdr.bnd= icwb_smoke

## case reframe (analysis/flow-driving → produce-task)
trace gold .cmd deck → 通用 gen_icwb_sprocess_cmd.py <spec.json> <output.cmd>
spec schema: gds_file/cell/layer_numbers/layer_names/sim2d/scale/mask_groups/lines/region/init/deposit/etch/struct_output/struct_mode/log_messages

## A/B
- A (visible): spec_A.json — real BICMOSinverter (9 layers NWELL/NPDIFF/PPDIFF/NPLUG/POLY/PBASE/EMIT/METAL/CONT, cell Inverter, sim2d {1000.0 4100.0 1000.0 6200.0}, scale 1e-3, STI_n negative, etch NWELL_n, struct tdr.bnd icwb_smoke, init Boron 1e14)
- B (hidden): spec_B.json — synthesized 6T SRAM bitcell (7 layers Psub/Nwell/Pwell/Active/Poly/Met1/Via1, cell Bitcell, sim2d {2500.0 5800.0 3200.0 7400.0}, scale 1e-4, ACT_p positive, etch Nwell_p, struct tdr.out sram6t_build, init Phosphorus 5e13) — all concrete values differ from A

## check.py (k=19 ≥ 8)
① zip 含 gen_icwb_sprocess_cmd.py ② py_compile ③ B 运行 exit0 输出>400B ④ icwb gds.file="SRAM6T_cell.gds"(反A) ⑤ cell= Bitcell(反A) ⑥ B 7层全有+A 8层不泄漏 ⑦ sim2d B bbox(反A) ⑧ scale 0.0001(反A 0.001) ⑨ icwb.create.all.masks ⑩ B mask group ACT_p positive(反A STI_n) ⑪ etch Oxide mask=Nwell_p(反A NWELL_n) ⑫ struct tdr.out sram6t_build(反A) ⑬ init Phosphorus 5e13(反A Boron) ⑭ line x 8.0(反A 10.0) ⑮ A-token 全不泄漏 ⑯ 3次md5一致 ⑰ >400B反空壳 ⑱ >200B+def+import反print-only ⑲ A spec 也 exit0 产 A 标记反 core-deleted

## verification
- ref PASS 19/19 (selftest in-place)
- E2E PASS (harness-layout: JUDGE/g1/g2 cwd, assets/CASE/hidden symlink → check.py 找到 hidden B + visible A)
- 3 negs FAIL: neg_empty(③空输出) / neg_print_only(④⑤A 值泄漏) / neg_core_deleted(④缺 gds.file)
- §4.9 三假 FAIL ✓

## A.jsonl 471 → 472; ledger 3ieaa claimed → case
