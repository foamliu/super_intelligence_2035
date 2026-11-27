# Deepread: udqmf — eco_dummy wrapper generation (rose3wang, digital)

- session: `1795576157175_udqmf.messages.json`
- user: rose3wang / host: hfeg0plg90 / mc: 169 / domain: digital
- trace_source keywords: rtl:355;netlist:83;verilog:52;synthesis:8;bandgap:8;.cdl:8;synopsys:7;mixed-signal:6
- size: 722KB / 201 msgs (104 user / 97 asst)
- claimed: r1492 (shard A, verification→digital)

## 用户意图梳理（produce-task 候选）

### U#1 (idx0, 主意图, act mode)
```
/proj/lacaa/V0/workdir/rose3wang/rtl_tv1/tsensor/tsensor.v
/proj/lacaa/V0/workdir/rose3wang/synflow/tsensor/flow_tsensor/results/tsensor.mapped.v
tsensor给我加一下eco_dummy
```
- 给两个文件（RTL 源 tsensor.v + 综合后 mapped.v），要求加 eco_dummy。
- 重复了 4 次（idx0-3，可能发送重试）。

### U#5 (idx51): "不要动原来的文件"
- 约束：不修改原 tsensor.v，新建文件。

### U#6 (idx61): 给出参考路径
```
... tsensor给我加一下eco_dummy 不动原来的文件
直接用下面这个可以吗？
/proj/lacaa/V0/workdir/rose3wang/rtl_tv1/psensor/eco_dummy_psensor.v
```
- 用户给出 psensor 的 eco_dummy 作为参考模板，问能否直接套用。

### U#7 (idx66): "重新定制一份 ，再生成一个wrapper"
- 要求：定制一份新的 eco_dummy，并生成 wrapper（不只是套用 psensor 模板）。

### U#9 (idx154): "把所有输入tie 0 CD tie1"
- 给 psensor 和 tsensor 两个 eco_dummy 路径，要求所有输入 tie 0，CD tie 1。
- 这是 eco_dummy 的核心逻辑：把原模块包起来，输入全 tie 0（CD 这种时钟/控制 tie 1），输出悬空/内部。

## 后续子意图（非主任务，k库/Q&A，可不作 case 主体）
- U#11/U#15/U#16/U#17/U#18/U#19/U#20: k库 lib_arc / tcl 循环 / capacitance 解释 / case_analysis / TR 分频 Q&A
- U#13/U#14: 简历优化（非 EDA）
- U#12: Retaining_rise/fall 解释

## 合成目标（DEBT — 下轮合成）

**case = L1 produce-task（digital），自包含 Verilog 生成，无需真跑 EDA。**

任务形态：给 tsensor.v（含 port list）+ 参考模板 eco_dummy_psensor.v，要求生成 eco_dummy_tsensor.v —— 一个 wrapper module，实例化 tsensor，所有 input port tie 0（CD 类 tie 1），output port 悬空（或内部 wire）。

### 需要从 trace 提取的真实素材
1. **tsensor.v port list**：需从 trace 抓取真实端口名/位宽（assistant 读取过该文件）。
2. **eco_dummy_psensor.v 模板**：参考结构（module 名、实例化方式、tie-off 注释风格）。
3. **CD tie1 规则**：CD 是哪个端口（需确认是 clk 还是 control）。

### 判分设计草案（≥8 断言）
- zip 内 eco_dummy_tsensor.v 齐全
- module 名 == eco_dummy_tsensor
- 实例化 tsensor（u_tsensor 或类似）
- 所有原 input port 在 wrapper 中被 tie 0（常数赋值）
- CD 端口 tie 1
- 原 output port 未被外部驱动（悬空或 internal wire）
- 端口位宽匹配（bus 位宽正确）
- 不修改原 tsensor.v（zip 内 tsensor.v == 原文 sha）
- hidden B：换一个模块（如 psensor 或 vsensor）的 port list，规模/端口名不同
- 负样本：空壳 / 只 print / 只套用 psensor 模板不改名 / tie-off 反了（input tie1）

### DEBT 原因
- r1492 候选搜索耗时（pool 重度挖掘，top A-pure 多 touched；7uaan Q&A 不适合 produce-task），到 udqmf deepread 完成已用 ~32min，剩余预算不足以完成 全量合成（assets/hidden/check.py 23+断言/negatives/selftest/SKIP_RUN 自验）。
- 下轮直接进入合成（素材路径已记录，port list 需从 messages.json assistant 段或原文件抓取）。

## 9 项全绿状态
- .75 REACH_OK hfhds201 RC0（open_session 秒级 + scp 722KB OK + ssh find OK）
- scan=11-28 不变（mc10=5374/mc30=4114/A_pool_mc10=4424，同 r1489）
- 本轮 0 改 check.py / 0 改既有 case / 0 改 judge_layers（纯新增 deepread + claim）
