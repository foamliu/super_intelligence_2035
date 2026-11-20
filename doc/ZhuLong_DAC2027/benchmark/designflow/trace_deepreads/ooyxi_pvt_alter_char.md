# 深读：ooyxi — sophiaw AnasimPro PVT 仿真 skill + testbench + 数据收集报告

**trace**: sophiaw @ hfeg0plg09 (172.16.8.175), session `1787897609476_ooyxi.messages.json`, mc=394, model=glm-5.2, 157 msgs, 3 用户轮，status=failed (stale_session_reconciler)。cwd `/proj/train/AI_Virtuoso/workdir/sophiaw`。

## AnasimPro 代码库（agent 深读 msg 1-29）
PyQt5 EDA **仿真管理工具**（非仿真器本身），驱动 HSPICE/FineSim/PrimeSim。核心模块：
- `alter_generator.py` — `generate_alter_statements(runset_cfg)`：从 runset config 生成 PVT `.alter` 块
- `benchmark/engine.py` + `excel_writer.py` — 多 domain benchmark 报告（Excel）
- `core/meas_file_parser.py` — 解析 HSPICE `.ma0/.mt0` 测量文件（正则 `[0-5]` 后缀）
- `tabs/runsim_control.py` + `runsim_mixins/sim_execution.py` — 仿真执行
- `tabs/pvt_generator.py` — PVT 角矩阵生成
- `core/skill_bridge.py` / `simfolder_context.py` — skill 桥接 + sim folder 上下文
- `core/__init__.py` / `benchmark/__init__.py` 触发 PyQt5 import → headless 不可直接 import

## 三轮用户意图
- **T1 (msg 0, act)**: 「请根据 /proj/.../AnasimPro 路径下 AnasimPro 的代码，生成一个 skill，后面用户可以用自然语言的形式来调用这个仿真程序，完成一系列的仿真，数据收集，报告生成等等。」
- **T2 (msg 69, plan)**: 「/anasim-pro 帮我在 当前工作空间中生成一个适用 anasim 仿真的 testbench」
- **T3 (msg 95, plan)**: 「收集 testbench_inv 的仿真数据并生成报告」

T2/T3 是「表达目标」轮（未给根因/方案）→ 可作 A 档任务说明候选。

## agent 真实工具链产物
1. **anasim_cli.py** (msg 45) — headless CLI 包装非 GUI 功能：`setup-folder / analyze-spice / generate-alters / build-runsim / collect-meas / benchmark`。绕过 PyQt5 import 链（`types.ModuleType('core')` stub）。msg 47-58 全命令测试通过。
2. **anasim-pro SKILL.md** (msg 59) + INDEX.md 更新 (msg 61)
3. **testbench_inv/** (msg 82-94)：`inv_tb.sp`（CMOS 反相器 DUT，tran 延迟 + DC voh/vol + 功耗 pavg）+ `inv_runset.cfg`（model path + .inc markers + alter 模板）+ `alter/inv_tb_alters.sp`（**64 PVT 角 = 5 MOS 角 × 3 温度 × 4 cload**）+ `runsim/runsim.sh`（FineSim）
4. **真实仿真** (msg 95-156)：
   - FineSim `libstdc++` 冲突 → 改 HSPICE
   - 模型文件缺 `.MODEL` 关键字 → HSPICE abort（`nmos nmos` 被当器件实例）→ 修
   - HSPICE 跑 65 alter 块成功，产出 `.mt64/.ms64/.lis`
   - **gotcha 1**: `.mt64` 后缀不匹配 AnasimPro 正则 `[0-5]` → `ln -sf inv_tb.mt64 inv_tb.mt0`
   - **gotcha 2 (核心)**: HSPICE `.alter` 只把**最后一个 alter** 的测量写进 `.mt0/.ms0` 及 `.lis` 详细段；前面 alter 的数据要从 `.lis` 重复测量节按 alter 顺序抠
   - **gotcha 3**: 瞬态 `.measure` trig/targ 方向错（输入下降→输出上升，反了）→ `tpdf/trise_meas = failed`
   - agent 手工构造 `inv_tb_meas.ma0`（13 列 vsw/voh/vol/pavg/pwr…）→ `collect-meas` 解析成功 → `benchmark` 生成 `benchmark_report.xlsx`（5704B, 3 domain）+ `simulation_report.txt`

## 可复现子技能（本 case 抽取）
**PVT 角表征：从 runset config 生成多 alter HSPICE deck → 真跑 HSPICE → 从 `.lis` 按 alter 顺序抠每角测量（`.mt0` 只存末角是核心陷阱）→ 产 per-corner 报告 JSON**。

不可移植部分：AnasimPro PyQt5 代码库 + CXMT foundry 模型 + LSF。可移植核心：runset→alter 生成 + HSPICE 真跑 + `.lis` per-alter 抽取 + 角报告。

## 与现有 InvPVTchar-001 的区分
InvPVTchar：给 deck，解析 `.lis` 找**最坏角** (argmax tpd)。本 case：候选须**从 runset config 生成 alter deck** + 抽**全 per-corner 表**（角标签 mos_corner/temp/cload 与测量按生成顺序正确关联）→ 击破「只收测量值不跟角标签」的 naive 解析。新增 generator 维度 + 全表 + 角标签关联。

## 真陷阱（烤进任务）
1. **`.mt0` 只存末角**：候选必须从 `.lis` 重复测量节按 `.alter` 顺序抠每角；只读 `.mt0` 只得 1 角 → 报告角数错。
2. **角标签关联**：`.lis` 测量节按 alter 出现顺序排列；候选须按自己生成的 alter 顺序（mos_corners×temps×cloads 笛卡尔积序）回贴标签。错序 → 角↔测量错配。
3. **瞬态 meas failed → not_met**：trig/targ 方向错或未触发返回 `failed`；须报 `not_met`，不当 0、不崩。
4. **HSPICE `.MODEL` 关键字**：模型文件须 `.MODEL nmos NMOS LEVEL=1 ...`，bare `nmos nmos` 被当器件。
