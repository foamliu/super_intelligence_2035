# deepread — 2ka5p (e0030760 @ hfeg0pkn004) — SRAM testbench measure audit

## trace meta
- session: 1793791169909_2ka5p (dir-based)
- user: e0030760, host: hfeg0pkn004
- 390 msgs, 2.06 MB, mtime Nov 5 17:02
- spice grep match_count: 2663 (cron 盲区直扫发现)

## 对话流（25 user text msgs）
- U#0: 「/home/e0030760/Documents/Solido/test_fix.sp 帮我检查一下这个testbench，里面测试WSNM、Iread、Iwrite、Ileak的指令是否存在问题」— **提出需求 ✓ A-档选轮**（无根因/修复方向）
- U#47: 「帮我修改一下，但不要删除原文件」— 修改请求
- U#54: 「为什么需要仿真峰值电流和平均电流？」— 追问
- U#56: 「用你提供的 testbench 进行 solido 仿真，检查 Iread/Iwrite/Ileak 是否正常」— 验证
- U#73: 「修改 iwrite_avg 的窗口」— 调整
- U#82: 「WNM solido 仿真值阶梯式分布，检查什么问题」— 诊断
- U#119: 「Ileak 和 Iwrite_avg 不满足正态分布，检查为什么」— 诊断
- U#135: 「增加 log_Ileak 测试」— 扩展
- U#148: 「logILEAK 转换回来和 Ileak 对不上」— 诊断
- U#167: 「取 log 还是 ln」— 方法
- U#169~U#225: model file 解读、solido MC 仿真逻辑、SNM 蝴蝶曲线脚本
- U#268~U#312: 总结文档、hspice 服务器、一键脚本、结果查看

## 金标准（assistant AST#46，对 U#0 的完整审查）
test_fix.sp 的 4 项 measure 逐一核对：

### ❌ Iwrite — 原理性错误（最大问题）
- 指令：`.MEASURE DC Iwrite FIND I(VIPRB_WRITE) AT=VVDD/2`
- 写单元 S_IWRITE=VDD, SB_IWRITE=0, WL 常开, BL(VDD3)=0 被 0V 源钳住
- **写电流是瞬态量**：DC 稳态解一变过去，S 节点被拉低翻转，通路两端压差归零，DC 工作点电流→0
- 实测 -6.6pA ≈ 0 vs solido MC Mean=-482nA → **Iwrite 坏**
- AT=VVDD/2 指向扫参量 VIN，Iwrite 跟 VIN 无关，"随便取了个点"
- 修复：用 .MEASURE TRAN（WL 脉冲 + 0V 安培计 + iwrite_peak/iwrite_avg），或 `.MEASURE DC Iwrite MAX par('abs(I(VIPRB_WRITE))')` 取峰值

### ✅ Iread — 能出数，但采样点含义需注意
- 指令：`.MEASURE DC Iread FIND I(VIPRB_READ) AT=VVDD/2`
- 读单元 S_IREAD=0, WL 开, BL 经探针预充到 VDD → 静态泄放电流
- 实测 21.86µA 合理。AT=VVDD/2 = VIN=0.3375，Iread 跟 VIN 无关，取的是"任意点的稳态读电流"

### ✅ Ileak — 正常
- 待机单元 WL 关, BL=BLB=VDD, 存储位保持，31pA 量级合理

### ✅/⚠️ WSNM (WNM_1/WNM_2) — 能出数，确认定义
- V_input1 VIN_1 0 DC='VVDD-VIN' 互补扫描, WL 开
- `WNM_1 find v(VIN_1) when par('v(S1_WNM)-v(SB1_WNM)')=0 cross=1`
- 实测 WNM_1=WNM_2=250.5mV，两路对称。指令本身工作正常
- 确认定义：直接取写翻转位线电压 vs VDD-VIN_at_flip(=0.425V)

### 其他
- `.tran 1p 10ns` 与 `.DC` 并存，但 measure 全是 `.MEASURE DC`/`.PROBE DC`，无 `.MEASURE TRAN` → **10ns 瞬态白跑，纯耗时**

## bitcell 端口接线（assistant 核对 netlist）
BitCell_FS_CH336 端口：BL BLB S SB VDD VSS WL

| 单元 | BL | BLB | S | SB | WL |
|---|---|---|---|---|---|
| IREAD | VDD2(探针) | VDD | S_IREAD(0) | SB_IREAD(VDD) | VDD(开) |
| IWRITE | VDD3(探针) | VDD | S_IWRITE(VDD) | SB_IWRITE(0) | VDD(开) |
| ILEAK | VDD4 | VDD4 | S_ILEAK(0) | SB_ILEAK(VDD) | VSS(关) |

## 合成（A-faithful L1 k=14）
- **prompt** = U#0 逐字原文
- **A (visible)** = test_fix_A.sp = 真实 test_fix.sp 原文（红线#2 不脱敏，.include 路径保留原值）
  - Iwrite=DC FIND → transient_misuse_dc; Iread=DC FIND → dc_at_arbitrary; Ileak=ok; WNM=ok; tran_without_measure=True
- **hidden B** = test_fix_B.sp（合成，结构不同）
  - Iwrite=.MEASURE TRAN (Iwrite_peak MAX + Iwrite_avg AVG) → ok（正确）
  - Iread=.MEASURE DC FIND AT=VBL/2 → dc_at_arbitrary
  - Ileak=DC FIND → ok; WNM=DC when cross → ok
  - .tran 1p 20ns + .MEASURE TRAN → tran_without_measure=False
  - 不同节点名(VIPRB_READ/net_rd/VBL2/S_WNM/VBI_1/V_amm_wr/BL_WR/VIPRB_LEAK/net_lk/VBL4), VVDD=0.75, 扫参 VBL
- **reference** = review_tb_measure_ref.py：解析 .sp（续行+/measure/tran/DC/voltage source），按 measure type+name keyword 分类
  - TRAN → ok; DC when cross → ok; DC FIND I(write) → transient_misuse_dc; DC FIND I(leak) → ok; DC FIND I(read) → dc_at_arbitrary
  - tran_without_measure = .tran present AND no .MEASURE TRAN
- **check.py 14 断言(a-n)**：含交叉输入守卫(k:A Iwrite==transient_misuse_dc)+交叉输入守卫(l:A tran_without_measure==True)+A-only 泄漏闸门(m)+3 次幂等(n)
- **negatives**: empty_shell(FAIL d)/print_expected_b(FAIL k,hardcode B)/core_deleted(FAIL g,全 ok)/naive_hardcode_a(FAIL f,hardcode A) — 4 distinct

## 自验
- ref PASS 14/14 ✓
- 4 neg ALL FAIL distinct (d/k/g/f) ✓ NEG_RC=0
- §4.9 三假(空壳FAIL d/打印期望FAIL k/删核心FAIL g)全 FAIL ✓
- 断言闸门 k_rationale=14==k_check=14≥8 ✓
- jsonl test==disk check.py sha 62798ed3ac2b901d ✓
