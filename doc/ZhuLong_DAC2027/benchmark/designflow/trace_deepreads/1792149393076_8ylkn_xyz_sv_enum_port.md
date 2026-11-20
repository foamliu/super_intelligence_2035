# Deepread: 1792149393076_8ylkn (xuluo @ hfeg0pkn001, mc331, digital/verification)

**Session**: `/home/xuluo/.cline/data/sessions/1792149393076_8ylkn/1792149393076_8ylkn.messages.json` (1.82MB, 292 msgs, 31 user_input turns)
**Host**: 10.129.2.10 (hfeg0pkn001), user xuluo
**Keywords**: verilog:1250;rtl:801;netlist:676;aether:51;systemverilog:42;cadence:25;mixed-signal:12;schematic:6
**Domain**: verification (DRAM Row-Hammer cyclic_xyz regression testbench enumeration)

## 真实任务主题

DRAM Row-Hammer (RHR) 仿真验证：`cyclic_xyz` pattern 用 x_num/y_num/z_num 三参数控制锤击地址循环。
- **SV 侧** (`/proj/dbcoa/V0/simdir/verilog/tsq/regression/cyclic_xyz/`): `xyz_regression.sv` 是枚举生成的 plusarg 清单（4409 行），`cyclic_xyz.sv` 是执行用的 hammer pattern（z→y→x 三层循环 + `$urandom_range(2,5)` 行距），`rhr_parameter.pkg` 给时序参数。
- **Python 侧** (`/proj/ddcpc/V0/workdir/gaozequn/PycharmProjects/PyRHR/`): `paralist_gen.py` 用三维笛卡尔积网格扫参（x∈[1,2,3,5..11], y∈1..39, z∈[1,2,3,5..11]），生成 `paralist.csv` 喂 Python 行为模型。
- **根因差异**：Python 笛卡尔积 53.5% 组合欠预算（x·y·z < 窗口 ACT 预算），直接搬到 SV 会超频刷新（REF 周期 << tREFI）；SV 用预算反推 z = act_max/(x·y)+2，只生成填满窗口的组合。

## 关键用户轮（31 个 user_input）

| # | 内容 | 性质 |
|---|------|------|
| 0 | 分析 cyclic_xyz 目录代码 + Python JSON 参数，对比差异 | 初始需求 |
| 26 | 列表对比所有 python 参数 | 追问 |
| 65 | nREFinBurst_replace 在 verilog 中没有？burst 刷新机制 | 追问 |
| 93-125 | under2 (DisUnder2) 地址保护功能深挖 | 追问（已给根因） |
| 153-181 | pkg 280ns vs driver 380ns tRFC 矛盾 | 追问（已给根因） |
| 204-254 | xyz 组合分布机制（1/169/3 vs 1/1/255）深挖 | 追问 |
| 256 | 贴 Python paralist_gen.py 代码 + "这是python用于生成xyz的方式，和sv是不是不同啊" | 提供代码 |
| **262** | **"你修改这里的代码，使得xyz逻辑和sv一样"** | **★ 唯一 clean 修复需求** |
| 291 | 总结对话 | 收尾 |

## A 档选轮：USER#262

"你修改这里的代码，使得xyz逻辑和sv一样" — 唯一不携带根因/方案的修复指令（USER#0 是分析需求非修复；USER#256 是贴代码+提问；其余用户轮要么是追问要么已点出根因）。

## 真实产物（gold）

agent 写了 `gen_paralist_sv_aligned.py`，按 SV enumeration 逐行对齐：
```
act_max = (burty*(tREFI - tRFC) - tRC) // tRC + 1   # 窗口 ACT 预算（整数除法）
for x in 1..act_max:
    y_max = act_max//x + 1
    for y in 1..y_max step 2 (odd only):             # y_step=2，与 results.csv 4336 次 sweep 一致
        z = act_max // x // y + 2                    # z 由预算反推（因变量，非自由）
        if x*y*z >= act_max:                          # 过滤：窗口必须填满（REF周期≈tREFI）
            if y==1 and printed: skip                 # y==1 去重：仅 x=1 输出一次
            emit(burty, x, y, z)
            if y==1: printed = True
```
- 用 `verify_sv_enum.py` 重建清单 vs `results.csv` 4336 次实际运行 100% 吻合（0 缺失）。
- spot-check: 1/1/255 ✓, 1/169/3 ✓, budget violation 0, odd-y 100%。

## 验证（本深读独立复算）

gold 公式 vs `xyz_regression.sv`（authentic，从 trace tool_result 提取，前 808 行含 burty=1 全量 636 条 + burty=2 前 172 条）：
- **burty=1: 636 组合，100% 吻合（sv-only=0）**
- 总 gold: 4408（burty=1:636 / burty=2:1446 / burty=3:2326）
- act_max: burty=1→253, burty=2→507, burty=3→761（tREFI=15600, tRFC=380, tRC=60 ns，4x 时基）

## 合成方案（A 档 faithful）

- **prompt** = USER#256 (Python 代码原文) + USER#262 ("你修改这里的代码，使得xyz逻辑和sv一样") 逐字
- **assets (可见 A)**: `paralist_gen.py`(原笛卡尔积) + `cyclic_xyz.sv`(hammer pattern 50 行) + `xyz_regression.sv`(枚举清单 808 行) + `rhr_parameter.pkg`(时序) + `config_A.json`(tREFI=15600, burty=[1,2,3])
- **gold**: `gen_paralist_sv_aligned_ref.py`（CLI `<config.json> [-o out.csv]`，读 config 的 tREFI/tRFC/tRC/burty_values，按枚举公式生成 tab-delimited CSV，burty_num 写入每行）
- **hidden B**: `config_B.json`(tREFI=7800 2x 时基, burty=[1,2]) → act_max(1)=123, act_max(2)=247, 总 878 组合，B 不含 1/1/255（反硬编 A）
- **check.py 18 conds (a-r)**: a-b zip/compile; c-j [A] 静态(结构/行数/1-1-255/1-169-3/窗口填满/y奇/z反推/y==1去重); k-r [B] subprocess 跑隐藏 B(行数/窗口填满/z反推/y奇/确定性/无欠预算/首组 1/1/125)
- **negatives**: naive_cartesian(原笛卡尔积) / always_255(硬编 z=255) / copy_gold_A(无视 config 输出 A 的 CSV) / empty
