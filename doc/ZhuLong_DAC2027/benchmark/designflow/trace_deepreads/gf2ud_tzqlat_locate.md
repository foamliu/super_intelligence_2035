# Deepread: 1793778069961_gf2ud (tongfanl @ hfhds201) — tZQLAT locate

**Trace**: `/home/tongfanl/.cline/data/sessions/1793778069961_gf2ud/1793778069961_gf2ud.messages.json`
- 222 msgs, 1077059 B, model glm-5.3-flash, 2026-11-04 07:41 → 11-05 01:32, completed
- kw=231 (spice-dominant), NOT in ledger before this round (hfhds201 cron 盲区 diff)

## User turns
- **U#0 (任务说明轮 → A-faithful prompt)**: 「抽激励的环境：/proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen_local/ 帮我看下环境里  ZQLAT命令到下一个Valid Command的时间tZQLAT是多少。」(提出需求, 无根因/修复 → 符合 A-档选轮)
- U#43「continue，timing.load.sv」/ U#74「continue」: nudge, 不入 prompt
- U#103「tZQLAT应该是ZQCAL LATCH命令到下一个有效命令的时间吧。tZQLAT 参数值 = 30 ns是如何加载到波形中去的？为啥我在波形上看，ZACAL LATCH到MRR之间的时间是14ns？」: 用户给理解+提差异 → 排除出 prompt
- U#105「/home/tongfanl/DDR6/DSCQA/analogsim/WTM 帮我检查下这个文件夹下的几个pattern有没有问题」: 新任务(WTM 检查), 与本 case 无关
- U#192「我修改了下，你再看下」: U#105 follow-up

## Assistant 工具链 (U#0 → U#102)
list_allowed_files(vecgen_local) → search_codebase(ZQLAT) [超工作区失败] → read_files(ddr6_timing.sv) → run_approved_command(grep ZQLAT via python search_zqlat.py, 多版迭代) → read_files(timing_load.sv 1220-1300/1400-1440/60-200/1-60/200-320, ddr6_package.sv 395-430/1140-1180, ddr6_tasks.sv 1300-1540/1405-1480) → 确认 max_val@ddr6_tasks.sv:2017

## 金标准 (assistant 结论, 人工复核 ✓)
- **tZQLAT = max(30ns, 4×tCK) = 30 ns (30000 ps)**
- 声明: `ddr6_package.sv:3089-3090` — `// ZQCAL latch quiet time` / `int tZQLAT, tZQLAT_min;`
- min 赋值(硬编码): `timing_load.sv:1237` — `timing.tZQLAT_min = max_val(30000,4*timing.tCK);  // max(30ns, 4tck)`
- 最终赋值: `timing_load.sv:1423` — `timing.tZQLAT = tminmaxselect(timing.tZQLAT_min, timing.tZQLAT_min, t_mode);`
- 操作码: `ddr6_specdef.sv:2059` — `parameter bit[MPCOP_BITS-1:0] OP_ZQCal_Latch = 'b10000110;` (OP_ZQCal_Start@2058 注释掉)
- 单位 ps (`timescale 1ps/1ps`) → 30000=30ns
- **tZQLAT_min 不在 timing table 的 ts_val 读取列表** (timing_load.sv:178-181 只读 tZQCAL4/8/16_min + tZQSTOP_max) → 硬编码, 非表格驱动
- max_val 为普通取大函数 (ddr6_tasks.sv:2017)
- tzqlatchclkcycle 声明于 ddr6_package.sv:1163 但 vecgen 侧未赋值/未消费 (预留)

## 合成 (A-faithful L1, spice_sim)
- 通用化: `locate_tzqlat.py <vecgen_root> -o out.json` 扫所有 .sv/.v/.svh/.inc, 正则提取 声明/min赋值/最终赋值/opcode/max_val_fn/timing_table_reads/tzqlatchclkcycle/issue_count/computed_value
- A = A_vecgen (真实 4 文件节选: ddr6_package.sv / timing_load.sv / ddr6_specdef.sv / ddr6_tasks.sv)
- hidden B = B_vecgen (并行 DDR6 环境: tZQLAT_min=25000/25ns/3tck, opcode 'b10000111, 同结构不同值)
- 判分 17 断言(a-q): 含交叉输入守卫(候选在 A 跑得 30000/10000110/30.0, 挡硬编码 B) + A-only 泄漏闸门 + 3 次幂等 sha256
- 自验: ref PASS 17/17 + 4 neg 全 FAIL distinct(d/e/f/q) + §4.9 三假(空壳/打印期望/删核心)全 FAIL + 断言闸门 k=17==17≥8
- 落库: EDA-Eval-DesignFlow_B.jsonl 154→155 + mark ledger (spice_sim 120→121)
