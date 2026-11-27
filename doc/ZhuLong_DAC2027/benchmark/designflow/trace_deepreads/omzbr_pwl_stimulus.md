# Deepread: 1795402738072_omzbr — HSPICE PWL 电流激励生成

- trace_source: user=yinyus, host=hfeg0pkn004, session=1795402738072_omzbr, match_count=322
- domain: spice_sim (B)
- keywords: drc:560;waveview:418;hspice:318;pyaether:94;synopsys:90;analog:59;netlist:46;virtuoso:26
- ledger: claimed r1335 (status=claimed, synthesis pending — DEBT next round)

## 用户真实意图（原话）
> `/proj/drcpa/V0/simdir/hspice/yinyus/vblh_SF/sim/tran/current_ability/ivblh_idd5b2.sp 读取这个文件 然后写成电流激励 形式仿照 ivblh vblh! 0 pwl(0 0  120u 0  120.001u 2mA) 规则如下 将上面的数据写成的电流激励加在120us之后 文件保存为 .../ivblh_iloadIDD.sp`

## 任务本质（B spice_sim，自包含可行）
用户从一次 transient 仿真（Custom WaveView 导出）得到一条 substrate 电流波形
`isub(inh_vblh)`（time vs current，单位秒/安培），需要把它改写成一个 HSPICE
PWL 分段线性电流源激励，规则：
- 源语句形态：`Ivblh vblh! 0 pwl(...)`
- 前段锚定 `0 0, 120u 0`（120us 前电流为 0）
- 120us 之后接上波形的全部 (time, current) 数据点，每个时间点 +120us 偏移
- 输出到 `ivblh_iloadIDD.sp`

## 输入文件格式（WaveView `#format table`）
```
#format table ## [Custom WaveView] saved 19:04:29 Thu Nov 19 2026
XVAL xi_array6g_t_0.xi_array3g_top_l.xi_array768meg_top_l_0.xi_m768meg.xi_m384meg_14b.isub(inh_vblh)
 0.000E+00  5.020E-08
 1.000E-11  5.427E-08
 ...
 2.952E-08 -4.687E-06
```
- 第1行注释 `#format table ## [Custom WaveView] saved <ts>`
- 第2行表头 `XVAL <current_signal_full_path>`
- 第3行起两列：`<time_sec> <current_A>`，可能含负值
- 数据点数百行（提取样本 119 行，blob 长度 >6000 字符；完整文件在
  hfeg0pkn004:/rundata/drcpa/V0/simdir/hspice/yinyus/vblh_SF/sim/tran/current_ability/ivblh_idd5b2.sp
  —— 注意真实路径是 `/rundata/...` 非 `/proj/...`，/proj 路径在 .75 上 Permission denied）

## 资产可移植性 ✅
输入数据已从 trace 的 read_files tool_result 完整提取（数据在会话消息里，不依赖
/proj 文件可达）。可把真实波形原样作为 asset A，hidden B 用同格式不同
time/current 尺度的合成波形（§4.1 B 与 A 规模/取值不同）。

## 合成计划（next round）
- task_id: `EDA-Eval-DesignFlow-PwlIloadGen-001`
- attachments: `assets/PwlIloadGen-001/ivblh_idd5b2.sp`（真实波形，从 trace 提取）
- hidden: `assets/PwlIloadGen-001/hidden/ivblh_idd5b2.sp`（同格式、不同 time/current）
- prompt: 自然语言，写 yinyus 真实场景（真实用户名/路径/工具/参考语句格式）
- reference: python 解析 WaveView table → 输出 `Ivblh vblh! 0 pwl(0 0 120u 0 <t+120u> <I> ...)`
- check.py 断言（≥8）：① 输出是单个 PWL 电流源 ② 源名 Ivblh ③ 节点 vblh! 0
  ④ 前导锚点 0 0 ⑤ 120u 0 ⑥ 所有数据点时间 = 原时间+120u（数值匹配）
  ⑦ 所有数据点电流值与输入一致 ⑧ 点数 = 输入点数 ⑨ 时间单调非递减 ⑩ 无负时间
- negatives: 空壳 / 只 print 期望 / 删 +120us 偏移（core-deleted）
- 真跑：可选 hspice 解析校验（deck 是 source 片段，非完整 sim；优先结构化解析断言）

## 选料背景（r1335 候选池复核）
- r1334 仅 peek mc≥592 high/mid，结论「fresh pool wrong-domain」
- r1335 复核：top30 by mc 全 touched；ranks 31-120 仅 6 fresh（fqrc2/txjim/omzbr/
  usgf7/gpy0p/1mmir），peek 后 2 条 B-viable（omzbr 干净自包含 / fqrc2 asset-heavy
  CFET pcell+GDS+DRC 混合），4 条 wrong-domain/meta（usgf7 grill-me / 1mmir
  brainstorm / gpy0p DRC 对比 / txjim wrapper 改名）
- ranks 121-260 + 261-420 的所有 hspice-dominant 候选（~40 条）全部 touched
  ⇒ 4-shard 台账已穷尽 mc≥137 的 hspice-dominant session
- omzbr 是 mc 200-450 区间唯一干净自包含 B spice_sim 候选 ⇒ 本轮 claim，下轮合成
