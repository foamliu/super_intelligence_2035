# gp8t1 — schematic hierarchy parent-locate (LPDDR6 precharge/AP defect debug)

- session: `1794797478286_gp8t1` (subdir path: `/home/e0027609/.cline/data/sessions/1794797478286_gp8t1/1794797478286_gp8t1.messages.json`)
- user: e0027609 @ hfeg0pkn005 (10.129.2.14), mc=70
- keywords: schematic:2056 verilog:283 cmos:200 analog:87 netlist:81 pyaether:71 transistor:62 drc:39
- tools col: 2055 schematic / 57 netlist / 41 pyAether / 3 virtuoso / 3 synthesis
- size: 803369 B, 88 msgs, 2026-11-16

## 真实任务弧（user turns）

- **U#0**: 「我现在有一个case，是和autoprecharge相关的，并且是BG2，BK2这个bank fail 我想知道可能会出现问题的地方 它的完整sequence是这样的 ACT(9 different banks)->[RD AP(no compare)->DES(44tck)](forward 9 banks' row+col)->ACT(Any Bank1)->ACT(BG2BK2)->RDAP(BG2BK2 no compare)->RDAP(Any Bank1 no compare)->ACT(BG2BK2)->WR->PRE->ACT(BG2BK2)->RD->PRE」→ DDR 协议时序分析（assistant 走 JEDEC tRAP/tRAS/tRC 推演）。
- **U#10**: 「这个case应该是读丢失，因为ACT-WR-RD可以pass，但是ACT-WR-PRE-ACT-RD会fail，且目前看起来和内部的timing没关系，怀疑和内部defect有关系，现在需要找可能有问题的电路模块，你帮我找一下可能的位置」→ 从时序分析转电路级定位。
- **U#12**: 「与最后一笔的row和col地址无关，只和bank地址有关」→ bank-wide bitmap，排除 row/col 电路。
- **U#14**: 4 条线索（fail 数据特征=上电后数据错乱/未上电无 data；PRECHALL 关 BG2BK2 仍 fail；只有 BG2BK2 fail；fail 与前面不同 bank 的 AP 已 Active 密不可分）+ **电路文件在 `/proj/dejoa/V0/workdir/e0027609` 的 schematic**。
- **U#65 / U#66**（选用，verbatim）:「找一下你怀疑的地方在电路中的所属模块，方便我能够迅速找到」→ 明确的「反向查父」交付请求：给定怀疑的叶子 cell，找出它们在 schematic 层次里的所属父模块路径（top→target），方便用户在 Aether 里一路点下去定位。

## assistant 工具链（msg 14-87）

1. pyAether/eda_agent 打开 OA workdir → 读 cds.lib → 拿到库定义（dejoa_top/dejoa_digital/dejoa_array/dejoa_MAT/dejoa_work）。
2. `list_allowed_files` 列库目录 → 发现 OA 平铺结构（cell 直接在 lib 下），dejoa_digital 有 4045 schematic cells。
3. 写 `zhulong_explore.py` 按关键词（PRE/BANK/AP/EQ/ISO/ACT/PLS/CMD）过滤 → 命中关键 cell：`AutoPreCtrlM6`、`PreChGenM6`、`PreBnkCntrl`、`CmdDecPre3Unit/33Unit/331Unit/332UnitM6/333Unit`、`BankLogic/CasBnkLogic/RasBnkLog*`、`RdApFifo*/WrApFifo*`、`RdApShifterM6`、`RdApLogicM6`。
4. **「反向查父」脚本** `zhulong_findparent.py`（msg 69-71）：扫所有 schematic 的 sch.oa 二进制，看哪些 cell 例化了关键子模块 → 汇聚点 = **`APBGBACtrlM6`**（同时例化 `RdAPBGBACtrlM6` + `PreBGBACtrlM6` + `PreChDecUnit0/1/2` + `PreFifoCtrlM6`）。
5. `zhulong_p2.py`/`zhulong_p3.py` 往上追父 + 取实例名（window 函数读 sch.oa 抽实例/网名字符串）。

## 金标准交付（msg 87，用户实际接受的形态）

top-down 层级路径（带实例名）：
```
LP6TOP (dejoa_top)
└─ Channel (dejoa_top)
   └─ ChanMidSC0 (dejoa_top)
      └─ ControllerM6 (dejoa_digital)
         ├─ AutoPreCtrlM6 (I_AutoPreCtrlM6_815)
         │    ├─ RdApShifterM6 (I_RdApShifterM6_25)
         │    ├─ RdApLogicM6   (I_RdApLogicM6_26)
         │    └─ WrApLogicM6 / nWTPLatCtrl
         ├─ BankLogic (I..._3059/_3060)
         │    ├─ RasBnkLogic → PreBnkCntrl
         │    └─ 2× CasBankLogic
         ├─ ActMultiBnk
         └─ PreChCmdDecM6 → PreChGenM6
            └─ PreChnACUShiftM6 → APBGBACtrlM6 → { RdAPBGBACtrlM6, PreBGBACtrlM6, PreChDecUnit0/1/2, PreFifoCtrlM6 }
```
结论：嫌疑在 `dejoa_digital`（外围控制逻辑），非 `dejoa_array`；核心 = `PreChGenM6`（生成 PreChBG0~3Bnk/AllBnk 预充电脉冲）+ `APBGBACtrlM6`（RD-AP 与显式 PRE 汇合处的 BG/BA 译码 + FIFO/移位链）。

## 造题设计（A 档 trace-faithful + synthesized-reframe produce）

- **真实意图**：U#66 — 给定怀疑叶子 cell，在 schematic 层次里找所属父模块路径（top→target），方便迅速定位。
- **reframe**：合成 schematic 例化表（A=LPDDR6 precharge/AP cluster 真实形状，token 保留真实 cell 名；B=完全不同芯片/层次，token 不相交）→ 通用「反向查父」脚本 `find_parent_modules.py`，输入例化表 + 怀疑 cell 清单，输出每个 target 的所有 top→target 父链 JSON。
- **判分范式**：subprocess-on-B + recompute-ground-truth-from-B-table（独立算法重算期望父链集合）+ anti-hardcode（B 输出零 A-only token）+ 多父 target（fan-in，需报全部链）给「牙」。
- **domain**: schematic_netlist（schematic cell 层次遍历，反向查父）。
- **与 r984 (NetlistInstHierTrace) 区分**：r984 = Verilog 网表 top-down 实例化父链追溯（给 module 名 climb instance hierarchy，named-port 风格）；本案 = schematic cell 库反向查父（扫所有 cell 找谁例化 target，DAG fan-in，OA 风格）。方向相反 + 数据形态不同（netlist 文本 vs cell 例化表）+ 多父链判分。
