# Deepread: ci2dm — xxchen drcpv QACELL GUI enhancement

**Session**: 1795163655095_ci2dm.messages.json
**User/host**: xxchen @ hfeg0plg18 (10.129.8.238), mc=138
**Agent**: lead, 105 msgs / 511KB
**CWD**: /home/xxchen/workspace/DRC_pattern_tool/0.6/device_rule1
**Keywords**: drc:591; .lef:48; .gds:14; techfile:13; pdk:13; calibre:4 (drc count from DRC_pattern_tool file paths, NOT DRC ops)
**Domain**: physical_verify (tooling) — drcpv = DRC pattern verification GUI tool (PyQt5)
**Status**: parked (source-access blocker)

## Real user intent (3 user_input requests)

### U#1 (msg 0 context + msg 1 bug report): right-click crash fix
- **Bug**: `_on_context_menu` used `self.table.isRowSelected(row)` — PyQt5 QTableWidget binding doesn't expose `isRowSelected` (protected slot in C++, not wrapped). Right-click → `AttributeError: 'DragReorderTable' object has no attribute 'isRowSelected'` → Abort.
- **Fix**: `self.table.selectionModel().isRowSelected(row)` (1-line API substitution at line 446 of qacell_page.py)
- **Verify**: agent wrote `_probe_rowselected_ctxmenu.py` headless probe (QT_QPA_PLATFORM=offscreen), confirmed fix; ran `_qacell_multidelete_test.py` regression — green.

### U#2 (msg 25): copy/paste info-box "don't show again" checkbox + persistence
- **Request**: "复制参数时能否不要每次都弹窗显示，复制粘贴说明，弹窗上面增加一个勾选项，下次不再显示。"
- **Impl** (qacell_page.py):
  - Module-level `_load_prefs()` / `_save_prefs()` → `~/.drcpv_ui_prefs.json`
  - New `_info_with_check(self, title, text, key)` helper: `QMessageBox` with `setCheckBox(QCheckBox("下次不再显示该提示"))`; if checked, persist `prefs[key]=True`; if already suppressed, skip entirely.
  - `_copy_params` / `_paste_params` now call `_info_with_check` instead of `QMessageBox.information`.
- **Verify**: `_probe_suppress_info.py` — first copy shows box+checkbox, check it → flag persisted; second copy → box suppressed. Updated existing `_qacell_copy_paste_drag_test.py` to patch `box.exec_` (not `QMessageBox.information`) since new helper uses instance exec_.

### U#3 (msg 75): param-config dialog scroll-area wrap
- **Request**: "独有参数太长了把整个界面Y方向撑太大，给固定高度，超过用滑动；通用参数也缩短一点，给固定高度滑动。"
- **Impl** (param_config_dialog.py):
  - Constants `_COMMON_BOX_HEIGHT = 190` (shorter), `_UNIQUE_BOX_HEIGHT = 320`
  - Wrap `common_box` and `unique_box` in `QScrollArea` with `setFixedHeight` / `setWidgetResizable(True)`
- **Verify**: `_probe_param_scroll.py` — dialog bounded at 868px, common box scrolls (content 412 > viewport 190), unique box scrolls (content 334 > 320). py_compile green.

## Agent tool chain
read_files (full + ranged) → editor (multi-segment old_text/new_text patches) → run_approved_command (python-runner + shell-runner, runs `_run_gui_test_via_pyqt.py` wrapper with QT_QPA_PLATFORM=offscreen) → list_allowed_files. search_codebase rejected (unavailable tool). All probes run headless via `_run_gui_test_via_pyqt.py` harness.

## Why parked (not synthesized)
1. **Source-access blocker**: the deliverable files (`drcpv/ui/qacell_page.py`, `drcpv/ui/param_config_dialog.py`) live in `/home/xxchen/workspace/DRC_pattern_tool/0.6/device_rule1/` on hfeg0plg18. scp to 10.129.8.238 returns "No such file or directory" — the workspace is NOT on the .75-accessible host (likely a different mount or the session ran against a remote-runner). Reconstructing full source from editor diffs (msg 5/39/41 are diff fragments, not full reads; msg 29 read_files result text is empty) is infeasible within 40-min budget.
2. **AST-only check risk**: without the real source to build public-A / hidden-B inputs, a pure structural check would devolve to substring assertions (§4.3 violation risk).
3. **Domain caveat**: drc:591 keyword is from `DRC_pattern_tool` file paths, not DRC verification operations. The task is PyQt5 GUI dev on a DRC tool. Legitimate real intent per 11-15 令 (debug-Q&A legal), but sandbox-verifiability is the blocker, not intent.

## Pool observation (r1029 选料)
Strict C-domain filter (phys≥30, phys>2×nonC, mc 30-150) on summary_20261123 → 60 candidates. After dedup against全 4 shard ledger 并集 (4615 base session ids): **only 1 truly fresh** (ci2dm). High-mc C-domain fresh pool is effectively exhausted; prior rounds (r1025-r1028) mined mc 50-220段. Next round should either (a) drop to mc 5-30段, (b) revive parked candidates under 11-15 令, or (c) do §4.9 anti-hardcode self-audit / test_rationale cleanup on existing cases.
