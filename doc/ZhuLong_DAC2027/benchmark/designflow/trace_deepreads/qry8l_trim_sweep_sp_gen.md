# trace deepread · qry8l — FineSim trim-sweep .sp 生成器 (joeyl@hfeg0pkn004)

**session**: `1792389569188_qry8l.messages.json` · joeyl@hfeg0pkn004 (10.129.2.13) · 36 msgs · 160KB · mc=34 (20 spice markers / 34 tot = 0.59) · mtime 11-04~11-05。
**source**: .75 cron 扫描缓存 `/tmp/qry8l.json`（22:35 轮 cron-log 聚合 5 un-ledgered strict 之一）。
**tool counts**: editor / read_files / run_approved_command / run_commands（assistant 写 `/home/joeyl/gen_trim_sps.py` + 跑 + 提交）。

## ① user_input

仅 2 条 user_input（msg0, msg26）：

- **U#1 (msg0, 单轮 produce-task)** — verbatim 726 字符：
  > 在这个目录中，/proj/drgqa/V0/simdir/finesim/workdir/joeyl/simulation/sim/SPF-sim/008_FullPath_skew_trim_range
  >
  > 目前只有0_000.sp，我需要你创建到7_111,文件更改对应这里：
  > 000时，V_Div_4p_trim_F0<0/1/2> ... '0*pvddq'
  > 001时，F0<0>='1*pvddq'，F0<1/2>='0*pvddq'
  > 111时，全 '1*pvddq'
  >
  > 最后用文件夹里的脚本提交任务进行仿真

  = 提需求（生成 7 个 sweep deck），未给根因/未给 fix → **A-faithful 合格** ✓。

- **U#2 (msg26)**「重新再来一次，我把mc去掉了」= redo-after-edit（用户改了模板后重跑），disqualify，**不进 case prompt**。

## ② A-faithful 选轮判定

- U#1 是 produce-need（"我需要你创建到7_111"），用户陈述目标而非根因 → eligible。
- U#2 是 redo 指令，不引入新 spec → 取 U#1 单轮作 case 主线。
- 用户仅 mask：无 key/token/密码（路径/用户名保留原始）。

## ③ 金标准 (assistant accepted deliverable)

assistant 写 `/home/joeyl/gen_trim_sps.py`：从 `0_000.sp` 模板，对三条 `V_Div_4p_trim_F0<0/1/2>` 激励源定义行做 **regex 替换**（值域 `'0*pvddq'` → `'<bit_i>*pvddq'`），exactly-once-match 守卫（每条恰好匹配 1 次，否则报错），在目标目录生成 `1_001.sp`...`7_111.sp` 共 7 文件（文件名 N_BBB，BBB=N 的 3 位二进制 MSB 在前；F0<0>=bit0 LSB … F0<2>=bit2 MSB）。其余逐字节保持与模板一致。然后用文件夹里的 `run` wrapper 提交 bsub 仿真。

**bit 映射**：N=1(001)→F0<0>=1; N=3(011)→F0<0,1>=1; N=7(111)→F0<0,1,2>=1。

## ④ 资产重建

`0_000.sp`（FineSim 仿真 deck，DQSIB_path_spf_check）688 行：
- 第 228-230 行 = 三条 trim 激励源 `V_Div_4p_trim_F0<0/1/2> ... 0 '0*pvddq'`（case 改写目标）。
- 第 111 行 = `XI_IO_DqsRcvTop ... Div_4p_trim_F0<2> Div_4p_trim_F0<1> Div_4p_trim_F0<0> ... IO_DqsRcvTop`（实例化行，B3 重复测试用）。
- 获取：trace read_files tool_results 重建（strip 行号前缀）；pkn004 /rundata 直读 perm-denied；本地 42137B vs .75 42949B 仅 tab/whitespace 差异，结构一致。

## ⑤ case EDA-Eval-DesignFlow-TrimSweepSpGen-001 (spice_sim, A-faithful, L1, k=14)

**check.py 14 条独立断言 (a..n)**：
- a: submit.zip 可解压且含≥1 个 .py 生成器
- b: B1(行移位模板)上生成器 subprocess 跑通 exit=0
- c: B1 产出 7 个 N_BBB.sp 文件名集合正确
- d: B1 各文件 trim 值 = `<bit_i>*pvddq` 按 N 映射
- e: B1 各文件除 trim 值域外与模板逐字节一致
- f: B2(trim 源序倒置+decoy)生成器跑通
- g: B2 trim 值正确(顺序无关)
- h: B2 decoy `V_Div_4p_trim_F0<0>_mon` 行保持 `'0*pvddq'` 未被改动
- i: B3(pvddq=1.2+实例化行重复)生成器跑通
- j: B3 XI_ 实例化行集合与模板一致(重复行保留)
- k: B3 trim 值正确
- l: B3 各文件除 trim 值域外与模板逐字节一致
- m: B1 上 3 个随机种子输出完全一致
- n: 任何变体均不输出 0_000.sp

**隐藏 B（结构差异，非文件重命名）**：B1 +40 行 leading comment → trim 行下移 ~40；B2 trim 源序倒置(F0<2>,<1>,<0>) + decoy `V_Div_4p_trim_F0<0>_mon ...'0*pvddq'` 不可改；B3 `.param pvddq=1.2` + `XI_IO_DqsRcvTop` 实例化行重复。三变体保持同信号族(V_Div_4p_trim_F0<0/1/2>, 'N*pvddq', 3-bit) → trace-faithful ref 仍 PASS。

**自验**：ref PASS 14/14 + 4neg(neg_stub/neg_nochange/neg_wrongbit/neg_touchdecoy)全 FAIL + §4.9 三假(空zip/print-expected/core-deleted)全 FAIL + byte-sync(sha faf89ecbfbdc062089279127cbe342432c39f29722f3faad26519df761a26bdf)。

**交付**：jsonl B 214→215；ledger mark qry8l→case(covered 215→216, spice_sim 172→173)。
