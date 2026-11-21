# deepread: 1yumf — shanliny mos_compara FineSim deck fix

**session**: 1795143772734_1yumf · user shanliny @ hfeg0plg107 · mc=111 · spice_sim/characterization
**trace_source**: scan snapshot ssh_eda_search_20261121_151844/summary.tsv (B fresh, mc≥5)
**78 msgs / 366KB**, 5 user inputs (4 act + 1 doc-pointer).

## 用户真实意图（原话）
- U[0]「帮我看 `/proj/train/V0_NCG_HF_Aether/workdir/shanliny/funchk_trainning_for_shanlin/mos_compara`，不太花太多token，精力留在帮我检查为什么程序跑出来会失败」
- U[13]「你没跑过仿真，如果是lv9的报错最暴力的解法是 `.probe isub(*) level=20` / `.probe lv9(*) level=20`，不过你本来就基本需要这些数据」
- U[36]「但你看 `results/sweep_dmby1.log`，这也有找不到sp文件的问题」
- U[57]「想让晶体管被仿真器识别，你的晶体管首字母应该用大写X而不是m」
- U[58]「一并改了」
- U[75]「帮我看 `/apps/synopsys/SRB/finesim/V-2023.12-1/doc/finesim_*`，你还是先把meas的理念先搞清楚」

## 程序用途（mos_compara.py）
MOS 前仿/后仿参数对比 & 寄生贡献分析工具（基于 MOSCHAR v4 改造，FineSim/LSF/LV9/FSDB）。
工作流：discover（从 DSPF 提晶体管，@N 合并）→ generate 三类 .netlist（pre 核心参数版 / post 全参数版 / sweep 仅一个寄生参数）→ FineSim 跑 → compare Idsat/Vth/Ioff。
入口 `0_run` = `bsub -n 8 -R "span[hosts=1]" -q lacaa_sram "finesim sa_template.sp -o sa_template/ -np 8"`。
DSPF 真名 `CXN4HC1PS64X8M4B2C1R1W1BW1RE1_FS.dspf.TYPICAL_25`，4907 晶体管，VDD=0.75V。

## 四个 bug（agent 诊断+修复，py_compile 全过）

### Bug 1: lv9 递归撑爆（致命）
**症状**（results/pre.log + post.log）：
```
ERROR! (pre.netlist:18450) overflow function depth '2048:max=2048'
ERROR! (post.netlist:18450) overflow function depth '2048:max=2048'
```
**根因**：`make_testbench()` 里每个晶体管写一行 `.probe tran lv9(名字:g, 名字:d, 名字:s, 名字:b)`。几千管逐行累积，FineSim 读网表时函数递归深度在每个 lv9() 上叠高，到第 18450 行突破硬上限 2048 直接 abort。报一行错（哪到上限哪炸），与 pre/post 无关。
**修复**：
1. `make_testbench()` 删逐管 `.probe tran lv9(...)` 行（只保留 `_idsat`/`_ioff` 的 `.measure`）。
2. `write_sp_file()` 在 `.tran` 后 `.end` 前加两条通配 probe：
   ```
   .probe lv9(*) level=20
   .probe isub(*) level=20
   ```

### Bug 2: sweep 找不到 sp 文件
**症状**（results/sweep_dmby1.log，所有 sweep 任务）：
```
Command line: finesim sp/sweep_dmby1.sp -np 8
ERROR! unable to read file 'sp/sweep_dmby1.sp' : No such file or directory
```
**根因**：两处目录/路径不一致：
1. Phase 5 生成 sweep `.sp` 放 `sp/sweep/sweep_dmby1.sp`，但 Stage A 自动提交用 `sp/{tag}.sp`（漏 `sweep/`）。
2. `submit_job()` bsub 命令没带 `-o sim/{tag}/`，结果不落 Stage C 采集的 `sim/{tag}` 下；`write_run_script` 原用 `-o {tag}/`（落 results 根）也和采集目录对不上。
**修复**：
1. `submit_job()` 增 `out_dir` 参数，命令带 `-o <out_dir>/`。
2. Stage A 按 tag 区分 sp 路径：`sweep_*` → `sp/sweep/{tag}.sp`，pre/post → `sp/{tag}.sp`；统一 `-o sim/{tag}/`。
3. `write_run_script()` 输出目录改 `-o sim/{sim_tag}/`。

### Bug 3: 器件首字母 M→X（make_testbench）
**症状**：用户指出「想让晶体管被仿真器识别，首字母大写 X 而不是 m」。
**根因**：DSPF 抽出来的是 X 前缀子电路/器件实例（`XGIO.XGIO_R...`、`X...MPMTG`），`make_testbench` 重新输出时却写成 `M{name}`。`M` 开头被仿真器当 MOSFET 查 `.MODEL`，但 design kit 里这些是抽好的 X 子电路/器件，无对应 `.MODEL`，`lv9()/isub()` 无法识别成晶体管。
**修复**（`make_testbench`）：
1. 实例行 `M{name} ...` → `X{name} ...`
2. 两条 `.measure FIND I(M{name})` → `FIND I(X{name})`（Idsat/Ioff 电流引用跟着实例名走）

### Bug 4: 清单文件 M→X（write_transistor_list）
`write_transistor_list()` 行首 `M{list_name}` 也改 `X{list_name}`（虽不进 FineSim，为与实际一致避免误导）。

## reframe（造题）
trace 原意图 = debug-Q&A（mos_compara.py 跑 FineSim 失败，诊断+修 4 bug）。判分有牙需参数化通用，故 reframe 成 produce：给定 buggy `mos_compara.py` + 晶体管表 A + FineSim 错误日志 + FineSim .measure doc，交付 (1) 修好的 `mos_compara.py`（4 bug 全修）+ (2) `diagnosis.json` + `diagnosis.txt`（每 bug 写 root_cause/fix），打包 `outputs/submit.zip`。
A-faithful：BKB/GIO 域名 + 12 器件 + 真错误签名（overflow 2048 / unable to read / X-vs-M）。
hidden B：WLD/SA 域名 + 15 器件 + 异参数 anti-hardcode-A。
判分 check.py 在 B 上跑候选脚本，断言 X 前缀 / I(X{}) / 无逐管 lv9 / .sp 有通配 probe / sweep sp 路径 / -o sim/ 输出目录 / diagnosis 4 条 / 3-seed 一致 / §4.9 三假全 FAIL。k=15。

## 产物
- `assets/EDA-Eval-DesignFlow-FinesimMosComparaFix-001/`：mos_compara_buggy.py + transistors_A.json + finesim_errors/{pre,post,sweep_dmby1}.log + finesim_meas_doc.txt + task_brief.md + hidden/transistors_B.json + hidden_manifest.json
- `reference/EDA-Eval-DesignFlow-FinesimMosComparaFix-001/`：mos_compara_fixed_ref.py + build_submit_ref.py + check.py + negative/{neg_empty,neg_print,neg_core_removed}*.py + negative_selftest.py
