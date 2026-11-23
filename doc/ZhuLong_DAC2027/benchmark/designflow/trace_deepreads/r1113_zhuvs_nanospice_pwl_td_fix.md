# trace_deepreads/r1113_zhuvs_nanospice_pwl_td_fix.md

**Session**: 1794916836811_zhuvs · **User**: youmingz · **Host**: hfeg0plg93 (10.129.8.225)
**Match count**: 5 (hspice:52 netlist:33 aether:31 drc:8 spectre:3) · **Domain**: spice_sim
**NMSG**: 13 (3 identical user repeats of the same question + assistant diag)
**Case**: EDA-Eval-DesignFlow-NanoSpicePwlTdFixProduce-001 (k=14)

## 1. 用户真实意图（U#0/U#1/U#2 三次重复同一问）

跑 NanoSpice DDR 仿真，FF corner 正常，SS/TT corner 直接退出，报错：

```
!!NanoSpice-ERROR: Instance Vcm0_ts_ODLBEn parameter wave expect even number values, but found odd number values.
```

用户贴了两条 PWL 激励语句对比：
- **正常(FF)**：`Vcm0_ts_ODLBEn\tXI_PERI0.XI_BCenter.XI_BCenterDQ.XI_D_DQBYTELOW_0.XI_T_CMDq.cm0_ts_ODLBEn\t0\tpwl\t 1080n 0  1080.01n pvdd  1151n pvdd  1151.01n 0  1181n 0 1181.01n pvdd 1234n pvdd 1234.01n 0`
- **报错(SS/TT)**：同上 + `  +  TD=5.2n`

用户问：哪里错了，应该怎么改，用中文展示答案和思考过程。

## 2. Assistant 工具链（A#3/A#6/A#8/A#10/A#12）

- list_allowed_files → 工作区空（/ai_sandbox/drcpa/V0/agentdir/youmingz 无网表文件）
- ask-eda 技能查 NanoSpice PWL TD 语法 → python-runner SIGABRT（encodings 模块缺失，沙箱 Python 坏）
- 改 shell-runner → 要求 filePath .sh，ask_eda.py 是 .py，失败
- **最终纯推理给出诊断 + 修复方案**（无外部工具依赖）

## 3. Assistant 诊断与修复（A#12，关键产物）

**思考过程**：
1. 逐字对比 → 唯一区别是末尾 `+ TD=5.2n`
2. PWL 源波形必须"时间/电压"成对，值总数必须偶数
3. 数值个数：正常 16 个（8 对，偶数 ✓）；报错 = 同样 16 个 + `TD=5.2n` 被当成第 17 个 → 17 奇数 ✗
4. 与报错信息印证：17 是奇数，"expect even number values, but found odd number values" 完全吻合
5. 解释为何偏偏 FF 能跑：激励网表生成脚本对 SS/TT corner 拼上 `+ TD=5.2n`（corner 相关延迟，FF 延迟为 0 或不输出），FF 网表无此段

**结论**：`TD=5.2n` 这个写法 NanoSpice PWL 源不支持，解析器把 `TD=5.2n` 当成波形数据一部分，使波形值 16→17（奇数），触发报错。这是激励网表生成问题，非 corner/模型问题。

**三个修复方案**：
- **方案1（推荐，数学等价）**：去掉 `TD=`，把所有时间点整体平移 +5.2ns（TD 语义=整段波形往后推，推迟期间输出初值 0，与第一个点 (1080n,0) 值一致，严格等价）
  - `1080n→1085.2n, 1080.01n→1085.21n, 1151n→1156.2n, 1151.01n→1156.21n, 1181n→1186.2n, 1181.01n→1186.21n, 1234n→1239.2n, 1234.01n→1239.21n`
- **方案2**：直接删 `+ TD=5.2n`（跳变沿提前 5.2ns，若有时序配合慎用）
- **方案3（根治）**：改激励网表生成脚本，不拼 `TD=`，输出波形时把延迟加进每个时间点

附带提醒：SPICE `+` 续行符必须独占行首；SS/TT 网表里其他带 `TD=` 的 PWL 源会同样报错。

## 4. Reframe（harness-for-teeth）

spec 驱动 L1 纯 Python NanoSpice PWL 奇偶校验 + TD 延迟修复器 `pwl_td_fix.py <spec.json> <out_dir>`：
- **诊断**：每条 PWL 源数波形值个数；NanoSpice 不识别 `TD=` → 计入波形值（奇偶翻转）；`td_recognized=true`（HSPICE 风格）则不计。输出 diagnosis.json（id/corner/instance/n_pairs/n_values/parity/has_td/td_delay/td_recognized/td_swallowed/has_error/root_cause）
- **修复（方案1）**：报错源生成 `fixed/<id>.sp`，去掉 `TD=`，延迟值加到每个时间点（Decimal 精确算术，SPICE 后缀 f/p/n/u/m/k/meg/g/t 解析回写，保持原 token 后缀），电压不变，值个数恢复偶数
- **report.md** 人类可读汇总

## 5. 资产

**A（faithful）**：simulator=NanoSpice，3 源（FF 无 TD 8 对 / SS TD=5.2n 8 对 / TT TD=5.2n 8 对），真实 instance Vcm0_ts_ODLBEn + 真实层次 + 真实 8 对（1080n..1234.01n / pvdd）。工作区空无网表，spec 从用户贴的两条 PWL 逐字重建。

**hidden B（7 重 anti-hardcode）**：①instance Vdqs_cmd_p ②hier XI_TOP.XI_DDRPHY.XI_DQ0.XI_T_DQS.cmd_p ③node dqs_p ④value pvddq ⑤times 2120n-based ⑥delays 3.5n/7.8n + 对数 6/10 ⑦B4 td_recognized=true + td_delay=4.0n → 不报错不修复（td_recognized 分支齿）。4 源：B1 FF 无 TD 6 对(12 偶 ok) / B2 SS TD=3.5n 6 对(13 奇 err) / B3 TT TD=7.8n 10 对(21 奇 err) / B4 TT2 TD=4.0n td_recognized 8 对(16 偶 ok 不修复)。

## 6. check 14 条断言（a-n）

a(zip+compile+size>200) b(B exit0+diagnosis 覆盖 4 源) c(每源 n_values/parity 正确) d(td_swallowed 仅 NanoSpice+有TD+不识别) e(has_error 恰落 B2/B3) f(root_cause 仅报错源非空) g(root_cause 含 TD/swallow|not recogn|odd 之一防废话) h(报错源有 fixed 文件+非报错源无+B4 命中 td_recognized 分支) i(fixed 值偶数+对数不变+无 '=' 残留) j(fixed instance/hier/node 与 B 一致) k(每时间 token 恰好 +td_delay，电压不变，逐对比较) l(anti-hardcode-A fixed 输出无 A token 词边界，pvdd 不命中 pvddq) m(anti-hardcode-A 工具源码无强 A token 词边界正则) n(3-seed sha256 一致)

## 7. 3 negs（§4.9 三假）

- **empty_shell**：125B 占位 → a(size<200)
- **print_expected**：硬编 A 实例/时间/延迟输出 → b(B 源 id 不匹配，A token FF_ODLBEn/SS_ODLBEn)
- **core_removed**：真解析 B 诊断正确，但 fixed 不平移时间(只删 TD) → k(time[0] 2120n != 2123.5n)

## 8. 自验

- REF 14/14 PASS（reference_submit.zip）
- NEG 3/3 FAIL（empty→a / print→b / core_removed→k）
- 3-seed sha256 ✓
- A 输出核对：FF 16 偶 ok / SS 17 奇 err / fixed SS 1080n→1085.2n... 与 assistant 方案1 逐字一致
- B 输出核对：B2 2120n→2123.5n / B3 2120n→2127.8n(10 对) / B4 无 fix 文件 ✓

## 9. 与既有 case 区别

- r1095 FineSimIgnoreDiff（.option finesim_ignore 解析）— option 解析非 PWL 奇偶
- r1094 SlicerMeasureGen（.meas 块生成）— 测量块非激励源
- r1086 PowerSupplyDcTypeGen（电源 DC 类型）— 电源类型非 PWL 延迟
- r1083 SpiceNetlistFaultAnalyzer（故障注入目标）— 实例分类非奇偶校验
- 本 case = 首个 PWL 激励源奇偶校验 + TD 延迟"烘焙"修复器，Decimal 精确 SPICE 后缀算术是核心齿

## 10. 台账

1794916836811_zhuvs: claim → mark case (EDA-Eval-DesignFlow-NanoSpicePwlTdFixProduce-001) ✓
