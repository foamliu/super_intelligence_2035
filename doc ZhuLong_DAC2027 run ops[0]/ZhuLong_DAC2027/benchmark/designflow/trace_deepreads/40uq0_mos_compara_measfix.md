# Deepread — 1795152734593_40uq0 (shanliny / hfeg0plg107 / mc547)

- **session**: `1795152734593_40uq0.messages.json` (2.6MB, 463 msgs, new cline subdir layout)
- **user/host**: shanliny @ hfeg0plg107 (ip 10.129.8.239)
- **scan**: ssh_eda_search_20261120_145529/summary.tsv -> summary_1120_reconstructed.tsv
- **keywords**: synopsys:3431; aether:1024; netlist:799; waveview:527; hspice:463; transistor:130; mosfet:112; spectre:33; pex:26; lvs:9
- **domain**: spice_sim (B shard)

## 真实任务上下文
shanliny 在 TOP_PLL_VCO 设计上跑 `mos_compara`（MOS 管前后仿参数对比 characterization）FineSim 仿真流。`mos_compara.py` 生成器逐管产出 testbench 网表块（实例行 + 漏/栅/源/衬底电压源 + `.measure` + `.probe tran lv9(...)`）。调试中用户多轮指出网表错误。

## 用户原话（关键转折）
- **msg0**：帮我看 .../mos_compara，精力留在帮我检查为什么程序跑出来会失败
- **msg21**：你没跑过仿真，如果是lv9的报错最暴力的解法是.probe isub(*) level=20 .probe lv9(*) level=20
- **msg57**：想让晶体管被仿真器识别，你的晶体管首字母应该用大写X而不是m
- **msg77**：蠢货，你的meas语句测电流的时候要在晶体管名字后加上晶体管的端子，我们要测的是:d端子，还有lv9...你的网表中应像测晶体管电流一样写上lv9相关meas，不过lv9不需要写端子
- **msg91**：lv9不能指定测量时刻吗？我应该说过我要测2.5ns那个点的
- **msg103**：蠢货，你把sp文件里的probe删了做甚，没有probe你能测出来？在每个sp文件中加上.probe v(*) level=all .probe isub(*) level=20 .probe lv9(*) level=20
- **msg127**：罢了，你先搞懂一下meas的理念，/apps/synopsys/SRB/finesim/V-2023.12-1/doc/finesim_*
- **msg283/361/409/429**：xlsx 生成 / 什么数字都没填进去 / POST=1 / 一个字填不进去

## agent 工具链
read_files×91 / editor×69 / run_approved_command×30 / list_allowed_files×27。多轮 edit `mos_compara.py` 的 `make_testbench`/`write_sp_file`/`submit_job`/`bjobs_active`/`parse_mt0`/`write_xlsx_report`。

## 关键 edits（make_testbench 网表块演化）
- msg22: 删逐管 `.probe tran lv9(...)`（overflow function depth 2048:max=2048 @ line 18450）
- msg61: 实例行 `M{name}` → `X{name}`
- msg63: `.measure ... I(M{name})` → `I(X{name})`
- msg79: `I(X{name})` → `I(X{name}:d)`（加漏端子）+ 加回逐管 `.measure tran {safe}_vth LV9({name}:g,{name}:d,{name}:s,{name}:b)`
- msg93: LV9 后加 `AT=2.5n`
- msg104: sp 加 `.probe v(*) level=all` / `.probe isub(*) level=20` / `.probe lv9(*) level=20`
- msg193/273: 试 `.d` / `I(v{safe}vds)`（FineSim 子电路端口电流语法探索，用户原话为 `:d`）
- msg367/399: 回退再加回 LV9 .measure

## 本 case 取材（聚焦 4 处网表修正子任务）
A 档 trace-faithful，聚焦 msg57/77/91/103 + msg21 的 4 处网表 `.meas`/`.probe`/实例前缀修正：
1. 实例首字母 M → X
2. 电流测量 `I(M<name>)` → `I(X<name>:d)`（加漏端子 :d）
3. 加每管 `.measure tran <name>_vth LV9(<name>:g,<name>:d,<name>:s,<name>:b) AT=2.5n`
4. 删每管 `.probe tran lv9(...)`

case_id: **EDA-Eval-DesignFlow-MosMeasDeckFix-001** (k=10 a–j, ref 10/10 PASS, NEG 4/4 FAIL 含 §4.9 三假全 FAIL, 3-seed 确定性). 纯 Python `meas_deck_fix.py <src_dir> <out_dir>`, hidden B 器件名/数量/文件集/corner 异于 A (dqv_pu0/dqv_pd0/dqv_pd1/dqv_pu1, 4+4+2, pre/post/sweep_rg, DDR4_IO_DQ, vdd=1.5), anti-hardcode-A.

## 留作后续候选（同 session 其它子任务）
- msg42: sweep sp 路径修复（生成 sp/sweep/ 子目录 vs 提交 sp/{tag}.sp + submit_job -o sim/{tag}）
- msg121: bjobs_active 只查自己提交的 ids
- msg283/361/409/429: xlsx 报告填数（parse_mt0 + openpyxl，数字没填进去）+ fsdb POST=1
- msg237+: WaveView FSDB reader 提取 lv9 Vth（waveview_fsdb_reader.py）
- msg415: parse_mt0 双布局（measform=1 表格 / measform=2 name=value）
