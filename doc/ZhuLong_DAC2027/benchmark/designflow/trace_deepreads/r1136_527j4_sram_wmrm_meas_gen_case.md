# r1136 (2026-11-24) — 527j4 case 合成轮 · SramWmRmMeasGenProduce-001 落库

## 背景
r1135 build-round deepread 完成对 527j4 (shanliny@hfeg0plg107) 的深读 + 资产抓取，推翻 r1131 "不可自包含" 结论，确定 case 可封装为 L1。本轮 r1136 执行合成 + 自验 + 落库。

## 本轮动作
1. eda_flow open_session → ssh hfeg0plg107 scp 完整 527j4 session uploads 全量资产 (sram_meas_gen.py 14744B ref + config_path.txt 48611B + racing.vec + config_racing_meas + rmwm 参考输出 + dspf_header 1.5KB)
2. ref 跑 A(64×8) 验证：rmwm.vec 33083B 与真实 rmwm_ref.vec 字节级一致 ✓
3. 构造 B (合成 32×4 instance MYTEST_SRAM_32X4M4B2)：cm=2/bk=2/nw=32/nb=4 → aw=5/dw=4/bw=4, mux=2, nxdec_perbk=1; dspf_header_B.txt(.SUBCKT) + config_path_B.txt($lio_*/$array_bk*/32 个 $bitcell_* 宏)
4. **发现 ref 的 Cfg._expand_one 宏展开 bug**：`\b\$` 正则在串首不匹配 + $nb_l/$nxdec_perbk 被 macro loop 先替换成原始表达式 "floor($bits/2)-1"/"$words/$mux/..." 而非计算值 → bitcell 路径破损。修复 ref：computed int 先替换 + macro loop skip computed keys + 用 `(?<![\w$])\$key(?![\w$])` 替代 `\b\$`。修复后 A/B bitcell 路径全干净 (xtop.xbkb.xbk_l.xarray.xir1.xic3...)。ref 是 grader oracle，必须正确 (§4.9)，修复合理。
5. check() 13 条独立断言 (a-m)：zip完整/3文件产出/VNAME列/拍数/WEB/BWEB/地址布局+唯一性(paired 4edge×2beat=8)/.param公式/v_电压源/RM-WM计数/cellid后缀/bitcell路径3抽样/3-seed确定性。oracle 独立解析 B .SUBCKT+config 重算期望结构，不依赖 ref。
6. 自验：REF 13/13 PASS ✓；3 假 (empty/only_print/core_deleted) 全 FAIL ✓ (negative_selftest.py)
7. case JSON 落 cases/B/EDA-Eval-DesignFlow-SramWmRmMeasGenProduce-001.json (29572B)

## 交付物
- case: `benchmarks/EDA-Eval-DesignFlow/cases/B/EDA-Eval-DesignFlow-SramWmRmMeasGenProduce-001.json`
- A 资产: assets/.../A/{dspf_header.txt, config_path.txt, racing.vec} + task_brief.md
- B 隐藏: assets/.../hidden/{dspf_header_B.txt, config_path_B.txt, hidden_manifest.json}
- 参考: reference/.../{sram_meas_gen.py (修复版), check.py}
- 负样本: reference/.../negative/{empty.py, only_print.py, core_deleted.py, negative_selftest.py}

## trace 溯源
user=shanliny · host=hfeg0plg107 · session=1794970325758_527j4.messages.json · mc=24 · domain=characterization
real_task_summary: 为 SRAM 奇偶核 (M4B2 64×8) 设计 WM/RM 测量方案 + 重写 sram_meas_gen.py 为对任意 instance 生效的通用引擎

## 指标
- 📊 covered=593/4529=13.1% (+1)
- 🎯 最近20条 20/20=100% (不变，本轮未 pi 实跑)
- 台账 B: 1758 不变 (527j4 claimed→case, 净 0)
- DEBT: 0

## 体积
📦 MEMORY_B < 32KB ✓
