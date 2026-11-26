# deepread — 1791959556511_kkjsm (panruan @ 10.129.35.68 / hfeg0plg52)

**trace**: `/home/panruan/.cline/data/sessions/1791959556511_kkjsm/1791959556511_kkjsm.messages.json`
(1,821,629 B / 136 msgs / 27 real user-text turns / single session)
**scan**: summary_20261116_072610 → mc=111, keywords drc:717;calibre:316;pex:93;pdk:67;analog:39;
pyaether:25;transistor:11;lvs:9; → physical_verify domain
**user**: panruan (real IC-EDA engineer, Calibre DRC rule deck author/maintainer)
**attached file**: `uploads/calibreDRC.rule` — 29,551-line real Calibre SVRC rule deck

## user intent (U#0, verbatim)
```
解析CT_F_015_00和CT_F_017_00
```
Single, clear analysis-Q&A intent: parse/explain two forbidden-type CT DRC rules
from the attached rule deck. User gives no root cause, no fix, no implementation
hint → fits A-trace-faithful selection rule (only取 "提出需求 / 表达目标" user turn).

## assistant tool chain (U#0 → answer @ msg 34)
1. `search_codebase` for `CT_F_015_00` / `CT_F_017_00` (timeout on huge file)
2. `run_approved_command` python-runner: `find_checks.py` grep → located rules at
   lines 16726 + 16733 of calibreDRC.rule
3. `read_files` lines 16680–16770 → full rule block bodies
4. `find_layers.py` / `find_layers2.py` / `find_layers3.py` → resolved referenced
   layers: CT_drawing (85:0 / 8475), CT_PCH (85:2 / 8476), CT_SL (85:24 / 8481),
   CT_CLOSE (85:16 / 8479), BORD_PERI (8818), TCP = COPY TCP_ARRAY (78:7 / 8458),
   M0U = OR M0U_drawing M0U_SL M0U_CMP, M0U_NO_CMP = OR M0U_drawing M0U_SL,
   M1_NO_CMP = OR M1_drawing M1_CLOSE M1_SL M1_MATCH, CT = OR CT_drawing CT_CLOSE
   CT_PCH CT_SL
5. msg 34: structured Chinese explanation
   - 一、背景信息 (CT layer GDS mappings + derived definitions)
   - 二、CT_F_015_00 (rule body + 逻辑解析 + 含义: 禁止在 BORD_PERI 内放 CT)
   - 三、CT_F_017_00 (rule body + 7 条子语句逐条解析 + 含义: 禁止悬浮 CT)
   - 四、小结对比 (类型/对象/关键层/算子/判罚逻辑/参数 表格)

## CT_F_015_00 (real, verbatim from line 16726)
```
CT_F_015_00 {
    @ Forbidden - CT_ALL cut BORD_PERI is not allowed. [in core/peri : check]
    @ CT_ALL= {CT_DRAWING OR CT_PCH OR CT_SL}
    CT_ALL= OR CT_DRAWING CT_PCH CT_SL
    CT_ALL CUT BORD_PERI
}
```
Forbidden 区域禁放：CT_ALL (CT_drawing + CT_PCH + CT_SL) 与 BORD_PERI 求交，凡落
在 PAD 周边边框带内的接触孔都报错。无参数，命中即报。

## CT_F_017_00 (real, verbatim from line 16733)
```
CT_F_017_00 {
    @ Forbidden - floating CT is not allowed, any one of condition 1/2 meet is floating CT [in core/peri : check]
    @ 1. CT_drawing outside {M0U_NO_DUMMY AND M1_NO_DUMMY}
    @ 2. CT_PCH outside {TCP AND M1_NO_DUMMY}
    CT_PCH NOT TCP
    CT_drawing INTERACT TCP
    CT_drawing NOT M0U
    CT_PCH INTERACT M0U    // NOT TCP)
    CT_drawing NOT INTERACT M1
    CT_drawing OUTSIDE (M0U_NO_CMP AND M1_NO_CMP)
    CT_PCH OUTSIDE (TCP AND M1_NO_CMP)
}
```
Forbidden 悬浮接触孔：7 条独立子检查覆盖 CT_drawing / CT_PCH 两类孔的"缺上金属 /
缺下金属 / 缺端子 / 未夹紧"等形态。

## reframe (r748)
- **reframe_name**: `drc-rule-explain-Q&A` (analysis-Q&A revival, physical_verify)
- **A-trace-faithful**: prompt = U#0 verbatim; asset A = curated real excerpt of
  calibreDRC.rule (96 lines: real LAYER defs + derived defs + CT_F_015_00 +
  CT_F_017_00 blocks verbatim + CT_ENC_013_00 / CT_DenMax_014_00 / CT_F_018_00
  distractors)
- **mode**: ③evidence-only (P-006 r618 (C)-(A) split) — SUT reads a fixed Calibre
  rule file excerpt, cannot launch Calibre in sandbox; produces structured JSON
  report (rule_name / line_number / description / comment_lines / statements /
  referenced_layers / resolved_definitions + per-fact evidence)
- **B/B2 judge-self-check**: hidden/b mock deck (CT_F_025_00 + CT_F_027_00, layer
  names CT_main/CT_via/CT_seal/PAD_RING/TEP/MET0/MET0_NO_CMP/MET1_NO_CMP) +
  hidden/b2 mock deck (CT_F_035_00 + CT_F_037_00, layer names CT_base/CT_pad/
  CT_sealring/EDGE_RING/TPC/M0/M0_NO_FILL/M1_NO_FILL); 3 fixtures' rule names +
  layer names + statement bodies all mutually disjoint → 反硬编码
- **check.py 16 条独立条件 (a-p)**: a zip valid+solve.py; b B exit0+non-empty
  JSON; c B rule_names==B_EXPECTED (反 A 硬编码); d B CT_F_025_00 line_number
  (独立重扫)+description+statements+refs+defs; e B refs 与 A 完全不相交; f B
  CT_F_027_00 同 d; g B evidence 与 B 文件原行一致; h B2 rule_names disjoint from
  A&B; i B2 两 rule 内容; j B2 evidence 一致; k anti-stub B/B2 refs 并集 != A; l
  robustness 空文件; m robustness missing rule; n determinism 3 跑字节一致; o
  退化提交1 print-A-gold FAIL; p 退化提交2 B名+A层 mixed stub FAIL
- **k_rationale = k_check = 16 ≥ 8 GATE PASS ✓**

## 自验
- reference solve.py PASS 16/16 ✓ (B + B2 + robustness + determinism + anti-stub)
- 3 negatives FAIL distinct:
  - solve_empty (空文件) → b-m FAIL
  - solve_print_gold (硬编 A gold) → c-f/h-k/m FAIL
  - solve_no_evidence (解析但无 evidence + wrong content) → d-f/i/k FAIL
- §4.9 退化提交 (空壳/print-gold/无 evidence) 全 FAIL ✓
- test_rationale = 16 条断言清单 (k=16 = k_check) ✓

## 落库
- cases/C/EDA-Eval-DesignFlow-DrcRuleExplainQa-001.json (source of truth, test
  字段含完整 check.py 22079B)
- build_jsonl.py --shard C 重建 EDA-Eval-DesignFlow_C.jsonl (468 → 469)
- assets/.../sample_input/{calibreDRC.rule, prompt.txt, task_brief.md} +
  hidden/{b,b2}/{calibreDRC.rule, prompt.txt} + hidden_manifest.json +
  reference/{solve.py, check.py} + negative/{3 stubs, negative_selftest.py}
- trace_ledger_C.tsv: kkjsm parked (2026-11-03) → case (r748, reclaim)

## 纪律
- SUT 沙箱只含 sample_input/calibreDRC.rule + prompt.txt + task_brief.md；
  hidden/ + reference/ 不进 SUT ✓
- 不脱敏: user=panruan / host=10.129.35.68 / session_file=1791959556511_kkjsm
  真值 ✓
- 只动 C shard 文件 ✓
- distinct vs r743 AetherPinErrorQa (community Q&A KB .md debug-Q&A) / r744
  AeGetSelSetInfoHowto (pyAether ref-manual .txt howto) / r746 PyAetherMoveInstHowto
  (pyAether ref-manual .txt howto): 本例 = **Calibre SVRC rule deck (.rule)
  drc-rule-explain analysis-Q&A**, physical_verify domain, 不同 source 格式
  (SVRC rule deck vs pyAether manual vs Q&A KB), 不同 trace (panruan vs lizwen/
  jianingw/ziyuny), 不同真实意图 (rule 解析 vs API howto vs pin-error debug)
