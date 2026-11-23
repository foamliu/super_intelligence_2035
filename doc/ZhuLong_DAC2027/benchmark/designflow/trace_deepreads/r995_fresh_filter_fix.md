# r995 — fresh-filter 修复 + 130 truly-fresh C 候选锁定

**日期**: 2026-11-23
**轮次**: r995 (DEBT round, 0 case synthesized)

## 问题发现

本轮选料时发现 **fresh-filter 有 bug**：只检查 `_touched_4shard_r1050.txt`（4-shard 并集，不含 C 自身 ledger slugs），未检查 `trace_ledger_C.tsv`。导致 7 个"假 fresh"候选被深读后才发现已入库：

| slug | 已有 case_id | shard | 状态 |
|---|---|---|---|
| jaay4 | EDA-Eval-DesignFlow-MdPyBlockCompileCjkAudit-001 | C | case |
| soebd | EDA-Eval-DesignFlow-SchemStubPlacementPolicy-001 | C | case |
| mj3pw | PgViaAutoGen-001 | C | case |
| js4n1 | EDA-Eval-DesignFlow-M1ViaDrcCoOptim-001 | C | case |
| w4hlp | EDA-Eval-DesignFlow-TerminalGuiLaunchPortingFlow-001 | C | case |
| ab6ck | PinPrefixIncrRename-001 | C | case |
| 1mmir | EDA-Eval-DesignFlow-SkillRepoAudit-001 | C | case |

## 修复

fresh-filter 现在检查 **ALL 4 shard ledgers** (A/B/C/D `trace_ledger_*.tsv`) + 4-shard touched 文件。slug 提取 regex 改为 `r'_(\w{5})(?:\.|$)'` 兼容 ledger 中的 bare session ID 格式（`1234567890_abcde`，无 `.messages.json` 后缀）。

修复后 touched set = 8515 slugs（原 8385，+130 C 自身）。

## 修复后结果

- **truly fresh C cands (mc≥50, C-domain)**: 130（原"假 fresh" 187 - 57 已入库 = 130）
- 保存 top 40 到 `designflow/_fresh_C_r995.tsv`
- top 10:
  1. mc=222 04qh0 junxu@hfeg0pkn005 layout_virtuoso (virtuoso:677/schematic:402/dbcreaterect:15) **claimed**
  2. mc=221 jcop7 dechaoc@hfhds201 physical_verify (drc:3912/verilog:3848/netlist:1167)
  3. mc=213 ixdcf junlingw@hfeg0pkn005 (.lef:504/netlist:327/pyaether:44)
  4. mc=200 7q6sq junlingw@hfeg0pkn005 (.lef:504/netlist:290)
  5. mc=193 sniau junlingw@hfeg0pkn005 (.lef:498/netlist:278)
  6. mc=190 2m9z2 junlingw@hfeg0pkn005 (.lef:494/netlist:269)
  7. mc=187 y1q1z e02141@hfhds201 (lvs:520/synopsys:370/cmos:50/bandgap:25)
  8. mc=187 3yqt8 e02141@hfhds201 (lvs:520/synopsys:370 — 同 y1q1z pattern)
  9. mc=186 xkwxk junlingw@hfeg0pkn005 (.lef:494/netlist:243)
  10. mc=181 fhfl3 jason17w@hfeg0pnd002 (drc:3464/verilog:3160/netlist:693/lvs:68)

## 本轮 claimed

- `1794986684920_04qh0` (junxu@hfeg0pkn005, mc=222, layout_virtuoso) — 下一轮深读 + 合成

## DEBT

- **DEBT: 1 case 未合成** (04qh0 已 claimed，深读 + 合成 ETA r996)
- 根因：fresh-filter bug 消耗 ~28 min 探索预算在 7 个已入库 trace 上；修复后所剩时间不足完成 1 条 case 全流程
- 下一轮直接用 `designflow/_fresh_C_r995.tsv` top 候选，跳过探索阶段

## 经验教训（写入 future-round checklist）

- **fresh-filter 必须检查 ALL 4 shard ledgers**，不能只查 4-shard touched 文件
- ledger session 列格式 = `timestamp_slug`（无 `.messages.json`），regex 要兼容
- 选料前先 `grep <slug> designflow/trace_ledger_C.tsv` 确认不在台账，再 fetch
