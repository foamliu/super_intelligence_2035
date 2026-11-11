# deepread: q9r9s (lanxinz@hfeg0pkn001) · finesim testbench 未定义参数 `.if` 条件语法修复

**trace_source**: user=lanxinz, host=hfeg0pkn001, session_file=1792134251943_q9r9s.messages.json, match_count=100, domain=spice_sim
**扫描来源**: 11-05 重扫令持续 · 11/12 rescan_1112_r417 mid-tier peek (spice=394, mc=100)
**A/B 档**: **B-synthesized**（A 档不可行：真实 .sp 依赖 /proj/drgqa PDK model .lib + Pattern_Power_lanxinz.sp .inc + lanxinz_RowPreDec.netlist，/proj 对 e0031982 permission denied，不可移植；但 trace 完整捕获 .sp 全文 + bug + fix + hspice 实跑证据）

## 用户原话（first user msg）
> 你能看到/proj/drgqa/V0/workdir/lanxinz/simulation/lanxinz_RowPreDec/simucode/ 目录下 run 将执行 sim_TT25c0.94v.sp，后者是 finesim 仿真的激励文件。你审阅 run 和 sim_TT25c0.94v.sp，如果有语法错误，则重新生成一个修改版的 testbench

## trace 关键事实
- **run 文件**：`bsub -q fqueue2h finesim -np 8 ./sim_TT25c0.94v.sp -o ./result_TT25c0.94v/finesim_TT25c0.94v`（finesim 仿真）
- **sim_TT25c0.94v.sp**（49 行，原文已存 `.75 workdir`）：`.inc Pattern_Power_lanxinz.sp` + 6 条 `.lib` model + `.inc ../lanxinz_RowPreDec.netlist` + 全局电源 Vvbn/Vvbp/Vvcc/Vvdbias/Vvss + `.inc R_RowPreDec_pwl_all`（PWL 激励）+ `.tran 1n 1.22u` + `.probe v()`
- **真实 bug**：`Pattern_Power_lanxinz.sp`（.inc 进来的）内含 `.if ((pvcc>=0.9v) && (pvcc<=0.92v)) .elseif ((pvcc>0.92v) && (pvcc<=0.97v)) .else .endif` 条件链，引用参数 `pvcc`/`pvbn`/`pvpcsg`，但主 .sp **从未定义 pvcc** ⇒ finesim/hspice 解析到 `.if` 时 `pvcc` 未解析
- **HSPICE 实跑证据**（trace A[12-14]，lanxinz 在 hfeg0pkn004 跑的 test_pvcc.sp repro）：
  ```
  **error** (test_pvcc.sp:5) Unresolved condition for parameter pvcc in .if
               ***** job aborted
  ```
  （PrimeSim HSPICE V-2023.12-SP1-1 linux64）
- **真实 fix**（sim_TT25c0.94v_fix.sp，61 行，trace MSG[21]）：在 `.inc Pattern_Power_lanxinz.sp` **之前**加 `.param pvcc=0.94`（filename corner TT25c0.94v → VCC=0.94V 落 (0.92,0.97] 分支），并把全局电源改成 `dc=pvcc/pvbn/pvbp/pvss`（让 .if 链定义的 param 驱动电源）。fix 注释原文：「FIX: define core supply so Pattern_Power_lanxinz.sp's .if chain resolves」

## test_pvcc.sp repro（trace A[12] editor new_text，最小复现）
```sp
.title test_pvcc
.option accurate runlvl=3
.temp 25
.param ptemp=25
.if ((pvcc>=0.9v) && (pvcc<=0.92v))
    .param pvbn  = -0.1v
    .param pvpcsg = 1.9v
.elseif ((pvcc>0.92v) && (pvcc<=0.97v))
    .param pvbn  = -0.1v
    .param pvpcsg = 1.9v
.else
    .param pvbn  = 0
    .param pvpcsg = 0
.endif
Vcc vcc! 0 dc=0.94
Rcc vcc! 0 1k
.tran 1p 1p
.print v(vcc!)
.end
```
→ HSPICE 报 `Unresolved condition for parameter pvcc in .if` + `job aborted`。

## 合成计划（下轮交付，DEBT:1）
- **case_id**: `EDA-Eval-DesignFlow-TbParamCondFix-001`
- **domain / level**: spice_sim / L2（真跑 HSPICE 验证 .if 条件解析 + 修复后 parse clean）
- **A 档不可行理由**：真实 .sp 三层 .inc/.lib 全指 /proj/drgqa + /apps/imctf PDK，e0031982 无读权限，沙盒不可达。
- **B 档合成思路**：构造可移植的「未定义参数 `.if` 条件链」testbench（不依赖 PDK model，用理想 R/C/MOS 开关级 `.subckt` 模拟 Pattern_Power 内的 `.if` 分支选电源）。候选脚本 `tb_paramcond_fix.py <testbench> <out_dir>`：
  1. 解析 testbench，找 `.if/.elseif/.else/.endif` 块引用的参数；
  2. 判定哪些参数在 `.if` 之前未 `.param` 定义（=bug）；
  3. 生成 fixed testbench：在 `.if` 之前补 `.param <param>=<value>`（值按 corner 取，落在某分支区间内）；
  4. 对 original 和 fixed 各跑一次 HSPICE，解析 .lis：original 应含 `Unresolved condition for parameter <p> in .if` + `job aborted`；fixed 应无该 error 且 `.tran` 完成。
- **隐藏输入 B**：与 A 不同 corner（不同 pvcc 落点 + 不同分支 + 不同未定义参数名/数量），B 放 `assets/<id>/hidden/` 不进 SUT 沙箱，`check()` 只跑 B。
- **check.py 断言（≥8, a..n 初拟）**：
  - a zip 解压 + 候选脚本 compile
  - b B 跑出 fixed testbench 文件
  - c original testbench HSPICE 实跑含 `Unresolved condition for parameter ... in .if`（证明 bug 存在）
  - d fixed testbench HSPICE 实跑**无** `Unresolved condition` 且**无** `job aborted`（证明 fix 生效）
  - e fixed testbench 在 `.if` 之前定义了被 `.if` 引用的参数（`.param` 出现且在 `.if` 之前）
  - f `.if/.elseif/.else/.endif` 条件结构在 fixed 中完整保留（数量与 original 一致）
  - g fixed 的 `.tran` 实际完成（.lis 含 transient analysis 完成标志，非 abort）
  - h 随机化：B 用 ≥3 个随机种子抽不同 corner/分支，fixed 全部 parse clean（反硬编码）
  - i 跨输入 A 也通（A corner 的 fixed 同样 clean）
  - j A 与 B 的 corner/参数取值不同（反硬编码值）
  - k L2 独立重跑 HSPICE（不靠候选自报，check 自己 subprocess 跑一次）结论与候选一致
  - l fixed 电源/激励节点值由 .if 分支选出的 param 驱动（分支不同则值不同，证明 .if 真生效非摆设）
  - m original 与 fixed 的 `.option`/`.temp`/`.tran` 仿真设置一致（fix 只动 param 定义，不偷改仿真条件）
  - n 重跑 fixed 的 HSPICE 退出码与候选报的一致
- **负样本**：(1) nosim——不跑 HSPICE 直接 print "no error"；(2) define-wrong-value——定义 param 但值落错分支；(3) delete-if——直接删 `.if` 块；(4) empty-fix——返回空 testbench；(5) ref_core_deleted——候选删核心解析。全 FAIL。
- **§4.9 三假**：空壳 / 只 print 期望串 / 删核心 全 FAIL。
- **自验**：`.75` HSPICE 跑 original（应 error）+ fixed（应 clean）+ 3 negatives + 三假。

## 本轮处置
- ledger_B: claim q9r9s → **claimed**（未 mark case，下轮合成后 mark）
- 10 reject 全 park（vuj95 wrong-domain / xcuds meta / rp1xk consultation / zd8iu borderline-L1 / ymjs5 phantom / nmz6w phantom / t9j7w consultation / 5ue0u wrong-domain / gn11a continuation / szdav near-dup）
- **DEBT: 1**（q9r9s deepread 完成，合成计划已就绪，下轮首事合成 TbParamCondFix-001）
- 11-peek (6 top spice≥452 + 5 mid spice 274-452) = 1 CLEAN (q9r9s) = 9% CLEAN yield（与 r413 的 14% 同量级，结构性压低确认）
- 新 reject 模式：**phantom/file-not-found**（ymjs5/nmz6w：rescan 找到 session 引用但文件在可达主机上不存在）—— r413 的 4 类之外第 5 类
