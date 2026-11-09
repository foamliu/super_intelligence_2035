#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build EDA-Eval-DesignFlow-BlConnEquivCheck-001 artifacts.
Theme: SPICE netlist BL connection equivalence check between two length-scaled netlists.
Trace: 1792743512849_1nuuf (victorq@hfeg0pkn002, mc=49, schematic_netlist).
"""
import json, os, shutil, subprocess, sys, tempfile, zipfile, hashlib

REPO = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE_ID = "EDA-Eval-DesignFlow-BlConnEquivCheck-001"
ASSETS = os.path.join(REPO, "assets", CASE_ID)
REF = os.path.join(REPO, "reference", CASE_ID)
CAND_NAME = "bl_conn_equiv.py"
A_SP = "dram_bl_array_A.sp"
B_SP = "dram_bl_array_B.sp"

os.makedirs(os.path.join(ASSETS, "hidden"), exist_ok=True)
os.makedirs(os.path.join(REF, "negative"), exist_ok=True)

# ============================================================
# A netlist (visible, BL length 1160)
# ============================================================
A_NETLIST = """* DRAM BL array netlist - variant A (BL length 1160)
.param R_BL=1.16e3
* ---- core bitline cell ----
.SUBCKT kcellCore B T vdd vss
M0 B T vdd vss nch W=0.1u L=28n
M1 B T vss vss nch W=0.1u L=28n
.ENDS
* ---- 4-cell BL stack, length 1160 ----
.SUBCKT kcellBLx4_BLlength1160 BlTop BlBot BlE BlO vdd vss
X0 BlTop net0 vdd vss kcellCore
X1 net0 net1 vdd vss kcellCore
X2 net1 net2 vdd vss kcellCore
X3 net2 BlBot vdd vss kcellCore
R0 BlE BlTop (1.16e3*R_BL)/4
R1 BlO BlBot (1.16e3*R_BL)/4
C0 BlTop vss 1.16e-15 m=143.5
C1 BlBot vss 1.16e-15 m=143.5
.ENDS
* ---- one section, WL x 1160 ----
.SUBCKT OneSection_SecA_WLx1160 BL0 BL1 vdd vss
XSec0 BL0 BL1 BlE0 BlO0 vdd vss kcellBLx4_BLlength1160
XSec1 BlE0 BlO0 BlE1 BlO1 vdd vss kcellBLx4_BLlength1160
XSec2 BlE1 BlO1 BlE2 BlO2 vdd vss kcellBLx4_BLlength1160
.ENDS
* ---- single BL connection block ----
.SUBCKT BL_Connection BLin BLout vdd vss
Rroute BLin BLout 50
Cload BLout vss 5f
.ENDS
* ---- write path ----
.SUBCKT msaq_write DQ WlSA vdd vss
Xsa DQ WlSA vdd vss ssa_core
Rdrv DQ WlSA 100
.ENDS
.SUBCKT ssa_core a b vdd vss
M0 a b vdd vss pch W=0.2u L=28n
.ENDS
* ---- top testbench ----
.SUBCKT TBTop DQin WLin vdd vss
XI_BL_Connection WLin WLrouted vdd vss BL_Connection
XI_Sec WLrouted BLint vdd vss OneSection_SecA_WLx1160
XI_wr DQin BLint vdd vss msaq_write
.ENDS
* ---- stimulus ----
Xtop DQin WLin vdd vss TBTop
Vdd vdd 0 1.2
Vss vss 0 0
VDQ DQin 0 PULSE 0 1.2 0 1n 1n 5n 20n
.tran 1n 200n
.measure tran tA trig V(DQin) val=0.6 fall=1 targ V(BLint) val=0.6 rise=1
.end
"""

# ============================================================
# B netlist (hidden, BL length 976, structurally different)
# ============================================================
B_NETLIST = """* DRAM BL array netlist - variant B (BL length 976)
.param R_BL=976
* ---- core bitline cell ----
.SUBCKT kcellCore B T vdd vss
M0 B T vdd vss nch W=0.1u L=28n
M1 B T vss vss nch W=0.1u L=28n
.ENDS
* ---- 4-cell BL stack, length 976 ----
.SUBCKT kcellBLx4_BLlength976 BlTop BlBot BlE BlO vdd vss
X0 BlTop net0 vdd vss kcellCore
X1 net0 net1 vdd vss kcellCore
X2 net1 net2 vdd vss kcellCore
X3 net2 BlBot vdd vss kcellCore
R0 BlE BlTop (976*R_BL)/4
R1 BlO BlBot (976*R_BL)/4
C0 BlTop vss 9.76e-16 m=120.5
C1 BlBot vss 9.76e-16 m=120.5
.ENDS
* ---- one section, WL x 976 ----
.SUBCKT OneSection_SecA_WLx976 BL0 BL1 vdd vss
XSec0 BL0 BL1 BlE0 BlO0 vdd vss kcellBLx4_BLlength976
XSec1 BlE0 BlO0 BlE1 BlO1 vdd vss kcellBLx4_BLlength976
XSec2 BlE1 BlO1 BlE2 BlO2 vdd vss kcellBLx4_BLlength976
.ENDS
* ---- BL connection SPLIT into Even/Odd (structural diff vs A's single block) ----
.SUBCKT BL_Connection_Even BLin BLout vdd vss
RrouteE BLin BLout 40
CloadE BLout vss 4f
.ENDS
.SUBCKT BL_Connection_Odd BLin BLout vdd vss
RrouteO BLin BLout 45
CloadO BLout vss 4.5f
.ENDS
* ---- write path with routing (renamed + extra instance vs A's msaq_write) ----
.SUBCKT msaq_write_wiRouting DQ WlSA vdd vss
Xsa DQ WlSA vdd vss ssa_core
Rdrv DQ WlSA 100
Xrt WlSA RtN vdd vss rt_buf
.ENDS
.SUBCKT ssa_core a b vdd vss
M0 a b vdd vss pch W=0.2u L=28n
.ENDS
.SUBCKT rt_buf a b vdd vss
M0 a b vdd vss pch W=0.15u L=28n
.ENDS
* ---- top testbench (4 inst vs A's 3) ----
.SUBCKT TBTop DQin WLin vdd vss
XI_BL_Even WLin WLrE vdd vss BL_Connection_Even
XI_BL_Odd WLrE WLrouted vdd vss BL_Connection_Odd
XI_Sec WLrouted BLint vdd vss OneSection_SecA_WLx976
XI_wr DQin BLint vdd vss msaq_write_wiRouting
.ENDS
* ---- stimulus ----
Xtop DQin WLin vdd vss TBTop
Vdd vdd 0 1.2
Vss vss 0 0
VDQ DQin 0 PULSE 0 1.2 0 1n 1n 5n 20n
.tran 1n 220n
.measure tran tA trig V(DQin) val=0.6 fall=1 targ V(BLint) val=0.6 rise=1
.end
"""

with open(os.path.join(ASSETS, A_SP), "w") as f:
    f.write(A_NETLIST)
with open(os.path.join(ASSETS, "hidden", B_SP), "w") as f:
    f.write(B_NETLIST)

# hidden_manifest.json
manifest = {
    "case_id": CASE_ID,
    "hidden_inputs": [{
        "name": B_SP,
        "purpose": "Hidden B SPICE fixture (judge-side ground truth). Same DRAM BL-array family as visible A but length-scaled (976 vs 1160) and structurally different in peripherals (BL_Connection split into Even/Odd; msaq_write renamed to msaq_write_wiRouting with extra routing instance; TBTop 4 inst vs 3). Used by check.py to run the candidate and verify structured connection-equivalence JSON output.",
        "different_from_A": "BL length 976 vs A's 1160 (R/C/m scaled); BL_Connection split into BL_Connection_Even/BL_Connection_Odd vs A's single BL_Connection; msaq_write_wiRouting (renamed + rt_buf routing instance) vs A's msaq_write; extra rt_buf subckt; TBTop 4 instances vs 3; .tran 1n 220n vs 200n; names/structure all distinct (anti-hardcode)."
    }],
    "check_runs_only_on_hidden_B": True,
    "A_visible_to_sut": [A_SP],
}
with open(os.path.join(ASSETS, "hidden", "hidden_manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2)

# prompt.txt + task_brief.md
PROMPT = """场景：我有两份 DRAM 位线（BL）阵列的 SPICE 网表，它们本应是「同一个阵列按 BL 长度缩放」的两个版本（BL length 1160 和 976），我想拿它们跑 TCS / WRTIME 仿真。在跑之前，我要确认两份网表里 BL 相关的**连接关系**是否一致——除了因 BL 长度不同而按比例缩放的阻容值 / m 倍数 / W/L 之外，节点连接拓扑应当等价；同时我要知道两份网表在层级结构 / 外围模块上有没有差异。

请你写一个 Python 命令行工具 `bl_conn_equiv.py`，对**两份 .sp 网表**做「连接等价性校验 + 结构差异报告」：

1. 解析两份网表里的 `.SUBCKT` / `.ENDS` 子电路定义，以及每个子电路里的实例调用（`X` 子电路调用、`R`/`C`/`M` 器件）的**节点连接**（实例类型、模型/器件类型、连接的节点列表）；忽略实例的数值参数（R/C 的值、`m=`、`W=`、`L=` 等），只保留节点连接关系。
2. 把两份网表的子电路**按规范化名配对**：子电路名规范化时**剥离尾部**的长度/缩放后缀 `_BLlength<数字>` 和 `_WLx<数字>`（可递归剥离多层）；规范化名相同且分别出现在两份网表里的，配成一对（每对取各自的第一名；多余的同名归到 unpaired）。
3. 对每一对，做**连接等价**判定：把两侧实例的连接签 `（实例类型, 规范化模型名, 节点元组）` 排序后比较多签集合是否相等（`X` 调用的模型名也按同样规则规范化）。等价条件：实例数相同 **且** 多签集合相同；否则不等价，并给出差异原因（实例数不同 / 仅 A 有的模型 / 仅 B 有的模型 / 节点连接不同）。
4. 只在 A 出现的规范化名 → `unpaired1`（子电路全名列表）；只在 B 出现的 → `unpaired2`。
5. 输出 JSON 到指定路径，结构固定：
```
{
  "summary": {"n_sub1":int, "n_sub2":int, "n_pairs":int, "n_equiv":int, "n_diff":int, "n_unpaired1":int, "n_unpaired2":int},
  "pairs": [{"norm_name":str, "name1":str, "name2":str, "conn_equiv":bool, "n_inst1":int, "n_inst2":int, "diff_reasons":[str]}],
  "unpaired1": [str],
  "unpaired2": [str]
}
```
（`pairs` 按 `norm_name` 升序；`unpaired1`/`unpaired2` 升序；JSON 写出时 `sort_keys=True`、`indent=2`。）

可见输入（本目录下）：
- `dram_bl_array_A.sp`：A 档样例（BL length 1160，单一 `BL_Connection` 块、`msaq_write` 写通路）。你拿它来跑通工具、确认输出形态。

交付接口（必须严格遵守）：
- 命令行：`python3 bl_conn_equiv.py <netlist1.sp> <netlist2.sp> <out.json>`（三个位置参数：网表1、网表2、输出 JSON 路径）。
- 退出码 0 表示成功；用法错误退出 2。
- 把工具脚本 `bl_conn_equiv.py` 打包成 `outputs/submit.zip` 提交（zip 内顶层就是 `bl_conn_equiv.py`）。

判分会用**另一份隐藏的 .sp 文件**（BL 长度 / 外围结构都和 A 不同：BL_Connection 被拆成 Even/Odd、写通路被重命名并加了 routing 实例）跑你的工具，再对产出的 JSON 做结构化字段断言（子电路数 / 配对数 / 等价数 / unpaired 集合 / 特定对等价性 / 反硬编码交叉验证 / 多 seed 重跑确定性等）。
"""

with open(os.path.join(ASSETS, "prompt.txt"), "w") as f:
    f.write(PROMPT)

TASK_BRIEF = """# 交付接口与文件位置

- 提交：`outputs/submit.zip`，zip 内顶层为 `bl_conn_equiv.py`。
- CLI：`python3 bl_conn_equiv.py <netlist1.sp> <netlist2.sp> <out.json>`，退出码 0 成功 / 2 用法错误。
- 可见输入：`dram_bl_array_A.sp`（A 档，用于跑通工具、确认输出形态）。
- 判分：在隐藏 B（`.sp`，BL 长度 / 外围结构与 A 不同）上真跑候选，对产出 JSON 做结构化字段断言。
"""
with open(os.path.join(ASSETS, "task_brief.md"), "w") as f:
    f.write(TASK_BRIEF)

print("[builder] assets written:", A_SP, B_SP, "prompt.txt", "task_brief.md", "hidden_manifest.json")
print("A subckts:", A_NETLIST.count(".SUBCKT"), "B subckts:", B_NETLIST.count(".SUBCKT"))
