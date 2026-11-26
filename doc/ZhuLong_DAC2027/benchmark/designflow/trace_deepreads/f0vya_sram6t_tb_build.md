# trace deepread — f0vya (e0030760 @ hfeg0pkn001) — SRAM 6T testbench build

## trace
- session: 1793174925139_f0vya.messages.json (1.765MB, 335 msgs, dir-based)
- user: e0030760, host: hfeg0pkn001 (10.129.2.10)
- discovered: 11-05 重扫令 pkn001/002/005 content-spice scan (spice_score=1107, unprospect)
- cron log 11-08: hfeg0pkn001, tool markers hspice/spectre heavy

## 任务说明轮 (A-faithful 选轮)
- U#0 (逐字): 「我需要根据现有的model建立简单的一个SRAM 6T单元的testbench，并仿真PMOS不同VDD对Iread和Iwrite的影响，应该怎么做？」
- 选轮判定: 提出需求（建 testbench + 仿真 VDD 影响），无根因/无修复方案 → A-档 ✓
- U#43「用中文跟我交流」/ U#146（第二阶段换 foundry model）不入 prompt

## 真实执行流（assistant）
1. read_files 读 /home/e0030760/Desktop/hspice_test/{test.sp,run_hspice.py,test.ic0,test.lis} + butterfly/{vtc_a.sp,vtc_b.sp}
2. 确认环境：HSPICE V-2023.12-SP1-1，level-1 MOS 模型（nmos vto=0.35 kp=250e-6 lambda=0.05 / pmos vto=-0.35 kp=90e-6 lambda=0.05），VDD=1.0
3. editor 建 sram_read.sp（读 '0'：Q=0/QB=VDD，BL/BLB 预充 VDD，WL 脉冲，测 I(VBL)）+ sram_write.sp（写 '0'：Q=VDD/QB=0，BL=0/BLB=VDD，WL 脉冲）
4. run_approved_command 跑 HSPICE → 失败：`.measure tran iread max abs(i(vbl))` 中 abs() 不被接受
5. editor 改 `.measure tran iread max i(vbl)`（去 abs()）→ 跑通，但 iread≈0、.STEP 被忽略（`unknown command ".step" is ignored`）
6. 诊断三因：① .STEP 不支持 → 改 Python 外部循环 ② 读电流负向（放电）MAX 取不到 → 取幅值 ③ 写失败（butterfly sizing PMOS W=1u > NMOS 0.5u，access 拉不动 PMOS）
7. 调 sizing：PMOS pull-up 0.5u（弱）/ NMOS pull-down 1.5u（强）/ access NMOS 0.9u（中），L=0.13u
8. **关键发现（A#101）**：access 晶体管 HSPICE pin-order bug。语法 `M name D G S B`。原写 `Ma1 bl q wl 0`（drain=bl, **GATE=q**, source=wl）→ 读 '0' 时 Q=0 → Vgs=0−1=−1 → access OFF → 电流~1pA。修正为 `Ma1 bl wl q 0`（drain=bl, **GATE=wl**, source=q）
9. 修正后跑通 5-point VDD sweep [0.8,0.9,1.0,1.1,1.2]：
   - Iread 101→365µA，Iwrite 19→100µA（均随 VDD 上升）
   - Q_peak read 0.086→0.164V（read-stable），Q_end write 0V（写成功）
10. 产出：sram_read.sp / sram_write.sp / run_sram_iv.py / sram_iv_vs_vdd.csv / .png，存 /home/e0030760/Desktop/hspice_test/sram_iv/

## 金标准（用于 case）
- 6T 拓扑 + level-1 模型 + 正确 access pin order（gate=WL）+ .measure tran iread/iwrite max/min（无 abs）+ .param vdd + .tran + .IC + VDD sweep（Python 外部循环，5 点）
- 关键 trap：access 晶体管 gate 必须接 WL（不是存储节点 Q）—— naive 解会写错 pin order

## 合成
- 通用化 gen_sram_tb.py <config.json> -o <outdir>：读 config（model/sizing/vdd_sweep/init/pulse/tran）→ 生成 sram_read.sp + sram_write.sp
- A=A_config.json（trace 同源 level-1, sizing 0.5u/1.5u/0.9u L=0.13u, VDD 0.8..1.2）+ A_model_ref.sp
- hidden B=B_config.json（vto=0.4/-0.4, sizing 0.4u/1.2u/0.8u L=0.18u, VDD 0.6..1.0）
- 判分 15 断言：含 access pin order 守卫（e/f）+ 交叉输入守卫（m, A 上也 gate=wl）+ A-only 泄漏闸门（n）+ 3 次幂等 sha256（o）

## case
- id: EDA-Eval-DesignFlow-Sram6tTbBuild-001
- domain: characterization, track: faithful, layer: L1（离线 Python 生成 .sp + 静态结构校验，判分器不跑 HSPICE）
- k_rationale = k_check = 15 ≥ 8 ✓
