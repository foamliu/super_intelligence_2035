#!/usr/bin/env python3
"""r839 MEMORY_B update — archive r838 verbose, write concise r839 summary."""
import os

MEM = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/MEMORY_DESIGNFLOW_B.md"
ARCH = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/ARCHIVE_OPERATOR_DESIGNFLOW_B.md"

lines = open(MEM, encoding="utf-8").read().split("\n")
# line 1 (idx 0) = WAITING r838 verbose; line 40 (idx 39) = r838 流水 verbose
r838_waiting = lines[0]
r838_liushui = lines[39]

# 1) append r838 verbose to ARCHIVE
arch_block = f"""

## r838 archived (r839-mem-trim) — 11-18 r838 verbose 原文

### r838 WAITING 行原文
{r838_waiting}

### r838 流水行原文
{r838_liushui}
"""
with open(ARCH, "a", encoding="utf-8") as f:
    f.write(arch_block)

# 2) new concise r839 WAITING line 1
r839_waiting = (
    "WAITING: 0（11-18 **r839 0-case 维持轮 + 档1 layer normalize batch14 +12 + 档3 reframe_note backfill batch14-FINAL +4 落地**"
    "（mc-matrix --shard B --src summary_1115_081559: mc>=10 池 943/已动 943/fresh=0 **第 210 轮 reconfirm** 四快照结构性饱和 ⇒ 0-case;"
    " **档1 layer normalize batch14 +12** = first 12 alphabetical missing-layer A→C 段"
    "(AcSimHowtoGuide/AgingDirSeparateTransform/AplmmxGen025RootCause/BlSpfCapClassify/C2cRfbCmStab/CTLETranDeck/CabufPvtDatAudit/CapCharProps/CbrForceMechanismExplain/CdlBulkSanitize/ClampPwrStateExtract/CmlBwExtensionHandbook),"
    " methodology r747(layer=check 是否真跑 EDA 二进制), classifier layer_classify_r839.py + 4-case spot-check(C2cRfbCmStab/CdlBulkSanitize/SlicerSizeOpt/Sram6tDcChar/Vcc2scActDeckGen hspice 真跑确认 L2),"
    " 10 L1(offline python parsing) + 2 L2(C2cRfbCmStab+CdlBulkSanitize check 真跑 hspice); missing-layer 92→80; layer dist L1 171→181 / L2 130→132 / L3 2;"
    " **档3 reframe_note backfill batch14-FINAL +4** = last 4 empty W→X→Z 段"
    "(WaveViewPanel/WriteDqPsdMappingExtract/XrunLogErrDiag/ZqCodeLinExtract), 全 keep_faithful A-faithful(track=faithful/spice_char),"
    " reframe_note 391/395→**395/395=100% 全量收口**(r773-r800 batch1-32 + r826-r838 batch1-13 + r839 batch14-final); XrunLogErrDiag layer 同步补 L1(layer 315→316);"
    " **存储架构**: cases/B single source of truth, build_jsonl.py --shard B 本地 rebuild 16 modified == B.jsonl 395 case rebuild ✓ 0 起数据丢失 16/16 applied;"
    " **§4.9 抽查**: CdlBulkSanitize-001(L2 batch14) 4 neg 全 FAIL + XrunLogErrDiag-001(reframe_note batch14-final) 4 neg 全 FAIL NEG_RC=0 + ref-PASS ClampPwrStateExtract-001(L1) PASS;"
    " **discuss**: r837→r839 diff=2<4 不发言, 下次 mandatory due r841, board OPEN=0)"
)
lines[0] = r839_waiting

# 3) replace r838 流水 (idx 39) with one-liner
r838_oneliner = (
    "- [r838 archived] 11-18 r838 0-case + 档3 reframe_note backfill batch13 +12 落地（reframe_note 379→391, miss 16→4, T 段 SvUsedModelExtract 后 12 missing; 8 keep_reframe portability[8 synth_deck] + 4 keep_faithful; T 段 keep_faithful 33% spice_sim 域 83%; track≠asset mismatch 累计 68; §4.9 抽查 SvUsedModelExtract-001 4 neg 全 FAIL）原文滚入 ARCHIVE (r839-mem-trim)"
)
lines[39] = r838_oneliner

# 4) insert new r839 流水 row right after the "## 流水（最新在上）" header
# find header line index
hdr_idx = None
for i, ln in enumerate(lines):
    if ln.startswith("## 流水"):
        hdr_idx = i
        break
r839_liushui = (
    "- r839 **0-case 维持轮 + 档1 layer normalize batch14 +12 + 档3 reframe_note backfill batch14-FINAL +4 落地**（mc-matrix --shard B --src summary_1115_081559: mc>=10 池 943/已动 943/fresh=0 **第 210 轮 reconfirm** 四快照结构性饱和 ⇒ 0-case;"
    " **档1 layer normalize batch14 +12**: first 12 alphabetical missing-layer A→C 段, methodology r747(layer=check 是否真跑 EDA 二进制), classifier layer_classify_r839.py 全 92 missing 分类(L1=87/L2=5[hspice: C2cRfbCmStab/CdlBulkSanitize/SlicerSizeOpt/Sram6tDcChar/Vcc2scActDeckGen]/L3=0), 4-case spot-check 确认 L2 真跑 hspice, batch14 = 10 L1 + 2 L2(C2cRfbCmStab+CdlBulkSanitize), missing-layer 92→80, layer dist L1 171→181/L2 130→132/L3 2;"
    " **档3 reframe_note backfill batch14-FINAL +4**: last 4 empty W→X→Z 段(WaveViewPanel/WriteDqPsdMappingExtract/XrunLogErrDiag/ZqCodeLinExtract), 全 keep_faithful A-faithful, reframe_note 391/395→**395/395=100% 全量收口**(r773-r800+r826-r838+r839 三段累计), XrunLogErrDiag layer 同步补 L1(315→316);"
    " **存储架构**: cases/B 16 modified, build_jsonl.py --shard B rebuild B.jsonl 395==395 ✓ 0 数据丢失; **§4.9 抽查**: CdlBulkSanitize-001 4 neg 全 FAIL + XrunLogErrDiag-001 4 neg 全 FAIL NEG_RC=0 + ref-PASS ClampPwrStateExtract-001 PASS;"
    " **discuss**: r837→r839 diff=2<4 不发言, 下次 mandatory due r841; **下一道 bounded queue**: layer 80 missing(P2 续, batch15 D→G 段) + layer 误判复核(WaveViewPanel 等 track=spice_char/perl-only 应 L1, ~39 例 P2-sub)）"
)
if hdr_idx is not None:
    lines.insert(hdr_idx + 1, r839_liushui)
else:
    lines.insert(1, r839_liushui)

# 5) update heartbeat line 21 (idx 20) — reframe_note + layer numbers
# find the line starting with `📊 trace 覆盖率`
for i, ln in enumerate(lines):
    if ln.startswith("`📊 trace 覆盖率"):
        # replace reframe_note count and add layer count
        new_hb = (
            "`📊 trace 覆盖率（mc>=10, **src=ssh_eda_search_20261115_081559/summary.tsv[A r617 切池 08:20, 本地 summary_1115_081559.tsv r617 建并复算]**）：covered 553 / 新池 943(mc10 B-kw dedup 池) = **58.6%**（旧池口径 553/2907=19.0% 历史对照）· ledger_B case 553·parked 968·total 1521 · 1115_081559 池 sessions=3791(B-kw dedup) mc10=943(B) fresh=0(r617 新池首验, **r839 第 210 轮 re-confirm**) · **四快照结构性饱和(1109/1113/1114/1115_081559)** · ALL mc10=3348(1115_081559 curated) · **r580 跨 4 shard ledger+4 jsonl 三式去重 top200+15低mc 100% USED 闭合** · **r618 意图审计: 319 keep/191 误杀复活(r619 起变现)/562 不可造/292 待定** · 📦 MEMORY_B r839 ~36KB · 🦾 断言 671/671(reframe_note/layer backfill 不动 test_rationale/check) · 🎯 cline_eval 137/15/12.2% current · 🎨 asset_fidelity 395/395=100%(r824 收口) · 📝 reframe_note **395/395=100% 收口**(r839 batch14-final +4, miss 0) · 🏷️ layer 316/395=80%(r839 batch14 +12, miss 80)`"
        )
        lines[i] = new_hb
        break

# 6) update discuss line (r839 no speak)
for i, ln in enumerate(lines):
    if ln.startswith("`💬 discuss:"):
        new_discuss = (
            "`💬 discuss: r833 mandatory 清付(r829→r833 diff=4 due). r834/r835/r836 diff<4 不发言. **r837 r833→r837 diff=4 mandatory 清付**. r838 r837→r838 diff=1<4 不发言. **r839 r837→r839 diff=2<4 不发言**, 下次 mandatory due r841. board OPEN=0.`"
        )
        lines[i] = new_discuss
        break

# 7) update 断言 line (r839)
for i, ln in enumerate(lines):
    if ln.startswith("🧾 断言:"):
        new_assert = (
            "🧾 断言: 本轮 r839 0-case 维持轮 + 档1 layer normalize batch14 +12 + 档3 reframe_note backfill batch14-FINAL +4(layer/reframe_note backfill 不动 test_rationale/check, k_rationale==k_check 一致率 671/671 维持) · 存量 395/395 达标(0 empty) · k_rationale==k_check 一致率 671/671 ✓"
        )
        lines[i] = new_assert
        break

with open(MEM, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("MEMORY updated. new size:", os.path.getsize(MEM), "bytes")
