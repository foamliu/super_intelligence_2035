# Deepread — 1794277030341_l1ngd (TDC 电压传感器 VDD 降压误差根因分析)

- session: `1794277030341_l1ngd`
- user: zhililu @ hfeg0pnd001 (D-pure analog_context)
- mc: ≥10 (in candidates_mc10.tsv)
- ledger: trace_ledger_D.tsv → status=case, case_id=EDA-Eval-DesignFlow-VddSensTDCRootCause-001
- claimed: 2026-11-17 21:35 / cased: 2026-11-17 r830
- freshness: not in `_anchors_4shard_r568.txt` (3268 sessions); first use in 4-shard ledgers

## Trace summary (4 messages, 243KB messages.json on .75)

User (verbatim, A档 task):
> 这个电路模块的工作电压是0.75V，可以将data数据转换为带测电压值，现在VDD降低到0.63V，输出误差为100多mV，这个模块基本由逻辑单元组成，为什么会出现这种情况，输入时钟频率为25MHz

附件：filter.sp（207KB SPICE 网表，27 个子电路，顶层 VS_DIG_FILTER_more）

Assistant (4 轮分析):
1. 读网表 → 识别电路为 TDC 电压传感器：VS_Delay_10INV 10 级反相器延时链 + VS_VSFilter13bNcounterIP 13 位计数器 + VS_ADDSUB_11b 校准加减器 + SDFFRD 分频链 + VS_VS_Lpulse 测量窗口
2. 根因：反相器传播延时 td 强 VDD 依赖；0.63V 接近阈值 (Vth~0.4-0.5V)，psvt/nsvt 最小尺寸管 (w=25nm l=6nm nfin=1) 进入近阈值区，I_DS 指数化 → td 非线性激增
3. 13 位计数器量化 25MHz 窗口内的延时脉冲数 → td 大→计数少→线性标定 (在 0.75V 饱和区拟合的 VS_ADDSUB_11b trim 系数) 失配 → >100mV 误差
4. 排查建议：VDD sweep 0.60-0.85V 测 td-VDD 曲线、双 VDD corner transient、在 0.63V 重新拟合校准系数、Monte-Carlo、probe FLT_CLK 分频链与 Lpulse 窗口

## Case making (r830)

- case_id: `EDA-Eval-DesignFlow-VddSensTDCRootCause-001`
- mode: design_flow (offline netlist-Q&A, no EDA tool run)
- domain: analog_context (D-pure, NOT net-prefix highlight — saturated per r829)
- entry_point: outputs/submit.zip (analysis.json)
- check(): 12 独立断言 a-l，全部静态 Python，无 EDA 工具依赖
  - a) 6 必需字段存在
  - b) circuit_type 含 TDC/延时链/电压传感器
  - c) topology 提反相器+延时链
  - d) key_components 含 INVD1/VS_Delay_10INV
  - e) root_cause 提 VDD+延时变化
  - f) vdd_sensitivity 提近阈值/亚阈值/非线性
  - g) root_cause/vdd_sensitivity 提标定/校准失配
  - h) topology/key_components 提 13 位计数器
  - i) root_cause/topology 提 25MHz/计数
  - j) key_components 提 MOS 最小尺寸 (w=25nm/l=6nm/nfin=1)
  - k) diagnosis_steps 含 VDD sweep/td-VDD 曲线
  - l) key_components/topology 提校准加减器/分频链
- k_rationale = 12 = k_check ✓ (≥8 硬门槛)
- asset: `assets/EDA-Eval-DesignFlow-VddSensTDCRootCause-001/filter.sp` (~7KB 精剪网表，保留 INVD1/VS_Delay_10INV/SDFFRD/VS_VSFilterCountUnitIP/VS_VSFilter13bNcounterIP/VS_VS_Lpulse/VS_ADDER_11b/VS_ADDSUB_11b/VS_VS_Filter_SlopeCtrl 9 个关键子电路 + 顶层结构描述；原始 207KB 太大不直传)
- reference/check.py + negative/negative_selftest.py + REF_ANALYSIS (in-memory)

## Self-verify (r830)

```
positive control (REF_ANALYSIS): PASS=1  12/12 conditions true
negative fake_empty            PASS= 0 FAIL=12  expected_fail=a     OK
negative fake_print_expected   PASS= 1 FAIL=11  expected_fail=b/c/d OK
negative fake_no_vdd_delay     PASS=10 FAIL= 2  expected_fail=e     OK
negative fake_no_sweep         PASS=11 FAIL= 1  expected_fail=k     OK
negative fake_no_counter       PASS=10 FAIL= 2  expected_fail=h/l   OK
NEG_RC=0
3-run md5 = 58b5cc397e6cd1d4eaba27202a6f3e25 (deterministic)
```

§4.9 degenerate-submission regression: fake_empty (空 zip) FAIL all 12 (a-l 全 False) ✓

## D.jsonl

`build_jsonl.py --shard D` 重建后 D.jsonl 462 行（461→462，新增 VddSensTDCRootCause-001 line 408）。无 dangling entry（走 cases/D/<id>.json + build_jsonl.py 路径，r828 lesson）。

## Notes

- e0031982 (gid=555 guest) 不在 hfdes 组，但 zhililu session 在 .75 上可读（243KB messages.json + 207KB netlist 均 readable）
- 选 l1ngd 而非 xvltf（备选 1794449745970_xvltf zhililu chopper clock charge-injection）因 l1ngd 网表更结构化、根因链条更清晰（5 个机理层全可量化）
- waveform 域在 D shard 已饱和（candidates_mc10.tsv 中的 D-pure waveform 候选几乎全 ledgered），优先 analog_context
