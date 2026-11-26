# r847 deepread: 0gv3z → 跨shard碰撞 defer D (gold 已提取备查, 不双取)

> 11-15 候选池重审「24 待深读」第 4 条深读 (r844 jeij7 / r845 l4tre / r846 iyyzq 已落库, r847 深读 3 条: 3s3zx 不可造 + cdrm1 NOFILE + 0gv3z 跨shard碰撞)

## 一、trace 溯源
- session: `1792378797897_0gv3z` · user `thomas1w` · host `hfeg0pkn002`(10.129.2.11) · mc291 · domain **verification** (A 域)
- 文件: `/home/thomas1w/.cline/data/sessions/1792378797897_0gv3z/1792378797897_0gv3z.messages.json` (subdir-path ALIVE 2.05MB, flat NOFILE = r528 path-bug 第 N 例)
- 397 msgs / 36 real user turns / agent=lead · 真实意图: 分析 LPDDR5 网表 (`/rundata/ddgoa/V0/simdir/verilog/thomaswu/verilog.lpddr5.ddgoa.new/netlist/V0_WOWTOP_2026Oct15.193816/netlist`) 中 mbist/mppr/repair/列冗余/GeniusRepair 模块结构与信号语义
- 旧判 (2026-11-14): "analysis Q&A not produce" → weak. **11-15 reaudit: analysis-Q&A 合法**, 本轮深读确认有 specificity-oracle gold → **可造**

## 二、为何选 CCR_RedCheck (realU#31, msg369) 作单轮 case
用户原话: `CCR_RedCheck是干什么的，输入和输出的功能`
- 单模块、边界清晰、assistant 答案 (msg374) 详尽且含可验证具体名 (端口/子块/计数/父例化)
- tool_result (msg373) **未被 sandbox 剥离** — 真实网表 dump 完整保留 → **A档 trace-faithful 可行** (与 l4tre/jeij7 read_files 被剥不同)
- 与 r818 NoConnPurposeExplainQA / r817 DdjocCircuitPlanReconQA 同范式 (S5 analysis-Q&A + specificity oracle + refuse-to-hallucinate), 不同域(verification)不同主题(列冗余读回校验), 非碰撞

## 三、提取的 GOLD (next round 合成直接用, 无需重抓 trace)

### A 资产: CCR_RedCheck 网表 dump (真实, 1736B, msg373)
```
MODULE CCR_RedCheck line 751460-751732 (273 lines)
   output [5:0] RedCPO
   output RedLatCheckBit
   input  CdeClkRd
   input  ColRedLatExpData
   input  [7:0] EFuseBit
   input  EqIoNAry
   input  PwrOn3
   input  [1:0] RCA87
   input  [5:0] RedCP
   input  RowRedLatCheckBit
   input  cm0_ts_ColRedCheck
   input  [1:0] cm0_ts_ColRedCheckLatDly
   input  cm0_ts_RedFlagCheck
   inout  inh_vss
   inout  inh_vdd2h
   wire   RedCheck / ErrFlag / ExpDatN / ExpDatD / RedCPD / RCA87D
   wire   fnColRedCheckLatDly[1:0] / fnDlySel[3:0] / CheckBitRst / ExpData_force
   sub-blocks: xor2tiny4T_RedCheck×8, ffrqLx1×2, nand2Lx1×24, invLx1×19, invLx2×12,
               bufLx8×7, dlyg6of8Ls1×3, dlyg8of8Ls1×3, dlyg4of8Ls1×1, mxi4Lx1×1,
               mx2Lx1×1, nor2Lx1×3, nor3Lx1×1, nor4Lx1×1, nor2Lx4×1, passgtLx1×1,
               pulsehi9gx1×1, invLx16×1, invLx4×1
   parents: BankTopX2_DFT ×2
```

### B 资产 (hidden, judge-only, msg395): ColRedComp_rev 网表 dump (936B, 同 CCR 族但结构/名全不同)
```
MODULE ColRedComp_rev line 618858-618913 (56 lines)
   output EnFz
   input  [8:6] CA
   input  ColSel
   input  [7:2] Fn
   input  cm0_ts_RedColDis
   input  fnColRedBist
   inout  inh_vbn/inh_vbp/inh_vssz/inh_vcc/inh_vss/inh_vccz
   wire   [8:6] ColCom
   sub: Xnor2FooterColx1×3, nand2GFx1_colred×2, Col_nand4GFx1×1, oai31PFx1_colred×1,
        invLx1_colred_new×2, nor3Lx1_colred×1, nand3Lx1_colred×1, Col_invPFx4×1
   ColCom drivers: Xnor2FooterColx1 .Y(ColCom[8/7/6]) .A(CA[8/7/6]) .B(Fn[7/6/5])
```
B 功能: 列冗余命中比较器 (CA vs Fn XNOR → ColCom → EnFz 使能), 与 A (读回校验, XOR 比较期望 vs 实际) 同族不同职。B-only 标识符 (report 必须不出现): `EnFz` `ColCom` `fnColRedBist` `cm0_ts_RedColDis` `Xnor2FooterColx1` `Col_nand4GFx1` `ColSel` `Fn[7:2]`

### 参考答案 (msg374, 1863B, 已落 `ccr_redcheck_ref_answer.md` 摘要)
核心可断言点:
- 模块定位: CCR=Column Redundancy, RedCheck=Redundancy Check, 列冗余"读回校验/命中检查"单元
- 父例化: BankTopX2_DFT ×2 (DFT 列冗余检查路径)
- 功能: 期望数据(eFuse/锁存) 与实际读出逐位比较 → 产生冗余 latch 检查位
- 输入语义: RedCP[5:0]冗余列指针 / RCA87[1:0]列地址段(CA8/CA7) / EFuseBit[7:0] fuse数据 / ColRedLatExpData期望 / RowRedLatCheckBit行侧 / CdeClkRd读时钟 / cm0_ts_ColRedCheck testmode使能 / cm0_ts_ColRedCheckLatDly[1:0]延迟 / cm0_ts_RedFlagCheck
- 子块: xor2tiny4T_RedCheck ×8 = 8个XOR比较器 (期望 vs 实际, 不匹配→RedCheck/ErrFlag); ffrqLx1×2锁存; mx2/mxi4选路; nand/nor/dlyg时序; pulsehi9gx1脉冲
- 输出: RedCPO[5:0]缓冲传出冗余列指针 / RedLatCheckBit=1bit冗余latch检查位 (上行 Bank 层 RedLatCheckBitLO/RO)
- 流程呼应: FzCPSel 判命中 → CCR_RedCheck 读回校验 → RedLatCheckBit 供 redbist/检测判定该列是否正确修复

## 四、合成决定: **DEFER D, 不双取** (r847)
- ⚠️ r847 ledger mark 时发现跨shard碰撞: 0gv3z 已是 D 的 case `EDA-Eval-DesignFlow-MbistMpprModuleFindQA-001` (schematic_netlist 域, 2026-11-17, 用 realU#0/#1 "看下网表结构+mbist/mppr模块有哪些" → produce-task 网表分类器 candidate.py)
- 本线 realU#31 CCR_RedCheck explain 虽不同 turn/不同 taskform(analysis-Q&A vs produce-task)/不同deliverable(报告vs脚本)/不同check, 但**同 session + 域偏 schematic_netlist**(网表模块功能解释), 守 r824 lesson「选料前必须全 shard 台账并集查重」+ shard 纪律不双取 D 已占 session
- **教训**: 选料前必须 grep 全 shard 台账并集 (本轮深读 0gv3z 前只查了 3s3zx, 漏查 0gv3z → 浪费深读时间). 已在 r847 ledger note + pool_reaudit_A.tsv 记录碰撞
- gold 保留备查: 若未来 D 明确放弃该 session 或运维裁决允许同session多case, 可复活本合成计划

## 五、3s3zx 深读结论 (本轮第 1 条, 不可造)
- session `1791446512697_3s3zx` xuebaok@hfeg0pkn002 mc347, subdir-path ALIVE 1.85MB
- 真实意图 (realU#1): "trantime.sim 里面定义 tran 10ps 是由 matrixrun 脚本决定的, 我如何更改, 让他生成的时候就是 500ps" (how-to Q&A)
- **session 无解终止**: assistant 130+ tool_use 搜索 matrixrun 脚本未果, 找到 trantime.sim 内容 `.tran 10ps 16242001ps` + d6vecgen_compress L201 `my $tranFile="$vecDir/trantime.sim"` 但**始终未定位 10ps 写入处/matrixrun 脚本**, 以 ask_question (msg268) 结束, 用户未答 → **无 ground-truth gold**
- 判定: **不可造(无牙check)** — trace 自身未解决问题, 无法提炼 specificity-oracle gold; reframe 为 produce-task 需凭空编造 matrixrun 答案, 违反 §真实性
- B/D shard 旧判 "incomplete/no resolution" 正确, A 旧判 "how-to Q&A weak" 理由作废但结论 (不可造) 一致, 依据改为 "无牙check"

## 六、cdrm1 NOFILE (本轮第 2 条尝试, 不可造)
- session `1794449150836_cdrm1` daiweilu@hfeg0pgn145(10.129.35.244) mc107 verification, subdir + flat 均 NOFILE (rotation 蒸发, 不在 11-19 scan)
- 判定: **不可造(无真实trace可读)** — 文件已蒸发不可复活 (r528 path-bug 是 flat NOFILE 但 subdir ALIVE; cdrm1 双 NOFILE = 真 rotation 蒸发)
