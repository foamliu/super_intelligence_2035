# 深读: 1792056947936_36yj3 (thomas1w / hfeg0pkn005, mc=347)

- session: `/home/thomas1w/.cline/data/sessions/1792056947936_36yj3/1792056947936_36yj3.messages.json` (2.65MB, 620 msgs)
- domain: schematic_netlist (Verilog 网表结构与数据流通路分析)
- 资产位置: `/rundata/ddgoa/V0/simdir/verilog/thomaswu/verilog.lpddr5.ddgoa.new/netlist/V0_WOWTOP_2026Oct14.192957/netlist` (49.3MB, 1,041,939 行, 6,050 module, thomaswu-owned → e0031982 无权读 → 按 trace 公开事实合成 A 资产, 见 §4.8 / rcx51 先例)

## 用户意图 (提出需求轮, 可作 A 档任务说明)

- msg[0]: `/rundata/.../netlist 分析一下这个网表的结构和数据流通路` ← **A 档任务说明(逐字原文)**
- msg[135]: DQ 数据写入 array 的通路
- msg[196]: row 地址如何确定 section / 开哪个 wordline
- msg[314]: Ra15:14:13 (3b) → 57 section 窗口映射
- msg[365]: row=0x02410 时各 Ra 字段 / SecG 计算值
- msg[550-586]: col=0x0C → Cslin 映射; YsDecX1104_U_DDGOA; Ca987/Ca654 → CslU
- msg[586]: 「把窗口↔块索引↔absolute Csl 地址段完整对应表排出来」← 终局交付需求
- 🚫 后续轮 (msg[367] Ra16 何时非 01 / msg[439] MAT0/MAT1 奇偶位 / msg[500] PhEnHv 来源) 是用户追问根因/修复 → 不作 A 档任务说明 (可作 hint, 不进 prompt)

## 金标准事实 (assistant 报告 + 网表实测, 人工复核)

### 网表总览 (asst[134])
- 顶层: `WOWTOP` (Wafer-on-Wafer top), 1853 端口
- 6050 module, 1,041,939 行, Verilog-2001, `timescale 10ps/10ps`
- 来源: Aether 2025.09.sp1.hf7 原理图导出 (jackliu, 2026-10-14), 顶层设计 `ddgoa_top/WOWTOP/schematic`
- 叶子: 2531 种类型未在文件内定义 (ntn/ptk/ntk_hv 晶体管, invLx/Nx 标准单元, RNPDIFF3t 电阻, AF_EfuseCell ×1632, brknet*, CXcap*)

### 层次树 (asst[134])
```
WOWTOP (仅 4 个实例)
└─ LP5TOP  I_C_Top          (2048 端口, CMOS die 逻辑顶)
   └─ Channel  I_Channel    (IO/控制通道)
      ├─ ChanMid (166 实例: CaRcvCoreM5, ControllerM5(1028端口), CMCenterL/R, Bist...)
      ├─ ChanLeft  I_ChanLeft   .DQ<-DQ[7:0]  .DMI0
      │   └─ DQByte  I_DQByteLo
      │       ├─ DqPad  I_DqPad_0..7      ← 焊盘接收
      │       ├─ WckDCMTop/WCKTop          ← WCK 采样时钟
      │       ├─ DqLat  I_DqLat            ← 写锁存
      │       └─ DqDbusDrv_2/4/6_rev0      → 驱动 Dbus
      │   Dbus[127:0] + DbusDm[15:0]  (128b = 16 时片 × 16b, BL16/16n prefetch)
      │       ├─ DbusPrc   I_DbusPrc       (M6 中继器树)
      │       ├─ DPHalf    I_DPHalf        (链路 ECC/DBI/WR 延迟)
      │       └─ AbusChanMidPrc_new_1      (CMOS→SCmos 低摆)
      │   AbusEv0-15[7:0] + AbusDmEv[15:0]
      └─ ChanRight I_ChanRight  .DQ<-DQ[15:8] .DMI1  (对称)
      └─ Array16GTop  I_Array16GTop
          └─ SpineTop  I_SpineTop   (A-bus 按 BG0-3 × E/W × MidUp/MidDn 分段)
              ├─ BankTopX2_Top/Bot_gut_0820 ×8  (每 BG 一对, 管 B0-B15)
              │   └─ BankTopX2_gut_0820 (LdrDM+EccPty 合成, CAC_Wr, WrX0/X1)
              │       ├─ AbusAryPrcNewU_ddgoa_0618
              │       └─ EccTop128x1/RWCB (ECC 读改写 + WrDrv2BnkW)
              ├─ Array8G_E/W → Array1G_Top_E/W ×8
              │   └─ m1G_TOP → lwdrq_U_CCR_fBcc_sK ×57 (SecWin0-56)
              ├─ CNT2ARYRowBUF  I_CNT2ARYRowBUF_1943 (130 引脚, Controller→ARaY Row BUFfer)
              └─ RasToXdecDrv_Secsel (RAS→Xdecoder Driver, section select)
```

### DQ 写数据通路 (asst[195])
`DQ[15:0]/DMI[1:0] → LP5TOP.I_C_Top → Channel.I_Channel → ChanLeft(ChanRight) → DQByte → DqPad/WckDCMTop/DqLat/DqDbusDrv → Dbus[127:0] → DbusPrc → DPHalf → AbusChanMidPrc_new_1 → AbusEv → Array16GTop → SpineTop → BankTopX2 ×8 → ... → Array`
- 每通道半边一条独立 128b 写总线, BL16/16n prefetch, 16 时片串行, 经 SCmos 低摆 A-bus 按 BG 扇出到 16 bank 写驱动

### Row 地址 → Section → Wordline (asst[281]/[313]/[364])
- 总线: `RowAdrLo_AbusIF[16:0]` (17b 行地址), `RasEnBnkG0-3Lo_AbusIF[3:0]` (每 BG 4 bank 使能), `RasPdlyG0-3[3:0]` (RAS 时序脉冲)
- `CNT2ARYRowBUF` (I_CNT2ARYRowBUF_1943, SpineTop, 130 引脚): in RowAdrLi/RasEnBnkG*Li → out RowAdrLo_AbusIF/RasEnBnkG*Lo_AbusIF + RowAdrLoN (SCmos 差分)
- **17 位行地址全程以 one-hot 预译码传输** (asst[313], 实测端口位宽):

| 地址字段 | 二进制位 | 总线形态 (one-hot) | 线数 |
|---|---|---|---|
| Ra16 (半区 U/V) | 1 | `Ra16[1:0]` / `Ra16_Far[1:0]` (1-of-2) | 2 |
| Ra15:13 (section 组) | 3 | `Ra151413_Near[7:0]` (1-of-8) | 8 |
| Ra8:6 | 3 | `Ra876_Near[7:0]` (1-of-8) | 8 |
| Ra5:3 | 3 | `Ra543_Near[7:0]` (1-of-8) | 8 |
| Ra2:0 | 3 | `Ra210_Near[7:0]` (1-of-8) | 8 |
| (派生) section 组选择 | — | `SecG[6:0]` (1-of-7) | 7 |
| **合计** | 17 | | **34 one-hot 线** |

- `RasToXdecDrv_Secsel`: 等宽重驱动器 (`[1:0]→[1:0]`, `[7:0]→[7:0]`, `[6:0]→[6:0]`), 把 Near 侧 SCmos 信号重建后送 Far 侧 (输出网 `*_Far/*_PreNi`), **不做译码**
- `BankTopX2_gut_0820` 内部生成 `SecG_E/W[6:0]` (1-of-7) + `Ra151413_E/W[7:0]` (1-of-8) + `SecEODisN_E/W[1:0]` (偶/奇 section 禁止) + `GrEn_E/W`
- **SecWin 序号 = 7×(组 0-7) + (组内位置 0-6)**; 57 个 section 窗口 `SecWin0..SecWin56` (asst[364])
  - `I_lwdrq_00` s0_edge SecWin0 (组0); `I_lwdrq_28` s0 SecWin28 (组4); `I_lwdrq_48` s6 SecWin48 (组6); `I_lwdrq_50` s1 SecWin50 (组7); `I_lwdrq_55` s6_edge SecWin55 (组7); `I_lwdrq_56` Edge_Top (第57个边缘)
- `m1G_TOP_E` 873 条匹配; lwdrq section 序号 = SecWin 序号, 呈「组×7+位置」规律
- m1G_YS_Near/Far_Top: `input Ra16` (1 位, 只取 Ra16_Far[1]); m1G_TOP: `.Ra16Bot <- {Ra16_Far[1], Ra16_Far[0]}` (两位都接)

## 合成判定

- A 档 trace-faithful: 任务说明 = msg[0] 逐字原文; 资产 = 合成 Verilog 网表 (按上述公开事实: module 名/信号名/层次/one-hot/57 section 全用原值; 真实 netlist 在 /rundata 无权读)
- 金标准事实 (数值容差 / 拓扑等价 / 产物确由工具生成): top=WOWTOP, 6050 module, DQ[15:0], 17b row→34 one-hot, 57 section, SecG 1-of-7, Ra151413 1-of-8, Ra16 1-of-2
- 隐藏 B: 换结构 (不同 top 名 / 不同 section 数 / 不同 one-hot 宽度 / 不同 DQ 宽度), 杀硬编码
- 判分: 真解析器跑 B → 断言结构 (top/module 数/端口计数/实例计数/层次深度/dataflow driver+fanout/one-hot 宽度/section 数/SecWin 列表) + 跨输入护栏 + 3 种子子集
