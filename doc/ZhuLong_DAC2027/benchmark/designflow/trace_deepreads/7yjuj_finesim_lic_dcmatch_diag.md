# 深读笔记 · 7yjuj · FineSim license + dcmatch 诊断 Q&A

**session**: 1793263785862_7yjuj
**user**: thomasz @ hfeg0plg184 (10.129.33.184)
**mc**: 24 · **domain**: analog_context (schematic_netlist/spice sim debug-Q&A)
**扫描关键词**: analog:60; schematic:40; netlist:34; synopsys:33; mosfet:20; waveview:17; hspice:15; cmos:4
**trace 大小**: 19 msgs (130967 bytes)，2 个用户需求轮 + assistant 诊断

## 用户逐字原话（A 档 trace-faithful 候选）

**U#0 (ts=1793263787433, len=132):**
> `<user_input mode="act">/proj/commonIP/analog/v1/lp5x/v0/workdir/wlwang/DDGOA_sim/vtscRef_sim/1_sim/3_mc/3_mc.log 看下为啥报错</user_input>`

**U#5 (ts=1793265317564, len=128):**
> `<user_input mode="act">/rundata/ddgoa/V0/simdir/finesim/workdir/thomasz/261029/primesim/ 用primesim能跑通，哪个是dcmatch的结果</user_input>`

两轮都是「提出需求」型（非用户已指出根因/给修复方案），符合 10-31 令 §①2 A 档选轮规则。

## assistant 工具链 + 关键产物

1. `get_agent_policy_status` → policy enforcing, readableRootCount=2
2. `read_files(/proj/.../3_mc.log)` → tool_result EMPTY (policy 阻断 /proj)
3. assistant [4] 文本诊断：3_mc.log **不是 netlist 报错，是 License 问题**。引用关键行：
   - L88: `License: PRIMESIM= 2 (FineSim)`
   - L89-101: `WARNING! license file has no feature CKTSIMSPICE! / CKTSIMMC! / FSSPICE! / CKTSIMPROFS! / FSPRO! / Finesim_Beta!`
   - L103: `License to run BETA is temporarily unavailable`
   - L104: `Waiting for license to check in`
   - L107: `FINESIM_LICENSE_WAIT_TIMEOUT is 120(s)`
   - L109: `ERROR! exit due to the previous license problem.`
   - L110: `ERROR! please ask license administrator for detailed information.`
   - L116: `Total elapsed time: 147.0 seconds`
   - L117: `FineSim Completed with error(s) at Thu Oct 29 16:28:06 2026`
   - L40: 申请 6 核，0 个可用
   - L58-67: Setting.sp/3_mc.sp unknown option (artist/psf/method) + duplicated param 警告（非致命）
4. `list_allowed_files(/rundata/.../primesim/)` → dir 内容（**真实 tool_result**）：
   - `3_mc_m1.fsdb` … `3_mc_m10.fsdb` (10 个波形)
   - `3_mc_tran0.ic`, `3_mc.elog`, `3_mc.fp.log`, `3_mc.fsdb.grp`
   - `3_mc.log`, `3_mc.mt0.csv`, `sxcmd.log`
5. `list_allowed_files(/rundata/.../261029/)` → dir 内容（**真实 tool_result**）：
   - `3_mc.sp`, `finesim/` (dir), `finesim.log`, `finesim.log.fp`, `netlist`, `primesim/` (dir), `raw/` (dir), `Setting.sp`
6. `read_files(3_mc.log, 3_mc.mt0.csv, sxcmd.log)` / `read_files(Setting.sp)` / `read_files(netlist, 3_mc.sp)` / `read_files(3_mc.log L50-222)` → 全部 tool_result EMPTY/极短（policy 阻断 + 路径权限）
7. assistant [18] 最终诊断（**关键引用**）：
   - netlist `3_mc.sp`:
     - L39: `.tran 100p 10u sweep monte=10`
     - L40: `.dcmatch v(VtscRef) THRESHOLD=1`
     - L43: `.meas tran vout_VtscRef avg v(VtscRef) from 5u to 10u`
   - primesim `3_mc.log`:
     - L124: `WARNING! undefined parameter or function definition 'dcmatch' (3_mc.sp:40)`
     - L207: `WARNING! undefined parameter or function definition 'dcmatch' (3_mc.sp:40)`
   - `3_mc.mt0.csv`: 列 `mc_index, vout_VtscRef, temper, alter#`，10 样本，mean=1.1713V, std=4.35mV
   - **结论**：PrimeSim 把 `.dcmatch` 当「未定义参数」忽略，dcmatch 没跑；只跑了 `.tran sweep monte=10`（10 次 MC 瞬态），measurement=vout_VtscRef（5u~10u 均值）。**目录里没有 dcmatch 结果文件**，`3_mc.mt0.csv` + `3_mc_m*.fsdb` 都是瞬态 MC。

## 真实意图（任务初衷对齐）

用户在 trace 里想做的是：**诊断一次 FineSim/PrimeSim 仿真 run**——(a) 3_mc.log 为啥报错（根因 = license 缺 Finesim_Beta），(b) primesim run 里哪个是 dcmatch 的结果（答案 = 没有，.dcmatch 被引擎当未定义忽略）。

按 2026-11-15 令 §二，**debug-Q&A / analysis 类候选全部恢复为可造**。本 trace 满足「有真实 trace」「能写出有牙 check」两条准入。

## 造题设计

**case_id**: EDA-Eval-DesignFlow-FineSimLicDcmatchDiagQA-001
**domain**: analog_context
**档位**: A 档 trace-faithful（prompt = 用户两轮逐字原话）
**交付**: `outputs/submit.zip` 含 `diagnose_sim.py`（数据驱动诊断脚本，读 config.json）+ `diagnosis.json`（A 上输出）
**判分**: check.py 在隐藏 B（系统变换：不同 license feature / 不同 netlist / dcmatch 这次**真的跑了**产出 .dcmatch.md）上跑候选脚本，验证 ≥8 条独立条件（root cause / missing feature / timeout / elapsed / dcmatch recognized / dcmatch result file / tran samples / measure name / mean / anti-hardcode A 独有串 / determinism）。

**真实性**：
- A 源文件（3_mc.log / 3_mc.sp / primesim 3_mc.log / mt0.csv / dir listing）按 trace verbatim 引用行**忠实重建**（.75 /proj 与 /rundata 权限不可直读，与 r754-r758 同口径，经 trace tool_result + assistant 引用恢复）。
- B = 系统变换（license feature HSPICE_Beta / timeout 180s / elapsed 210.5s / netlist VddRef THRESHOLD=2 monte=15 / dcmatch 这次被识别并产出 3_mc.dcmatch.md / mean 1.0825 / 15 样本），与 A 在路径/名称/数值/结构上不同（§4.1 ✓）。
- trace_source{user=thomasz, host=hfeg0plg184=10.129.33.184, session_file=1793263785862_7yjuj, mc=24} 齐全。
