# r598 deepread — feng1z / 1794561894844_927j6 (SPF WL/BL coupling with short-merging)

**选料**：r598 fresh-pool 选料。summary_1115_081559.tsv → candidates_mc10 (mc≥10) → 4-shard ledger anchor 归一交叉 → 374 truly fresh。top by mc 70+ 多为 xinqiaoz skill-orch / steveny doc / miccao GUI / e0039602 sim（已知 reject 模式）。转 mc 40-73 段 peek 3 候选：hktklin/2dyfr(mc50 SKILL 文本转换 L1 简单)、laryu/nckh5(mc66 SVRF via debug+env 错误 messy)、**feng1z/927j6(mc73 pex:172) ACCEPT**。

## trace 概览
- user=feng1z, host=10.129.8.221, sid=1794561894844_927j6, mc=73
- TOTAL msgs=111, USER_TURNS(user_input)=13
- domain=physical_verify (PEX / SPF parasitic)
- 真实 SPF: /proj/drgqx/V0/ver/pex/feng1z/Ary_m392Meg_U_1028_final/lpe/Ary_m392Meg_U/Ary_m392Meg_U.spf_CC (**359MB**, 359121674 bytes)

## 用户意图演进（13 个 user_input）
- UI#0-3（重复 4 次）："查看这个文件夹下的脚本...告诉我每个脚本的基本逻辑" = Q&A/explain（KevinChen 的 spf_script/DRGQX_kevinc/*.pl）。**非 produce-task**。
- **UI#9（CORE produce-task）**："WL routing 需要在SPF原始文件中找 sxxxxcxxxwlb/a，BL routing 需要找 s0102cxxxblb/a 这条线路径上如果遇到 brknet 或者 switch 就按 short 成一根信号处理，SPF 原始文件在 /proj/.../Ary_m392Meg_U.spf_CC"。→ 解析 SPF，找 WL/BL routing path，brknet/switch 按短路合并成一根信号。
- UI#38：澄清 WL pattern = "sxxxxcxxxwlb/a"
- UI#44：另一 WL pattern = "s00m0wle/wlo<...>（e/o 结尾）"
- UI#46："如何运行脚本"
- UI#63："输出不要 topBLb 这样，直接按 SPF 原始文件 sxxxxcxxxwlb/a 输出" → display name 用 routed net 名而非 topBLb 标签
- **UI#78-79（关键扩展）**："当 s0102cc00blb 遇到 brknet 或 switch 接了 $Mq1blb{$num}，也算同一条线，$Mq1blb{$num} 遇到 brknet 或 switch 接下去，都算 short 成同一根 blb，直到不接内容，wl 同理" → **transitive short closure**：短路链传递闭包，blbMq1/blbMq0 子节点也参与合并
- UI#97："增加两个 .pl，把 WL to BL coupling 大于等于 15aF 的取出来" → 阈值过滤（15aF = 0.015fF）
- UI#109："介绍下这套脚本每一个脚本的逻辑" = Q&A

## agent 交付物（gold）
agent 写了 inspect_spf.py~inspect_spf6.py（迭代探测）+ smoke 环境（mini.spf 1168 bytes + prepare_and_smoke.py + smoke_env.py）+ 最终交付 `/home/feng1z/spf_script_fixed/`：
- task1_0124_bla.pl (6886B, BLa coupling)
- **task1_0124_blb.pl (6886B, BLb coupling)** ← 本 case 核心
- task1_0124_bla_15aF.pl / task1_0124_blb_15aF.pl (15aF 阈值变体)
- task2_0124.pl / task3_0124.pl (BL loading / BL2BL coupling)
- run_cxsa_spf.pl (driver)

## 核心算法（task1_0124_blb.pl，逐行确认）
1. **parse SPF**：逐行读
2. **short adjacency**：`/^X\S+\s+(\S+)\s+(\S+)\s+(?:switch_close|brknet)/i` → 两 net 互为邻居（switch_close 与 brknet R= 都算短路）
3. **connected components**（DFS 传递闭包）：每 component = 一根信号
4. **BLb grouping**：component 含 `bl[ab]Mq\d<\d+>` 成员 → 按 Mq pattern 分类：
   - blbMq1<N> → topBLb（cat1），Mq1blb{N}=disp
   - blaMq1<N> → normalBLa（cat2）
   - blbMq0<N> → normalBLb（cat3），Mq0blb{N}=disp
   - blaMq0<N> → botBLa（cat4）
   - **display name** = component 中 routed `s\d+c\S*bl[ab]<\d+>` 成员，否则用 Mq 名（UI#63 要求）
   - 每 member → bit num
5. **isolated Mq fallback**：0..4495 中未在 component 出现的 blbMq1/blbMq0 → 自成 bit（disp=Mq 名）
6. **WL grouping**：component 含 `s\S+wl\S+<\d+>` 成员 → WL group，disp = 该 s..wl 名；每 member → WL group name
7. **coupling extraction**：`/^C\S+\s+(\S+)\s+(\S+)\s+(\S+)/` → net1/net2/cap：
   - net1∈WL_group & net2∈topBLb → cap1b["{wl} to {Mq1blb disp}"] += cap
   - net2∈WL_group & net1∈topBLb → 同上（双向）
   - net1∈WL_group & net2∈normalBLb → cap2b["{wl} to {Mq0blb disp}"] += cap
   - net2∈WL_group & net1∈normalBLb → 同上
8. **unitConvert**：`e-` 且无 [NPF]F 后缀 → ×1e15（F→fF）；`PF` 后缀 → 去后缀 ×1e3；否则原值
9. **output**：WLtoBLb_coupling_{data}.txt：先 cap1b（topBLb，sorted keys），再 cap2b（normalBLb，sorted keys），每行 `"%s : %.6f fF"`，过滤 `cap <= 0.0035`（_15aF 变体用 0.015）

## mini.spf（agent 合成的 smoke fixture，本 case A 档模板）
```
*|DSPF 1.3
.SUBCKT MINI blaMq1<5> ... s0102cc00blb<4>
Xsw1 blaMq1<5> s0102cn04bla<9> switch_close      # BLa short
Xsw4 blbMq1<2> s0102cc00blb<4> switch_close       # BLb short
Xbr1 blbMq0<5> net1<5> brknet R=0.001             # brknet
Xsw5 net1<5> s0102cn13blb<99> switch_close        # 3-hop BLb chain
Xwlsw1 XImary00.net1<0> s00m0wle<100> switch_close # WL short
Xwlsw4 XImary00.C_m0wleL<0> XImary00.C_m0wleR<0> brknet R=0.001
*|NET ... PF
Cc1 blaMq1<5> blaMq1<7> 1e-18
Cwl1 s00m0wle<100> blaMq0<3> 5e-18
.ENDS
```

## case 设计（B档 mock-behavioral，承 r593-r597 script-task 模式）
- 把"live 359MB SPF + Perl 脚本"重构为**纯 Python3 `spf_wl_blb_coupling.py <spf> <out> <threshold_fF>`**，离线可判分
- **input A**（SUT 可见）：合成 mini SPF（忠实 DSPF 结构，本 case 模板）
- **hidden B**（check 跑）：不同 nets/chains/values，4 条输出
- **hidden B2**（反硬编）：3 条输出，不同 top 值
- **核心测点**：transitive short closure（3-hop brknet+switch chain）、WL/BLb member 归属（coupling via 非首节点）、PF vs e-notation 单位转换、阈值过滤、isolated Mq fallback、display name = routed net、cap1b/cap2b 分块排序、确定性、反硬编

## 拟定 case_id
EDA-Eval-DesignFlow-SpfWlBlbCoupling-001 (physical_verify, L2-boundary, B档)

## 断言清单（k=14 a-n，与 check() 一一对应）
14 条断言：①zip 含 spf_wl_blb_coupling.py 且 py_compile 过 ②B exit0 产非空 out ③B 输出行数==4 ④B 含 "s00m0wle<50> to sb1cc00blb<3> : 6.000000 fF"（transitive member 累加 C1+C2+PF C7）⑤B 含 "s00m0wle<50> to sb1cc22blb<6> : 6.000000 fF"（normalBLb）⑥B 含 "s00m0wlo<33> to sb1cn09blb<8> : 5.000000 fF"（3-hop brknet+switch chain）⑦B 含 "s00m0wle<50> to sb1cn09blb<8> : 2.500000 fF"（intermediate chain node nb1<2> 归属）⑧B 不含 "blbMq1<4>"（0.5fF 阈下排除）⑨B 不含 "s00m0wlo<33> to sb1cc00blb<3>"（0.5fF 阈下排除）⑩B 所有输出 cap > 1.5（阈值过滤）⑪cap1b block 先于 cap2b block（BLb 分块排序）⑫PF 单位转换正确（C7 0.001PF→1.0fF 已并入④）⑬B2 输出 3 行且 top 值 9.0≠B 6.0（反硬编）⑭两跑字节一致（确定性）
