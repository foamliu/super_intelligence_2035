# Deepread — sid 1792206946923_goqly (xinqiaoz @ hfeg0pkn004)

- **trace**: `1792206946923_goqly` · user `xinqiaoz` · host `hfeg0pkn004` (10.129.2.13) · mc=244 · 165 msgs · cwd `/home/xinqiaoz/PDK_QA/pdkQaSystem` · tools: 385 calibre (pure physical_verify)
- **session file** (nested): `/home/xinqiaoz/.cline/data/sessions/1792206946923_goqly/1792206946923_goqly.messages.json` (407KB)
- **domain**: physical_verify (calibre SVRF dummy rule deck RCA + fix)
- **A-档 seed (msg 1, 纯意图)**: 「我认为 frame 的 M1Z/M9Z/M1Zb/M9Zb 在测试 GDS 上不产 dummy 可能还是和 border 有关。请尝试改一改，看看有没有办法解决。」— 合格 A-档 seed（用户提目标+假设，未给根因/方案）

## 真实任务与工具链

PDK Dummy QA 工程师对 `DUMMY/qa_workspace/data/DYT4E_WHCFP_LHCRP_DHCFP`（chip/frame 各 v0d5_rev01）执行 dummy QA。本会话聚焦 **QA-18 frame border 根因修复**。assistant 工具：editor×57（改 rule/config/约定文件）、run_approved_command×16（shell_generic_pdkqa / ssh_test_pdkqa / python_generic_pdkqa profile）、read_files×5、search_codebase×1。

## 根因链（assistant 推导，msg 2–12）

grep `calibreDummy_frame.rule`：
- 行 5666: `LAYER MAP 301/0 → 10018`（TEG 边框层 → 内部层 10018）
- `BORD_CHIP:TEG` mask ← 内部层 10018 ← GDS 层 301_0
- frame `CMP_BLK_OR` 表中 `BORD CHIP:TEG` 行**只对 M1Z/M9Z 列标 N**（生效）
- 行 5670: `BORD_NOT_ignore1_defineMaskBLK_M1Z_BORD_CHIP:TEG = (BORD NOT BORD_CHIP:TEG) NOT ignore_...`

**根因**：测试 GDS 没画 301_0/302_505 → `BORD_CHIP:TEG` 空 → `BORD NOT 空 = BORD 全部`（实心 1500×500 测试边框矩形）进入 `DefMaskBlk` → 整个画布变成避让区 → `EmptyArea` 空 → DFM FILL 无可填区域 → M1Z/M9Z/M1Zb/M9Zb 不产 dummy（M1Zb/M9Zb 经 MAP 归并到 M1Z/M9Z，同因）。

## 修复（assistant 执行，msg 14–30）

1. 改 `config_frame_full.ini` 把 301_0/302_505 加入 layers
2. 跑 `DummyPatternGenerator_v5.py config_frame_full.ini` → 重新生成 `QA_frame_full.gds`（61 target 含 301_0/302_505）
3. 写 `prepare_qa_frame_full.py`：`cp calibreDummy_frame.rule` → QA 目录 + `sed LAYOUT PATH "AAAAA.gds" → "../QA_frame_full.gds"` + `sed LAYOUT PRIMARY → QA_chip` + 清 `run.log`/`exit_code`
4. 跑 `run_calibre_dummy.py frame` → calibre 执行 dummy deck

## 验证结果（msg 140–141，用户接受）

- `exit code = 0` ✓（上次 GDS 缺失时 exit 4）
- `M1Z.gds = 25208 bytes` ✓（之前静默缺失）
- `M9Z.gds = 632 bytes` ✓
- `M9Zb.gds = 376 bytes` ✓
- M1Zb 未单独输出（疑经 MAP 归并到 M1Z）

border 假设验证成功。会话末尾用户要求 handoff（msg 131），editor 工具持续漏 `path` 参数故障（贯穿全会的工具陷阱），最终用户要求直接把交接内容输出到会话（msg 163），assistant 输出 `HANDOFF_qa18_frame_border_fix.md` 纯文本（msg 164）。

## 合成子主题（与本 shard 既有 case 正交）

取核心 RCA 逻辑：**calibre SVRF dummy deck 中 `BORD NOT <KEY>` 在 `<KEY>` 输入层缺失时退化为整片 BORD → EmptyArea 空 → 不产 dummy**。合成离线 Python 工具 `dummy_border_rca.py`：解析 rule deck（LAYER MAP / LAYER <KEY> / CMP_BLK_OR 表 / BLK_<T> 引用）+ config（layers）→ 判定 missing_layers / affected_targets / ok_targets → 生成 report.json + fix/（config_fixed.ini + prepare.py）。与 r155 DrcConnScriptAudit（connectivity 脚本缺陷审计）、r156 TaperChainDoeGen（锥形缓冲链 DOE）、r153 PcellBasexEnclose、r154 Nand3LefDerive 均正交。

- **金标准** = trace 末尾用户接受的根因链 + 修复产物（regenerate GDS with TEG layers + rebuild rule sed LAYOUT PATH/PRIMARY + rerun calibre → M1Z/M9Z/M9Zb.gds 出现）
- **断言**只对事实（缺失层集合、受影响 target 集合、修复产物结构、跨输入泛化、确定性），不对措辞
- **L1-boundary**（离线 Python 解析合成 deck，不真跑 calibre），与 r155/r156 同档
