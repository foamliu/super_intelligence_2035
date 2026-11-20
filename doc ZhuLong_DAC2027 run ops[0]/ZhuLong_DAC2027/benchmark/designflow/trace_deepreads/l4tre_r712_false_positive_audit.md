# l4tre r712 false-positive audit + fresh-filter bug fix (2026-11-17)

## trace
- session: `1794386548710_l4tre.messages.json` (1.18MB, 494 msgs, 7 user text turns)
- user: xinqiaoz @ hfeg0pkn002 (10.129.2.11) / also hfeg0plg56 (10.129.35.75)
- mc=575, keywords: pdk:1226;drc:306;calibre:235;lvs:128;rtl:101;cmos:22;techfile:6
- tools column: 232 calibre / 2 innovus

## user turns (verbatim excerpts)
- U#0 (context summary): "确定 genReleaseNote 脚本的最终权威版本，清理废弃快照，并解答该脚本的配置常量、硬编码及格式优化相关问题。" — about `/home/xinqiaoz/workspace/genReleaseNote/genReleaseNote.py` (1813 lines, PDK release-note generator with 3-domain config: RUNSET_BASE/SC_BASE/TECHLIB_BASE)
- U#1: "把 tools 下的也删掉。" (delete the tools/ copy)
- U#2: "这个正式版本，如果我要执行，应该怎么执行？" (how to execute)
- U#3: HTML style — change table header "Current（正式版）"/"Frozen（测试版）" to line-broken "Current\n（正式版）"
- U#4: "默认收件人加上 huobin.peng@cxmt.com。"
- U#5: "dry-run 之后发现有部分版本的'内容'字段是空的，请聚焦于这些空字段的内容，看看是我们漏了还是说真的没有写？"
- U#6: "请修复 A 类，修复完 dry-run 验证"

## false-positive verdict
This session is **PDK release-note Python tooling maintenance** — NOT physical verification.
The calibre:235 / lvs:128 / drc:306 keywords come from the **content** of the release notes
the script generates (calibre runsets / LVS runsets / DRC rules metadata), NOT from the
agent performing physical-verify operations. The agent's tool calls are file edits on
genReleaseNote.py, not calibre/LVS/DRC runs.

Same trap class as:
- r708 v593e (DDR project name misread as physical DRC)
- r706 DRCPA/DRCOA (DDR project name)
→ C-domain hard gate NOT satisfied. Do NOT build a C case on l4tre.

## fresh-filter bug (root cause of r711's "145 fresh" being unreliable)
r711 reported fixing the suffix-normalization bug and got "truly fresh moderate C=145".
r712 reused the same filter logic (trace_ledger_C.tsv + `_all_ledger_suffix_4shard.txt`)
and got 370 fresh — but l4tre (which is parked in shard A's ledger since 2026-11-14)
showed as fresh. claim REFUSED.

Root cause: `_all_ledger_suffix_4shard.txt` (59KB, generated 2026-11-14) is **stale and
incomplete** — it does not contain l4tre. Relying on it undercounts ledgered sessions.

Fix: fresh filter MUST union-read all 4 `trace_ledger_{A,B,C,D}.tsv` (3640 ledgered total,
cross-shard mutex per r549), NOT the stale 4-shard summary file.

After fix: truly fresh C candidates (candidates_mc10_classified.tsv domain contains C,
4-shard-ledger-excluded, mc≥10) = **199** (not 370, not r711's 145).

## genuine C-domain fresh candidates (keyword-profile verified, for next round)
| slug | user | host | mc | keywords | verdict |
|---|---|---|---|---|---|
| 29j7y | lizwen | hfeg0plg89 | 60 | drc:288;lvs:40;aether:32;.spi:8;calibre:7;cellview:6;.cdl:6;pyaether:5 | **FIRST CHOICE** DRC+LVS+aether real PV |
| ayqtu | simplec | hfeg0plg92 | 54 | drc:341;aether:121;techfile:53;calibre:16;.cdl:9 | DRC+aether+techfile |
| o2192 | kenwang | hfeg0plg16 | 41 | drc:78;calibre:68;pyaether:7 | calibre DRC (check r711 57s2p collision) |
| fywl4 | adminai | hfeg0plg107 | 45 | virtuoso:133;aether:90;drc:77;rtl:65 | virtuoso+aether layout |
| yavow | miccao | hfeg0plg92 | 90 | lvs:216;aether:29 | LVS-heavy |

AVOID: ncasl/azj7y (steveny, r706 cluster: context-infrastructure workspace.md indexing,
virtuoso keywords from SKILL.md filename not real layout ops).

## selection heuristic for C shard (refined)
Prefer candidates whose keyword profile has **layout-tool-call** keywords
(virtuoso/cellview/dbcreate/dbget/dbopencellviewbytype/.gds/.cdl) over those with only
drc/calibre/lvs keyword counts — high drc/calibre/lvs counts frequently come from
PDK-release-note content or netlist-extraction docs, not physical-verify operations.
