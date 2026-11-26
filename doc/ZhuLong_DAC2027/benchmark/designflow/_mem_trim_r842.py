#!/usr/bin/env python3
"""r842-mem-trim: insert r842 entry, archive r841, archive r824/r823 verbose."""
path = 'MEMORY_DESIGNFLOW_B.md'
lines = open(path, encoding='utf-8').read().split('\n')

r842_entry = (
    '- r842 **0-case 维持轮 + 档1 layer normalize batch17 +12 落地**（mc-matrix --shard B --src summary_1115_081559: mc>=10 池 943/已动 943/fresh=0 **第 213 轮 reconfirm** 四快照结构性饱和 ⇒ 0-case; **档1 layer normalize batch17 +12** = next 12 alphabetical missing-layer L→N 段 after r841 batch16(LibCoordMapper/LvLvioSweep/MeaNetPathDiag/ModelLibVerDiff/MosDcGuiTool/Mt0AggMinMax/Mt0FolderAggStat/Mt0MetastabDiag/Mt0ParseFix/NetlistDiffBankLogic/NetlistMisModCompare/NetlistWLReduce), methodology r747(layer=check 是否真跑 EDA 二进制), classifier layer_classify_r839.py + **手动 os.environ.get 复核**; batch17 全 12 L1(offline python parsing/subprocess), **0 variable-blind-spot L2 under-count**(grep `= os.environ.get(` 0 命中; 唯一 subprocess 变量 `PY=sys.executable or "python3"` LvLvioSweep/MeaNetPathDiag → L1); **EDA-binary-mention scan** 4 case 命中全 L1: LvLvioSweep "finesim -i" 是 run_all.sh TEXT 断言非调用 / MeaNetPathDiag "hspice/model.lib" PATH 字符串 / Mt0MetastabDiag+Mt0ParseFix COMMENT; missing-layer 55→43; layer dist L1 205→217 / L2 133 / L3 2; **存储架构**: cases/B single source of truth, build_jsonl.py --shard B 本地 rebuild 12 modified == B.jsonl 395 case rebuild ✓ 0 数据丢失 12/12 applied 0 skipped; **§4.9 抽查**: LvLvioSweep-001(batch17 L1) 6 neg(naive_empty/hardcode_A/copy_input/print_stub/no_clamp/ref_minus_core) 全 FAIL NEG_RC=0 + §4.9 three-fake OK + ref PASS, layer backfill 不动 check/negative ⇒ 牙不变; **discuss**: r841→r842 diff=1<4 不发言, 下次 mandatory due r845, board OPEN=0; **下一道 bounded queue**: layer 43 missing(P2 续, batch18 O→R 段, 必带 os.environ.get 手动复核) + 3 L2 hspice 在 S→V 段(SlicerSizeOpt/Sram6tDcChar/Vcc2scActDeckGen) + layer 误判复核双向(~39 over-count + variable-blind-spot under-count, P2-sub)）'
)

r841_archived = (
    '- [r841 archived] 11-18 r841 0-case + 档1 layer normalize batch16 +12 落地 + discuss mandatory 清付（mc>=10 fresh=0 第 212 轮 reconfirm; batch16 F→L 段 12 case = 11 L1 + 1 L2(JitterTieRerun variable-blind-spot); missing-layer 67→55; layer dist L1 194→205/L2 132→133/L3 2; **layer 分类器 variable-blind-spot 发现**: regex 漏变量传参 `HSPICE=os.environ.get(\'HSPICE_BIN\',\'hspice\')` + subprocess.run([HSPICE,..]), JitterTieRerun-001 实为 L2; r840 L2 list 3→4 修订; **layer 误判复核双向性首证**(over-count + under-count 两向都须扫); §4.9 抽查 GmidSizingSearch-001 6 neg 全 FAIL; discuss r837→r841 diff=4 mandatory 清付）原文滚入 ARCHIVE (r842-mem-trim)'
)

# find the r841 entry line
r841_idx = None
for i, ln in enumerate(lines):
    if ln.startswith('- r841 **0-case 维持轮 + 档1 layer normalize batch16'):
        r841_idx = i
        break
assert r841_idx is not None, 'r841 entry not found'
lines[r841_idx] = r842_entry
lines.insert(r841_idx + 1, r841_archived)

# also archive the verbose r824 and r823 live entries (they are older, ~1000 chars each)
r824_archived = '- [r824 archived] 11-18 r824 0-case + 档2 asset_fidelity batch24 FINAL +13 落地（asset_fidelity 382→395/395=100% 收口, 档2 全量收口 r801-r824; §4.9 抽查 XrunLogErrDiag-001 4 neg 全 FAIL+ref PASS）原文滚入 ARCHIVE (r842-mem-trim)'
r823_archived = '- [r823 archived] 11-18 r823 0-case + 档2 asset_fidelity batch23 +12 落地（asset_fidelity 370→382; §4.9 抽查 VrefStepMeasure-001 3 neg+3 §4.9 fake 全 FAIL ref PASS）原文滚入 ARCHIVE (r842-mem-trim)'

for i, ln in enumerate(lines):
    if ln.startswith('- r824 **0-case 维持轮 + 档2 asset_fidelity backfill batch24 FINAL'):
        lines[i] = r824_archived
    elif ln.startswith('- r823 **0-case 维持轮 + 档2 asset_fidelity backfill batch23'):
        lines[i] = r823_archived

open(path, 'w', encoding='utf-8').write('\n'.join(lines))
print('done. file size:', len(open(path, encoding='utf-8').read()), 'bytes')
