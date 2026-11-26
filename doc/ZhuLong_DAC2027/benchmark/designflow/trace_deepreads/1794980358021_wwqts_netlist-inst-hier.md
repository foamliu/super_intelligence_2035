# Deepread — 1794980358021_wwqts (wenfeiz @ hfeg0pgn145, mc=162)

- shard: D | domain: schematic_netlist | scan: 20261119_172105
- keywords: netlist:2026; schematic:970; verilog:1503; cmos:610; aether:82; analog:56
- D-pure score 3052 (netlist+schematic+analog+waveview), bad 0 — clean D-pure.
- ledger: claimed r984 → case `EDA-Eval-DesignFlow-NetlistInstHierTrace-001`

## 真实任务（3 段，本案取第 2 段）

1. (msg 6–17) 分析 `V0_WOWTOP_2026Oct29.172927/netlist` 目录信息 → Aether 2025.09.sp1.hf7 / jackliu / 2026-10-29 18:08 / 0 err 0 warn / 顶层 WOWTOP。
2. **(msg 18–41) 本案核心**：用户给 3 个 module（`RHR_compare_LH_TOP`、`RH_DLUT6_STRU_REV01`、`RH_PTR_DISC_SKIP_REV02`），要它们的「path」。
   - assistant 第一次用 grep 给了**模块定义所在文件行号**（文件路径）。
   - 用户纠正：**「不是文件路径，是实例化层次结构」**。
   - assistant 改写脚本追溯实例化父链（instance hierarchy path），结果：
     - `RHR_compare_LH_TOP` → inst `I_RHR_compare_LH_TOP_34`，深度 11：
       `WOWTOP.I_C_Top.I_Array16GTop.I_SpineTop.I_BankTopX2B76.I24.IBankTop_E.I_BankLogic_17(BankLogic_DDGOA_rev).I_RH_DLUT_FULL_New_33(RH_DLUT_FULL_REV01).I_DLUT6_CON_REV01(RH_DLUT6_CTRL_REV02).I_POINTER_DISCARD_SKIP_REV00(RH_PTR_DISC_SKIP_REV02).I_RHR_compare_LH_TOP_34`
     - `RH_DLUT6_STRU_REV01` → inst `I_DLUT6_STRU_REV01`，深度 9（与 CTRL 平级，RH_DLUT_FULL_REV01 下）
     - `RH_PTR_DISC_SKIP_REV02` → inst `I_POINTER_DISCARD_SKIP_REV00`，深度 10（RH_DLUT6_CTRL_REV02 下）
   - 关键发现：RHR 嵌在 PTR_DISC_SKIP 内；STRU 与 CTRL 平级；三模块都在 Bank17 的 RH_DLUT_FULL_REV01 下。
3. (msg 42–107，未完结) `proj_special.sv` L6615 `bind CBRCounter_S_PN1p76 internal_monitor_rhr ...`，找 `CBRCounter_S_PN1p76` 模块定义（不在 Aether 网表，属 RTL 设计模块）。本案不取。

## 案件合成（NetlistInstHierTrace-001）

- asset_fidelity: **synthesized-reframe**。真实网表 ~104 万行 50MB 无法入沙盒，故合成保留真实层次形状的小网表。
- A（可见）：`netlist_A.v`（DDGOA/LPDDR5，顶层 WOWTOP，深 11 层链路 + 2-sibling fan-out + decoy Channel/PllTop），`targets_A.txt`（3 个真实目标模块名），`task_brief.md`（含「不是文件路径，是实例化层次结构」澄清）。
- B（隐藏）：`netlist_B.v`（SERDES PHY，顶层 SERDES_TOP，同形状深 7 层 + sibling + decoy PllTop），`targets_B.txt`（TxEyeMonitor/RxDeserializer/TxAligner，完全不同名）。
- 候选 deliverable：`candidate.py`（通用 Verilog 网表实例化层次追踪器）+ `hierarchy_report.json`（A 上结果）。
- check 12 条断言（a–l）：a zip 结构 / b 编译 / c A schema / d A 含 3 目标 / e–g A 三路径精确匹配 / h B 跑通+schema / i–k B 三路径精确匹配 / l 反硬编码（B 输出零 A-only token）。
- 3 个负样本：empty(h)、print_only(h，硬编码 A-only)、core_deleted(i，真解析但 climb 少一层丢 top 前缀)。ref PASS / 3 neg FAIL / 3-seed md5 一致。

## 教训 / 注意

- 「文件路径 vs 实例化层次」是真实用户澄清点，本案把它做成 task_brief 的显式约束，强迫候选做 instance-hierarchy 而非 grep 行号——天然区分真解析与表面 grep。
- 合成网表用 named-port 风格 `inst module ( .p(net) );`，parser 必须平衡括号 + 排除关键字，避免误把 `wire/reg/assign` 当实例化。
