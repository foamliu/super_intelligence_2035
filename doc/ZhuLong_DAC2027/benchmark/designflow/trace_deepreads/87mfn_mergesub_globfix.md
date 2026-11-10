# Deepread — 1794203732169_87mfn (thomasz @ hfeg0pfn060)

- shard D, mc=48, d_frac=0.97, domain=schematic_netlist
- session: `/home/thomasz/.cline/data/sessions/1794203732169_87mfn/1794203732169_87mfn.messages.json` (58 msgs)
- produce turn: U[0] (single user request, fully resolved by A[57])

## Real task summary
thomasz 在 hfeg0pfn060 维护 IR drop 报告合并流 `autoquery_sc`。用户在 run 目录
`/rundata/totem/dscqa/IR/20261105/DDR6TOP_IDD5B_11600_TT1.025v70c/autoquery_sc/` 改
`mergesub.py`，要求"让输入不要写太死"，并指出第 66 行 `--netlist '../finesim/idd*/netlist'`
会导致 netlist 找不到。

## Root cause（助手 U[22] 给出）
`mergesub.py` 第 63-69 行用 `subprocess.run([...])` **列表方式**传参（无 `shell=True`）调用
`/home/thomasz/script/convertNetlistSubAndInst4.py`。列表形式不经过 shell，第 66 行的 `*`
通配符被当**字面量**原样传给子进程 → 子进程 `parse_netlist()` 执行
`open('../finesim/idd*/netlist')` 打开不存在的字面路径 → netlist 找不到。
确认：`finesim` 是指向 `idd5bx2p3-11600.23.TT1.025v70c.current/` 的软链，必须靠 `idd*` 匹配。

## Fix（助手 A[24..35] 三处编辑，写到的可写源副本 `/home/thomasz/script/autoquery_sc/mergesub.py`）
1. **Edit 1**：加 `import glob` + `import argparse`。
2. **Edit 2**：新增 `resolve_netlist(pattern)` 助手：`sorted(glob.glob(pattern))`；空 →
   `print(f"Error: no netlist matched pattern '{pattern}'")` + `exit(1)`；多个 → 警告并用
   `matches[0]`。重写 `run_conversion_script(ins_file, sub_file, netlist_pattern)`：先
   `resolve_netlist`，再 `subprocess.run([converter, '--netlist', resolved, '--ins', ins,
   '--o', sub])`（仍列表形式），检查 returncode。
3. **Edit 3**：重写 `__main__` 为 argparse，参数 `--dr/--netlist/--ins/--sub/--dr-new/--merged`
   （默认值保留 DDR5TOP 命名），各步骤传入参数。

## Validation（助手 A[36..40]，临时脚本 `_check_mergesub.py` 经 python-runner profile 跑）
- `py_compile.compile(..., doraise=True)` → "syntax OK"
- `importlib.util` 导入 → "import OK, resolve_netlist present: True"
- `resolve_netlist('netlist')` 在临时目录 → "resolved: netlist" / "glob resolution OK"
- `resolve_netlist('/tmp/xxx/nope*/netlist')` → 打印 Error 并 exit → "no-match error path OK"
- 临时脚本被多步 self-remove 清理（A[41..54]）。

## 关键事实
- run 目录副本 `.../DDR6TOP.../autoquery_sc/mergesub.py`（第 66 行 `idd*/netlist`）在
  policy.writableRoots 之外（A[25] 报错），不可写。
- 可写源副本 `/home/thomasz/script/autoquery_sc/mergesub.py`（第 66 行 `'netlist'`，DDR5TOP
  命名）有同 bug 类，助手把补丁应用到这份。
- 转换脚本 `/home/thomasz/script/convertNetlistSubAndInst4.py` 预存在，逻辑：解析 netlist
  的 `.SUBCKT` 块 + X-instance 调用 → instance→subckt 映射 → 按 `--ins` 的 XI 路径生成
  `<path> -> <subckt>` 的 `.sub` 文件。
- mergesub.py 四步流水：(1) extract_xi_paths 从 .dr CSV 抽 XI 前缀段 → .ins；
  (2) run_conversion_script 调转换器 → .sub；(3) apply_replacements 用 .sub 映射替换
  .dr 的 sch_hierpath → .dr.new；(4) merge_rows 按 (power, sch_hierpath) 合并、保留
  max drop、count、count>1 时输出 drop/volt 区间、按 max drop 降序、重排 num_new → .dr.merged。

## 为什么 B-grade synthesized
真实产物在用户私有 run 目录 + finesim 软链 + DDR6TOP_IDD5B_11600_TT1.025v70c corner
目录，不可在沙盒复刻。本 case 取最可独立判分的"glob 解析 + argparse 配置 + subprocess
列表调用"核心，合成 A/B 自包含输入（dr CSV + tiny netlist + 提供 convert_sub.py）复刻
该流水。A(6 行, VDDQ/VDD, dly/buf/inv) vs 隐藏 B(12 行, VDD2/VDDT, nand/nor/xnor/oai)，
corner 目录名/实例名/subckt 名/数量/幅度全不同 → 反硬编码。

## Case 维度 vs 既有 D case（不重复）
- SiInpTokenStrip-001 / DQTXStim / SpStimGen / SpiceMeasInserter：stimulus/.meas **插入**
  维度。本 case 是 merge driver 的 **glob 解析 + argparse 配置 + subprocess 列表形式**
  维度，正交。
- CellFamilyMatch-001：名称族类分类。本 case 是 IR-drop 报告合并驱动，正交。
