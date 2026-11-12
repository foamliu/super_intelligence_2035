# 深读笔记 · 1793583887609_nwlan · reedchen@hfeg0pkn001 · mc=44 · waveform/sim-data

**session**: `/home/reedchen/.cline/data/sessions/1793583887609_nwlan/`（hfeg0pkn001，788KB，336 msgs，agent=claude，agent-policy-engine enforcing python-runner/shell-runner）
**scan**: 11/09 summary.tsv，netlist:109;rtl:34;synopsys:6;schematic:3;cmos:3;waveview:1 → D-keyword，waveform/sim-data 域
**fresh**: sid 不在 4-ledger（fresh-sid），reedchen 不在 D.jsonl 162 users（FRESH-USER ✓ 双重 fresh）

## 真实任务（11 轮用户原文，逐字）

| # | 用户轮原文 | 阶段 |
|---|---|---|
| U0 | (continuation context: 追加 collect_batches/harvest/analyze_batch/main 到 analyze_four_batch.py) | 续写分析脚本 |
| U1 | 「给我一个一键生成读写仿真环境的shell脚本」 | gen_all_env.sh |
| U2 | 「把这些东西写道Readme里」 | README |
| U3 | 「你现在生成的各自读写版本还有问题 第一个，读写版本的sh命令没办法正常运行 第二读版本的数据统计规则还是没有规范好，收集的数据应该做前处理，计算完的结果应该做后处理，Setup/hold数据如果低于-750ps，应该+3ns，然后所有数据向1.5ns取余」 | post_sh 规则 v1（-750ps→+3ns, mod 1.5ns）|
| U4 | 「请你更新一下分析数据的能力，要求在各个case的报告结尾，汇总一个各PVT的平均／最小的setup/hold表格」 | per-PVT summary |
| U5 | 「请你再次确认脚本后处理的逻辑，Setup/hold数据如果低于-750ps，应该+3ns，之前有其他操作吗」 | 确认逻辑 |
| U6 | 「把后处理的+3ns改成1.5ns」 | post_sh v2（+1.5ns）|
| U7 | 「请你注意，取余的时候要做符号保持，-500ps取余应该还是-500ps」 | smod 符号保持 |
| U8 | 「我现在希望你进一步修改统计脚本， Setup/hold数据如果低于-600ps，应该+1.5ns， Setup/hold数据如果高于900ps，应该-1.5ns」 | post_sh v3 窗口折叠 [-600,+900)ps |
| U9 | 「test」 | (噪声) |
| U10 | 「请你帮我把gen_all_env.sh这个脚本改成可以指定PVT的」 | PVT 参数化 |
| U11 | 「[OK] /rundata/.../ReedChenWork_TB_DbusDrvSetupHoldLF/script/ 我在这个目录下运行这个脚本分析数据run_four_rd.sh，但似乎脚本抓取的还是我.../ReedChenWork_TB_DbusDrvSetupHold路径下的数据，请你分析原因解决报错，并且连同写相关的数据分析脚本也一并修改」 | symlink 路径 bug |
| U12 | 「我希望你进一步修改统计脚本的逻辑 现在统计脚本支持HF和LF模式，默认HF模式，保持原有逻辑不变 新增LF模式，首先TrTf数据不需要被前处理， 另外，Setup/hold数据，如果低于-1000ps，应该+5ns 如果高于4000ps，应该-5ns 最后取得结果向5ns取余，并且注意保持符号」 | LF 模式 post_sh_lf v1 |
| U13 | 「改动同步进Readme和skill」 | doc sync |
| U14 | 「reedchen@hfeg0plg93: /rundata/.../LF/script/ ... LF=1 sh run_four_rd.sh ... summary.log ...」 | LF 端到端反馈 |
| U15 | 「...LF 下仍出现 -2732.5ps 这类 -2000 多的 setup...」(agent 自查) | post_sh_lf v2 模折叠修复 |

## 工具链（agent 5 步循环 ×11 轮）
read_files → editor/apply_patch → run_approved_command(python-runner/shell-runner) → verify(py_compile + 单测) → cleanup。agent-policy-engine 限定 readableRoots/writableRoots，editor 对 workdir 只读 → 改用 python 脚本做原地文本替换写回。

## 金标准机制（最终态，agent 末轮确认）

### mt0 CSV 命名约定（FineSim alter 默认）
```
<corner>.mt0.csv      → base    → WP_normal   #0
<corner>#1.mt0.csv    → #1      → WP_stress   (SIGMA4)
<corner>#2.mt0.csv    → #2      → PP_normal   (PP_sigma2)
<corner>#3.mt0.csv    → #3      → PP_stress   (PP_sigma4)
```
batch 由**文件名后缀**（base / #1 / #2 / #3）判定，与 CSV 内容无关。

### post_sh（HF 模式，最终实现 msg 185）
```python
def post_sh(v, result_period, lo=-600e-12):
    P = abs(result_period)              # 1.5ns
    return ((v - lo) % P) + lo          # 折叠进 [-600ps, +900ps)
```
窗口 = `[lo, lo+P)` = `[-600ps, +900ps)`，宽度 = P = 1.5ns。Python `%` 对负数向下取整 ⇒ `((v-lo)%P)+lo` 天然符号保持（窗口内值不变，窗外反复 ±P 折回）。

验证表（P=1.5ns, lo=-600ps）：
| 输入 | 结果 |
|---|---|
| -900ps | 600ps（< -600 → +1.5n）|
| -600ps | -600ps（下界）|
| -500ps | -500ps（窗口内，符号保持）|
| +800ps | 800ps |
| +900ps | -600ps（≥上界 → -1.5n）|
| +1200ps | -300ps |
| -3000ps | 0ps（多次折叠）|

### post_sh_lf（LF 模式，最终实现 msg 335 — 关键修复）
```python
def post_sh_lf(v, period=5e-9, lo=-1000e-12):
    P = abs(period)                     # 5ns
    return ((v - lo) % P) + lo          # 折叠进 [-1000ps, +4000ps)
```
**修复原因**：LF 不对 TrTf 前处理 → setup/hold 原始差值可很大（如 -7.7ns）。旧实现「一次 +5ns + smod」对 -7732.5ps → +5ns → -2732.5ps → smod 不再折叠（2732.5<5000 保持负）⇒ 残留 -2732.5ps。改模折叠后 -7732.5ps → 2267.5ps。

验证表（P=5ns, lo=-1000ps）：
| 输入 | 旧 | 新 |
|---|---|---|
| -2732.5ps | -2732.5 | 2267.5 |
| -3017.1ps | -3017.1 | 1982.9 |
| -7732.5ps | -2732.5 | 2267.5 |
| -500ps | -500 | -500（符号保持）|
| +4500ps | -500 | -500 |

### smod 符号保持取余（msg 167）
```python
def smod(v, period):
    P = abs(period)
    r = abs(v) % P
    return -r if v < 0 else r
```
`-500ps % 1.5ns = -500ps`（不被 python 向下取模折成正）。注：最终 post_sh/post_sh_lf 改用 `((v-lo)%P)+lo` 窗口折叠，已隐式符号保持，smod 保留为 LF 旧路径。

### per-PVT 汇总（msg 114/131）
每个 batch 报告结尾追加 per-PVT 平均/最小 setup/hold 表：按 corner 分组，avg = mean(post_sh_setup), min = min(post_sh_setup)，hold 同理。

### TrTf 前处理（HF only，LF 跳过）
HF: `smod(v, data_period=3ns)`，过滤 ≤0。LF: 直接用原始 crossing 值，不过滤不取余。

## B-grade 合成设计（SetupHoldPostShFold-001）

**选子任务**：mt0 CSV 解析 + batch 收集（文件名后缀）+ post_sh 窗口折叠（HF/LF）+ per-PVT 汇总 → JSON 报告。
**放弃**：gen_all_env.sh 生成 / symlink 路径 bug 修复 / README+SKILL.md 同步 / .alter deck 生成 / run_four_*.sh 包装（解释性或环境依赖，难≥8断言）。

### A/B/C 不相交设计
| 档 | mode | corner 数 | batch | signal 前缀 | post_sh 参数 | value seed |
|---|---|---|---|---|---|---|
| A（可见） | HF | 3 | 4 (base/#1/#2/#3) | sigA_ | lo=-600ps,P=1.5ns | 1100 间隔 |
| B（hidden） | LF | 4 | 4 | sigB_ | lo=-1000ps,P=5ns | 2200 间隔 |
| C（嵌入 check.py） | HF | 2 | 4 | sigC_ | lo=-600ps,P=1.5ns | 3300 间隔 |

A/B/C：mode(HF/LF/HF) + corner 数(3/4/2) + signal 前缀(sigA_/sigB_/sigC_) + value seed(1100/2200/3300) + lo/P 全不相交 ⇒ 反硬编码 + 防泄漏。

### SUT 契约
`setup_hold_postsh.py <mt0_dir> --mode rd|wr --lf --out <report.json>`（纯 stdlib: csv/json/math/os/re/sys/argparse；禁 subprocess/socket/urllib/ctypes/eval/exec/numpy/pandas；禁 B/C 字面量）。
- 解析 mt0_dir 下 `<corner>.mt0.csv` / `<corner>#1/#2/#3.mt0.csv`
- CSV 列：`signal,setup,hold,tr,tf`（秒，科学计数）
- batch 收集：文件名后缀 → WP_normal/WP_stress/PP_normal/PP_stress
- post_sh (HF) / post_sh_lf (LF) 窗口折叠
- per-PVT summary（avg/min setup/hold per corner per batch）
- 输出 JSON：{mode, batches:{WP_normal:{corners:[{corner,signals:[{signal,setup,hold,post_sh_setup,post_sh_hold,tr,tf}],pvt_summary:{avg_setup,min_setup,avg_hold,min_hold}}],...}, summary:{...}}

### check.py 14 条件 a-n（独立 oracle）
a. zip 含 py + 源码非空 + 无禁 import/call + 无 B/C 字面量泄漏
b. py_compile
c. 跑 B 退 0 + 产 report_B.json
d. JSON 顶层键齐全 (mode/batches/summary)
e. batches 4 键齐全 + 每 batch corner 数 == B(4)
f. 每 signal post_sh_setup == oracle((setup-lo)%P)+lo 逐条（B: LF lo=-1000ps,P=5ns）
g. 每 signal post_sh_hold == oracle 逐条
h. LF 模式 tr/tf == 原始值（无前处理）
i. per-PVT avg_setup == oracle mean(每 corner post_sh_setup)
j. per-PVT min_setup == oracle min
k. per-PVT avg_hold/min_hold == oracle
l. 反硬编码 C：跑 C 退 0 + C post_sh 匹配 C-oracle(HF) + C ≠ B
m. 符号保持：B 中至少一个 in-window 负值保持负（如 -500ps → -500ps）
n. 3-seed sha256 一致（deterministic）

### 维度正交（非 dup）
vs IrunWarnClassify(irun *W 码分类) / Ddr5ClDelayPivot(Verilog CL 速度档透视) / FuseAddrCompare(fuse rpt 比对) / CdsLibNetlistInventory(cds.lib 多库 inventory) / RailMapMissingAudit(power-rail 审计) → FineSim mt0 setup/hold 窗口折叠后处理 + per-PVT 汇总，机制全不同 ⇒ 非 dup ✓

### 难度
L2（解析 sim 数据 CSV + 多步数值变换 + per-PVT 聚合；纯 stdlib 无 EDA 工具运行时，与 D 域近期 #518-#531 parse/transform 类一致诚实标 L1）。
