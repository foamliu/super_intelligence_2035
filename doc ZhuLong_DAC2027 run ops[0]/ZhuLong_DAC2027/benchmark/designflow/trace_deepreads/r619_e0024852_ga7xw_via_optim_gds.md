# r619 deepread — e0024852 ga7xw via_optim_gds (layout_aether)

- **session**: 1794275548538_ga7xw
- **user/host**: e0024852 / hfeg0plg75 (10.129.8.x)
- **mc**: 199 (pex:379;pyaether:563;aether:288;dbopencv:146;cellview:127;.gds:75)
- **trace**: 252 msgs / 24 user_text / 1.3MB (via .75 eda_flow ssh cat + python peek)
- **domain**: layout_aether (pyAether via/GDS optimization)
- **selection**: fresh-pool C-keyword scan mc~200, e0024852 1 existing case (CalibreLvsRepDiag-001 sakf0), ga7xw distinct (iyl1p was recon Q&A about the file, parked). ACCEPT.

## 用户真实意图

e0024852 是 foundry 工程师，做 SRAM bitcell DTCO 的 PEX/寄生优化。trace 前半（UI#0-9）是 GloryEX RC (pex extraction) 调试 + DSPF 寄生 R/C 分析 + "我是个 foundry 厂 我可以改 design rule 我现在就是要把寄生改小"（UI#6）+ dbCrtVia/pyAether 导入问题（UI#7-9）。

核心 produce-task 在 UI#10：用户写了 `via_optim_gds.py` 草稿——**Design-Rule + GDS joint optimization of via size AND lateral position, with metal-width constraints**：
- VIA_SIZES_NM = [12,14,16,20] nm（方形 via 候选）
- OFFSET_FRAC = 0.10（横向 ±10% via 边长平移）
- via 受连接 metal 宽度约束：via size ≤ metal width；平移后必须留在 metal 内
- 每个导出 GDS variant 恰含 ONE optimized via（其余不变，便于 DR/RC 对比）
- 支持 V0D/V0G/V1 三类 via

UI#11-13 是调试：草稿 `aeGetCurDesign()` 返回 None → `cv.libName` AttributeError；`dbGdsIn` renameMode 拼错；`dbOpenCV` 失败。agent 产 `via_optim_gds_fixed.py`（10971B, .75:/home/e0024852/），相对草稿 4 处修复：
1. **getBBox 签名**：`getBBox([fig])` 返回 emyBoxF，读 `.l/.b/.r/.t` 属性（草稿用 `b[0]..b[3]` 索引 = bug，emyBoxF 不可索引）
2. **shape 迭代**：`cv.shapes` flat emyRect 列表（草稿猜 cv.shapes/figList/figures dict-like = bug）
3. **headless 打开**：`dbOpenCV` 替代 `aeOpenDesign/aeGetCurDesign`（后者返回 None = 崩溃根因）；`dbGdsIn` 返回值检查
4. **emyInitAether('-adv')** + `dbuPerUU` → `NM_PER_DBU = 1000/dbuPerUU` DBU-nm 缩放

## case 合成（B档 mock-behavioral reframe）

真实 pyAether/GDS 环境沙盒不可达 → asset_fidelity=synth。提供 data-driven mock `ae_mock.py`（ faithfully 复现 API quirk：emyBoxF 不可索引 / aeGetCurDesign 返 None / cv.shapes flat list / dbGdsIn 返 bool / 调用日志），参数化 `run_via_optim.py` 加载 JSON fixture + exec 脚本。

- **输入 A**（SUT 可见）：fixture_a.json dbuPerUU=1000, M0/M1 W=18 axis=y, M2 W=18, V0D/V0G center(120,199), V1 center(120,309) → 21 candidates
- **隐藏 B**：fixture_b.json dbuPerUU=1000, M0/M1 W=22, M2 W=14, V0D/V0G center(114,112), V1 center(114,407) → 26 candidates（V1 W=14 排除 s≥16）
- **隐藏 B2**：fixture_b2.json dbuPerUU=2000 (NM_PER_DBU=0.5) → 10 candidates（测 DBU-nm 缩放，反硬编 NM_PER_DBU=1.0 产 12 ≠ 10）

## 14 条 a-n 断言（k=18 条件，k_rationale=k_check=18 ≥ 8 ✓）

a zip 含 via_optim_gds.py + py_compile / b B 退出 0 / c headless dbOpenCV 非 aeOpenDesign / d getBBox 列表参数+属性读 / e B 导出数=26 / f B V0D=11 / g B V0G=11 / h B V1=4 且无 s≥16（metal-width 约束）/ i 每候选满足约束（size≤W + 平移留 metal 内）/ j 恢复平衡 creates==detaches / k tag 格式 / l B 候选集==oracle / m B2 dbuPerUU=2000 缩放=10 且≠硬编 nmp1 / n 确定性两跑 basename 一致

## 自验
- ref 18/18 PASS ✓
- 3 neg（naive_empty→c / print_expected→c / deleted_core→d）全 FAIL ✓
- NEGATIVE_SELFTEST ALL-FAIL-OK ✓
- §4.9 (a)(b)(c) 三假全 FAIL ✓
- fixture_A 21 exports ✓（SUT 可开发）
- bool(check)=True ✓
