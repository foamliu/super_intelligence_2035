# Deepread — sid 1792302557875_myvdg (xinqiaoz / hfeg0pkn004 / mc=326 / 216 msgs / 1.28MB)

**域**：physical_verify (PDK Dummy QA, calibre DFM FILL)
**deck**：DYT4E_WHCFP_LHCRP_DHCFP (frame 4 mask M1Z/M9Z/M1Zb/M9Zb + chip 多 mask)

## 用户意图演进（genuine user turns，逐字）

- **msg0 (HANDOFF)**：「# HANDOFF — QA-18 frame border 根因修复（已验证成功，待 merged 复核与 QA_LOG 补录）」——交接文档**已给根因**（测试 GDS 缺 301_0/302_505 → BORD_CHIP:TEG 空 → BORD NOT 空=BORD 全部 → DefMaskBlk 覆盖 → EmptyArea 空 → DFM FILL 静默零）+ 已给修复（补画 TEG 层、config_frame_full.ini、QA_frame_full.gds、prepare_qa_frame_full.py）+ calibre 重跑 exit 0、M1Z/M9Z/M9Zb 输出恢复。⇒ **A-档 disqualified（用户已给根因+修复方案）**。
- **msg66**：「我们现在已经做了哪些 QA，有哪些 QA 的疑点？请列出来。」（提问，无根因）
- **msg72**：「我们先不管这些疑点，现在开始 qa 19，这一线你先不要着急开始，请告诉我你打算怎么做？」——**A-档 seed（提出目标未给根因/修复）**：QA-19 逐 mask dummy 几何校验。但 gold 依赖 live GDS(gdspy)+live expanded SVRF deck → .75 沙盒不可达 → **A-档 disqualified（tooling）→ B-档 synthesized L1-boundary**。
- msg193「刚才被我中断了，请继续」；msg214「editor 又出问题...用 handoff 技能」——会话因 zhulong editor bug 终止。

## assistant 工具链（关键）

- msg0-65：editor 改 QA_LOG.md 补录 QA-18（修 §3.17 缺标题、§3.18 重复标题、§3.18 记录、§4 陷阱、§6 评级、§7 回顾）；`grep -n '^### 3\.'` 验标题序号连续唯一；写 HANDOFF_dummy_qa18_closed_qa19_ready.md。
- msg72-214：建 `check_dummy_geometry.py`：
  - `parse_expanded(rule)` → (targets, outs, prohibit_num, forbid_map) 从展开 SVRF；
  - `load_rects/load_gds_cells` 用 gdspy 读 GDS → per-(layer,dt) 矩形清单；
  - `check_mask` 5 检查：① dummy count non-zero（catch 静默零）② dummy-dummy gap/pitch==space_value(xStep/yStep for RECT, LWidth for LINE/CMP) ③ vs own target squares >= Mspace ④ vs forbidden (Prohibit layer) >= bordSpace ⑤ vs border inside + gap >= bordSpace；size histogram + orientation set judgment + WenLarge whitelist + WARN-ify pitch；
  - Phase 0 口径定标 → Phase 1 pilot（chip M1Z 88/8 swapped orientation, M9Z 3.4055 linewidth）→ Phase 2 全量 chip13+frame12。
  - editor 工具反复 reject（zhulong bug），多次 `python - <<'PYEOF'` heredoc 改写文件。

## gold（用户实际接受）

1. QA-18 收官：QA_LOG §3.18 补录 + frame border 根因（BORD NOT TEG 退化）+ calibre 重跑恢复输出。
2. QA-19 check_dummy_geometry.py：per-mask 5 几何检查 + silent-zero 检测。

## 合成方案（B-档 L1-boundary，与存量正交）

`EDA-Eval-DesignFlow-DummyGeoVerify-001`：把 deck/GDS 固化为 `dummy_qa_manifest.json`（mask values/target+forbid layers/border bbox/TEG layer dep/test GDS layer inventory/per-mask dummy rect inventory/calibre output existence）。候选 `dummy_geo_check.py`（纯标准库，无 gdspy/calibre）跑 6 per-mask 检查（silent_zero/size_match/pitch/target_avoid/forbid_avoid/border_contain）+ global 根因交叉核对（teg_layers_absent ⇔ silent_zero_masks 非空）+ layer_map_rule_present → `geo_check_report.json` + verdict OK/HAS_ISSUES。

**与 r88 DrcPatCheckAudit（good/bad 配对+层映射）/r84 FillImplantFlowAudit（AST 审计）/r80 DRCSpecGen(spec→SVRF)/r81 MVValueCmp（多值 LDR 比对）正交**——本案是 **dummy fill 几何校验 + 静默零输出根因审计**。

资产 A：6 mask(M1Z/M9Z/M1Zb/M9Zb/V1/V2) 全 TEG 画 → 全 OK。
隐藏 B：TEG 301_0/302_505 缺 → 4 frame mask silent_zero + V1 pitch 违例 → HAS_ISSUES；B2/B3 跨输入全 OK（击穿硬编码 A/always-FAIL）。
check.py 15 条断言 a-o；ref PASS 15/15；4 neg(fake_empty→b / fake_print_expected→c / core_deleted_silent→d / naive_pitch_ignore→e)全 FAIL NEG_RC=0；§4.9(a)(b)(c)全 FAIL；test==disk roundtrip 6901B。
