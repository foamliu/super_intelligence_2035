# r1032 — mc 5-29 fresh C-domain probe (2026-11-24)

## 选料方法
- 源: .75 `/home/t0002965/log/ssh_eda_search_20261123_064315/summary.tsv`
- 过滤: mc 5-29, $6 ~ /calibre|virtuoso|aether|ipcustom|layout|lvs|drc|pexivirtuoso/
- phys-dominant: phys-keyword-count ≥ 5 AND phys > 2×nonphys
- anti-join: 4-shard ledger 并集 (4619 touched sessions)
- 结果: 50 phys-dominant candidates → 10 fresh (not in any shard ledger)

## 10 fresh candidates — 全 weak/parked

| # | session | user | host | mc | domain | keywords | peek result |
|---|---------|------|------|----|--------|----------|-------------|
| 1 | 1794900145536_upku1 | e0047722 | hfeg0plg49 | 22 | layout_aether | aether:482;dbget:163;cellview:163;drc:142 | skill-setup(env-config): ask-eda/eda_script_standard/argus-tool-helper check, 16msgs, 0 produce-task deliverable → parked |
| 2 | 1795141108384_ax6eo | e0047722 | hfeg0plg49 | 27 | physical_verify | drc:511;pdk:209;calibre:57 | waiver-agent skill DRC QA scan, 33msgs, skill-driven infra-dependent(case-lib/config.ini parse), no self-contained runnable gold → parked |
| 3 | 1794971660724_zk2xa | ruisongs | hfeg0pgn145 | 8 | physical_verify | drc:1597 | file-organization task (move /home/ruisongs scripts to folder), 20msgs, not design-flow deliverable → parked |
| 4 | 1795004447847_txkot | e0025768 | hfeg0pkn001 | 18 | physical_verify | drc:296;aether:158;pyaether:100;calibre:88;lvs:87;pex:82 | analysis-report-gen (read dept .md usage reports → HTML), 50msgs, data-analysis not physical_verify → parked |
| 5 | 1794968719744_90j7n | e0025768 | hfeg0pkn001 | 25 | layout_aether | aether:298;pyaether:209;drc:173;lvs:88 | analysis-report-gen (analyze session json/jsonl → .md), 45msgs, data-analysis not layout_aether → parked |
| 6 | 1794796686431_rwhuv | thomasz | hfeahpc501 | 11 | physical_verify | .gds:1012;lvs:5 | doc-search (find xtor snap error report in /rundata/totem/ IR run dir), 36msgs, source dir Permission-denied to e0031982 → parked |
| 7 | 1795001895719_c37je | e0025768 | hfeg0pkn001 | 25 | layout_aether | pyaether:331;aether:196;dbget:112 | dup of 90j7n (same e0025768 analysis-report-gen session json→md), 44msgs → parked |
| 8 | 1794999105032_qrkzg | e0025768 | hfeg0pkn001 | 21 | physical_verify | drc:296;aether:213;calibre:113 | dup of 90j7n (same e0025768 analysis-report-gen), 47msgs → parked |
| 9 | 1795141940424_cpd1g | ellawu | hfeg0pkn001 | 24 | physical_verify | drc:1180;calibre:12 | DRC deck analysis-Q&A (Calibre SVRF SHRINK PRB_RANGE dummy fill deck, user asks can-expand-prboundary), 26msgs, prose deliverable teeth-fail; near-dup ellawu DRC deck flow → parked |
| 10 | 1794965367964_6mjph | zhililu | hfeg0plg10 | 13 | physical_verify | pex:814 | cross-domain (circuit timing analysis DischgCnt/Cnt_ks/Cnt_clk +1 count, spice/schematic), 15msgs, belongs to D shard → parked |

## 模式分析

mc 5-29 段 C-domain fresh 候选的失败模式分布:
- **analysis-report-gen** (3/10): e0025768 txkot/90j7n/c37je/qrkzg — 用户要分析会话/使用报告生成 .md/.html，数据分析师任务非 design-flow
- **skill-setup/env-config** (1/10): upku1 — 验证 skill 安装状态，无交付件
- **skill-driven DRC QA** (1/10): ax6eo — waiver-agent 依赖外部 case-lib/config.ini 基础设施，非自包含
- **file-organization** (1/10): zk2xa — 整理脚本到文件夹，非 design-flow
- **doc-search source-inaccessible** (1/10): rwhuv — /rundata/totem/ 对 e0031982 Permission-denied
- **DRC deck analysis-Q&A** (1/10): cpd1g — prose 交付，teeth-fail，near-dup ellawu DRC deck
- **cross-domain** (1/10): 6mjph — spice/circuit timing 属 D shard

核心发现: mc 5-29 fresh 段被 **analysis-report-gen**(e0025768 4连) + **skill-setup** + **doc-search** 占据，真 produce-script design-flow task 稀缺。

## 累计 (r1031 + r1032)
- r1031: mc 28-30 fresh 8条全 weak (j36z8/6jzy6/zcg5s/b089y/ty5vg/wtxsx/acz79/hvt59)
- r1032: mc 5-29 fresh 10条全 weak (上表)
- 合计 18 fresh C-domain mc 5-30 候选全 weak
- **连续 2 轮 0-case** (r1031 + r1032)，距 "连续 3 轮" 止损阈值还差 1 轮

## 下轮建议
1. **第 3 轮仍 0-case 则触发止损**: 转做不依赖新候选的产出 (§4.9 anti-hardcode 自查 / test_rationale 断言清单补全 / ledger 治理)
2. **或复活 parked 中 source-reachable 的中-mc 候选**: 如 v80cd(e0014566 mc=398 layout_virtuoso AutoViaGen-001 near-dup 需判 intent-dup)、4ckeg(e0014566 mc=29 virtuoso:546 layout_virtuoso 旧 parked)
3. **或下沉到 mc<5 段**: 但 mc<5 信号更弱，预期质量更差
4. **扩大选料面**: 尝试 20261123 之前的老 summary.tsv (如 20261028_174426)，可能有未探的 fresh
