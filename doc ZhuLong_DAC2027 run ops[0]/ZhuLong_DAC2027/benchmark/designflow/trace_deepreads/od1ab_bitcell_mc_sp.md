# 深读 od1ab — 6T bitcell MC HSPICE .sp 生成

- session: `1793675697038_od1ab.messages.json`
- user: e0030760 @ hfeg0pkn004 (10.129.2.13)
- mc=46, nmsgs=35, nuser_text=2, model=GLM-5.2
- keywords: netlist:113 schematic:56 transistor:17 hspice:11
- 资产可读性: /proj/lacaa/V0/... → /rundata/lacaa/... **policy 可读**（agent 成功 read_files + grep）但 e0031982 跨身份访问 .75 上该路径 permission-denied → B-grade synthesized
- domain: schematic_netlist（6T SRAM bitcell 网表 + HSPICE MC 仿真 deck 生成）

## 用户意图（2 个 user turn）

- U0 (msg#0): "对比一下这两个路径下的网表，其中一个调用的mis_mod是用来做什么的？" — 分析（对比两网表，解释 mis_mod）→ agent 结论：mis_mod 不是独立子电路，是 PDK 模型里的失配注入，通过 `sda_rnd_mis_*_local` 参数体现；网表1 含 72 个 `BitCell_FS_CH336_{XPD1,XPD2,XPG1,XPG2,XPU1,XPU2}_sda_rnd_mis_0..8_local` 失配参数，网表2 干净无失配。
- **U1 (msg#34): "如果要用第一个netlist做MC hspice仿真，模拟HNM、SNM、WSNM、Iread、Iwirite、Ileak，应该怎么写.sp"** — **produce-task**：用第一个（含失配的）网表写 MC HSPICE .sp，测 6 个指标。trace 在此截断（无 assistant 回答被捕获），但任务意图清晰。

## 网表结构（msg#33 agent 总结）

- 顶层 `BitCell_FS_Simulation_CH336`，6T bitcell 子电路 `BitCell_FS_CH336`：
  - XPU1/XPU2 = `hc_pu_fs`（上拉，接 VDD）
  - XPG1/XPG2 = `hc_pg_fs`（传输门，接 WL）
  - XPD1/XPD2 = `hc_pd_fs`（下拉，接 VSS）
  - 尺寸 w=25e-9 l=6e-9 nfin=1 wgaa=0.025e-6
- 9 个 DC 测试场景子电路：ILEAK（漏电）、S_RSNM/SB_RSNM（读稳定度）、S_HSNM/SB_HSNM（保持）、S_WNM/SB_WNM（写）、IREAD、IWRITE
- 网表1 含 72 个 `sda_rnd_mis_*_local` 失配参数（6 器件 × 12？实际 6 器件 × 9 = 54... agent 说 72，按 XPD1/XPD2/XPG1/XPG2/XPU1/XPU2 × 0..8 = 54，可能含 extra）。实测 grep "rnd_mis" 命中 105 行。

## 6 个测量指标（用户要求）

- HNM = Hold Noise Margin（保持噪声裕度）
- SNM = Static/Read Noise Margin（静态/读噪声裕度）
- WSNM = Write Static Noise Margin（写静态噪声裕度）
- Iread = 读电流
- Iwrite = 写电流
- Ileak = 漏电流

## 合成计划（B-grade synthesized）

- 选 U1 为主任务；trace 无交付物 → 完全合成 gold standard
- 候选写通用 `gen_bitcell_mc_sp.py` (--netlist <spf> --config <json> --out <sp>)：读 bitcell .spf 网表 + 配置 JSON，生成 HSPICE MC .sp deck
  - 配置含：design 名、vdd、temp、mc_samples、mismatch_param_prefix/count、metrics 列表（每 metric：name/scenario 子电路名/meas 表达式/sweep）
  - 生成 .sp：.include 网表 + .param vdd/temp + 逐 metric 例化 scenario 子电路 + .dc sweep + .meas + .monte carlo(采 mismatch 参数, samples=N) + .option post + .end
- A: BitCell_FS_CH336, vdd=0.9, temp=27, mc=200, mismatch_prefix=sda_rnd_mis count=9, 6 metrics [HNM,SNM,WSNM,Iread,Iwrite,Ileak]
- 隐藏 B: BitCell_FS_CH512, vdd=1.0, temp=85, mc=300, mismatch_prefix=mc_rnd_mis count=12, 7 metrics [SNM,RNM,WSNM,Iread,Iwrite,Ileak,HNM]（加 RNM、顺序不同、计数 7 vs 6，每维度反硬编码）
- check() 跑 B (subprocess)，断言 .sp 结构 + 6/7 metrics + .meas/.dc/.monte + vdd/temp/mc_samples + mismatch prefix + scenario 子电路 + 反硬编码跨输入 A + 3-seed 确定性
- L1（离线 .sp 文本结构生成，不跑 hspice；与 prior D L1 案一致）
