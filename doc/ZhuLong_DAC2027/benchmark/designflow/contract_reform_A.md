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
