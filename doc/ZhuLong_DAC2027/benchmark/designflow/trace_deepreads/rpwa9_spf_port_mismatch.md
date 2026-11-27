# rpwa9 深读 — SPF 端口缺失致 SPICE 仿真失败诊断 + 修补

> session: `1795684460868_rpwa9.messages.json` · user: chloezh · host: hfeg0pkn002 · mc=118
> domain: schematic_netlist · 571KB / 101 msgs (53 user / 48 asst) · fetched via .75 scp→hfeg0pkn002
> claim: r1642 入台账 domain=schematic_netlist · DEBT: 1 deepread 未合成（40min 预算耗于候选开采+trace 获取+深读）

## 用户真实意图（逐字）

- U1: 「/proj/.../input_TrimDly.log 查看报错原因，以及怎么改」
- U27: 「仿真出来没有结果」
- U43: 「可以在 input_TrimDly_2 里面重新再定义 vdd1 码」
- U48: 「input_TrimDly.sp 和 input_TrimDly_2 是用的同一个 RCCspf,都是没有带 vdd1 的，input_TrimDly.sp 要怎么改才能跑通」
- U53: 「有没有还是用 include 但是也能跑通的方法，告诉我怎么改不需要帮我改」

## 任务语义

模拟工程师 chloezh 跑 FineSim ALPS 后仿（delay cell `trimbuf_WrEn2Csl_dly_test`），`input_TrimDly.sp` 用 `.inc` 把寄生 SPF 网表当子电路 include，仿真报 `ERROR! port size mismatch between xi0(13) and trimbuf_wren2csl_dly_test(12)` 退出。诊断根因 + 给出仍用 `.inc` 也能跑通的改法。

## 核心痛点（可合成）

1. **端口数不匹配根因**：`trimbuf_WrEn2Csl_dly_test` 存在两份同名 `.SUBCKT` 定义——
   - 原理图网表 `netlist.presim`：13 端口 `In InDly2 Out cm1<3:0> inh_vbn inh_vbp inh_vcc inh_vdbias inh_vdd1 inh_vss`
   - SPF 寄生网表 `trimbuf_WrEn2Csl_dly.spf_RCC:23`：12 端口 `... vbn! vbp! vcc! vdbias! vss!`（**缺 vdd1!**）
   - 顶层例化 `XI0 ... vbn! vbp! vcc! vdbias! vdd1! vss!` 连 13 节点
   - FineSim 报 `duplicated subckt ... use the latter one`，采用 SPF 版（12 端口），13 连接对 12 端口 → mismatch
2. **vdd1 缺失根因**：StarRC 做 LPE 提取时漏掉 `vdd1` 顶层 pin（电源端口无 R/C 寄生，被丢弃）；全文件搜 vdd1 完全不出现
3. **`.inc` 仍能跑通的改法**：SPICE 例化按**位置**绑定端口，名字不一致没关系，只要**数量和顺序**对齐。在 SPF `.SUBCKT` 行 `vdbias!` 与 `vss!` 之间补 `vdd1!` → 13 端口，与顶层例化顺序一致，mismatch 解除
4. **"跑通"≠"有结果"**（重要提醒）：只补端口仅解除崩溃报错；`.inc` 把整份 SPF 当子电路 include 会触发 duplicate-subckt，SPF 版（纯 RC 无管子）顶替原理图版（有管子）→ Out1 不翻转 → delay 测量 `targ not found`。真正出 delay 结果须用 `.option finesim_spf=`（FineSim 正规后仿，按端口合并 SPF 寄生回带管子的 schematic 子电路），即 input_TrimDly_2 一直用的方式

## synthesized-reframe（case 设计 plan）

**task_id**: `SpfPortMismatchPatchProduce-001` · LIVE-NA · judge_layers=[L0,L1]
**reframe**: 把「真实跑 FineSim 诊断 + 改 SPF 文件」（强依赖仿真器/文件系统）reframe 为 **spec-JSON 驱动「SPICE 端口不匹配诊断 + SPF `.SUBCKT` 端口对齐修补器 `spf_port_patch.py(spec)->report.json` + hidden-B 反硬编码」**——纯 Python 解析 SPICE `.SUBCKT`/例化行 + 子序列对齐 + 修补行生成，无真实 EDA 二进制依赖。

### spec schema
```json
{
  "cell": "trimbuf_WrEn2Csl_dly_test",
  "schem_subckt_ports": [{"name":"In","spf_name":"In"}, ..., {"name":"inh_vdd1","spf_name":"vdd1!"}, {"name":"inh_vss","spf_name":"vss!"}],  // 13 entries, ordered, 每条含 spf_name
  "inst_nodes": ["In1","net3","Out1","Code3","Code2","Code1","Code0","vbn!","vbp!","vcc!","vdbias!","vdd1!","vss!"],  // 13, len==schem
  "spf_subckt_ports": ["In","InDly2","Out","cm1<3>","cm1<2>","cm1<1>","cm1<0>","vbn!","vbp!","vcc!","vdbias!","vss!"],  // 12, 有序子集（缺 vdd1!）
  "error_line": "ERROR! port size mismatch between xi0(13) and trimbuf_wren2csl_dly_test(12)",
  "dup_warning": "subckt trimbuf_wren2csl_dly_test ... are duplicated <-- use the latter one"
}
```

### reference `spf_port_patch.py` 算法
1. `_validate`：必填字段（cell/schem_subckt_ports/inst_nodes/spf_subckt_ports/error_line/dup_warning）；malformed（缺字段/inst_nodes 长度≠schem/spf_subckt_ports 不是 schem 的有序子集/count 相同无 mismatch）→ valid=False + errors 非空 + exit 1
2. 解析：schem_spf_names = [p["spf_name"] for p in schem_subckt_ports]（13）；inst_nodes（13）；spf_subckt_ports（12）
3. **诊断**：inst_count=13 vs spf_count=12 → mismatch=True
4. **缺失端口识别（LCS 子序列对齐）**：把 spf_subckt_ports 作为子序列对齐到 schem_spf_names（按名精确匹配，保序）；schem_spf_names 中未对齐的 = missing。missing = [{position:11, schem_name:"inh_vdd1", spf_name:"vdd1!", inst_node:"vdd1!"}]
5. **修补行生成**：patched_spf_ports = schem_spf_names（全 13，有序）；patched_subckt_line = ".SUBCKT <cell> " + " ".join(patched_spf_ports)
6. **duplicate 解释**：report 含 `duplicate_explanation`：`.inc` 引入第二份同名 `.SUBCKT`，FineSim `use the latter one`，SPF 版（纯 RC）顶替原理图版（有管子）→ 仅补端口解除 mismatch 但不保证有结果
7. report.json：{valid, cell, inst_count, spf_count, mismatch, missing_ports, patched_spf_ports, patched_subckt_line, duplicate_explanation, diagnosis}

### A（visible）spec_A.json
cell=trimbuf_WrEn2Csl_dly_test，13 schem 端口，13 inst_nodes，12 spf 端口（缺 vdd1! 在 pos 11）。error_line/dup_warning 同上。GT: missing=[{pos:11,spf_name:vdd1!}], patched 13 端口 `... vdbias! vdd1! vss!`。

### hidden B（token-structurally 不同）spec_B.json
cell=`clkbuf_dly8x_test`（不同 cell），**15** schem 端口，15 inst_nodes，**13** spf 端口（缺 **2** 个：vdd1! 在 pos 12 + vdd2! 在 pos 13，均在 vdbias! 与 vss! 之间）。不同信号名（clk_in/clk_out/dly_code<5:0>/vcc1!/vcc2!）。GT: missing=[{pos:12,vdd1!},{pos:13,vdd2!}], patched 15 端口。A 硬编码器（只补 1 个 vdd1!）在 B 全错。

### check.py（~14 conds，独立 GT 复算）
独立 `_gt_align`（与 ref 不同代码路径）做 LCS 子序列对齐复算 missing + patched。断言：
- a zip 含 spf_port_patch.py
- b py_compile
- c A 运行 exit0 写 report_A.json valid==True
- d A mismatch==True
- e A inst_count==13 / spf_count==12
- f A missing 集合==独立 GT 复算（[{pos:11,spf_name:vdd1!}]）
- g A patched_spf_ports==独立 GT 复算（13 端口，vdd1! 在 vdbias! 与 vss! 之间）
- h A patched_subckt_line 含 ".SUBCKT trimbuf_WrEn2Csl_dly_test" 且 13 端口顺序正确
- i A duplicate_explanation 含 "use the latter one" + "duplicated"
- j A diagnosis 含 "port size mismatch" + "vdd1"
- k malformed spec（count 相同无 mismatch / inst≠schem / spf 非 schem 子集）→ valid==False + errors 非空 + exit≠0
- l B 运行 exit0 写 report_B.json valid==True
- m B missing==独立 GT 复算（2 个：vdd1! pos12 + vdd2! pos13）且 ≠A missing（反硬编码）
- n B patched_spf_ports==独立 GT 复算（15 端口）且 ≠A patched
- o 源码无 A 专属 token（trimbuf_WrEn2Csl_dly_test/InDly2/cm1/In1 等）
- p B report 无 A 专属 token

### negatives（≥3 + live-neg 不适用 LIVE-NA，至少 trio + hardcode_a）
- empty: 空壳 → a/c FAIL
- print_only: 只打印期望 report → c FAIL（不写合法 json）
- core_deleted: 删对齐逻辑只回固定 dict → f/g FAIL（missing/patched 不匹配独立 GT）
- hardcode_a: 硬编码 A 答案 → m/n FAIL（B missing/patched 全错）

### LIVE-NA 判据
deliverable=Python 脚本，check 跑候选 subprocess + 独立 LCS 对齐复算断言，无真实 EDA 工具二进制依赖；FineSim/StarRC 不在 eval 沙盒不强求 L2.live；仿真器运行时行为（duplicate-subckt/use the latter one）reframe 为 spec 静态字段判分。judge_layers=[L0,L1] 无 check_live。

## 下轮合成 ETA
按本 plan 合成（assets 4 文件 + reference 4 文件 + case JSON + 自验）≈ 20 min。下轮 r1643 直接按 plan 落库 SpfPortMismatchPatchProduce-001。
