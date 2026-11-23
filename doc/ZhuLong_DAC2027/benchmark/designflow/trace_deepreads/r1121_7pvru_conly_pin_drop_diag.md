# r1121 (shard B) — 1-case 产出轮: 7pvru → ConlyPinDropDiagProduce-001

**日期**: 2026-11-24 04:2x
**轮次**: r1121 (loop shard B)
**trace**: `1795425823004_7pvru` (e0044979@hfhds201, mc58, hspice:583/schematic:366/netlist:85/spectre:65)
**case**: `EDA-Eval-DesignFlow-ConlyPinDropDiagProduce-001` (k=15 a-o, L1 纯 Python)

## 1. 候选发现

r1120 判 "1124 scan top hspice-dominant 候选全 ledgered"。本轮复查 1124 scan
(`ssh_eda_search_20261124_023802/summary.tsv`) mc5-60 / spice>=10 / spice_frac>=0.10
的 top-80 去重 21 sids，cross-check 4-shard 台账发现 **3 个真未 ledger**:
- `1795425823004_7pvru` (e0044979@hfhds201, mc58, hspice:583) ← 选中
- `1795418883724_ounw7` (pirinliu@plg77, mc55, hspice:403) ← 备选
- `1795318721598_nakpz` (yohannw, mc59, waveview:128/hspice:18) ← waveview-dominant, 偏 D 拒

r1120 的 top-10 by spice 检查漏掉了 7pvru(spice648)/ounw7(spice403)，因它们落在
4msey(spice679) 之下。**修正**: 1124 scan 仍有未 ledger 强 B-spice 候选。

## 2. 深读 7pvru (188 msgs / 1.8MB)

**真实意图**: e0044979 跑 FineSim SRAM tailoring on
`CXN4HCSPS16384X8M8B8C1R1W1BW1RE1_FS_i4_c4_l6` (420250 nets / 1233423 instances /
10GB DSPF)。两个 run:
- **shm_version1** (old, Python `stream` two-pass conly engine) — 结果正确
- **out_NativeC_ver2** (new, Native C++17 `native_core`) — 精度损失

用户令 "check stage by stage to narrow down the reason"。

**assistant 工具链**: 31 run_approved_command + 29 read_files + 21 list_allowed_files
+ **13 editor** (patch C++ 源)。逐 stage 对比 stage1(conly)/stage2(split)/detect/
tailor_map/tailor_fold/powerrep 日志 + load.log + C++ 源(stage1.cpp/stage2.cpp/
emit.cpp/source.cpp) + Python 源(plan_emit.py/array_fold.py/conly_stage.py)。

**根因** (assistant 最终结论):
- stage1 conly: 两 run 同 nets/instances/caps/coupling，但 engine 不同
  (stream 537.03s ledger NOT BALANCED vs native_core 65.55s ledger ok)
- **fold stage pin_dropped 发散**: shm_version1=325760 vs out_NativeC_ver2=80000
  (deficit 245760)，而 net_dropped/cc_dropped/device_dropped/devices_emitted 全匹配
- **根因**: C++ `emit.cpp` `write_conly()` 只 emit `*|P` (port pin) 行，**完全漏掉
  `*|I` (instance pin) 行**；Python stream engine 有 emit `*|I`。fold stage 用 `*|I`
  元数据计数/丢弃 pin，C++ run 缺 `*|I` → pin_dropped 严重偏低 → 下游精度损失
- assistant patch: 在 `write_conly()` 的 `*|P` 循环后加 `*|I` 循环，rebuild binary ✓

## 3. reframe (L1 纯 Python, 无 EDA 沙盒依赖)

spec 驱动 `stage_diff.py <run_a_dir> <run_b_dir> <out_json>`:
- 解析两 run 的 stage1.log (conly) + tailor_fold.log
- 提取 stage1: engine(stream/native_core)/nets/instances/ledger_balanced/
  conly_time/stage1_total/structure_workers
- 提取 fold: cc_dropped/device_dropped/net_dropped/pin_dropped/nets_emitted/
  devices_emitted/device_pin_dangling
- 输出 JSON: {a, b, divergences[], root_cause}
- root_cause: pin_dropped deficit + net_dropped 匹配 → 非 net pruning → b engine
  native_core → C++ conly emit 漏 *|I instance-pin

**A** (给 SUT): `run_shm_version1/` (stage1.log + tailor_fold.log, 真实日志摘录)
**hidden B**: `run_out_NativeC_ver2/` (stage1.log + tailor_fold.log, 真实日志摘录,
engine/timing/ledger/pin_dropped 全异)

## 4. 自验

- REF `stage_diff_ref.py`: **15/15 PASS** (a-o)
- §4.9 三假:
  - neg_a_empty (空壳) → 2/15 FAIL ✓
  - neg_b_print_only (硬编 A 值给两 run) → 11/15 FAIL ✓ (b assertions i/e/f 挂)
  - neg_c_core_removed (解析对但无 divergences/root_cause) → 12/15 FAIL ✓
- `negative_selftest.py`: REF PASS + 3 negs 全 FAIL → 4/4 OK, exit 0
- 3-seed (B 日志行洗牌 seed 11/22/33): b.pin_dropped 恒 80000 ✓ (解析器顺序无关)

## 5. check 15 条 (a-o)

a(zip解压) b(script+py_compile) c(A+B exit0+合法JSON) d(a.engine=stream)
e(b.engine=native_core anti-hardcode) f(ledger 发散 a NOT BAL/b ok)
g(conly 时间发散 a>b) h(a.pin_dropped=325760) i(b.pin_dropped=80000 anti-hardcode)
j(net_dropped 匹配 325760) k(divergences 含 pin_dropped diverge)
l(root_cause 含 pin_dropped deficit + instance-pin/*|I/conly emit)
m(两 run nets=420250) n(devices_emitted 匹配 260535)
o(3-seed B 行洗牌 b.pin_dropped 恒 80000)

## 6. 台账

`1795425823004_7pvru`: claim → mark case ✓ (covered +1)
