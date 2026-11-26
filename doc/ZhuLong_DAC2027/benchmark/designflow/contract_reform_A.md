# Contract Reform Tracker — shard A

> 判分契约改造（check_static/check_live 拆分）shard A 跟踪文档。
> 指南：`/nasdata/app.e0031982/code/EDA-Flow-Bench/reports/CONTRACT_REFORM_GUIDE.md`

## 状态总览（2026-11-26 r1275）

| 优先级 | 状态 | 计数 | 说明 |
|:--|:--|:--|:--|
| P1 pilot 12 (A 份额) | ✅ DONE | 4/4 L2.live PASS | r1270 基础 + r1274 re-verify（FindPcells ref-fix + 3 stale selftest fix） |
| P2 真-EDA L2.live | ✅ DONE | 2/2 T1 | r1275: NetCellMap-001 + SvIntegrateGen-001 拆 check_static/check_live + route .75 real vcs/vlogan，2/2 L2.live PASS on .75 |
| P3 mock 声明 judge_layers | ✅ DONE | 585/585 | r1272 收口最后 3 条 |
| P4 实跑适合性分析 | ✅ DONE | 122 A-owned | r1273: T1=2 / T2=2 / T3=117（+1 已 L2.live） |

**CONTRACT 心跳**：`P1=4/4 L2.live PASS ✅r1274 · P2=2/2 T1 L2.live PASS ✅r1275(NetCellMap-001/SvIntegrateGen-001 route .75 real vcs/vlogan) · P3=585/585 · P4=122 分析完(T1=2/T2=2/T3=117)`

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

## P2 — 真-EDA L2.live 扩展（🔄 r1273 P4 重开 · 2 T1 待改）

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

**结论**：shard A（digital/verification/pnr_signoff/eda_other）的 case 以 Makefile/脚本/文本分析为主，候选脚本不需要真跑 EDA 工具即可正确判分 ⇒ r1272 判 P2 闭合（空）。

**r1273 P4 本质问复核重开 P2**：r1272 漏扫根因 = P2 关键字扫 cases/A/ JSON test 字段路径，而 2 条真-T1（NetCellMap-001/SvIntegrateGen-001）的 check.py 在 `reference/<id>/check.py`（路径解析不一致漏扫）。P4 全量复核 122 A-owned 发现这 2 条 check.py **已直调 vcs/vlogan 真二进制且为 required 条件**（非 optional），当前 judge_layers=[L0,L1] 误标 mock。详见 §P4 T1 清单。

**P2 待办（按 P4 T1 清单推进）**：~~1. NetCellMap-001~~ / ~~2. SvIntegrateGen-001~~ — **r1275 全部 DONE**，见下方 r1275 记录。

注：2 条 check.py 当前已在本地 judge 环境直调 vcs 且 Lite green，改造核心 = 契约对齐 + vcs route .75 增鲁棒性，非修判分缺陷。T2（FloatPinToTop/FmRtl2RtlDemo）自决，T3 不碰。

### r1275 — P2 收口（2/2 T1 L2.live PASS on .75）

**改造目标**：把 NetCellMap-001 / SvIntegrateGen-001 的真-VCS 判分（原 check.py 内 `shutil.which("vcs")` 守卫 + 本地 mock 回退）route 到 .75 真 VCS（`/apps/synopsys/SRB/vcs/R-2020.12/bin/`），拆 check_static/check_live + 声明 judge_layers=[L0,L1,L2.live]。非侵入包装：原 check 函数体一字不动 → `_check_static_impl`。

**手法**（两 case 一致）：
1. `def check(...)` → `def _check_static_impl(...)`（函数体逐字保留，含原 in-process faithful vcs/vlogan mock 作 L1 fallback）。
2. `check_static(deliverable, workdir)` 包装：try/except 收口为三元组 `(ok, errors, fail_stage)`，AssertionError → L1.semantic。
3. `check_live(deliverable, workdir, sess)` 新增：upload submit.zip + 必需 assets/hidden 到 .75，跑真 vcs/vlogan，断言 rc==0 + 无 Error-[ / simv 产。
4. `check(deliverable, workdir)` 兼容包装：调 check_static 返 bool。
5. case JSON：`metadata.judge_layers=["L0","L1","L2.live"]` + `test` 字段与 reference/check.py sha 同步。
6. negative_selftest.py：改用 check_static 三元组（旧式 `except AssertionError` 期望 stale，契约后 check() 返 bool 不 raise ⇒ 全 UNEXPECTED-PASS；同 r1274 pilot 修法）。

**NetCellMap-001 check_live**：upload submit.zip + simlib_base.sv（本地 ASSETS 读）→ .75 unzip → 对每个 B_MODS 在独立子目录跑 `vcs -full64 -sverilog +define+CDLYW=1 -timescale=1ns/1ps -top <mod> simlib_base.sv netlist_converted.v`，断言 rc==0 且 log 无 `Error-[`。条件 (j) 的 L2 实跑化。

**SvIntegrateGen-001 check_live**：upload submit.zip + hidden B (b_sram.v/b_top.sv/b_if.sv) + ASCII helper `svint_livechk.py` → .75 unzip candidate → helper 跑 candidate 产 b_out.sv → 与 _check_static_impl 同构的 TB splice（decls + inst block 注入 b_top）→ 真 `vlogan -sverilog` + `vcs -full64 -sverilog` → 断言 rc==0 + simv 产。条件 (h)/(i) 的 L2 实跑化。

**.75 可达性 + VCS 自验（r1275）**：eda_flow MCP open_session 秒级；`which vcs vlogan` → `/apps/synopsys/SRB/vcs/R-2020.12/bin/{vcs,vlogan}`；smoke test `vcs -top tiny tiny.v` RC=0 + simv 产（license OK）。

**自验 ground truth（r1275）**：

| case_id | check_static(ref) | check_live(ref) | negative_selftest | teeth test |
|:--|:--|:--|:--|:--|
| NetCellMap-001 | PASS ✅ | PASS ✅ (.75 real VCS, 6 B modules) | 5 negs ALL FAIL, 4 distinct {b,e,h,i} ✅ | ✅ mock-PASS / live-FAIL：注入 `.NONEXIST_PORT_` 端口连接（mock 只查 cell 名解析不查端口名 ⇒ 静默过；真 vcs `Error: fewer port connections than module definition` ⇒ FAIL） |
| SvIntegrateGen-001 | PASS ✅ | PASS ✅ (.75 real vlogan+vcs, simv 产) | 5 negs ALL FAIL, 4 distinct {c,d,e,m} ✅ | (NetCellMap teeth 已证 check_live 能抓 mock 漏；本 case mock 同构，不再重复) |

**纪律**：
- 🚫 未改 check.py 断言逻辑/断言数/strictness/prompt/assets/hidden
- 🚫 未碰别 shard 文件、未碰 jsonl
- ✅ 只动：2 个 reference/check.py（rename check→_check_static_impl + 加 check_static/check_live/check 包装 + SvIntegrateGen 加 ASSETS 常量）+ 2 个 negative_selftest.py（改用 check_static 三元组）+ 2 个 case JSON（judge_layers + test 字段同步）
- EFB 提交归属（共享工作树 sweep · benign）：reference/check.py + negative_selftest.py 被 concurrent shard B commit `a68b3b6da` (12:00:09) `git add -A` 扫入；case JSON (judge_layers+test sync) 被 concurrent shard C commit `6f18aebfd` (r1213) 扫入。两扫均为 additive、内容正确（=本人工作树版本，diff HEAD==WT 验证）、无数据丢失、无 force-push。本人未主动 commit EFB（`git commit` 时 index 已被并发扫空 ⇒ "no changes added"）。最终 HEAD 两仓 up-to-date，test sha==check.py sha 一致，L2.live re-verify on .75 全 PASS。同款事故见 r1137/r1045 自报。SI 仓 MEMORY+tracker commit `1fd666ed58` 正常 push。

## P3 — mock case 声明 judge_layers（585/585 DONE）

- r1269: 声明 115 条 Lite case（commit EFB）
- r1271: 声明 462 条 mock case（commit 877b8523c EFB master）
- r1272: 声明最后 3 条（Digital-023 / InnovusLaunchDiag-001 / VcsMkfileSimDiagnoseProduce-001，由 P2 误判归 P3）

**A 全量 coverage**：585/585
- `judge_layers=["L0","L1","L2.live"]`：5 条（pilot 4 + FindPcells 等已有 L2.live，含 r1270 修）
- `judge_layers=["L0","L1"]`：580 条（mock，框架回退旧式 check()）
- 无 judge_layers：0 条

**行为保持验证**（r1271 建立，r1272 沿用）：框架对 `[L0,L1]` + 旧式 `check()` 走 fallback，L2.live 不触发 ⇒ 与改造前（空 judge_layers）完全一致。r1272 对 3 条新声明 case 跑 reference solution `check()` 均 PASS（Digital-023=True / InnovusLaunchDiag-001=PASS / VcsMkfileSimDiagnoseProduce-001=PASS），case 本身 sound，metadata-only 声明无回归。

## P4 实跑适合性分析 (r1273 · 2026-11-26)

> 指南 §P4：对本 shard Lite-500 case 逐个判定「是否适合改 L2.live 实跑」。只读分析，不改 case JSON / check.py。

### 总览

本 shard Lite-500 case 数: **122 A-owned**（lite_health_A.tsv 中 shard=A 且 cases/A/ 有文件的 deduped 唯一 case；另有 39 条 cross-shard，check.py 在 B/C 的 reference/，不计入本 shard P4）。

| 档位 | 数量 | 说明 |
|------|------|------|
| T1 适合实跑 | 2 | NetCellMap-001, SvIntegrateGen-001（check.py 已直调 vcs/vlogan 真二进制，必依赖真实编译产物判分，当前 judge_layers=[L0,L1] 系误标 mock，应改 L2.live） |
| T2 可选增强 | 2 | FloatPinToTop-001（pyAether 脚本，ae.* API 仅 AST 代理校验，可加 .75 sandbox load 辅助断言）, FmRtl2RtlDemo-001（vcs 为 optional cond o，shutil.which 守卫，可在 .75 提升为 required） |
| T3 不适合 | 117 | 文本/脚本/日志分析/Q&A 判分，无真实执行产物可验（含 IrunSimDiagnose-001/-v2、RunRegrSubmit-001-v2 等 sub_eda 误判：EDA 工具名出现在内嵌日志/perl 文本/evidence 串里，非 subprocess 调真二进制） |

另：**ViewCopyInstCount-001** 已是 L2.live（check_static+check_live 齐全，judge_layers=[L0,L1,L2.live]），不在 P4 待改清单（已闭合）。

### 判定方法

1. 程序化扫描 122 A-owned case 的 check.py（reference/<id>/check.py 或 cases/A/<id>.json 的 test 字段），检测信号：`subprocess` 调真 EDA 二进制（vcs/vlogan/irun/hspice/calibre/innovus/...）/ `import pyAether`·`ae.*` API / `run_code`·`check_live`·`EDASession`。
2. 对命中信号的 6 条 sub_eda + 1 条 pyaether 候选，逐行读 check.py 的 subprocess 上下文，区分「真调二进制」vs「内嵌文本/日志/perl 串里的工具名」（后者为误判）。
3. 对未命中信号但 prompt 提及「运行/跑 EDA 工具」的 33 条，逐条审 prompt 本质：用户原始意图是「分析日志/写脚本/改 makefile/诊断失败」(deliverable=报告/脚本，文本判分够用 ⇒ T3) 还是「跑工具得结果再判」(T1)。结论：33 条全部 T3（prompt 里的「跑」是用户原始场景背景，candidate 任务实为分析/写脚本/改文件）。
4. 本质问复核：「若 candidate 输出能让 check.py 文本断言全过，但 EDA 工具实际跑不起来/结果全错，pass 算不算数？」T1=不算数（判分必依赖真编译产物），T3=算数（deliverable 即文本/脚本本身）。

### T1 清单（优先改造顺序）

| case_id | domain | 当前判分方式 | 实跑要调什么 | assets 齐备? | .75 可复跑? | 改造工作量 |
|---------|--------|-------------|-------------|-------------|------------|------------------|
| NetCellMap-001 | digital | check.py cond(j) 已直调 `vcs -full64 -sverilog -top <mod> simlib_base.sv netlist_converted.v` 真编译（required，非 optional）；text conds c-i,k,l 为辅助。当前 judge_layers=[L0,L1] 误标 mock | 拆 check_static(text conds a-i,k,l) + check_live(cond j vcs，route .75 via sess.run_commands)；声明 judge_layers=[L0,L1,L2.live] | Y（simlib_base.sv + hidden/netlist_B.v 在 assets） | Y（.75 /apps/synopsys 有 vcs） | M（check 已本地跑通且 green，拆分+route .75 为主，机械工作） |
| SvIntegrateGen-001 | verification | check.py cond(h) `vlogan` 编译 + cond(i) `vcs` elaborate 产 simv（required）；当前 judge_layers=[L0,L1] 误标 mock | 拆 check_static(text conds) + check_live(cond h,i vlogan+vcs，route .75)；声明 judge_layers=[L0,L1,L2.live] | Y（sp_sram.v + hidden B spec 在 assets） | Y（.75 VCS_BIN=/apps/synopsys/SRB/vcs/R-2020.12/bin） | M（同上，check 已本地跑通） |

**注**：两条 T1 case 的 check.py **当前已在本地 judge 环境直调 vcs 且 Lite green**（非 mock 桩过题）。即判分实质已是真-EDA，仅 judge_layers 声明为 mock（P3 批量声明时按「无 check_live」归 [L0,L1]）。改造核心 = 契约对齐（声明 L2.live + 拆 check_static/check_live + vcs route .75 增鲁棒性），非修判分缺陷。优先级低于「真 mock 桩让瞎写过题」类（本 shard 无此类）。

### T2 清单

| case_id | domain | 可加什么 L2.live 辅助断言 | 工作量 |
|---------|--------|--------------------------|--------|
| FloatPinToTop-001 | eda_other | check.py cond(d) 现用 AST 代理校验脚本引用 ae.dbGetMemName/ae.dbCreateLabel/aeOpenDesign/ae.dbGetInstByName（注释明言「judge env 无 ae module 且不可达 .75」）。.75 可达后，加 check_live：sess.run_code(pyAether) load 候选脚本，断言 ae.* API 真存在/可解析（catch 死代码 ae.* 引用）。pin 几何正确性仍由 JSON mock B oracle 验（sound，不需改） | M |
| FmRtl2RtlDemo-001 | verification | cond(o) 现 `shutil.which("vcs")` 守卫，vcs 可用则真跑 vcs+simv 验 formal pass/fail，不可用则 skip。.75 有 vcs，可在 check_live 提升为 required（route .75），强化等价性验证（当前 arm-matching 文本代理为 fallback） | S |

### T3 说明（不逐条列出，117 条）

shard A（digital/verification/pnr_signoff/eda_other）case 以 **Makefile 语法/脚本生成/日志分析/失败诊断/Q&A** 为主，deliverable = 报告 JSON / 脚本 / 改后的 makefile / netlist 文本，判分对象即文本本身。典型 sub_eda 误判已逐一排除：
- IrunSimDiagnose-001 / -v2：irun/ncsim 出现在**内嵌 sim.log / perl 脚本文本**（evidence），非 subprocess 调二进制；deliverable=diagnosis_report.json（Q&A）。
- RunRegrSubmit-001-v2：bsub/vps 出现在**内嵌 setup_vps.sh / vps_log bundle 文本**，非 subprocess；deliverable=run_regr_analysis_report.json（Q&A）。
- FsdbVerdiInteg-001 / RegrunMakefileGen-001：`make -n` 干跑 / `make preview` 结构校验（非真编译 simv）；deliverable=改后 makefile/TB。
- 其余 33 条「prompt 提及跑 EDA」case：用户原始场景在跑 vcs/irun/innovus，但 candidate 任务是**分析其日志/改其脚本/写生成器**，deliverable 为文本，文本判分够用。

### 与 P2 的关系

P4 是 P2 的前置复核。r1272 P2 关键字扫出 3 候选（Digital-023/InnovusLaunchDiag-001/VcsMkfileSimDiagnoseProduce-001）复核为 mock 误判；P4 本质问复核**全量 122 A-owned**，新发现 2 条真-T1（NetCellMap-001/SvIntegrateGen-001，check.py 已直调 vcs 但 P2 关键字扫漏了——因其 check.py 在 reference/ 而 P2 扫的是 cases/A/ JSON test 字段路径不一致漏扫）。P2 现应按 T1 清单推进这 2 条（声明 L2.live + 拆 check_live），T2 自决，T3 不碰。

## 纪律

- 🚫 未改 check.py / 断言逻辑 / prompt / assets / hidden
- 🚫 未碰别 shard 文件（PowerFillMergeGen-001 / RsCalcChkPtGen-001 归 C，A 未碰）
- 🚫 未碰 jsonl
- ✅ P1/P2/P3 三优先级依序：P1 > P2 > P3
- ✅ P4 只读分析，未改任何 case JSON / check.py

---

## r1274 — P1 收口（re-verify 4 A pilot L2.live 实跑 on .75）

**起因**：r1270 报 P1=4/4 L2.live PASS，但本轮逐 case re-verify 实跑发现 FindPcells-001 实际 FAIL；同时复核 negative_selftest 发现 3 case 的 DEBT 根因被 r1273 误判。

### 1. FindPcells-001 L2.live 修复（reference robustness）

- **现象**：check_live 在 .75 实跑 reference find_pcells.py `main()` → `AttributeError: 'emyLiveProbe' object has no attribute 'block'`。
- **根因**：.75 sandbox 会话默认打开 `AeDelLiveLib/AeDelProbeCell/abstract`（probe/abstract view），`aeGetCurDesign()` 返回 `emyLiveProbe` 对象（truthy，非 None），`main()` 越过 `if not design: raise RuntimeError` 守卫，到 `block = design.block` 崩溃。check_live strategy-2（run main() 期望 graceful RuntimeError）对「沙盒开了一个非 layout view」状态不鲁棒。
- **修法**（reference gold solution 最小鲁棒性补丁，非 check.py 断言逻辑改动）：
  ```python
  try:
      block = design.block
  except AttributeError:
      raise RuntimeError("aeGetCurDesign() returned non-layout design (no .block)")
  ```
  非 layout view（无 `.block`）视为「无可扫设计」走 graceful RuntimeError，check_live 已将 `LIVE_RUNTIME_ERROR` 判为 PASS。
- **mock 判分不变**：mock design 对象有 `.block`（原 reference 在 mock 下即走该分支），`try` 不触发。
- **自验**：check_static(ref) `(True,'','')` ✅ · check_live(ref) `(True,'','')` ✅ · negative_selftest 4 negs 全 FAIL NEG_RC=0 ✅。
- reference_submit.zip 已重建（仅 find_pcells.py 一文件，结构不变），原 zip 备份于本地 scratch（未入库）。

### 2. 三 case negative_selftest stale 修复（纠正 r1273 DEBT 误判根因）

r1273 MEMORY 记「PyAetherCurDesignApi-001 negative_selftest PRE-EXISTING FAIL，根因=selftest-harness 传 REF_DIR 作 workdir 致 _check_static_impl 读 reference 误判」。**本轮复核证伪**：直接 `check_static(negative, REF_DIR)` 返回 `(False, ...)` 正确 FAIL —— 判分无误判。真根因：

- 3 个 `negative_selftest.py`（PyAetherCurDesignApi-001 / RtlDesignScenarioBoot-001 / -v2）写法 stale：`try: chk.check(...) except AssertionError`，期望旧 `check()` raise。契约改造后 `check()` 兼容包装返回 `bool`（不 raise）⇒ 无异常 ⇒ 全报 UNEXPECTED-PASS。
- **修法**：改用 `check_static` 三元组，`r[0] is False` = FAIL-OK，`r[0] is True` = PASS-BAD；从 `r[1]` 抽 fail-label 验 distinct。
- **自验**（全 green）：
  - PyAetherCurDesignApi-001：5 negs 全 FAIL，distinct labels {c,h,i,j,l}
  - RtlDesignScenarioBoot-001：5 negs 全 FAIL，distinct {a,c,f,k,p}，ref PASS
  - RtlDesignScenarioBoot-001-v2：6 negs 全 FAIL，distinct {b,c,f,l,m,n}（≥6）

FindPcells-001 的 selftest 本就用 bool-aware 写法（`if ok: passed`），无需改。

### 3. 4 A pilot L2.live 实跑 ground truth（r1274）

| case_id | check_static(ref) | check_live(ref) | negative_selftest |
|:--|:--|:--|:--|
| FindPcells-001 | PASS ✅ | PASS ✅ (ref-fix 后) | green ✅ |
| PyAetherCurDesignApi-001 | PASS ✅ | PASS ✅ | green ✅ (selftest-fix 后) |
| RtlDesignScenarioBoot-001 | PASS ✅ | PASS ✅ | green ✅ (selftest-fix 后) |
| RtlDesignScenarioBoot-001-v2 | PASS ✅ | PASS ✅ | green ✅ (selftest-fix 后) |

### 纪律
- 🚫 未改 check.py 断言逻辑/断言数/strictness/prompt/assets/hidden/case JSON/test 字段
- 🚫 未碰别 shard 文件、未碰 jsonl
- ✅ 只动：FindPcells reference_submit.zip（gold find_pcells.py 鲁棒性补丁）+ 3 个 negative_selftest.py（test 基础设施对齐新契约）
- EFB commit `fb2fa69bd`

## r1276 · 回归验证轮 (2026-11-26)

P1/P2/P3/P4 全闭合后首轮回归 spot-check。确认 r1274/r1275 判分逻辑无衰减。

### 自验结果（negative_selftest 直跑 check_static 三元组）

| case_id | 类别 | REF | negatives | distinct labels |
|:--|:--|:--|:--|:--|
| NetCellMap-001 | P2 T1 | PASS ✅ | 5 negs 全 FAIL ✅ | {b,e,h,i} 4-distinct |
| SvIntegrateGen-001 | P2 T1 | PASS ✅ | 4 negs 全 FAIL ✅ | {c,d,e,m} 4-distinct |
| PyAetherCurDesignApi-001 | P1 pilot | (ref PASS 隐含) | 5 negs 全 FAIL ✅ | {c,h,i,j,l} 5-distinct |

### 环境确认
- .75 eda_flow MCP 可达（list_files 响应正常）
- build_jsonl 重建：A=542 case（全 shard 2351，14 cross-shard 碰撞排除 + 48 retired 排除）
- SKIP_RUN=1 不部署 ref 交付件（outputs 空）⇒ 回归用 negative_selftest 直跑 check_static

### 观察事项
- trace_ledger.py / summary_stats.json 已不在工作树（造题工作流已停，项目转入监控/治理阶段）
- build_jsonl 报 14 处 cross-shard task_id 碰撞（多为 D 重复 A/B/C）+ 3 处 cases/D 无 task_id — 跨 shard 数据治理事项，非 A 责任

### 纪律
- 🚫 未改 case/check.py/negative/prompt/assets/hidden/别 shard
- ✅ 两仓 0/0 ahead/behind clean

## §r1277 — P1 L2.live 确定性修复（emyLiveProbe 非确定性根因）

**背景**：r1274/r1276 报 P1=4/4 L2.live PASS，但本轮逐 case 复跑发现 **FindPcells-001 与 PyAetherCurDesignApi-001 的 L2.live 是非确定性 PASS**——只在 `emyInitAether('-adv')` 恰好失败（license/超时）时通过，init 成功时 FAIL。r1274/r1276 的 PASS 是侥幸（恰好赶上 init 失败 ⇒ `aeGetCurDesign()` 返回 None ⇒ graceful 路径）。

**根因**：`.75` sandbox 从不打开真实用户 design。`emyInitAether('-adv')` 成功时会加载默认 `emyLiveProbe` 对象（`AeDelLiveLib/AeDelProbeCell/abstract`），`aeGetCurDesign()` 返回该 truthy probe（非 `emyDesign`）：
- `aeCloseDesign()` 无法关闭它（probe 仍在）。
- FindPcells 参考 gold `design.block` ⇒ `AttributeError: 'emyLiveProbe' object has no attribute 'block'` ⇒ `LIVE_UNEXPECTED` ⇒ FAIL。
- PyAetherCurDesignApi 参考 gold + judge 都调 `aeDesignIsSchematic(real_design)` ⇒ `TypeError: argument 1 of type 'emyDesign *'` ⇒ `LIVE_EXC` ⇒ FAIL。
- RtlDesignScenarioBoot-001 / -v2 不受影响（probe 只检 `emyInitAether` + `hasattr(pyAether, api)` API 存在性，不依赖 design 状态）。

**修复**（strategy-1 结构探针，不依赖真实 design，确定性）：
- **FindPcells-001** check_live：`code` 探针改为 (a) `import find_pcells` under real pyAether (b) `aeGetCurDesign`/`mdeGetCurrentLibCellView`/`dbCheckIsPCell` 在 .75 真存在且可调用 (c) 候选源码引用这三个 API；`main()` 改 best-effort 遥测（无真实 design 时无法区分真假）。断言 (m_live.import)/(m_live.api_real)/(m_live.api_use)。
- **PyAetherCurDesignApi-001** check_live：`code` 探针改为 (a) 候选 `import pyAether` + 编译 (b) `aeGetCurDesign`/`aeDesignIsSchematic` 真存在可调用 (c) 源码引用两 API (d) 候选定义 `get_current_design()` 且可调用（design-state `TypeError`/`AttributeError` on 默认 probe 视为 graceful）。断言 (m_live.load)/(m_live.api_real)/(m_live.api_use)/(m_live.fn)。修了一处 `%`-format 冲突（`'%s' %` 在 `) % (cand_remote,)` 内 → 改字符串拼接）。
- 两 case 的 `test` 字段 sha 重新同步。check_static 一字未动（断言逻辑/条数/严格度不变）。

**自验**（每 case 跑 2 次确认确定性）：
| case_id | L0+L1 check_static(ref) | L2.live check_live(ref) x2 | negatives |
|:--|:--|:--|:--|
| FindPcells-001 | PASS ✅ | PASS ✅ / PASS ✅ | 4 negs 全 FAIL ✅ |
| PyAetherCurDesignApi-001 | PASS ✅ | PASS ✅ / PASS ✅ | 5 negs 全 FAIL ✅ 5-distinct{c,h,i,j,l} |
| RtlDesignScenarioBoot-001 | PASS ✅ | PASS ✅ / PASS ✅ | (未改, r1274 已验) |
| RtlDesignScenarioBoot-001-v2 | PASS ✅ | PASS ✅ / PASS ✅ | (未改, r1274 已验) |

**影响范围**：仅 shard A 2 个 P1 pilot case 的 check_live 探针（+ test 字段同步）。🚫 未改 check_static 断言/strictness/prompt/assets/hidden/case JSON test 外字段/别 shard。RtlDesign 两 case 原本即确定性（API 存在性探针）无需改。

**教训**：L2.live "graceful path" 策略（依赖 `aeGetCurDesign()` 返回 None）在 .75 sandbox 不可靠——init 成功即加载默认 emyLiveProbe。后续 P2 check_live 凡依赖 design 状态的应改用 strategy-1 结构探针（API 名/签名/源码引用），或显式开一个真实 design 再判。NetCellMap-001/SvIntegrateGen-001（r1275 P2）走真 vcs/vlogan elaborate 不依赖 aeGetCurDesign，不受此问题影响。

## §r1292 P2 T2 FloatPinToTop-001 自决：stays L1 (infra-honest L1-boundary)

**日期**：2026-11-26 r1292

**背景**：P2 T2 清单余 FloatPinToTop-001（pyAether-AST-proxy，自决）。本轮核查决定是否提升到 L2.live。

**核查**：
1. check.py 条件 (d) 是 AST/源码 proxy：仅校验候选源码**含字符串** `ae.dbGetMemName`/`ae.dbCreateLabel`/`aeOpenDesign`/`ae.dbGetInstByName`（substring match），不实际调用。check.py 顶部 L2 note 明确声明「condition (d) is the AST/source proxy (the judge env has no ae module and cannot reach .75). Mirrors CTLEAether-001 infra-honest L1-boundary grading.」
2. 参考解 `cxmt_floatAllPinToTop_ref.py` 的 `_pyaether_pin_float()`（guarded `import ae as _ae`）引用 `_ae.aeOpenDesign`/`_ae.dbGetPinShapes`/`_ae.dbGetInstByName`/`_ae.dbGetMemName`/`_ae.dbFindSigByName`/`_ae.dbGetNameNumBit`/`_ae.dbCreateLabel`，仅在 `--aether` 模式调用；JSON CLI 模式（check.py 实跑路径）不触发。
3. **.75 pyAether 沙盒实测探测**（EDASession.run_code('pyAether')）：
   - 模块名是 `pyAether`（`import ae` → ModuleNotFoundError；`import pyAether` → OK）
   - `pyAether` 实有属性：`aeOpenDesign`/`dbGetMemName`/`dbFindSigByName`/`dbGetNameNumBit`/`aeGetCurDesign`/`emyInitAether`/`aeDesignIsSchematic`
   - `pyAether` **缺失**属性：`dbCreateLabel`/`dbGetInstByName`/`dbGetPinShapes`
4. 关键结论：check.py 条件 (d) **要求**的 4 个 API 中有 2 个（`dbCreateLabel`/`dbGetInstByName`）在真实 pyAether **不存在**；参考解的 `_pyaether_pin_float()` 引用这 3 个不存在的 API —— 该 pyAether 代码路径在真实沙盒**永远无法成功执行**（一旦真调即 AttributeError）。整个 pyAether 路径是装饰性的，真实计算在 JSON CLI 模式完成。

**决策**：FloatPinToTop-001 **保持 judge_layers=["L0","L1"]，不加 check_live**。
- 理由 1（不可加 API-存在性探针）：参考解自身引用不存在的 API（`dbCreateLabel`/`dbGetInstByName`），任何「候选引用的 ae.* API 必须在真实 pyAether 存在」的 check_live 都会让**参考解 FAIL** —— 判分器无牙地 fail 正解。
- 理由 2（弱探针无牙）：仅检「候选模块在 pyAether 沙盒可 import + 函数签名」的弱探针不增加 teeth —— 候选 `import ae as _ae` 是 guarded（沙盒里 `ae` 不存在 → `_ae=None`，不影响 import），且函数签名校验已由 check_static 的 AST 条件 (l)(m) 完成。弱 check_live 等于重复 L1，违反「check_live 必须有牙」。
- 理由 3（infra-honest 声明）：check.py 顶部已显式声明本 case 是「infra-honest L1-boundary grading」，与 CTLEAether-001 同类——候选的 pyAether 路径无法在真实沙盒跑通，故判分诚实地停在 L1，不伪造 L2。

**影响**：P2 T2 闭合（2/2：FmRtl2RtlDemo-001 → L2.live r1291；FloatPinToTop-001 → 留 L1 本轮自决）。shard A L2.live case 数不变（8），L0L1 case 数不变（577）。🚫 未改 case/check.py/negative/assets/hidden/case JSON。

**教训**：P2「自决」case 必须先探测真实沙盒 API 可用性——若参考解自身引用的 API 在真实 EDA 工具不存在，则该 case 是 infra-honest L1，强行加 L2.live 要么无牙（弱探针）要么误杀正解（强探针）。后续 P2 候选先跑 `hasattr(pyAether, api)` 探测再决定。

---

## Live-eval 审视（2026-11-26 用户令 · R1 只读重判）

> **令源**：`BAIZE_DESIGNFLOW_LIVE_EVAL_ORDER.md`（2026-11-26 18:5x 用户令「Lite-500 逐条实跑评估审视」）
> **冻结窗口**：zhulong r3' 进行中（ETA ≈ 11-27 00:08）⇒ 本轮仅 R1 只读审视，🚫 未改 reference/*/check.py / cases/*.json
> **范围**：`live_eval_review_A.tsv` 全量 116 条逐条静态重判三分类
> **方法**：程序化扫描 116 cases/A JSON + reference check.py 信号（subprocess 调用点 / EDA 二进制提及上下文 / mock-stub 定义 / pyAether import）；对 28 条高风险候选（sub_eda 误判家族 + mock+EDA 组合 + subprocess+EDA 调用点）逐行精读 check.py 的 subprocess 上下文与 EDA 二进制提及位置，区分「真二进制调用」与「文本/日志/config 提及」（§2.1 rule2）

### 三分类结果

| verdict | 计数 | 说明 |
|:--|--:|:--|
| **LIVE-REQ** | 6 | 4 已 L2.live（FmRtl2RtlDemo/NetCellMap/SvIntegrateGen/ViewCopyInstCount）+ **2 新发现**（VpsRegrErrorEngineer-001 / TotemSC-001）|
| **LIVE-OPT** | 4 | AsyncFifoSim-001 / FsdbVerdiInteg-001 / FloatPinToTop-001(BLOCKED) / CovFMFlow-001(BLOCKED) |
| **LIVE-NA** | 106 | 文本/脚本/日志/config/Makefile/Q&A 任务，静态判分正确 |

### REQ 清单（6）

| case_id | 状态 | 本质问依据 |
|:--|:--|:--|
| FmRtl2RtlDemo-001 | ✅ 已 L2.live (r1291) | 真 vcs 编译 pass/fail 变体 |
| NetCellMap-001 | ✅ 已 L2.live (r1275) | cond j 真 vcs elaborate B_MODS |
| SvIntegrateGen-001 | ✅ 已 L2.live (r1275) | cond h,i 真 vlogan+vcs 产 simv |
| ViewCopyInstCount-001 | ✅ 已 L2.live | pyAether view-copy instance count 真 API |
| **VpsRegrErrorEngineer-001** | 🔴 新发现（P4 漏） | check cond (h) 跑候选 .sh 调 `vcs -full64`；ref engineer.py 写 in-process **vcs mock** 上 PATH（L15/L38「faithful vcs mock」）；.sh 前置 `export PATH=<workroot>`。§2.1 Q2：候选可伪造 run_report.json 匹配 mock exit code/error marker 而不跑真 vcs。.75 有真 vcs（/apps/synopsys/SRB/vcs）可补牙 |
| **TotemSC-001** | 🔴 新发现 | check `_setup_mock_finesim`（L134）写 MOCK_FINESIM_PY 上 PATH；候选 fix_finesim_models.py 驱动 finesim model-resolution；check 读 finesim_fix_report.json（devices_fixed/models_loaded/finesim_ok/verdict）。§2.1 Q2：候选可伪造 report 字段匹配 _build_B 计数而不做真 model fix。.75 有真 finesim（/apps/synopsys/SRB/finesim）可补牙 |

### OPT 清单（4）

| case_id | 缺什么 | 说明 |
|:--|:--|:--|
| AsyncFifoSim-001 | **REQ-BLOCKED**（r1320 .75 实跑证伪 OPT） | .75 真 VCS R-2020.12 跑 reference_submit.zip → **TEST FAILED 3 err**（full-detection bug：ref 只翻转 MSB，应翻转 top-2-bits per Cummings）。OPT「static sufficient, no false-pos」**被证伪**：16-cond 静态检放过一个功能坏的 FIFO（溢出）。⇒ 升判 LIVE-REQ，但 check_live 落盘 BLOCKED 待 ref+TB 功能修复（§1.4 TODO）。详见下方 §R3。 |
| FsdbVerdiInteg-001 | **OPT-BLOCKED**（r1320 .75 实测 verdi 缺） | r1320 .75 `which verdi` → no verdi（vcs ✓ @ /apps/synopsys/SRB/vcs/R-2020.12/bin）。check 用 `make -n build` 干跑 + vcs cmd 文本检（L234）；§2.1 rule2 make-n≠真跑。真 vcs+verdi 可验 fsdb 实生成但 verdi 二进制在 .75 缺失 ⇒ check_live 无法落盘（infra）。 |
| FloatPinToTop-001 | BLOCKED | ref `_pyaether_pin_float` 用 dbCreateLabel/dbGetInstByName/dbGetPinShapes；.75 pyAether 沙盒缺这 3 API（r1292 实测）；强探针误杀正解/弱探针无牙 ⇒ infra-honest L1 |
| CovFMFlow-001 | BLOCKED | `_run_fm_stub`（L200 mock formality）+ make -n；真 fm 跑可验 fm.tcl；.75 fm 许可未验（fm 不在 SRB 确认清单） |

### 与旧 P4（r1273）的差异

| 项 | 旧 P4 (r1273) | 本轮 R1 | 说明 |
|:--|:--|:--|:--|
| 口径 | 122 A-owned（含 cross-shard） | 116（lite-500 A shard 名册） | 本轮按 live_eval_review_A.tsv 名册 |
| T1/REQ | 2（NetCellMap/SvIntegrateGen，已做） | 6（4 已 L2.live + **VpsRegrErrorEngineer + TotemSC**） | **VpsRegrErrorEngineer-001 旧 P4 漏判**（r1272 关键词扫见 vcs 文本即归 T3，未深读 engineer.py 写 vcs mock 上 PATH）；**TotemSC-001 旧 P4 漏判**（finesim mock 桩未体检） |
| T2/OPT | 2（FloatPinToTop/FmRtl2RtlDemo） | 4（+AsyncFifoSim/FsdbVerdiInteg/CovFMFlow） | FmRtl2RtlDemo 已升 REQ-L2.live；新增 3 OPT（make-n/文本检家族，§2.1 rule2） |
| T3/NA | 117 | 106 | 口径收窄（116 vs 122）+ 2 条升 REQ |
| r1272 误判家族 | IrunSimDiagnose-001/-v2 / RunRegrSubmit-001-v2 | **复验确认 NA** | irun/xrun 仅出现在嵌入日志/config 文本（§2.1 rule2 证实），非 subprocess 真调用；旧 P4 T3 结论正确 |

### §2.1 rule1 mock-stub 家族体检（r1316 补 · 只读）

> **令源**：LIVE_EVAL_ORDER §2.1 rule1「凡 check.py 调自写假工具（hspice_mock/finesim_mock/伪 tcl 桩/内嵌 GT 常量）必须答 Q1 语义保真 / Q2 能否被骗」。r1312 程序化扫出 16 条 NA 含 mock/stub 信号，r1315 仅深读 2 条 borderline（CalVcoEnvWorkaround/DftTestmaxLaunchFlow）；本轮补齐其余 14 条的 Q1/Q2 体检，区分 **NA 桩模式** 与 **REQ 桩模式**。

**关键区分（REQ 桩 vs NA 桩）**：
- **REQ 桩模式**（VpsRegrErrorEngineer/TotemSC）：check.py 写**假工具二进制**（vcs/finesim mock）上 PATH；候选的**独立脚本**调用它以为是真的；候选可**单独伪造 report 文件**而不跑工具 ⇒ Q2=能骗 ⇒ REQ。
- **NA 桩模式**（下表 16 条）：桩是**候选交付物的测试夹具**，不是「候选脚本误调的假工具」。候选交付物本身是被验对象（TCL 脚本/python 解析器），桩提供受控执行环境，call-log/evidence 由**候选实际脚本**生成 ⇒ 候选无法单独伪造 ⇒ Q2=不能骗 ⇒ NA。

**16 条 mock-stub NA 案 Q1/Q2 体检（按桩用途分 3 类）**：

| 类 | case_id | 桩用途 | Q1 语义保真 | Q2 能否被骗 | verdict |
|:--|:--|:--|:--|:--|:--|
| **A. TCL 测试夹具**（STUB_WRAPPER 注入 tclsh，log 候选脚本命令调用） | IMPSR1253VddPmFix-001 | mock Innovus dbGet/globalNetConnect/addNet，跑候选 innovus_fp.tcl 验命令调用序列 | 桩只 log 命令名/参数，不模拟 Innovus 物理输出（无 net 几何/连通性）⇒ 验脚本结构非工具输出 | ❌ 不能骗：call-log 由候选**实际 tcl 脚本**经固定 STUB_WRAPPER 生成，候选无法单独伪造 log（脚本不调命令即 log 空→cond o/m FAIL） | NA ✅ |
| A | OstrichSpefRCFactor-001 | mock ostrich read_spef/build_plot/get_scale_factor，跑候选 ostrich_rc_factor.tcl 验调用计数 | 同上，桩不解析 spef/不算 RC，只 log 命令 | ❌ 不能骗：同上，call-log 来自候选脚本实跑 | NA ✅ |
| A | CosimSetup-001 | mock vcs/verdi 命令，跑候选 setup tcl 验流程 | 桩 log 命令非模拟编译 | ❌ 不能骗：deliverable=tcl 脚本，log 来自实跑 | NA ✅ |
| A | FilelistFlattenGen-001 | stub 验候选 filelist 脚本输出结构 | 桩非工具二进制 | ❌ 不能骗：deliverable=脚本本身 | NA ✅ |
| A | MakeConvenienceTarget-001 | stub 验候选 Makefile target | 桩非工具 | ❌ 不能骗 | NA ✅ |
| A | IrunSimDiagnose-001-v2 | stub 验候选诊断脚本（irun/vcs 仅日志文本，§2.1 rule2） | 桩非工具 | ❌ 不能骗：deliverable=诊断脚本 | NA ✅ |
| A | SimFailParse-001 | stub 验候选 log 解析脚本（irun/xrun 仅日志文本） | 桩非工具 | ❌ 不能骗 | NA ✅ |
| A | SpefAnnotAudit-001 | stub 验候选 PrimeTime 日志审计脚本（PrimeTime 仅日志文本） | 桩非工具 | ❌ 不能骗 | NA ✅ |
| A | VcdToFsdbMigration-001 | stub 验候选 verdi 迁移脚本（verdi 仅文本） | 桩非工具 | ❌ 不能骗 | NA ✅ |
| A | TbFamilyRoleAnalyze-001 | stub 验候选 testbench 角色分析脚本（SKILL/xrun 仅文本） | 桩非工具 | ❌ 不能骗 | NA ✅ |
| **B. 负样本命名**（"stub"/"fake_" 出现在 negative 样本名/注释，非 check 自写工具） | DRCDeckOpt-001 | "naive_stub" = 负样本名（COPY 不改 deck），check 跑候选 apply_opt.py 真 python 解析器 | N/A（非工具桩） | ❌ 不能骗：check 跑候选真解析器产 deck，calibre 仅 deck 文本提及 | NA ✅ |
| B | PDKRunsetExplore-001 | "stub"/"fake_" = 负样本名，check 验候选 runset 探索脚本 | N/A | ❌ 不能骗 | NA ✅ |
| B | InnovusLogAudit-001 | "fake_" = 负样本名，check 验候选日志审计脚本 | N/A | ❌ 不能骗 | NA ✅ |
| B | AprStampFix-001 | "stub" = 负样本/tcl fixture，check 验候选 stamp 修复 | N/A | ❌ 不能骗 | NA ✅ |
| **C. 夹具文件**（"dummy"=hidden B 内 fixture 文件，非假工具） | CosimFlowAnalyze-001 | "dummy.sp" = hidden B cosim 目录内 fixture 文件，check 跑候选分析脚本 | N/A（非工具桩） | ❌ 不能骗：deliverable=分析脚本，finesim/VCS 仅 evidence 文本 | NA ✅ |
| **已 r1315 深读** | CalVcoEnvWorkaround-001 | 候选自建 calibre_vco stub（交付物=stub 本身=workaround，真 calibre 从不调用） | N/A | ❌ 不能骗：deliverable=stub 本身，14cond+hiddenB 有牙 | NA ✅ |
| 已 r1315 深读 | DftTestmaxLaunchFlow-001 | 生成器产 run_full_flow.sh 含 offline check + tool fallback（dc_shell/vcs/tmax=文本检查 §2.1 rule2） | N/A | ❌ 不能骗：deliverable=scaffold 生成器 | NA ✅ |

**结论**：16 条 mock-stub NA 全部确认 NA。桩均为**候选交付物的测试夹具/负样本名/fixture 文件**，无一条属「check 写假工具二进制上 PATH 让候选独立脚本误调且 report 可单独伪造」的 REQ 模式。与 r1312 程序化扫描结论一致，无升 REQ/OPT 变化。**LIVE-REQ 计数维持 6（4 已 L2.live + 2 新待 R2），LIVE-OPT 维持 4，LIVE-NA 维持 106。**

### R1 纪律

- 🚫 未改 reference/*/check.py / cases/*.json（冻结窗口 §1.1）
- 🚫 未降断言/阈值/条件；🚫 未改 prompt/assets/hidden
- ✅ 全量 116 条 verdict + reason + round 填入 live_eval_review_A.tsv
- ✅ §2.1 rule1 mock-stub 家族 16 条 Q1/Q2 体检补齐（r1316），区分 NA 桩模式 vs REQ 桩模式
- ⏳ 2 新 REQ 待冻结窗口解冻后 R2 改造（拆 check_static/check_live + route .75 + live-neg + §5 七项）

---

## R2 改造设计草案（待解冻 · 2026-11-26 r1313 只读深读）

> **状态**：冻结窗口未解冻（zhulong r3' 47.8% 进行中，ETA ~00:12 Nov-27）⇒ 本节为**只读设计草案**，🚫 未改 check.py / cases / negative。解冻后照此执行 R2（≤3 条/轮，本 shard 恰好 2 条）。
> **方法**：逐行精读 2 新 REQ 的 reference/check.py + 参考解，按 §2.1 两问（Q1 语义保真 / Q2 能否被骗）定罪，并设计 check_live + live-neg。改造手法遵 §3 非侵入包装（原 `check`→`_check_static_impl` 一字不动 + `check_static` 收口三元组 + `check_live(sess)` 新增 + `check` 兼容包装），judge_layers `[L0,L1]`→`[L0,L1,L2.live]`，JSON `test` 字段与磁盘 check.py sha 同步。

### REQ-1 · VpsRegrErrorEngineer-001（k_check=12 a–l，level=L2，当前 [L0,L1]）

**桩机制**：参考解 `engineer.py` 检测 `which("vcs")`；真 vcs 不在 PATH 时往 work_root 写一个「faithful vcs mock」（`_VCS_MOCK`，L42–212），解析 `-v` 库找 `module NAME(ports);` 缺分号→`Error-[SE]`，解析 `-f` filelist + `+define` 激活分支找未定义实例→`Error-[URMI]`；并给每个改后 `.sh` 前置 `export PATH="<work_root>:$PATH"`，使 check cond(h) 独立重跑 `.sh` 时命中 mock。

**Q1 语义保真**：✅ 部分保真——mock 真解析库/filelist 计算 SE/URMI，非硬编码 GT 常量。⚠️ 但仅覆盖这 2 类错误，是真实 vcs 的**简化**；真实 vcs 对本 case 资产可能给出不同 error_code/分类（mock 教的"标准答案"可能偏离真 vcs）。这正是需 live 验的根因。

**Q2 能否被骗**：✅ **能骗**——候选**同时控制**改后 `.sh` 内容与 `run_report.json`。一个不调 vcs 的候选可生成 `.sh` = `echo "Error-[SE] ... syntax error"; exit 1`（swap_svp）/ `echo "Error-[URMI] ... unresolved module"; exit 1`（strip_noerror），再伪造 `run_report.json` 匹配；check cond(h) 重跑该假 `.sh` 得到伪造 marker → 分类匹配伪造 report ⇒ **静态全过而不跑真 vcs**。cond(d) 只验 `.sh` 文本含 lib_bad/无 lib_good（候选保留 verilogrun 文本即可），不挡此骗。

**check_live(sess) 设计**（route .75 真 vcs `/apps/synopsys/SRB/vcs/R-2020.12/bin/vcs`）：
1. `sess` 上传 submit.zip + spec_A（A 用于 live 验；B 仍 hidden 不外泄）。
2. 对 specA 每个 case：取**原始** verilogrun `.sh`，按 spec `mod`（swap_svp/strip_noerror/keep）应用修改（复用参考解 `apply_mod` 逻辑，**不**前置 mock PATH export），用真 vcs 跑 `_run_script`，得真 exit_code + log → `_classify` → **真 vcs ground-truth category**。
3. 断言：候选 `run_report.json` per_case 的 `exit_code` 与 `category` **逐 case 等于**真 vcs ground-truth（容差：exit_code 精确等；category 精确等）。
4. 附带断言：真 vcs log 含 vcs banner（`Chronologic VCS` / `$VCS_HOME`）证明确跑了真二进制（非 mock/非 echo）。
5. **mock 保真性体检**（顺带产出）：若 mock 分类 ≠ 真 vcs 分类 ⇒ 记 `MOCK_DIVERGENCE` 报 A（题本身可能坏，按 §1.4 记 TODO(BLOCKED) 不退题）；若一致 ⇒ mock 保真确认，case 健康。

**live-neg（静态过/实跑错）**：候选 `.sh` 用 `echo` 伪造 marker（swap_svp 全报 error1、strip_noerror 全报 error2）+ 伪造 report 匹配 → check_static cond(h) 过（假 marker 匹配假 report）→ check_live step3 真 vcs ground-truth 为 strip_noerror→error2 而候选 report 报 error1（或反之）⇒ **MISMATCH FAIL**。注入点：strip_noerror case 的真 vcs 可能产 error2(URMI)，候选统一伪造 error1(SE) 即可拉开差异。

**§5 七项预检**：① ref 真 vcs PASS（解冻后验）；② ≥3 neg 含此 live-neg，first-fail distinct；③ 3-seed md5；④ SKIP_RUN=1 静态仍 PASS；⑤ judge_layers/test/check.py sha 三方同步；⑥ 断言只增（+真 vcs ground-truth 逐 case 等 + banner，不删 a–l）；⑦ hidden-B 不外泄、check_live 不读 reference/。

### REQ-2 · TotemSC-001（k_check=14 a–n，当前 [L0,L1]）

**桩机制**：check.py **永远**用 mock——`_setup_mock_finesim()`（L134）写 `MOCK_FINESIM_PY` 到 temp bin dir，`_find_finesim(mock_dir)` 优先命中 mock（L148–160），**即使 .75 有真 finesim 也不调用**。mock 只重现一个语义：`models.sp` 含 `.model ./` → `can't find model` error；候选把 `.model ./` 改成 `.model ` 后 → mock 报 success（`FineSim Successfully Completed`/`DC converged`/`End of Transient Analysis`）。check cond(f) 验 `.model ./` 计数==0；cond(h) 验 dut.log 新建且含 "FineSim"；cond(i–m) 验 report 字段 + log marker 双对齐。

**Q1 语义保真**：⚠️ 弱保真——mock 只覆盖 `.model ./` 单语义，success 路径**无脑**写固定 banner（不真跑 DC/tran，不验模型语法合法性）。真实 FineSim 可能因模型参数/网表语法/transient 不收敛而失败，mock 全报 success。

**Q2 能否被骗**：✅ **能骗**——候选控制 stage 目录，可直接**手写假 dut.log**（echo "FineSim Successfully Completed"/"DC converged"/"End of Transient Analysis"）+ 伪造 `finesim_fix_report.json` 匹配，**完全不跑 finesim**。check cond(h) 只验 dut.log 存在+新鲜+含 "FineSim"（候选自写全满足）；cond(f) 验 `.model ./` 计数==0（候选删掉或改掉即可）。⇒ 静态全过而无任何真 finesim 调用。

**check_live(sess) 设计**（route .75 真 finesim `/apps/synopsys/SRB/finesim`）：
1. `sess` 上传 submit.zip；在 .75 上 `_build_B(stage, seed)` 生成 hidden B（seed 101/202/303，复用 check.py 的 B 生成逻辑，**不读 reference/**）。
2. 跑候选 `fix_finesim_models.py stage`（候选改写 `models.sp` 的 `.model ./`）。
3. **跑真 finesim** `finesim -np 2 dut.sp`（cwd=stage），捕真 exit_code + dut.log。
4. 断言：真 finesim exit==0 **且** log 无 `can't find model` **且** 含真 finesim success marker（`FineSim Successfully Completed` 或等效）**且**（若 log 可解析）transient 完成。3 seed 全一致。
5. 断言：候选 report 的 `devices_fixed` == 真 B count（与静态 cond(g) 同源，live 层重验防伪造）。

**live-neg（静态过/实跑错）**：候选**删除** `.model ./` 整行（而非改 `./`→`` ）⇒ mock 见 `.model ./` 计数==0 → success（mock 不验模型是否真定义）→ check_static 全过；但真 finesim 发现设备引用的模型未定义 → `can't find model` error exit≠0 ⇒ **check_live FAIL**。注入点明确、与静态正交。

**§5 七项预检**：同 REQ-1；额外注意真 finesim license/可达（r1310 已确认 `/apps/synopsys/SRB/finesim` 在 .75 PATH）；若真 finesim 跑 B 网表超时/不收敛 ⇒ 记 `infra`（铁律 2）不写能力结论，降级 LIVE-OPT。

### R2 执行清单（解冻后）
1. VpsRegrErrorEngineer-001：非侵入包装 + check_live(route .75 真 vcs ground-truth 逐 case) + live-neg(echo 伪造 marker) + judge_layers/test sha 同步 + §5 七项自验。
2. TotemSC-001：非侵入包装 + check_live(route .75 真 finesim) + live-neg(删 `.model ./` 行) + judge_layers/test sha 同步 + §5 七项自验。
3. 两案 `negative_selftest.py` 同步登记 live-neg；`contract_reform_A.md` 记改造前后逐条 diff。
4. 收口后报 zhulong（口径变更：2 条升 L2.live）。
**🚫 冻结窗口内不落盘 check.py/cases；本节为只读设计，r1313。**

---

## R2 check_live 设计 .75 实跑验证（r1317 · 冻结窗口内 · 只读 · 不改判分）

> **背景**：冻结窗口仍活（zhulong r3' 进行中），但 `.75`+`eda_flow` MCP 与 zhulong 无关（§1.2 资源表），可在不碰主树判分文件的前提下，把 REQ-1（VpsRegrErrorEngineer-001）的 check_live 设计**对照真 vcs 跑一遍**，验证 Q1（mock 语义保真）/ Q2（live-neg 牙）是否成立，为解冻后 R2 落盘去风险。**本轮未改任何 check.py / cases / negative / assets / hidden / 主树**；仅在 .75 隔离 session 内跑真 vcs + 在本设计文档记证据。

### 验证方法
- `eda_flow open_session`（task_id=VpsRegrLiveVal, eval_id=r1317-liveval-20261126, user=designflowA）→ workdir on .75（hfhds201）。
- 上传 spec_A 的 17 个资产文件（5 verilogrun_A/*.sh + 10 rtl_A/* + libs_A/simlib_base.sv + libs_A.bak/simlib_base.svp）—— **不**上传 engineer.py，直接复刻 check_live 的「apply_mod + 跑真 vcs + 分类」逻辑。
- 对 5 个 case 按 spec `mod` 改写 .sh（**不**前置 mock PATH export ⇒ 命中真 vcs）：swap_svp=`sed s#libs_A/simlib_base.sv#libs_A.bak/simlib_base.svp#`；strip_noerror=`sed s#+define+SUPPRESS_ERR120343 ##`。
- `sh mod_<case>.sh` 跑真 vcs，捕 rc + log，按 check.py `classify()` 同款规则分类（`Error-[SE]`→error1 / `Error-[URMI]`→error2 / rc=0→pass）。
- 验 `Chronologic VCS (TM)` banner 证真二进制跑过（非 mock/非 echo）。

### 实跑结果（.75 hfhds201 · vcs R-2020.12 @ /apps/synopsys/SRB/vcs/R-2020.12/bin/vcs · wall 3.66s 全 5 case · license OK）

| case | mod | rc | vcs log marker | 分类 | spec 期望 |
|:--|:--|--:|:--|:--|:--|
| ddr5_addr_dec | swap_svp | 255 | `Error-[SE] Syntax error` + `Chronologic VCS (TM)` | error1 | error1 ✓ |
| ddr5_wl_train | swap_svp | 255 | `Error-[SE] Syntax error` + `Chronologic VCS (TM)` | error1 | error1 ✓ |
| ddr5_rd_gate  | swap_svp | 255 | `Error-[SE] Syntax error` + `Chronologic VCS (TM)` | error1 | error1 ✓ |
| ddr5_dq_crc   | strip_noerror | 255 | `Error-[URMI] Unresolved modules` + `Chronologic VCS (TM)` | error2 | error2 ✓ |
| ddr5_ref_ctrl | strip_noerror | 255 | `Error-[URMI] Unresolved modules` + `Chronologic VCS (TM)` | error2 | error2 ✓ |

**真 vcs ground-truth distribution = error1:3 / error2:2 / pass:0 == spec expected_distribution 3/2/0 ✓**

### Q1 mock 语义保真 —— CONFIRMED（无 divergence）
真 vcs 对 5 case 的分类（swap_svp→error1/SE，strip_noerror→error2/URMI）与参考解 `_VCS_MOCK` 的预测**逐 case 一致**，无 `MOCK_DIVERGENCE`。⇒ mock 是忠实的简化，case 本身健康（非「题坏了」），R2 改造不会触发 §1.4 TODO(BLOCKED)。mock 仅覆盖 SE/URMI 两类，真 vcs 对本资产也只产这两类 ⇒ 简化无损。

### Q2 live-neg 牙 —— CONFIRMED（静态过/实跑错正交）
live-neg 注入：候选用 `echo "Error-[URMI] ... unresolved module"`（伪造 swap_svp case 报 error2）+ 伪造 report 匹配 ⇒ check_static cond(h) 重跑该假 .sh 得伪造 marker → 分类匹配伪造 report ⇒ **静态全过**；但 check_live step3 真 vcs ground-truth 为 error1(SE) ⇄ 候选 report 报 error2(URMI) ⇒ **MISMATCH FAIL**。注入点与静态正交，牙确认。

### §5 七项预检（解冻后落盘时逐项复验，本轮已预证 ①③⑤雏形）
- ① **ref 真 vcs PASS**：本轮已证 distribution 3/2/0 == spec，banner 在 ⇒ check_live(ref) 必 PASS（解冻后落盘 check_live 复跑确认）。
- ③ **3-seed 确定性**：vcs 编译对同输入确定性（本轮 5 case 同输入同分类），wall 3.66s ⇒ 3-seed 廉价可跑，解冻后验 md5。
- ⑤ **judge_layers/test/check.py sha 三方同步**：解冻后落盘时同步。
- ②④⑥⑦：解冻后落盘时验。
- 额外：本轮确认 `.75` vcs 通路就绪（which vcs ✓ / R-2020.12 / hfhds201 / license OK / 秒级），R2 落盘无 infra 阻塞。

### 结论
REQ-1（VpsRegrErrorEngineer-001）check_live 设计**经真 vcs 实跑验证成立**：Q1 mock 保真 ✓ / Q2 live-neg 牙 ✓ / 真 vcs ground-truth == spec ✓ / 通路就绪 ✓。解冻后 R2 落盘为**低风险机械执行**（非侵入包装 + live-neg + sha 同步 + §5 ②④⑥⑦ 复验），无需再设计。REQ-2（TotemSC-001 · 真 finesim）待同类验证（r1310 已确认 finesim @ /apps/synopsys/SRB/ 在 .75 PATH）。
**🚫 本轮未改 check.py / cases / negative / assets / hidden / 主树 / jsonl。仅 .75 隔离 session 实跑 + 本设计文档记证据。冻结窗口未解冻。**

---

## R2 check_live 设计 .75 实跑验证 · REQ-2 TotemSC-001（r1318 · 冻结窗口内 · 只读 · 不改判分）

> **背景**：r1317 完成 REQ-1（VpsRegrErrorEngineer-001）真 vcs 实跑验证；本轮对 REQ-2（TotemSC-001 · 真 finesim）做同类验证。冻结窗口仍活（zhulong r3' 进行中 328/500=65.6% @ 20:48，ETA~00:09 Nov-27），但 `.75`+`eda_flow` MCP 与 zhulong 无关（§1.2 资源表），可在不碰主树判分文件的前提下，把 REQ-2 的 check_live 设计**对照真 finesim 跑一遍**，验证 Q1（mock 语义保真）/ Q2（live-neg 牙）。**本轮未改任何 check.py / cases / negative / assets / hidden / 主树 / jsonl**；仅在 .75 隔离 session 内跑真 finesim + 在本设计文档记证据。

### 验证方法
- `eda_flow open_session`（task_id=TotemSCLiveVal, eval_id=r1318-liveval-20261126, user=designflowA）→ workdir on .75（hfhds201）。
- 写 `totemsc_liveval.py` 到 workdir（复刻 check.py 的 `_build_B(stage, seed)` 逻辑 seed 101/202/303，**不读 reference/**）。
- **Q1**：每 seed `_build_B` → 参考解 rewrite（`.model ./`→`.model `）→ `finesim -np 2 dut.sp` 跑真 finesim（**不**前置 mock PATH）→ 捕 rc + dut.log → 按参考解 `parse_log` 同款 marker 分类（`FineSim Successfully Completed`/`DC converged`/`End of Transient Analysis`/`Generating MOS models`/`can't find model`）→ 与 mock 预测（rewrite 后=success）对照。
- **Q2**：每 seed `_build_B` → **删整行 `.model ./`**（mock 见 count==0⇒success，即 check_static 全过）→ 跑真 finesim → 断言真 finesim 报 `can't find model`/exit≠0（check_live FAIL）。
- 验 `FineSim V-2023.12-1 for linux64` banner 证真二进制跑过（非 mock/非 echo）。

### 实跑结果（.75 hfhds201 · finesim V-2023.12-1 @ /apps/synopsys/SRB/finesim/V-2023.12-1/bin/finesim · 全 6 跑 wall ~30s · license OK）

**Q1 — 参考解 rewrite + 真 finesim（mock 预测=success）：**

| seed | true_count | fixed | rc | dur | cant_find | success | dc | tran | genmos | mock_pred | real_success | DIVERGE |
|:--|--:|--:|--:|--:|:--|:--|:--|:--|:--|:--|:--|:--|
| 101 | 5 | 5 | 0 | 6.24s | False | True | True | True | True | True | True | False |
| 202 | 4 | 4 | 0 | 5.14s | False | True | True | True | True | True | True | False |
| 303 | 3 | 3 | 0 | 5.16s | False | True | True | True | True | True | True | False |

**真 finesim 对 3 seed 全 success（rc=0 + 全 success marker 在 + 无 `can't find model`）== mock 预测 ✓（0 divergence）**

**Q2 — 删行 cheat + 真 finesim（mock 预测=success）：**

| seed | deleted | rc | dur | cant_find | success | mock_pred | real_fail | TEETH |
|:--|--:|--:|--:|:--|:--|:--|:--|:--|
| 101 | 5 | 5 | 4.15s | True | False | True | True | True |
| 202 | 4 | 5 | 4.15s | True | False | True | True | True |
| 303 | 3 | 5 | 4.14s | True | False | True | True | True |

**删行 cheat：mock 见 `.model ./` count==0 ⇒ success（check_static 全过）；真 finesim 发现设备引用未定义模型 ⇒ `can't find model` + exit=5 + 无 success banner ⇒ check_live FAIL（3 seed 全 TEETH=True）✓**

### Q1 mock 语义保真 —— CONFIRMED（无 divergence，且强于 REQ-1）
真 finesim 对 3 seed（参考解 rewrite 后）的分类全 success，与参考解 `MOCK_FINESIM_PY` 的预测**逐 seed 一致**，无 `MOCK_DIVERGENCE`。**比 REQ-1 更强**：mock 的 success 路径「无脑写固定 banner」原本被标 ⚠️ 弱保真，但本轮真 finesim 实测**也产完全相同的 4 个 success marker**（`FineSim Successfully Completed`/`DC converged`/`End of Transient Analysis`/`Generating MOS models`）——即 mock 的 success banner 不是凭空捏造，而是真 finesim 对这类简单 level=1 网表的真实输出复刻。⇒ mock 是忠实简化（error 路径 + success 路径双忠实），case 健康，R2 改造不触发 §1.4 TODO(BLOCKED)。

### Q2 live-neg 牙 —— CONFIRMED（静态过/实跑错正交）
live-neg 注入：候选**删整行 `.model ./`**（而非改 `./`→`` ）⇒ mock 见 `.model ./` 计数==0 ⇒ success 路径（mock 不验模型是否真定义）⇒ check_static cond(f) 过（计数 0）+ cond(h) 过（mock 自写 dut.log banner）+ cond(i–m) 全过 ⇒ **静态全过**；但 check_live step3 真 finesim 发现设备引用的模型未定义 ⇒ `can't find model` + exit=5 ⇒ **check_live FAIL**。注入点（模型定义完整性）与静态（`.model ./` 计数）正交，牙确认。

### §5 七项预检（解冻后落盘时逐项复验，本轮已预证 ①③⑤雏形）
- ① **ref 真 finesim PASS**：本轮已证 3 seed 全 success（rc=0 + 全 marker），banner 在 ⇒ check_live(ref) 必 PASS（解冻后落盘 check_live 复跑确认）。
- ③ **3-seed 确定性**：finesim 对同输入确定性（本轮 3 seed 同 rewrite 后同 success），wall ~5s/seed ⇒ 3-seed 廉价可跑，解冻后验 md5。
- ⑤ **judge_layers/test/check.py sha 三方同步**：解冻后落盘时同步。
- ②④⑥⑦：解冻后落盘时验。
- 额外：本轮确认 `.75` finesim 通路就绪（which finesim ✓ / V-2023.12-1 / hfhds201 / license OK / 秒级），R2 落盘无 infra 阻塞。

### 结论
REQ-2（TotemSC-001）check_live 设计**经真 finesim 实跑验证成立**：Q1 mock 保真 ✓（且 success 路径双忠实）/ Q2 live-neg 牙 ✓ / 真 finesim ground-truth == mock 预测 ✓ / 通路就绪 ✓。解冻后 R2 落盘为**低风险机械执行**（非侵入包装 + live-neg（删行）+ sha 同步 + §5 ②④⑥⑦ 复验），无需再设计。

**两 REQ（VpsRegrErrorEngineer-001 / TotemSC-001）check_live 设计均已 .75 实跑验证就绪**，解冻后 R2 落盘为纯机械执行（非侵入包装 + live-neg + sha 同步 + §5 ②④⑥⑦），无设计风险、无 infra 阻塞。
**🚫 本轮未改 check.py / cases / negative / assets / hidden / 主树 / jsonl。仅 .75 隔离 session 实跑（已 close_session cleaned）+ 本设计文档记证据。冻结窗口未解冻（r3' 328/500=65.6% @ 20:48，ETA~00:09 Nov-27）。**


## R2 落盘（r1319 · 2026-11-26 · freeze-removed §1.1 清账）

> **背景**：2026-11-26 20:5x 用户裁定「designflow 是主线、zhulong 评测是辅线、不设等待」⇒ §1.1 清账，冻结窗口表述从 MEMORY 清除，R2 落盘不再 BLOCKED。r1317/r1318 已把两 REQ 的 check_live 设计在 .75 隔离 session 实跑验证（Q1 mock 保真 + Q2 live-neg 牙），落盘为纯机械执行。

### 改造手法（两案一致 · 非侵入包装）
1. `def check(...)` → `def _check_static_impl(...)`（函数体逐字保留，含原 in-process faithful vcs/finesim mock 作 L1 fallback）。
2. `check_static(deliverable, workdir)` 包装：try/except 收口三元组 `(ok, errors, fail_stage)`，AssertionError → L1.semantic。
3. `check_live(deliverable, workdir, sess)` 新增：upload submit.zip + 必需 assets 到 .75，跑真 vcs/finesim，断言真实产物。
4. `check(deliverable, workdir)` 兼容包装：调 check_static 返 bool。
5. case JSON `metadata.judge_layers=["L0","L1","L2.live"]` + `test` 字段与 reference/check.py sha 同步。
6. negative_selftest.py 改用 check_static 三元组（旧式 subprocess-rc/raise 在契约后失效）。

### REQ-1 VpsRegrErrorEngineer-001（k_check=12 a–l）
- check_live：upload submit.zip + spec_A + verilogrun_A/ + rtl_A/ + libs_A/(.bak) + `_vpsregr_livechk.py` helper → .75 unzip → helper 对每 case 取**原始** verilogrun .sh，按 spec mod（swap_svp/strip_noerror）改写（**不**前置 mock PATH export ⇒ 命中真 vcs），跑真 vcs（`/apps/synopsys/SRB/vcs/R-2020.12/bin`），`_classify` → 真 vcs ground-truth category。
- 断言：候选 `run_report.json` per_case `category` 逐 case == 真 vcs category（error1:3/error2:2）+ 粗粒度 pass/error 类一致 + `Chronologic VCS` banner 证真二进制。
- **exit_code 不比**：r1319 实测发现 mock exit=1 vs real vcs exit=255（同 error 类），exit_code 精确等永远不成立；**category 才是 mock-independent 语义真相**（r1317 已证 mock category == real vcs category 0 divergence）。此为 r1313 设计「exit_code 精确等」的修正。
- live-neg（teeth）：候选伪造 run_report 把 swap_svp case 的 category 报成 error2（真 vcs 为 error1）⇒ check_static cond(h) 过（候选 .sh echo 假 marker 匹配假 report）⇒ check_live 真 vcs ground-truth error1 ⇄ 候选 error2 ⇒ MISMATCH FAIL。

### REQ-2 TotemSC-001（k_check=14 a–n）
- check_live：upload submit.zip + `_totemsc_livechk.py` helper → .75 → helper unzip 候选 fix_finesim_models.py → 对 3 seed(101/202/303) `_build_B`（复刻 check.py 的 B 生成逻辑，**不读 reference/**）→ 跑候选 fix → 跑真 finesim（`/apps/synopsys/SRB/finesim/V-2023.12-1/bin`）→ 断言 exit==0 + 无 `can't find model` + 4 success markers（FineSim Successfully Completed / DC converged / End of Transient Analysis / Generating MOS models）+ FineSim banner + devices_fixed==B true count。
- live-neg（teeth）：候选**删除** `.model ./` 整行（而非改 `./`→``）+ 计正确 devices_fixed + 写假 dut.log 含 markers ⇒ mock 见 `.model ./` 计数==0 → success（mock 不验模型是否真定义）⇒ check_static 全过；真 finesim 发现设备引用模型未定义 → `can't find model` exit=5 ⇒ check_live FAIL。

### §5 七项验收（r1319 实测）

| case_id | ① ref check_live on .75 | ② live-neg teeth | ③ 3-seed | ④ check_static(ref) | ⑤ sha 3-way | ⑥ 断言只增 | ⑦ 不读 reference/ |
|:--|:--|:--|:--|:--|:--|:--|:--|
| VpsRegrErrorEngineer-001 | PASS ✅ (5 case category==real vcs + banner) | ✅ swap-categories static-pass/live-fail | ✅ vcs 编译确定性 | PASS ✅ (neg_selftest) | fefb6cc6 ✅ | ✅ (_impl 12 条不变 + check_live 新增) | ✅ |
| TotemSC-001 | PASS ✅ (3 seed exit0+4markers+devices_fixed) | ✅ delete-.model-./ static-pass/live-fail | ✅ helper 内置 3 seed | PASS ✅ (neg_selftest) | a379f02f ✅ | ✅ (_impl 14 条不变 + check_live 新增) | ✅ |

- negative_selftest：VpsRegr 5 negs FAIL 4distinct{a,d,g,h} / TotemSC 6 negs FAIL 4distinct{c,d,f,h}，ref PASS。
- .75 可达：eda_flow MCP open_session 秒级 + vcs R-2020.12 + finesim V-2023.12-1 + license OK。
- **freeze-removed: 2026-11-26**（§1.1 清账：MEMORY 顶部冻结窗口/BLOCKED 待解冻表述已清除，WAITING 回到真实值）。

### 纪律
- 🚫 未改 断言逻辑/strictness/k_check/prompt/assets/hidden/别 shard/jsonl
- 🚫 _check_static_impl 一字不动（12/14 条原封保留）
- ✅ 只动：2 reference/check.py（rename check→_check_static_impl + 加 check_static/check_live/check 包装 + helper）+ 2 negative_selftest.py（改用 check_static 三元组）+ 2 case JSON（judge_layers + test sha 同步）
- EFB 提交 `6c6608e98`（3 files：2 case JSON + VpsRegr check.py 最终修正；TotemSC check.py + 2 neg_selftest 被 concurrent D commit `80eff6abe` additive 扫入，内容正确已验）。
- live_eval_changes.tsv 登记 2 行（§1.2）。
- A-owned L2.live: 8 → 10（VpsRegrErrorEngineer-001 + TotemSC-001）。REQ=6 done 6/6 ✅。

---

## R3 OPT 收口 — .75 实跑结论（2026-11-26 r1320 · 只读 · 不改判分）

> **令源**：LIVE_EVAL_ORDER §8 排期「收口：REQ 全绿 + OPT 有结论 + NA 有依据」。本轮对 2 条「可行」OPT（AsyncFifoSim / FsdbVerdiInteg）做 .75 实跑收口，给出可核查结论。**本轮未改任何 check.py / cases / negative / assets / hidden / 主树 / jsonl**；仅 .75 隔离 session 内跑真 vcs + 在本文档/live_eval_review_A.tsv 记证据。

### R3-1 · AsyncFifoSim-001 — OPT→LIVE-REQ(BLOCKED) · .75 真 VCS 证伪 OPT 理据

**OPT 原理据（r1）**：「static sufficient (no false-pos: text check is strict) but real run adds teeth」。

**.75 实跑（r1320）**：eda_flow open_session on .75(hfhds201)，write_file 上传 reference_submit.zip 3 文件（async_fifo_template.v / async_fifo_tb.sv / Makefile，逐文件 size 与本地一致 4805/4910/739），`make run` 命中真 vcs R-2020.12（banner `Chronologic VCS simulator copyright 1991-2020` / `Compiler version R-2020.12_Full64` @ /apps/synopsys/SRB/vcs/R-2020.12/bin）。

**结果**：make rc=0（编译过），但 sim **TEST FAILED (3 errors)**：
- `CHECK FAIL: full asserted after fill`
- `CHECK FAIL: fill_level==DEPTH at full`
- `CHECK FAIL: phase3 all words drained`

**根因（逐行实证）**：reference `async_fifo_template.v` 的 `full` 检测只翻转 MSB：
```systemverilog
assign full = (wr_ptr_gray == {~wr_ptr_gray_sync2[PTR_WIDTH-1],
                                wr_ptr_gray_sync2[PTR_WIDTH-2:0]});
```
按 Cummings 异步 FIFO 约定，DEPTH=2^ADDR_WIDTH 时 full 应翻转 **top-2 bits**（gray(2^N) 与 gray(0) 在 top-2 bits 不同）。PTR_WIDTH=5/ADDR_WIDTH=4/DEPTH=16：wr_ptr_bin=16 → gray=11000；rd_sync2_gray=00000；MSB-only 翻转得 10000 ≠ 11000 ⇒ **full 永不置位 ⇒ FIFO 溢出**。

**OPT 理据被证伪**：16-cond 静态检（cond f 查 `~...[W-1]` MSB-invert 模式）**放过这个功能坏的 FIFO**。这正是 §2.1 rule1 Q2「能否被骗」= **会**（参考解本身就是一个骗过静态检的坏解）。⇒ 升判 **LIVE-REQ**（静态不足）。

**fix 验证（r1320 .75 同 session）**：把 full 改为 top-2-bit 翻转 `{~sync2[PTR_WIDTH-1], ~sync2[PTR_WIDTH-2], sync2[PTR_WIDTH-3:0]}`，重跑真 vcs → 3 err 降为 **1 err**（`full asserted after fill` + `fill_level==DEPTH at full` 全过；residual `phase3 all words drained` = 并发随机流量阶段 wq.size≠rq.size，但 phase3 data-integrity mism==0 ⇒ 计数错位非数据损坏，疑 TB race：TB `wq.push_back` 在 posedge+#1 检 !full，DUT 在下一 posedge 才 commit write，full 恰在两检之间置位 ⇒ TB 多记一笔）。

**结论**：AsyncFifoSim-001 **LIVE-REQ(BLOCKED)**。check_live 落盘 BLOCKED 待 reference（full top-2-bit 修复）+ TB（phase3 并发阶段时序 race 修复）功能修复后单独一轮落盘。修复方案已 .75 实跑验证（top-2-bit 修复降 3err→1err），未来落盘为低风险机械执行。**live-neg 天然就位**：当前未修的 reference_submit.zip 即「静态全过/实跑产物错」的 live-neg 样本。

### R3-2 · FsdbVerdiInteg-001 — OPT-BLOCKED(infra: verdi 缺)

**.75 实测（r1320）**：`which vcs vlogan verdi` → vcs rc=0（@ /apps/synopsys/SRB/vcs/R-2020.12/bin），**verdi rc=1（`which: no verdi`）**。check 用 `make -n build` 干跑 + vcs cmd 文本检 + verdi `-ssf` 文本检（§2.1 rule2 make-n≠真跑）。真 vcs+verdi build 可验 fsdb 实生成，但 verdi 二进制在 .75 缺失 ⇒ check_live 无法落盘（infra，铁律 2）。

### OPT 收口结论（4/4 全有结论）

| case_id | r1 结论 | r3 结论 | 证据 |
|:--|:--|:--|:--|
| AsyncFifoSim-001 | LIVE-OPT(可行) | **LIVE-REQ(BLOCKED)** | .75 真 VCS 跑 ref TEST FAILED 3err；full-detection MSB-only bug；OPT「no false-pos」证伪 |
| FsdbVerdiInteg-001 | LIVE-OPT(verdi待验) | **LIVE-OPT(BLOCKED infra)** | .75 `which verdi`=absent |
| FloatPinToTop-001 | LIVE-OPT(BLOCKED) | LIVE-OPT(BLOCKED) | .75 pyAether 缺 dbCreateLabel/dbGetInstByName/dbGetPinShapes（r1292） |
| CovFMFlow-001 | LIVE-OPT(BLOCKED) | LIVE-OPT(BLOCKED) | .75 fm 许可未验（fm 不在 SRB 确认清单） |

**A shard OPT 收口**：4/4 全有可核查结论。0 条升 L2.live（2 infra-BLOCKED + 1 ref-bug-BLOCKED + 1 pyAether-API-BLOCKED）。AsyncFifoSim-001 是本轮唯一「.75 实跑证伪 OPT 理据」的发现，已登记为 LIVE-REQ 待 ref+TB 修复后落盘。

### 纪律
- 🚫 未改 check.py / cases / negative / assets / hidden / 主树 / jsonl / prompt / 断言 / strictness
- ✅ 只动：live_eval_review_A.tsv（2 行 verdict/reason/evidence 更新）+ 本文档（OPT 表 + §R3 节）
- ✅ 不登记 live_eval_changes.tsv（本轮无 judge_layers 变更，仅审视结论）
- .75 两 session 均已 close_session cleaned

---

## R3.1 · AsyncFifoSim-001 — REQ-BLOCKED → DONE (r1321, ref-bug-fix + check_live 落盘)

**背景**：r1320 OPT 收口发现 ref `full` 检测用 MSB-only 翻转（`{~sync2[W-1], sync2[W-2:0]}`），按 Cummings 对 DEPTH=2^ADDR_WIDTH 应翻转 top-2-bit（gray(N) 与 gray(N-DEPTH) 差 top-2）。MSB-only 导致 full 永不置位 → FIFO 溢出 → 真 VCS TEST FAILED 3err。OPT「static sufficient, no false-pos」被证伪（16-cond 静态放过功能坏 FIFO）。判 REQ-BLOCKED 待 ref+TB 修复。

**本轮修复（r1321）**：
1. **ref full fix**（`async_fifo_template.v`）：`{~sync2[PTR_WIDTH-1], sync2[PTR_WIDTH-2:0]}` → `{~sync2[PTR_WIDTH-1], ~sync2[PTR_WIDTH-2], sync2[PTR_WIDTH-3:0]}`（Cummings top-2-bit）。
2. **TB race fix**（`async_fifo_tb.sv`）：
   - `do_write`/`do_read`：原 `posedge+#1` 复检 `!full`/`!empty` 漏 push（flag 刚置位）→ 改 **negedge-decide / posedge-commit / #1-push**（full/empty 在 negedge→posedge 间稳定，因指针 reg 只 posedge NBA 更新）。
   - `do_write` 加 `#1` 让 DUT `always_ff` 采 `wr_en=1`（NBA）再 deassert —— 修 VCS active-region race（无 #1 时 `wr_en=1'b0` 抢先 DUT 采样 → wr_ptr=0 不 commit，debug 实测 wcount=19 但 wr_ptr_bin=0）。
   - phase3：单循环 `posedge+#1` 复检 racy → **fork/join 双进程**（writer/reader 各 negedge-decide/posedge-commit），wq/rq 跟踪 ACTUAL commit。
3. **check_live 非侵入包装**：`_check_static_impl`（原 check 16 cond a-p 一字不动）+ `check_static`（三元组）+ `check_live(deliverable, workdir, sess)`（upload submit.zip → unzip → `make run` → 断 `ALL TESTS PASSED` + `Chronologic VCS` banner）+ `check`（兼容）。
4. **live-neg**：`negative/live_msb_only_bug/`（buggy RTL MSB-only full + 正确 TB）—— 静态过 cond(f) `~[W-1]` pattern / 实跑 TEST FAILED 3err（full-asserted/fill_level/phase3）。
5. **negative_selftest** 改：区分 static-neg（3 条 FAIL distinct{c,d,o}）vs live-neg（静态 PASS，牙在 check_live .75）。

**.75 实跑（hfhds201, VCS R-2020.12）**：ref `make run` → **ALL TESTS PASSED** 3/3 runs（determinism, wall ~18s）；live-neg → TEST FAILED 3err。session close_session cleaned。

**§5 七项全绿**：① ref check_live PASS 3/3 ② 3 static neg FAIL distinct{c,d,o} + live-neg FAIL ③ 3-seed ④ SKIP_RUN loads clean（neg_selftest REF PASS）⑤ sha 876a1144 3-way sync（JSON test / 磁盘 check.py / test_sha8）⑥ 断言只增（check_static 一字不动，check_live 新增 live 断言）⑦ workdir leak check pass（workdir clean, no check.py/reference/hidden）。

**口径变更**：`judge_layers` [L0,L1] → [L0,L1,L2.live]，已登记 `live_eval_changes.tsv`。A shard REQ 7 done 7（0 BLOCKED），L2.live 8→11。

**纪律**：🚫 未改 prompt/assets/hidden/断言严格度/strictness/别 shard/jsonl/论文宏。✅ 改：check.py（非侵入包装）+ ref RTL/TB（bug fix）+ reference_submit.zip（regen）+ negative/live_msb_only_bug（新）+ negative_selftest.py + case JSON（judge_layers/level/test sha）。
