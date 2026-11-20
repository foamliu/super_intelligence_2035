# trace_deepread: 1794881298870_ned46 (zlhou @ hfeg0plg52, mc=119, physical_verify/PEX)

## 会话概览
- 56 msgs, 2 真实用户轮, 287KB messages.json
- 工具链: cline read_files / list_allowed_files / run_approved_command (python-runner) / editor
- 域: physical_verify (Calibre/GloryEX PEX parasitic extraction)

## 真实用户意图 (A-档合规: 提出需求轮)
- **U#1** (1794881299237): 「查看目录 /proj/lacaa/TV1_FS/workdir/zlhou/2prf_work/pex/pex420/pex1024x72，抽取pex失败了，是什么原因」
- **U#2** (1794881619615): 「我把*CAPTAB 前面的 * 去掉了，但是还是不行，看看为什么」

## assistant gold 诊断 (根因双层)
1. **配置层 (config_precedence)**: pex1024x72 跑的是 MULTI_CORNER（多角）流程。gxrc 选项文件 `gxrc_cci_cmd_V0d1_Rev07` 顶层 `*CAPTAB <path>` 被 `*` 注释。用户去掉 `*`（→ `CAPTAB <path>`）仍失败，因为在 multi-corner 模式下 `corner_file` 里每个 corner 的 CAPTAB 路径**覆盖**顶层 CAPTAB 关键字，编辑顶层无效。
2. **runset 层 (runset_stale)**: `corner_file` 6 个 corner 的 CAPTAB 路径都指向 `/apps/imctf/cad/runset/lacaa/tv1_fs/current/lpe_gxrc/GloryEX_20261106_V0d1_Rev07_3Corner/FS/CAPTAB/...`。该 runset 目录已被删除/升级，当前 runset 下只有 `GloryEX_20261113_V0d1_Rev07_9Corner`（9 corner 新版）。gxrc 启动第一件事读 CapTab → `TRIO-0428 Cannot open CapTab file` → `prepare failed` → `GloryEX extraction of design failed!`。
3. **修复**: 把 `corner_file` 6 处 CAPTAB 路径的 `GloryEX_20261106_V0d1_Rev07_3Corner` 改为 `GloryEX_20261113_V0d1_Rev07_9Corner`。

## 关键证据
- PEX log: `CXN4HC2PS1024X72M4B4C1R1W1BW1RE1_FS_420.log` 含 TRIO-0428 + error path (Rev07_3Corner)
- 对比: 父目录 `FS/` 是同 block 单 corner 成功运行（`*MULTI_CORNER` 注释，用顶层 CAPTAB 加载本地 FS/CAPTAB）
- 时间线: 配置 10:09:21 改 (`*CAPTAB`→`CAPTAB`)，10:12:50 重跑仍读 /apps 默认路径 → 证实顶层 CAPTAB 在 multi-corner 下不生效
- runset 现状: lpe_gxrc/ 下 `Rev07_3Corner` MISSING，`Rev07_9Corner` present

## reframe (档 B → PexGxrcDiag-001)
A 档 gold = free-text 根因诊断 prose (依赖 live /apps、/proj 不可达，无 ≥8 独立硬断言牙) → reframe 为离线纯 stdlib `pex_fail_diag.py`，4 输入(gxrc_config/corner_file/pex_log/runset_listing)，输出结构化 JSON。
- visible A: 忠实 trace (multi-corner 激活 + 顶层 *CAPTAB 注释 + 6 corner Rev07_3Corner MISSING + Rev07_9Corner present → root_causes=[config_precedence, runset_stale])
- hidden B: 全反相 (single-corner + 顶层 CAPTAB 激活 + 1 corner Rev04_1Corner MISSING + Rev08_4Corner present → root_causes=[runset_stale]，无 config_precedence)
- 6+ 轴全异防硬编码 A: mode / captab_source / multi_corner_active / top_level_captab_commented / n_corners / runset_referenced / runset_replacement / root_causes 集合

## 意图审计判定: keep
zlhou 真实意图（诊断 PEX 抽取失败根因，理解为什么去掉 *CAPTAB 的 * 还是不行）完全保留；reframe 是 grounding（把依赖 live 文件的诊断离线化），非加难。2026-11-15 reaudit 后 debug-Q&A/env-config 合法。
