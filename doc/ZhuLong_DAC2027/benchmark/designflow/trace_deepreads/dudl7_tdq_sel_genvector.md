# trace_deepread: dudl7 — DDR5 genvector TDQ bit-selection SV generator

- **session**: `1795654937853_dudl7` (ericw@hfeg0plg102, mc=253)
- **domain**: analog_context (analog-context dominant; DDR5 genvector SV flow)
- **claim**: D-ledger r1655, analog_context
- **verdict**: FRESH → reframe → `TdqSelGenvectorProduce-001`

## 真实任务 (286 msgs, 1.1MB)

用户 ericw 在 DDR5 genvector 流里维护 `ddr5_genvector.sv`，需要把 `exp_TDQ` 的
**位选择 (bit-selection)** 做成可配置：原硬编码 `EXP_TDQ` 12-bit 总线选择写死在
SV 里，要改成可按预设 (ALL12/HIGH6/LOW6/HIGH4/MID4/LOW4) 切换选哪几位灌进 DUT。

agent 路径：
1. 反复读 `ddr5_genvector.sv` 找 `exp_TDQ` 声明/赋值点 (12-bit 总线, 表头循环)
2. 尝试用 SV `int X[]={...}` 拼接数组初始化位选择表 —— **ncvlog 陷阱①**：
   `{...}` 是赋值模式 (assignment pattern) 不是拼接，数组初始化须用 `'{...}`，
   ncvlog 报 illegal primary
3. 尝试在 const 上下文 (`$clog2` / 参数声明) 用 `$size(EXP_SEL)` 算总线宽 ——
   **ncvlog 陷阱②**：`$size` 不是 const function，const 上下文报 *E,AQFCNT
   (size in constant function)
4. 复用了一个名叫 `count` 的宏做位计数 —— **ncvlog 陷阱③**：与既有 `count`
   信号/标识符 shadow 冲突，宏展开后语义错
5. session 在反复改 SV + ncvlog 编译报错循环里结束 (286 msgs)，**没产出可配置版**

## 可合成核心 (synthesizable core)

SV genvector 位选择的**生成**：从结构化 spec 拼出完整 `.sv` testbench 片段：
1. spec {prefix, dut_signal, bits, default_preset, presets{name,bit_indices}}
2. 外层 `` `ifndef <PREFIX>_LIST `` / `` `define <PREFIX>_LIST `` 包裹防重定义
3. 预设 `elsif` 链：每分支 `` `define <PREFIX>_LIST=<csv of bits> `` +
   `` `define NUM_<PREFIX>=<num> ``
4. `else` 默认分支 = default_preset 的 GT 值
5. 声明 `int EXP_SEL[NUM_<PREFIX>]='{<PREFIX>_LIST}` (显式尺寸 + 赋值模式, 避陷阱①)
6. 聚合总线 `reg [NUM_<PREFIX>-1:0] <bus>`
7. 表头循环上界 `NUM_<PREFIX>`，引用 `EXP_SEL[k]` 与 `dut_signal` (避陷阱② $size)
8. MSB-first 反序聚合赋值 `<bus>[NUM_<PREFIX>-1-k]=<dut_signal>[EXP_SEL[k]]`
9. `$fmonitor` 用 `%b` 打聚合总线 >= fmonitor_count 次

## reframe

把"改 ddr5_genvector.sv 把 exp_TDQ 位选择参数化"reframe 为 **spec-JSON 驱动 SV
文本生成器** `gen_genvector.py(spec)->{valid, sv_text, errors}`：
spec 给 {prefix, dut_signal, bits, default_preset, presets{name,bit_indices}}；
生成器输出 `.sv` text + valid/errors。交付物是 SV 文本 (不跑 ncvlog 二进制)，
check 解析 text + 独立 GT 复算每预设位集 (csv==join(bits), num==len(bits)) +
3 个 ncvlog 陷阱静态检测 (无 `int X[]={..}` 拼接初始化 / 无 `$size(` / 无 shadowed
count 宏) + malformed spec (num≠len / 位号越界 / 默认预设不在 list / presets 空)
→ valid=False + errors 非空且不抛异常。无 EDA 二进制依赖, LIVE-NA,
judge_layers=[L0,L1]。

与既有 D case 区别：
- r1654 BitlineLeakDeck = 漏电 deck 装配 (PVT corner × supply 缩放)
- r1653 NetNameConsistAudit = 网名一致性双向核 (partition+set diff)
- r1648 MosWByLayer = 层次 MOS W 遍历
- **本 case = SV genvector 位选择文本生成 (3 ncvlog 陷阱静态检测 + spec 驱动 SV emit)**，
  切面 = SV 文本结构 + 编译器陷阱静态扫 + spec→GT 位集独立复算，独立

## hidden-B (token-structural-disjoint)

`EXP_DQ`：prefix=DQ (vs A TDQ), 16 bits (vs A 12), 4 presets ALL16/HIGH8/LOW8/EVEN8
(vs A 6 presets ALL12/HIGH6/LOW6/HIGH4/MID4/LOW4), dut=exp_DQ (vs A exp_TDQ)。
前缀 / 位数 / 预设名 / 预设数量全异，token-structurally disjoint。A-hardcoder
喂 B → prefix 字面量全错 / 位宽 12≠16 / 预设名 6≠4 全 fail。

## negatives (trio distinct first-fail)

- empty → cond c (不产 submit.zip / gen_genvector.py)
- print_only → cond e (只打印期望 SV 不写文件)
- core_deleted → cond i (gen 返回 valid=False / sv_text 空)
- hardcode_a → cond e (B 前缀/位宽/预设名与 A 字面量错)
- ncvlog-pitfall concat-init stub → cond g (产 `int X[]={..}` 拼接初始化, 触陷阱①)
- ncvlog-pitfall $size stub → cond h (产 `$size(`, 触陷阱②)
