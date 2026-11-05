# 任务：从大 SPICE 网表流式提取 `.SUBCKT` 定义段并解析一层实例/端口/网

## 真实场景背景

你是 EDA 工程师 **rongtaoy**，在主机 **hfeg0pkn001** 上分析一张 DRAM 仿真网表
`/home/rongtaoy/Documents/workspace/netlist_analyse/netlists/Netlist_Vcap_20261008PM/netlist_org`
（emy2netlist 导出的 hspice/ALPS 格式，约 **115MB**，含上万条 `.SUBCKT` 定义）。

你的工作流（来自真实 cline 会话 `1i0em`）分三步对一个**目标 cell** 复用：
1. **定位**：在大网表里 `grep -n "^\.SUBCKT <目标>\|^\.ENDS <目标>"` 拿到目标 `.SUBCKT` 段的起止行号；
2. **流式提取**：把该 `.SUBCKT <目标> ... .ENDS <目标>` 段单独抽到一个文件（不要 `read()` 整个 115MB 进内存，逐行流式扫描）；
3. **解析**：解析这一段，报告目标的**端口**、**一层子 cell 实例**（`X` 实例化调用，**不是** M/C/R 等基本器件）、以及该层的**网（net）**清单。

你和 cimi 的协议要求脚本**按目标 cell 名参数化复用**——切换目标只需改一个参数，不能把任何具体 cell 名 / 端口名 / net 名写死进逻辑。

## ⚠️ 关键陷阱（真实踩坑记录）

真实会话里用户明确抓到一个 bug：
> "parser 把最后一个 token 误认成 cell 名了（因为跨了 `+` 续行）"

SPICE 的 `+` 续行规则：以 `+` 开头的行是**上一行卡片的继续**，要把它们**拼接回上一行**再解析。
一个 `X` 实例化卡片可能跨多行：
```
xRP1 rd0 rd1 rd2 rd3 sa4 sa5 sa6 sa7 vdd vss
+ SpineRpt_A
```
这里 `cell` 名是**拼接后整张卡片的最后一个 token** = `SpineRpt_A`，**不是**第一行的最后一个 token `vss`。
`.SUBCKT` 头的端口列表同样可能跨 `+` 行：
```
.SUBCKT SpineTop_A clk rst_n ec bl0 br0 bl1 br1 wl rd0 rd1 rd2 rd3
+ sa_en bg_en vdd vss
```
端口 = 拼接后 `.SUBCKT` 之后、除 cell 名外的全部 token。

**逐行单独解析、不拼接 `+`** 的 naive 实现，会把第一行末尾的 net 当成 cell 名、丢掉 `+` 行上的端口/引脚，导致 cell 名错、端口不全、net 错——这是本题的核心 discriminator。

## CLI 接口（交付脚本必须遵守）

```
python3 extract_subckt.py --netlist <netlist.sp> --cell <目标cell名> --out <report.json> [--extract <out.sp>]
```

- `--netlist`：输入网表（可能很大，必须流式逐行读，不要 `read()` 整文件）。
- `--cell`：目标 cell 名（大小写不敏感匹配 `.SUBCKT` 头）。
- `--out`：写 JSON 报告到此路径。
- `--extract`（可选）：把目标的 `.SUBCKT ... .ENDS` 段原文（逐行原样）抽到该文件。

退出码：成功一律 0；目标 cell 找不到时退出码非 0 并把 `found:false` 写进 JSON（不要崩溃）。

## JSON 报告 schema

```json
{
  "subckt": "SpineTop_A",
  "found": true,
  "ports": ["clk", "rst_n", "ec", ...],
  "subcells": [
    {"inst": "xECC0", "cell": "ECC_LbusDrv_A", "pins": ["ec","rd0","rd1","vdd","vss"]},
    ...
  ],
  "subcell_types": ["ECC_LbusDrv_A", "BankTopX2_A", "SpineRpt_A", "invLx4"],
  "nets": ["clk","rst_n","ec","nclk", ...],
  "line_range": [起行号, 止行号],
  "line_count": 段总行数
}
```

字段口径：
- `ports`：`.SUBCKT <cell>` 头上**除 cell 名外**的全部 token（已拼接 `+`），按出现顺序、去重。
- `subcells`：该段内所有 `X` 实例化卡片（`X` / `XI` 开头，后接 net 列表，**最后**一个 token 是被调用的 cell 名）拼好 `+` 后逐条记录 `{inst, cell, pins}`；`inst` = 卡片第一个 token，`cell` = 最后一个 token，`pins` = 中间的 net 列表。**不含** M/C/R/L/I/V/D/Q 等基本器件。
- `subcell_types`：`subcells` 里出现过的 cell 名去重、排序。
- `nets`：`ports` ∪ 所有 `subcells` 的 `pins`，去重、排序。
- `line_range`：目标段在原网表里的 `[起始行号, 结束行号]`（1-based）；`line_count` = 止-起+1。

## 约束

- 纯 Python 标准库实现，**不 import 第三方包**，不调任何 EDA 工具，全本地可跑，ASCII only。
- 必须**流式**逐行读网表（`open(..., buffering=...)` + `for line in f`），不要 `f.read()` 整个文件进内存。
- 必须**正确拼接 `+` 续行**后再解析（这是核心）。
- 必须**按 `--cell` 参数泛化**，不能硬编 `SpineTop_A` / `ECC_LbusDrv_A` 等任何具体名字。

## 交付件（打包成 `outputs/submit.zip`，内含 2 个文件）

1. `extract_subckt.py` —— 上述工具。
2. `sample_report_A.json` —— 用你的 `extract_subckt.py` 跑附件 `netlist_A.sp` 的 `SpineTop_A` 得到的 JSON 报告实跑结果。

## 判分提示（隐藏输入）

判分会在一个**你看不到的隐藏网表 B**（不同 cell 名、不同端口数、不同 `+` 续行样式、不同 net、不同规模，且含 ≥3 个可被选为目标的 `.SUBCKT`）上**真跑**你的 `extract_subckt.py`，并独立重解析逐条比对端口/子 cell/net/`+` 续行拼接/基本器件排除/跨输入泛化。所以工具必须按规则泛化，不能记忆 A 的具体名字，也不能逐行不拼 `+` 就解析。
