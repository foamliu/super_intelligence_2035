# Deepread: 1794815174300_xotrf (cliu @ hfeg0plg19, mc=275, schematic_netlist)

## session 概况
- 451 messages, 1.68MB, agent=lead (zhulong), 2026-11-16
- 用户意图：在 `/home/cliu/c_VeriligLibVerifier_Archieve` 上用 Verilog 镜像比对(mirror-compare)框架跑 dscqa digital 库验证
  - golden = `final_merged_netlist_digitial.v`（317 module）
  - DUT = `simlib_dscqa_digital.sv`（734 module）
  - simlib = base + TECHLIB（本地缺 TECHLIB_add / LVS / _gld.v）
  - 仿真目录 = `digitial_sim_log`

## agent 做了什么（真实流程）
1. 探目录、读 `verify_cell.py`（mirror-compare 框架：逐 cell xrun 编译仿真比对 golden __gld alias vs DUT）
2. 发现本地缺 simlib 2 文件 + golden alias，patch `verify_cell.py` 只编译存在的 2 个 simlib
3. golden 引用 stdcell 子模块(invYx4 等)不在 digital 网表 → 合并 digital+stdcells+stdcells_ac 三份 merged netlist 建 combined golden(1474 def)，生成 __gld alias
4. 写驱动 `run_local_dscqa_digital.py`：common cell 列表、逐 cell verify_one、--resume 断点续跑、--free 清 build/worklib(磁盘只有 2.15GB)、--scrub 清临时脚本
5. 跑完 298 common cell（294 出 result.json + 4 个 DUT 缺定义 NOT_IN_DUT），分类 PASS / FAIL(功能 mismatch) / TIMEOUT / XRUN_ERROR(SOURCE_GAP，golden 引用未定义子模块如 invIOLV_pc60/nand2IOLVIO)
6. 第二轮用户问「simlib 只用目前两个文件能跑起来吗」→ 确认 verify_cell.py 已收敛 simlib 列表，能跑

## 可造题的内核（extracted intent）
离线可验证性分析：Verilog 解析 → common cell → 每个 cell 的子模块引用 → 判定 PASS_CANDIDATE(all resolved) / SOURCE_GAP(有未定义子模块) / NOT_IN_DUT(DUT 缺可解析 module)。这是确定性、可自包含、可 subprocess 验证的内核，不需真 xrun。

## 造题决策
- task_id: EDA-Eval-DesignFlow-VerilogMirrorCompareAnalyze-001
- L1（离线 Python Verilog 解析，不依赖 EDA 沙盒/xrun）
- A 档: 10 golden module（7 PASS / 2 SOURCE_GAP / 1 NOT_IN_DUT），6 simlib 原语
- 隐藏 B: 8 golden module（4 PASS / 3 SOURCE_GAP / 1 NOT_IN_DUT），5 simlib 原语，模块名/原语名/分布均与 A 不相交
- check.py 12 条独立断言，含反硬编码扰动（不给 --simlib 重跑，仅叶子 or3_gate 仍 PASS，6 个变 SOURCE_GAP）
- 3 负样本(print_only/core_deleted/hardcode_a)全 FAIL，reference 12/12 PASS
- 已自验：reference A 报 golden=10/common=9/PASS=7/GAP=2/NOT_IN_DUT=1；B 报 golden=8/common=7/PASS=4/GAP=3/NOT_IN_DUT=1；no-simlib B 报 PASS=1/GAP=6
