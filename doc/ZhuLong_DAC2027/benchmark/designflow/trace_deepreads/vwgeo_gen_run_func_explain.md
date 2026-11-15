# deepread: vwgeo — gen_run.py 功能解释 Q&A

- **session**: 1792546653992_vwgeo
- **user/host**: deniss@hfeg0plg91 (10.129.8.223), mc=74
- **domain**: waveform (FSDB 波形后处理)
- **trace 来源**: /home/deniss/.snapshot/hourly-new.2026-11-14_1700/.cline/data/sessions/1792546653992_vwgeo/ (live dir 已清，snapshot 保留)

## verbatim 用户轮

- **U#0**: `@gen_run.py 分析文件功能` —— 核心意图：解释 gen_run.py 脚本做什么（code-grounded function-explanation Q&A）
- U#2: `fscript GLIBC_2.17 not found 怎么处理` —— env-fix（GLIBC 版本问题，本 case 不取）
- U#3: `@run_all.sh 想办法让这个脚本正确跑起来` —— script-fix（本 case 不取）

## 助手响应（U#0）

助手读 gen_run.py 后给出详细功能分析：脚本是一个**仿真后处理自动化生成器**，从 FineSim/NanoSpice 仿真产出的 FSDB 波形文件路径中提取 PVT 信息（如 SS0.92V-40C）与版本号（如 X2P6），按版本决定执行哪些测量命令（all_CAS_RD_timing / all_CAS_WR_timing / all_CAS_RMW_timing），生成 fscript 测量 tcl 脚本（gen_run_*.tcl）与批量运行 shell（run_all.sh）。

## gen_run.py 关键结构（真实源码）

- `fsdb_list`：内嵌 3 条 FSDB 路径
- `conners_pattern = r"(X\d+P\d+_\d+\.[^/]+?\.X\d+P\d+)"`：提取版本号+PVT
- 版本分支：`X2P6/X1P6 → +WR_timing`，`X2P3 → +RMW_timing`
- 输出：`gen_run_{pvt}.tcl` + `run_all.sh`（fscript 并行执行）
- `os.makedirs("outputs")` + `os.system("chmod +x run_all.sh")`

## case 设计

- **case_id**: EDA-Eval-DesignFlow-GenRunFuncExplainQA-001
- **形态**: code-grounded function-explanation Q&A → tool reframe（套 #254 v2 pattern）
- **reframe**: 候选写 `script_func_explain.py` 读脚本源码 + 问题 → 结构化功能解释 JSON（question/script_summary/purpose/key_components/workflow_steps/output_artifacts/cited_identifiers/overall_function），cited_identifiers 必须 grounded 于真实源码
- **assets A**: gen_run.py（真实源码）+ question_A.txt（逐字）+ README.md
- **hidden B1**: pmt_agg.py（fscript .pmt 聚合工具，不同脚本同问题）
- **hidden B2**: pwl_gen.py（HSPICE PWL 激励 deck 生成器，不同脚本不同问题措辞）
- **hidden B3**: dump_config.py（trivial 配置打印，优雅降级）
- **check**: 15 条件 a-o（grounding + 反硬编码 A 专属标识符 + data-driven + 优雅降级 + 确定性）
- **自验**: REF PASS 15/15 ✓ / 3 negs 全 FAIL ✓ / §4.9 退化全 FAIL ✓ / k_rationale==k_check==15 ✓
- **交付**: r722，D.jsonl 413→414
