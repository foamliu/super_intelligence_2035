# trace_deepread: 1795001261903_fejb2 (fejb2) — FineSim dVOHdT stimulus sweep+meas fix

- **user**: clarawu @ hfeg0pkn005 (10.129.2.14), model deepseek-v4-flash, 95 msgs, mc=110, kw `hspice:423;netlist:318;schematic:126;synopsys:58;analog:10;pdk:2;mixed-signal:2`
- **cwd**: `/proj/m2701/V0_DDR4/workdir/clarawu/simulation/sim_FinalDrv_Ron_cio_leakage_versionD/hspiceD/schematic/netlist/stimulus_file_for_metrics/dVOHdT/`
- **skill invoked**: `spice_tb_stimulus` (cline skill, `/home/clarawu/.cline/skills/spice_tb_stimulus/`)

## 真实任务
DDR4 FinalDrv Ron/CIO-leakage versionD 表征仿真里 dVOH/dT（VOH 随温度变化率）的 FineSim DC 温度扫描 stimulus deck `stimulus_dVOHdT_M40C.sp` 跑不起来。

deck 结构（trace msg 52 agent editor new_text 逐字）：
- `.param Tref=-40` / `.temp 'Tref'` / `.param VVDDQ=0.5` / `.param VVDD=0.85`
- 12 个 vZqPu/vZqPd 源（zqpu/zqpd 0..5 × VVDD）
- `.inc '../../netlist_delvto'`
- `.dc temp list 'Tref-1' 'Tref' 'Tref+1'` ← **bug 1: FineSim 不支持 `list` 关键字**
- `.probe V(*) except='*:*'` / `.probe I(*) isub(*)`
- `.meas dc VOH_Tref_minus1 find v(DQ_VOH) at=1` / `at=2` / `at=3` ← **bug 2: at= 在 FineSim DC 扫描下返回 error**
- 3 corner `.lib '../zqcode_75pvt.sp' ZQCODE_FF/TT/SS_M40C_0P85V_0P5V` + 2 `.alter` + `.end`

## 用户三轮交互
1. U2 (msg 57): `ERROR! incomplete or unsupported sweep statement 'tref+1' (stimulus_dVOHdT_M40C.sp:34)` — FineSim 把 `list` 当 start/stop 解析，第 3 个 token 报错。
2. agent fix 1 (msg 62): `.dc temp list ...` → `.dc temp POI 3 'Tref-1' 'Tref' 'Tref+1'`（参考同项目跑通的 dRONdT deck：`.dc VOUT POI 1 '0.5*VVDDQ' sweep temp POI 3 'Tref-1' 'Tref' 'Tref+1'`）。
3. U3 (msg 67): 用户改后跑，md0 输出 `temper voh_tref_minus1 voh_tref_0 voh_tref_plus1 alter#` 三行 -41/-40/-39 但 measure 全 `error`：
   ```
   -4.1000e+01  error  error  error  1.0000e+00
   -4.0000e+01  error  error  error  1.0000e+00
   -3.9000e+01  error  error  error  1.0000e+00
   ```
4. agent 诊断 (msg 84/90): `DQ_VOH` 节点确实存在（netlist_delvto line 259 `R2 net010 DQ_VOH 0`），问题是 `find ... at=` 形式本身在 FineSim DC 扫描下 error。查同项目所有 `.meas dc`（dRONdT/dRONdV2/dRONdVQ/Ron/MC）**没有一条用 at=**，全是 `find ... when`。FineSim 已按 `temper` 列逐点输出，at= 冗余且报错。
5. agent fix 2 (msg 90): 3 条 `.meas dc VOH_Tref_* find v(DQ_VOH) at=...` 合并成一条 `.meas dc VOH find v(DQ_VOH)`（去 at=）。

## 交付
`/ai_sandbox/m2701/V0_DDR4/agentdir/clarawu/stimulus_dVOHdT_M40C_corrected.sp`（/proj 路径在 agent-policy.json writableRoots 之外，写到 /ai_sandbox）。

## 访问约束
原始 /proj/m2701/.../stimulus_dVOHdT_M40C.sp + /ai_sandbox/.../corrected.sp 对 e0031982 **权限拒访**（只有 clarawu 自己的 cline agent 能 read_files）。A 档 asset 按 trace msg 52 editor new_text 逐字重建（at=1/2/3 形式自 msg 48 editor old_text）。

## case 合成
- **case_id**: EDA-Eval-DesignFlow-FineSimStimSweepFix-001
- **domain**: spice_sim, **layer**: L1 (纯 Python 文本变换，check 真跑脚本在 hidden B 上，无 EDA 二进制), **track**: faithful, **tier**: B
- **reframe_driver**: harness_for_teeth (portability subtype) — 原始交付是一次性 corrected .sp 文件（不可复用/未参数化），reframe 提取可复用修复逻辑成 `fix_finesim_stimulus.py --input/--output`
- **asset A**: stimulus_dVOHdT_M40C.sp (format-faithful)
- **hidden B**: stimulus_dVODdT_25C.sp (10 维度结构性差异 + 2 decoy non-at= .meas 行)
- **check**: 16 条断言 a-p, k_check=k_rationale=16, 真跑候选在 B 上
- **§4.9**: 5 neg (empty_shell/print_expected/hardcoded_A/core_deleted/no_poi_count) 全 FAIL NEG_RC=5/5, ref 16/16 PASS
