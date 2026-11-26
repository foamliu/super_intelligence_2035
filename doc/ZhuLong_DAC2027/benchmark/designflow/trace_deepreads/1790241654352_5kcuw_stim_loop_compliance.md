# Trace Deepread: 1790241654352_5kcuw (Stimulus Loop-Construct Compliance + Rewrite)

- **trace**: 1790241654352_5kcuw / ghyang @ hfeg0pkn003 (10.129.2.12) / mc=41 / 67 msgs / 678KB
- **agent**: lead (cline), tools: read_files:21, list_allowed_files:6, search_codebase:2, RAG:2, run_commands:1 (DENIED mostly), editor:1, fetch_web_content:1
- **simulator**: Synopsys FineSim V-2023.12-1, mode `promd`/`spicead` (via `finesim_option`), invoked through `sim_w0w1r1w0r0_normalYio_PN.sp` which `.inc './stimulus_PatternAll.sp'`
- **domain**: spice_sim (DDGOA Yiotwist SRAM write/read pattern characterization stimulus)

## 用户轮（A-档选轮评估）

- **U0**「帮我检查这份仿真激励文件 /proj/ddgoa/V0/workdir/ghyang/DDGOA/Yiotwist/stimulus_PatternAll.sp中的R 循环和for 循环的使用是否符合仿真器的要求，如果不符合应该改成什么样的规范，它被用于同路径下的sim_w0w1r1w0r0_normalYio_PN.sp文件」→ **A-档选轮合规**（pure requirement，未给根因/修复方向）
- U23「如果我想使用循环的方法写激励，结合当前的仿真器，有什么合规的语句可供使用吗，比如先写出前四个周期，后面每4周期一循环，以及使用类似于for循环的办法写32组相同的信号线」→ follow-up (需求扩展)
- U28「我尝试用你推荐的方式写循环激励，报错信息在这里：res_0924/sim_w0w1r1w0r0_normalYio_PN_testfor.log，帮我分析下有什么问题」→ **用户已给根因方向**（报错信息）→ 不可作 A-档任务说明
- U31「sim_w0w1r1w0r0_normalYio.sp 我运行了这个仿真文件，输出了对应的波形和probe的timing，但是其中的tb_w0显示没找到targ，检查输出的波形我认为是存在这个点的，我想知道是为什么」→ .measure targ debug (separate sub-skill)
- U36「如果我想提取abs之后，第二次经过目标值的时间怎么办，上次试过cross = 2 和 rise = 2 好像不成功」→ .measure cross/rise on abs() (separate sub-skill)

**A-档可用**（仅 U0），但 trace 多轮且用户最终接受的是 agent 的文字分析（无具体可运行产物）→ design_flow 契约需 `outputs/submit.zip` 可运行交付 → **B-档 synthesized**（保留 "FineSim stimulus loop-construct compliance checker + simulator-verified rewrite" 子技能，金标准 = FineSim -spice 跑 rewritten stimulus 干净通过）。

## 真实流（agent 分析）

### 问题 1: `.for` 循环 (stimulus_PatternAll.sp L190-194)
```sp
.param i=0
.for i=0 to 3
VDatain<{i}> Datain<{i}> 0 pulse (pvss pvcc '4.6n+tdelay' trise trise 2.7n 100n)
.endfor
```
- FineSim 日志：`WARNING! Unknown command '.for' is ignored (stimulus_PatternAll.sp:192)`
- 后果：Datain<0:3> **无激励源定义**，节点 floating，仿真继续但写操作错误
- 严重度：**WARNING**（sim 继续，construct 被忽略）
- 附加：`.param i=0` 多余（HSPICE `.for` 自声明循环变量，但 FineSim 根本不支持 `.for`）
- 修复：展开为 32 个显式 VDatain 实例（对照同目录 stimulus_Pattern1.sp L196-227，已验证可运行）

### 问题 2: PWL `+ R` 重复关键字 (L155-167)
```sp
vwren_dsain wren_dsain 0 pwl (
* 第1个周期
+'tdelay-1.3n' pvss
+'tdelay-1.3n+trise' pvcc
+'tdelay-1.3n+trise+thold*2' pvcc
+'tdelay-1.3n+trise+thold*2+trise' pvss
* 第2个周期
+'tdelay-1.3n+tperiod' pvss
...
+ R
```
- FineSim 日志：`ERROR! incomplete resistor 'r' (stimulus_PatternAll.sp:166)`
- 根因：FineSim **不支持 PWL `R` 重复关键字**；解析器看到行首 `+` 后紧跟 `R`，**误解析为电阻元件声明开始**，后续无两节点 → `incomplete resistor 'r'`
- 严重度：**ERROR**（sim 立即终止，不产生结果）
- 修复：删除 `+ R`，手动展开每个周期（因第3周期跳过模式非均匀，`R` 无法实现）

### 严重度对比（关键陷阱）
| 问题 | 严重度 | 后果 |
|---|---|---|
| `.for` 被忽略 | WARNING | sim 继续，但 Datain<0:3> 无激励 |
| `+ R` 被当作不完整电阻 | **ERROR** | sim 立即终止，不产生结果 |

### A16: FineSim 合规循环写法方案
- 32组相同信号线：① Subcircuit 实例化（最简洁，`.SUBCKT datain_src node ... Xdi<0:31> Datain<0:31> datain_src`）② 向量总线展开 ③ 显式展开
- PWL 4周期循环：① R 关键字（仅均匀重复可用，FineSim 不支持→必须显式）② 显式展开（非均匀跳过模式唯一选项）

### A22/A26: .measure targ/cross on abs() （独立子技能，不入本 case）
- `tb_w0` targ not found：`targ v(net852)-v(net941) val=0.3*pvblh` → Write0 时 net941 升 net852 降 → 差分负向 → 永不跨越 +0.3*pvblh → 改 `abs(v(net941)-v(net852))`
- `cross=2`/`rise=2` on abs() 失败：abs() 信号 ≥0，通常只一次正向穿越 → 无第二次 rise；建议改用极性正确的 cross 或 parametric

## distinct vs 已有 B spice_sim/char cases
- NetlistLintHsp-001 = netlist 语法 lint（unclosed subckt/pin mismatch/undefined model）+ HSPICE elaboration 权威
- FineSim 四 case (gvm3g/hk622/uky6c/cllpy) = FineSim elaboration 失败修复器
- FineSimWorkflowRunner-001 = 自主 FineSim 工作流生成器
- Tr0JitterRemeas-001 = .tr0 二进制 jitter 重测
- 本条 = **FineSim stimulus 文件 loop-construct (`.for`/`.while`/`R` keyword) 合规检查 + 严重度分类 (warning-ignored vs error-fatal) + 合规改写 (subcircuit/explicit expansion) + FineSim -spice 真跑验证改写干净通过** → shard B 首个「stimulus loop-construct compliance + rewrite」case，distinct ✓

## .75 L2 可行性
- FineSim -spice V-2023.12-1 在 .75 已验证可用（FineSimDcConvFix/FineSimWorkflowRunner/McRonMismatch 三 case）
- 需实测：构造最小 stimulus 含 `.for` + `+ R` → 跑 `finesim -spice` → 确认 `WARNING! Unknown command '.for'` + `ERROR! incomplete resistor 'r'` 复现
- DUT 用 Level-1 Shichman-Hodges NMOS 反相器（Datain<0:N> 驱动 gate），.75 无 foundry PDK

## case 设计 EDA-Eval-DesignFlow-StimLoopComplianceFix-001
- domain: spice_sim, B档 synthesized, L2 真跑 FineSim -spice, k=14
- A: stimulus_A.sp (`.for i=0 to 3` + `+ R` PWL repeat + `.param i=0`) + sim_top_A.sp (4 NMOS inv, .inc stimulus_A.sp, .tran, .measure) + spec_A.json
- B (hidden): stimulus_B.sp (`.while` loop + 不同 R pattern + Datain_B<0:7> 8 nodes + 5-cycle skip PWL) + sim_top_B.sp (8 PMOS inv) + spec_B.json
- 交付 (submit.zip): stim_loop_compliance.py + compliance_report.json + stimulus_rewritten.sp (for B) + sim_log/{original_B.log, rewritten_B.log}
- check.py 14 条 a-n: 见合成阶段
