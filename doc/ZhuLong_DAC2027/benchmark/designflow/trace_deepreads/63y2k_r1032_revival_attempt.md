# trace_deepread: 63y2k — r1032 revival attempt (NOT revivable as A)

## trace 来源
- session: `1794966767607_63y2k.messages.json` (subdir-path ALIVE on 10.129.35.82/hfeg0plg58)
  - 注意：ledger 旧记录 host=hfeg0pkn001 是错的；summary_20261123_064315 实测 host=hfeg0plg58(10.129.35.82)
- user: rongjiez @ 10.129.35.82 (hfeg0plg58)
- mc: 10, ledger domain: verification (misclassified, 见下)
- keywords: `synopsys:22;analog:6;waveview:3;netlist:2;virtuoso:1;cadence:1;aether:1`
- messages: 199 msgs, 10 substantive human turns

## 用户逐字原话（HU#2，主意图轮）
> @compare_wave_new.pl @compare_wave.pl 我的compare_wave_new.pl是对compare_wave.pl的升级重构，
> 在compare_wave.pl中有@ztypeEXPSigList数组，根据不同的dqst信号而不同，在后续信号平移对比时
> 对于在@ztypeEXPSigList中的信号直接检测对应的fsdb信号是否有跳变。现在在compare_wave_new.pl中
> 没有@ztypeEXPSigList，而是在parallel_compare函数中的job_compare_res函数通过is_all_Z和
> chkTypeJumpFromFSDB对所有的全Z的EXP信号进行对比。现在需要改成和compare_wave.pl逻辑一致，
> 可以在filterSkipSigs函数中写好@ztypeEXPSigList数组。**请先告诉我怎么修改，不要直接修改我的文件**

后续 HU#3-#10 全是细化同一意图：`_ztype_data_exp(product, dt_a2d)` 按 DDR5/DDR6/LP6/LP5/LP4 +
dqs_t 域返回 @ztypeEXPSigList，严格对齐旧版字面量写法（exp_$dqsc1/exp_$dqst1）。

## 为什么 NOT revivable as A（三条独立否决）

### 1. INTENT-DUP with existing case
现有 case `EDA-Eval-DesignFlow-ZtypeWaveCompareProduce-001`（cases/A/，s59t7，rongjiez）的
real_task_summary 记录的 UT#0 用户原话：
> @compare_wave.pl @compare_wave_new.pl compare_wave_new.pl 是对 compare_wave.pl 的重构升级,
> 但丢失了全-Z exp 信号处理 (原 @ztypeEXPSigList + chkTypeJumpFromFSDB ...)

**同一用户、同一 compare_wave 重构、同一 @ztypeEXPSigList Z-type 恢复意图。** s59t7 已 reframe 成
自包含 `ztype_compare.pl`（chkTypeJumpFromFSDB + writeZtypeSigReport + dqs_t 两遍过滤）。
63y2k 是同用户后续/并行 session 细化同一重构的 per-product 列表构造子方面 —— 核心意图重复。
sibling brcv3 同样 intent-dup。

### 2. WRONG DOMAIN（16:4x A-domain attribution fail）
keyword 构成：synopsys:22(宽词) + analog:6 + waveview:3 + netlist:2 + virtuoso:1 + cadence:1 + aether:1。
去掉宽词 synopsys 后，analog/waveview/netlist/virtuoso/cadence/aether = 14 条全为 waveform/analog/virtuoso。
compare_wave.pl 是 **FSDB 波形对比脚本** —— waveform 域（D），不是 A(digital/verification/pnr_signoff/eda_other)。
按 16:4x 令三：「virtuoso/skill/layout/... 主导 ⇒ C；hspice/netlist/spice/schematic 主导 ⇒ B/D；
只有 digital/verification/pnr_signoff/eda_other 主导才算 A」。本 session ⇒ D，跨域，不改别人的题。

### 3. ADVICE-NOT-PRODUCE（排除#2 风险）
用户明确「请先告诉我怎么修改，**不要直接修改我的文件**」。assistant 全程给代码建议/注释改英文，
未产出独立可判分交付物。要造成 produce-task 需强行 reframe，但 s59t7 已用同源意图做过 reframe，
再做=重复造题。

## 结论
r1011 旧 note「viable but complex, deferred」是在 16:4x A-domain-attribution 令 + intent-dup 全量
核查**之前**写的。r1032 实测深读后三条独立否决，**不可作为 A 复活**。ledger 已更新 63y2k + brcv3
parked note。

## 给后续轮的提示
- rongjiez compare_wave 系列在 A 已有 s59t7(ZtypeWaveCompareProduce)、D 已有 546be(ScriptCompareMergeReviewQA)，
  该系列不要再取。
- 「viable but complex, deferred」类旧 parked note 须在 A-domain-attribution + intent-dup 双重核查后才能信。
