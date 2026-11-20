# Deepread Note — 1795079879562_3ydq7 (D, netlist ULVT delvto inject)

- session: `1795079879562_3ydq7.messages.json`
- user/host: joeyl @ hfeg0plg74
- mc: 246 (D-pure, schematic_netlist / analog_context)
- claimed: r1005 (2026-11-20), marked case → `EDA-Eval-DesignFlow-NetlistUlvtDelvtoInject-001`

## 真实任务
用户要求对 HSPICE 网表中 ULVT 器件（模型 `pulvt_ckt`/`nulvt_ckt`）追加 vth-shift 参数 `_delvto=-0.2`。
- MSG 0（意图轮，逐字）：`请帮忙用这个：/home/joeyl/ulvt_delvto/  给这里的netlist：/rundata/m2701/V0_DDR4/simdir/finesim/workdir/joeyl/simulation/Bias/hspiceD/schematic/netlist/netlist  加vth=-0.2v`
- assistant 构建 `reduce_vth.py`（313 行）：扫描网表 X 实例行，按模型名（首个含 `=` token 的前一个 token）识别 ULVT 器件，在语句末尾（`$`/`//` 注释前）追加 `_delvto=<值>`，已有 `_delvto=` 则替换（幂等），保留 `delvto_user=`，跳过 `.subckt`/注释/非 X 行；支持 `+` 续行。
- 对 4 个生产网表（Bias / CML_C2C / Solo_Divider / WCKTop）处理后 VERIFY: PASS。
- 后续会话（MSG 89 附近）用户修正 PMOS 应 +0.2 / NMOS -0.2（模型相关），但本 case 采用 A-faithful 单轮：prompt = MSG 0 逐字，期望 = 所有 ULVT 实例追加 `_delvto=-0.2`。

## 资产选取
- A（assets/.../netlist）：真实 Bias 网表，84 行，3 个 ULVT 实例（XM10/XM9 pulvt_ckt @ WCKIbBias_Opamp 子电路；XNM18 nulvt_ckt @ Bias 顶层）。
- B（hidden/netlist）：真实 CML_C2C 网表，131 行，8 个 ULVT 实例（XPM2 pulvt_ckt @ WCK_C2C_RFB；XM10/XM9 pulvt_ckt @ WCKIbBias_Opamp；XNM6/XNM0/XNM5/XNM1 nulvt_ckt @ WCK_C2C_RFB；XNM18 nulvt_ckt @ Bias）。
- A/B token/结构不相交：A 顶层 = Bias（无 WCK_C2C_RFB/CML_C2C），B 顶层 = CML_C2C（含 WCK_C2C_RFB 子电路 + B 独有实例 XPM2）。

## check.py 12 断言（a-l）
a zip 含 solver.py；b py_compile；c solver.py≥500B 反空壳；d B 上 subprocess exit0 + stdout>1000B；e 行数==B 输入行数；f 仅 ULVT 行被改；g pulvt_ckt 行含 `_delvto=-0.2`；h nulvt_ckt 行含 `_delvto=-0.2`；i 非 ULVT 实例行逐行不变；j `delvto_user=` 计数保持；k 3-seed md5 确定性；l 反硬编码—输出含 B 独有 token `WCK_C2C_RFB`。

## 自验
- ref check PASS(True)；3 negatives（empty/print_only/core_deleted）全 FAIL；§4.9 (a) hardcode-A-names → FAIL[g]（XPM2 漏改）；(b) modify-all-X → FAIL[f]（非 ULVT 行被改）。
- 与 D 已有 `EDA-Eval-DesignFlow-UlvtDelvtoReducer-001`（同用户早期 mc23 会话 qsn6y，synthesized 非 a-faithful）区分：本 case 来自后期 mc246 会话，a-faithful 逐字 prompt，hidden B 为真实 CML_C2C 生产网表。
