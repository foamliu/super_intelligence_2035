# Deepread: wlxsu — xrun.log 报错自动修 libs (verification, B档 synthesized)

- **trace**: `1795003416811_wlxsu` / harveyl @ hfeg0pfn085 / mc=128 / 152 msgs (86 user / 66 assistant) / 623KB
- **session_file**: `/home/harveyl/.cline/data/sessions/1795003416811_wlxsu/1795003416811_wlxsu.messages.json`
- **domain**: verification (xrun/verilog/netlist/pt_shell；verilog:1704 / netlist:514 / pt_shell:78)
- **A-faithful 提需求轮**: ✓ U#0 单 shot 提出能力需求（修 libs 的两条规则），未给具体修复实现

## U#0 (逐字原文)
```
你的理解没有问题，现在需要更新：6.0部分在原网表路径/proj/drvqa/V0/simdir/verilog/lhtian/verilog.ddr5.drvqa.netlist/netlist下对应路径提交任务；除此之外，如果检测到build_file中/noregression.x8/xrun.log报错，你需要根据报错结果修改libs，如果显示有module缺失，你可以在libs下寻找和缺失module命名最相近的module，将其复制后更改命名作为缺失module的补全，如果是libs和网表pin对应不上，在libs中进行对应修改，以上所有的修改都需要生成rpt共我查看
```
意图：扩展 `drvqa-autobuild` skill —— 检测 xrun.log 报错后自动修 libs：
1. 缺失 module → 在 libs 下找命名最相近的 module，复制+改名为缺失 module 补全；
2. libs 与网表 pin 对不上 → 改 libs 端口；
3. 所有修改生成 rpt 供查看。

## 为什么 B 档（不是 A 档）
真实资产 `/proj/drvqa/` 是 drvqa 组私有（Permission denied），无法拷出真实的 xrun.log / libs / netlist。
但用户意图清晰且规则完全可参数化，故用同构合成资产（DDR5/drvqa 主题 A，LP5 主题 hidden B）还原。

## agent 工具链（trace 摘要）
- 读 drvqa-autobuild skill 既有逻辑 → 理解 6.0 提交流程
- 解析 xrun.log 两类报错格式：`*E-MODNTF` (module not found) + `*E-PINMIS` (port width mismatch)
- 缺失 module：Levenshtein 最近名 → 复制 module 块 → 改名 → 落新文件
- pin 不匹配：定位 libs 端口声明 → 改位宽为 netlist 期望
- 生成 JSON rpt（modifications 列表）

## 合成计划（B 档 · §5 produce-task reframe）
真实执行非确定性（依赖真实 libs 内容 + xrun 报错实例）→ 降级为参数化 `fix_libs.py`：
- **A 资产**：DDR5/drvqa 主题，2 缺失 module + 1 pin 不匹配
  - `xrun_log_A.txt`、`libs_A/{simlib_drvqa_digital.sv, simlib_drvqa_array.sv, simlib_drvqa_io.sv}`、`netlist_A.v`
- **hidden B**：LP5 主题（反硬编码），3 缺失 module + 1 pin 不匹配（不同名/位宽）
  - 缺失：`lp5_cmd_dec_x8`←`lp5_cmd_dec`、`lp5_addr_buf_4r`←`lp5_addr_buf`、`lp5_timing_gen_odd`←`lp5_timing_gen`
  - pin：`lp5_refresh_ctrl` 端口 `req` 从 `[0]` 改成 `[2:0]`（在 `simlib_lp5_ctrl.sv`）
- **判分**：check.py 内联 build_env_b 真跑 SUT fix_libs.py on B，15 条独立断言
  - 落盘 3 缺失文件 + 改名正确 + body 与源块逐行一致 + 最近源正确
  - pin 位宽改对 + netlist 不动 + rpt 4 条结构正确
  - 幂等（再跑 rpt 空）+ 确定性（3 跑字节一致）+ 反硬编码（无 ddr5_*/simlib_drvqa 字面量）

## 反硬编码设计
A 用 DDR5/drvqa 名（`ddr5_dq_drv`、`simlib_drvqa_*`），B 全用 LP5 名（`lp5_*`）。
SUT 若硬编码 A 名作为字面量，在 B 上永远匹配不到 → ⑮ 扫源码字面量直接 FAIL。
A 名清单（check.py A_ONLY_FORBIDDEN）：
`ddr5_dq_drv`、`ddr5_dq_drv_a`、`ddr5_dqs_pll`、`ddr5_dqs_pll_top`、`ddr5_wr_fifo`、
`ddr5_addr_buf`、`ddr5_cmd_dec`、`ddr5_io_pad`、`ddr5_wr_fifo_aux`、`simlib_drvqa`

## 自验
- ref `fix_libs_ref.py` on B: EXIT=0, 4 modifications (3 missing + 1 pin), 幂等 rpt=[], 3 跑字节一致 ✓
- check.py 15 条全 PASS ✓
- 5 negatives 全 FAIL（③ / ⑤ / ⑤ / ⑮ / ⑪ 各档独立）✓
- §4.9 a/b/c (empty/print-only/core-deleted) 全 FAIL ✓
- e2e embedded test field 独立跑 PASS ✓

## case 落位
- `cases/A/EDA-Eval-DesignFlow-XrunLibsFixProduce-001.json` (source of truth, 37608B)
- `EDA-Eval-DesignFlow_A.jsonl` 第 375 行（401 case 总计，原 400 → +1）
- ledger `trace_ledger_A.tsv`: wlxsu → case (EDA-Eval-DesignFlow-XrunLibsFixProduce-001)
