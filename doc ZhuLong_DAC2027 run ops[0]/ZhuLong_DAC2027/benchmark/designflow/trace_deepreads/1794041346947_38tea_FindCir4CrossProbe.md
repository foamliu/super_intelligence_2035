# Deepread — 1794041346947_38tea (FindCir4CrossProbe_wx)

- **session**: `1794041346947_38tea` (xiwang @ hfeg0pkn002, mc=67, schematic:884/cmos:764/pyaether:76)
- **domain**: schematic_netlist (shard D)
- **grade**: B (synthesized), level L2
- **delivered case**: `EDA-Eval-DesignFlow-FindCir4CrossProbe-001` (appended to `EDA-Eval-DesignFlow_D.jsonl` line 307)

## Real task (single produce)

用户在 Aether/OA 芯片设计项目里调用 `FindCir4CrossProbe_wx` skill：从 DDGOA V0 的 WOWTOP 向下找所有用 `vbncore` 族的电路，生成 cross-probe CSV（从芯片顶层逐层取真实 OA 实例名拼 `hierPath`，每行一个实例）。

助手产出：
- `find_vbncore_cells.py` / `inspect_fullmap.py`（调试用，探查 fullmap 结构）
- `scan_parents.py`（pyAether 沙箱内跑：`dbOpenCVByType` + `emyGetAllInstHeaders` → `fullmap.json` `{lib|parent:{child:[instNames]}}`，分块增量合并）
- **`build_records.py`**（**gold produce**，纯 stdlib：`os/re/sys/json/argparse/collections`）：读 `fullmap.json` 从 `--chip-root` 做 scanned-edge BFS → 过滤 numbered_only 实例名 → bus-expand → 加 prefix → 拼 hierPath → 排序 → 写 10 列 CSV。

环境踩坑：默认 `/apps/local/python/python-3.7.1` 损坏（`libpython3.7m.so` 打不开）+ Aether `PYTHONHOME` 污染 → 用 `/usr/bin/python3.11` + `unset PYTHONHOME PYTHONPATH` 绕过。证实 produce 是纯 Python 工作，不依赖 EDA 工具运行时。

## Why B-grade synthesized

真实 `/proj/ddgoa` 库 + pyAether 沙箱 + 698 台主机环境不可复刻。但 gold produce `build_records.py` 是**确定性、stdlib-only** 的——只要把 `scan_parents.py` 产出的 `fullmap.json` 当静态输入资产 ship，整个 produce 就变成单文件 CLI 工具，自包含可判分。

## Synthesized A/B (disjoint)

**A (visible)**：vbncore 族 / chip-root `LP5TOPA` / top-instance `I_C_Top` / prefix `X` / 9 行
- fullmap_A.json：LP5TOPA → {ArrayMod(I_Array), ChanMod(I_Chan), vbncore_top(I1,I2,I17<1:0>), TBcellA(I_TB)}
- 种子：vbncore_unit/vbncore_buf/vbncore_top/vbncore_drv/vbncore_leaf
- 总线 I17<1:0> → I17<0>,I17<1>

**B (hidden)**：vbpcore 族 / chip-root `COREB` / top-instance `I_TopB` / prefix `X` / 10 行
- fullmap_B.json：COREB → {AnalogCore(I301,I302), vbpcore_top(I5,I6,I8<3:0>)}
- AnalogCore → {vbpcore_unit(I21,I22,**I_vbpcoreSpurious**), vbpcore_amp(I9), **auxcell**(I99)}
- CDF 名 `I_vbpcoreSpurious` 应被 numbered_only 丢弃；非种子 `auxcell` 应被跳过；总线 I8<3:0> → I8<0..3>
- A/B 种子集完全不相交（vbncore_* vs vbpcore_*）

## check.py (13 条 a-m, 独立 oracle)

子进程真跑 SUT 的 build_records.py 在 B 上 → 对 out_B.csv 断言：
- (a) zip 顶层含 build_records.py + py_compile
- (b) 源码无禁止运行时
- (c) B 退 0 + out_B 非空
- (d) 首行==精确 10 列表头
- (e) 每行 10 字段
- (f) hierPath 以 `/XI_TopB.` 开头
- (g) instName==hierPath 末段
- (h) cellName∈B 种子集
- (i) 无未展开 `<hi:lo>`（bus 已展开）
- (j) 反硬编码源码无 B-only 字面量
- (k) 跨输入 A 字节匹配 expected_A.csv + A/B 种子不相交 + 无 A-only 泄漏
- (l) 3-seed 确定性
- (m) out_B 字节级匹配 gold expected_B.csv

独立 oracle：从 B 的 libs.txt 重推导种子集/顶层前缀/总线展开不变量（结构上与 reference 的 BFS 不同），不信任候选输出。

## negative (4 stubs, 全 FAIL check)

- `empty_csv`：写空文件 → (c) FAIL
- `header_only`：只写表头 → (k) cross-input FAIL
- `hardcode_A`：硬编码 A 的 CSV → (f) top-instance 不符 FAIL
- `hardcode_B`：硬编码 B 的 CSV → (j) 反硬编码源码含 B-only 字面量 FAIL

## Self-verify

- ✅ reference_submit.zip PASSES check (13/13)
- ✅ negative_selftest: 4/4 negatives FAIL check
- ✅ JSON round-trip: 从 D.jsonl 反提取 test 字段重跑 → PASS

## Reference scripts saved

- `_ref_38tea_build_records.py` (gold produce, 138 行)
- `_ref_38tea_scan_parents.py` (pyAether 采集, 97 行)
- `_ref_38tea_SKILL.md` (skill spec) — 已存本地（SKILL.md 内容见 trace_deepreads 同目录，未单独存为 _ref 前缀；可在 .75 workdir ref_SKILL.md 取）
