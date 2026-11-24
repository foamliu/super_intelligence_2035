# r1130 深读 · reedchen @ hfeg0plg93 · lbsbf · QuotedUnitValueNormalize

## trace 溯源
- session: `1793085965170_lbsbf.messages.json` (2 msgs, 13497B)
- user: reedchen · host: hfeg0plg93 · mc=17 (hspice:7;finesim:6;spice:2;simulator:1;netlist:1)
- match_count=17, domain=spice_sim, shard B
- ledger: r1130 claim ✓

## 用户真实意图（原文 MSG0）
reedchen 把 SPF/RCC 抽取网表里的若干电阻实例定义贴进自己的 FineSim testbench：
```
.inc "/proj/ddgoa/V0/ver/lvs/ddgoa_cmos_work/DbusTB_1012_1014/lpe/DbusTB_1012/DbusTB_1012.spf_RCC"
.inc "/rundata/ddgoa/V0/simdir/finesim/workdir/yifansun/simulation/subckt"
*instence initialization
XI_DbusTB_1012 D D1 D1_Dq ... DbusTB_1012
r0 vintbusDq6! vintbuspin '8.995Ohms'
r8 vintbusDq2! vintbuspin '6.991Ohms'
r7 vintbusDq1! vintbuspin '6.954Ohms'
r5 vintbusDq5! vintbuspin '8.124Ohms'
r4 vintbusDq3! vintbuspin '6.913Ohms'
r3 vintbusDq4! vintbuspin '7.528Ohms'
r2 vintbusDq7! vintbuspin '9.505Ohms'
r1 vintbusDq0! vintbuspin '6.877Ohms'
```
FineSim 报错（8 条）：
```
ERROR! undefined parameter or function definition '8.995ohms' (postsim_FF.82V-40C.sp:32)
... (line 33-39 同样模式)
```
用户问："我这样在 tb 里面定义好像会报错，有没有什么解决办法"

## assistant 解答（MSG1 thinking+text）
- 诊断：单引号 `'8.995Ohms'` 让 FineSim 解析器把 `8.995Ohms` 当成**表达式/字符串**求值，搜索名为 `8.995ohms` 的参数/函数；`Ohms` 不是 SPICE 内置单位后缀（标准缩放后缀是 T/G/MEG/K/M/U/N/P/F），所以报 undefined。
- 根因：原抽取网表里 `'8.995Ohms'` 能过是因为抽取工具在文件头带了 `.PARAM`/单位定义；reedchen 单独把 r 定义贴进 TB 没带那些定义。
- 修复（推荐）：电阻值直接写纯数字，去引号去 `Ohms`：
  `r0 vintbusDq6! vintbuspin 8.995`
- 备选：保留数值+单位写法需先定义单位，但没必要。
- 提醒：r7/r8/r6 节点只连了一个 `vintbuspin`，确认另一端 `vintbusDqX!` 在 TB 里存在，否则"未定义节点"。

## reframe（合成方向）
**有效意图 = 把 SPF 抽取网表里"单引号+非标准单位后缀"的 R/C/L 值规范化成 FineSim 合法纯数字**。
- 抽取网表常见写法：`'8.995Ohms'` / `'2.2Kohms'` / `'1.5pF'` / `'10nF'` / `'4.7uH'` 等
- FineSim 把单引号内容当表达式求值 → 非标准单位后缀报 undefined parameter
- 程序化交付：Python stdlib 工具读网表 → 识别 R/C/L 实例行（含 `+` 续行）→ 剥离单引号+非标准单位后缀并按隐含 scale 换算 → 输出规范化网表(stdout) + JSON 变换报告(stderr)
- L1 纯 Python，domain=spice_sim，与近期 B 档案例同形态

## case 设计
- **A（可见）**：reedchen 原场景 8 个电阻 r0-r8，值 8.995/6.991/6.954/8.124/6.913/7.528/9.505/6.877，全 `'XOhms'`
- **hidden B**（三重 anti-hardcode）：① 实例名异 A（R_pull_a/R_pull_b/Rgate/Rsense/Cload/Cpar/Lchoke...）② 值异 A ③ 单位混（Ohms/Kohms/Farads/pF/nF/uH 而非全 Ohms）④ 含 `+` 续行带 quoted-unit ⑤ 含 `'tdelay'` quoted-非单位-token（必须 NOT 被规范化，反 over-normalize）⑥ 含纯数字 R 行（skipped）⑦ 含注释/`.subckt`/X 子电路调用（不可改）
- **check 12 条**：a(zip+compile+size) b(B exit0+stdout+stderr JSON) c(JSON 结构) d(instances 字段类型) e(normalized_count==oracle) f(unit_breakdown==oracle) g(每条 normalized_value==oracle num*scale) h(stdout R/C/L 行无 quoted-unit 残留+非单位 quoted 保留) i(注释/.控制/X 行字节不变) j(`+`续行 quoted-unit 被规范化且入 instances) k(skipped_count==oracle) l(3-seed sha256 一致)
- **§4.9 三假**：空壳(无 JSON→b/c fail)/只print A 期望(B 值不同→e/f/g fail)/删核心(quote-detection stub→normalized_count=0→e fail)
