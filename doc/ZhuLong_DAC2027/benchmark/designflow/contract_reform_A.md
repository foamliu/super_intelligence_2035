# Contract Reform Tracker — shard A

> 判分契约改造（check_static/check_live 拆分）shard A 跟踪文档。
> 指南：`/nasdata/app.e0031982/code/EDA-Flow-Bench/reports/CONTRACT_REFORM_GUIDE.md`

## 状态总览（2026-11-26 r1272）

| 优先级 | 状态 | 计数 | 说明 |
|:--|:--|:--|:--|
| P1 pilot 12 (A 份额) | ✅ DONE | 4/4 | r1270 已修+验 |
| P2 真-EDA L2.live | ✅ CLOSED (空) | 0 | r1272 复核: 3 候选均为 mock 误判, 归 P3 |
| P3 mock 声明 judge_layers | ✅ DONE | 585/585 | r1272 收口最后 3 条 |

**CONTRACT 心跳**：`P1=4/4 done · P2=0 L2.live(无真-EDA 候选) · P3=585/585 judge_layers declared`

## P1 — pilot 12 case（A 份额 4/4 DONE）

pilot 12 清单中 6 条标 shard A，但实测：
- **PowerFillMergeGen-001 / RsCalcChkPtGen-001**：物理在 `cases/C/`，`domain=layout_virtuoso` ⇒ 归 shard C（指南表 shard=A 系误标，A 未碰）。
- **A 实际 pilot 4 条**（均在 `cases/A/`）：

| case_id | judge_layers | ref check.py | test 字段同步 | L2.live 自验 |
|:--|:--|:--|:--|:--|
| FindPcells-001 | [L0,L1,L2.live] ✅ | check_static+check_live+check ✅ | sha 一致 ✅ | PASS (.75 hfhds201) |
| PyAetherCurDesignApi-001 | [L0,L1,L2.live] ✅ | check_static+check_live+check ✅ | sha 一致 ✅ | PASS |
| RtlDesignScenarioBoot-001 | [L0,L1,L2.live] ✅ | check_static+check_live+check ✅ | sha 一致 ✅ | PASS |
| RtlDesignScenarioBoot-001-v2 | [L0,L1,L2.live] ✅ | check_static+check_live+check ✅ | sha 一致 ✅ | PASS |

r1270 修 check_live upload-robustness bug（FindPcells + PyAetherCurDesignApi：`sess.upload(deliverable)` → `sess.upload(deliverable,"submit.zip")` 显式定名；真实 eval 行为不变，自验亦通）。

**DEBT**（非 P1 范畴，另行跟踪）：PyAetherCurDesignApi-001 `negative_selftest` PRE-EXISTING FAIL — 5 negs UNEXPECTED-PASS，根因是 selftest-harness 调 `check(path,REF_DIR)` 传 REF_DIR 作 workdir 致 `_check_static_impl` 读到 reference 文件误判（HEAD 同样失败，非本批引入）。

## P2 — 真-EDA L2.live 扩展（CLOSED · 空）

r1271 关键词扫出 3 条「真-EDA subprocess」候选（含 vcs/verdi/calibre/innovus 关键字）：
- Digital-023
- InnovusLaunchDiag-001
- VcsMkfileSimDiagnoseProduce-001

**r1272 复核（逐行读 check.py）结论：3 条均为 mock 误判，非真-EDA**：

| case_id | check.py 实际行为 | 真调 EDA 二进制? | 判定 |
|:--|:--|:--|:--|
| Digital-023 | 仅 `make -n` 干跑校验 makefile 语法/变量替换；vcs/verdi/bsub 出现在 make 展开输出串里 | ❌ 否 | mock → P3 |
| InnovusLaunchDiag-001 | `subprocess([python, check_launch.py, ...])` 跑候选 python 脚本解析**内嵌文本** evidence（calibre/innovus 是 evidence 文本里的 module 名/路径，非二进制） | ❌ 否 | mock → P3 |
| VcsMkfileSimDiagnoseProduce-001 | 仅 `make -n` 干跑校验 Makefile；vcs/verdi/simv 出现在 make 展开输出串里 | ❌ 否 | mock → P3 |

误判根因：r1271 用关键字扫描（vcs/verdi/calibre/innovus 出现 ⇒ 标真-EDA），但关键字实为 `make -n` 干跑输出串 / evidence 文本，非 `subprocess` 调真二进制。

**结论**：shard A（digital/verification/pnr_signoff/eda_other）的 case 以 Makefile/脚本/文本分析为主，候选脚本不需要真跑 EDA 工具即可正确判分 ⇒ **无 P2 真-EDA 候选**。P2 闭合（空）。若后续造新题触及真 pyAether API 调用（如 pilot 4 条），再回 P2 流程加 check_live。

## P3 — mock case 声明 judge_layers（585/585 DONE）

- r1269: 声明 115 条 Lite case（commit EFB）
- r1271: 声明 462 条 mock case（commit 877b8523c EFB master）
- r1272: 声明最后 3 条（Digital-023 / InnovusLaunchDiag-001 / VcsMkfileSimDiagnoseProduce-001，由 P2 误判归 P3）

**A 全量 coverage**：585/585
- `judge_layers=["L0","L1","L2.live"]`：5 条（pilot 4 + FindPcells 等已有 L2.live，含 r1270 修）
- `judge_layers=["L0","L1"]`：580 条（mock，框架回退旧式 check()）
- 无 judge_layers：0 条

**行为保持验证**（r1271 建立，r1272 沿用）：框架对 `[L0,L1]` + 旧式 `check()` 走 fallback，L2.live 不触发 ⇒ 与改造前（空 judge_layers）完全一致。r1272 对 3 条新声明 case 跑 reference solution `check()` 均 PASS（Digital-023=True / InnovusLaunchDiag-001=PASS / VcsMkfileSimDiagnoseProduce-001=PASS），case 本身 sound，metadata-only 声明无回归。

## 纪律

- 🚫 未改 check.py / 断言逻辑 / prompt / assets / hidden
- 🚫 未碰别 shard 文件（PowerFillMergeGen-001 / RsCalcChkPtGen-001 归 C，A 未碰）
- 🚫 未碰 jsonl
- ✅ P1/P2/P3 三优先级依序：P1 > P2 > P3
