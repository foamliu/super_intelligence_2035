# Deep-read: 1789453040533_94ezt — junxu FIFO block-sim

- **user**: junxu
- **host**: hfeg0pkn005 (10.129.2.14)
- **session**: 1789453040533_94ezt.messages.json (582KB)
- **date**: 2026-09-15
- **match_count**: 183 (spice_sim, hspice:224/netlist:306/schematic:118)
- **status**: FRESH → claimed r997 → case EDA-Eval-DesignFlow-BlockSimHarnessGen-001

## User intent (U[0])
> /block-sim /home/junxu/.cline/skills/block-sim 解析相对路径时按照文件本身路径进行解析。
> 对 cli_test_lib fifo_3x8 进行仿真，验证 fifo 功能

## Task
junxu 用自建 `block-sim` skill 对 `cli_test_lib` 里的 `fifo_3x8` 做 FineSim block-level 仿真，
验证 FIFO 功能。block-sim 是一条 5 阶段流水线：

1. **netlist extraction** — `extract_netlist.py` 从 schematic 经 virtuoso-cli 抽 hspiceD flat netlist
   （force `setTopLevelAsSubckt=nil`，`cxmt_SchmaticTool_Dsim_SpiceOut`）
2. **PVT corner setup** — `vrwck_lookup.pl` 从 vrwck.csv 双线性插值 pvdbias，生成 `pvt.sp`
   （每 corner 一个 `.lib` block：pcorner/ptemp/.temp/pvdbias/model .lib/voltage .inc）
3. **control file** — agent 从 `control-template.md` 生成 `sim.sp`
   （.option + model .lib + .inc stimulus + .lib pvt.sp 主corner + .tran + .probe + .meas + .inc netlistHeader + .inc netlist + .alter blocks）
4. **stimulus** — agent 从 `stimulus-template.md` 生成 `stimulus.sp`
   （按 pin 类型 PWL/DC：clock=方波、reset=复位脉冲、data=PWL、enable/shift=电平；电源来自 voltage file 不在 stimulus 加）
5. **sim & results** — `run_simulation.py` LSF `bsub -K` 提交 + `extract_results.py` 解析 `.mt0.csv`

## FIFO 结构 (from 57i4y compression summary)
- 3-stage 8-bit FIFO (`fifo_3x8` in `cli_test_lib`)
- data path: `mx_s0` → `mx_s1` → `mx_s2` → `DOUT`，每个 mux 按 `SHIFT` 选 feedback 或 input
- control: 2-bit counter `(cnt1,cnt0)` 跟踪 fill level；`EMPTY=~(cnt1|cnt0)`，`FULL=cnt1&cnt0`
- `SHIFT=0`: hold (feedback); `SHIFT=1`: shift forward
- 验证激励: RSTN 复位(0-5ns) → DIN<0>=1, SHIFT=1, 3 CLK edges 传播 DIN→s0→s1→DOUT

## Reframe (r997)
produce `blocksim_gen.py`：读 netlist+pins+simconfig+corners → 生成 pvt.sp/sim.sp/stimulus.sp/meas.sp/harness_report.json。
- A: fifo_3x8 (3-stage 8-bit, CLK/RSTN/SHIFT/DIN<7:0>/DOUT<7:0>/EMPTY/FULL, 5 corners, 10p/40n, 0.9v, model/current)
- B: shift_4x16 (4-stage 16-bit, CLK/RSTB/EN/DIN<15:0>/DOUT<15:0>/FULL, 3 corners, 5p/80n, 1.0v, model/v2) — 结构全异 anti-hardcode

## Related lineage (same task family, NOT claimed)
- 1789374352756_57i4y — skill-building continuation (compressed, 2 compression cycles)
- 1791533874882_mxct2 — later re-run (2026-10-09, deepseek-v4-flash, "调用 block-sim 对 cli_test fifo3x8 仿真")
- 1789025585206_gzpja — block-design skill (FSM impl, different task)

## Files used
- `/home/junxu/.cline/skills/block-sim/SKILL.md` (full pipeline doc)
- `/home/junxu/.cline/skills/block-sim/references/control-template.md` (sim.sp template + .meas examples)
- `/home/junxu/.cline/skills/block-sim/references/stimulus-template.md` (pin classification table)
