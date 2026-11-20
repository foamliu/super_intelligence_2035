# trace_deepread · nunyc · reneeg@hfeg0plg53 · 2026-11-10

## ① trace 定位
- sid: `1793273304598_nunyc.messages.json` (live dir: `1793273304598_nunyc/`)
- user: reneeg · host: hfeg0plg53 (10.129.35.69) · mc=117
- keyword: pex:88;netlist:66;waveview:58;analog:48;hspice:30;schematic:13;calibre:8;synopsys:7
- mtime: 2026-10-30 15:33 (msg file) / session 10-29 19:28
- 129 msgs (69 user / 60 assistant), 818KB
- 域判定: **spice_sim**（Finesim `.probe` 激励生成 / WaveView session 信号提取）。pex/netlist 主导但本任务 U#0 是仿真激励改写，归 B。

## ② 选轮（A-faithful 候选）
| msg | 用户原话（摘） | 判定 |
|---|---|---|
| **U#0** | 「我要改个激励，内容是不存所有电压了，只存这个文件里的，帮我写一下probe的激励」+attached `4DP_2.sx` | **CLEAN produce-task** ✓（提需求，未给根因/修复）|
| U#28 | 报 HSPICE syntax error `xi_zqtopm5_0.v(bicnt<6:0>)`，要求直接改文件 | 给症状(error)→fix 任务（hint 候选）|
| U#34 | 「zq校准电路 code 偏了两个，会是什么原因，怎么debug」| consultation/debug，非 produce-task |
| U#36/38/114 | 后仿波形/网表 debug 跟进 | consultation |
| U#127 | 「仿真还在跑吗，怎么不更新」| consultation |

→ 选 **U#0** 作任务说明原话（A-faithful 合规：提需求未给根因）。本轮按 B-synthesized 造可控资产（真实 4DP_2.sx 23.9KB / input.sp 在 reneeg home 可读，但为反硬编码与判分稳定选 B 档合成）。

## ③ 金标准（assistant 实际产物）
- U#0 → assistant 读取 `4DP_2.sx`（WaveView session，`cvt_a2d` 行 `name=v(sig)` 列出实际查看的信号）+ 现有 `input.sp`（含 `.probe V(*)` 存所有电压，FSDB 巨大）。
- msg#27：首版输出 `.probe` 块，把总线写成 `V(adjzqpd_master<5:0>)` 向量形式、层次信号写成 `xi_zqtopm5_0.v(complo)`（嵌套 v()）。
- U#28 报 Finesim syntax error → msg#29/33 **两处关键修正**：
  1. **总线 `<5:0>` 向量语法在 Finesim probe 不支持** → 逐 bit 展开：`V(adjzqpd_master<5>) V(adjzqpd_master<4>) ... V(adjzqpd_master<0>)`
  2. **层次信号 probe 语法**：所有信号必须 `V(...)` 包裹，层次路径用 `.` 分隔，不要嵌套 `v()`：`V(xi_zqtopm5_0.complo)` / `V(xi_zqtopm5_0.xi_zqcomp_18.refnodelpn)`
- 最终金标准 = msg#29 editor new_text（已写入 input1.sp，msg#31 read 验证）。

## ④ 算法（金标准提炼，供 reference 复刻）
1. 解析 `.sx`：从 `cvt_a2d` 行提取 `name=v(SIG)`（SIG = `signame` 或 `path.signame`，可含 `<bit>` 或 `<hi:lo>`）。
2. 归一化：`v(sig)` → `sig`；`path.v(sig)` → `path.sig`（层次用 `.`）。
3. 拒绝非信号 token（`waveview`、bus-group 描述 `MdZqStop<0:3>`、`0|...` 前缀的 raw 引用）。
4. **向量展开**：`name<hi:lo>` → 逐 bit `name<hi>` ... `name<lo>`（Finesim probe 不支持 `<N:M>`）。
5. 输出 Finesim `.probe` 块：首行 `.probe V(s1) V(s2) ...`，续行 `+ V(...)`；每个信号 `V(...)` 包裹；去重保序。
6. 替换原 `.probe V(*)`。

## ⑤ case 设计（B-synthesized / L1 / spice_sim）
- case id: **EDA-Eval-DesignFlow-ProbeStimFromSx-001**
- deliverable: `gen_probe_stim.py` — 读 `<sx_file>` `<out_file>`，解析 .sx 信号 → 写 Finesim 选择性 `.probe` 激励文件。
- 资产 A: `sample.sx`（合成 ~20 信号，含 per-bit + 向量 `<3:0>` 待展开 + 层次）+ `input_template.sp`（含 `.probe V(*)`）
- 隐藏 B1: `hidden_b1.sx`（不同信号集，更多层次 + `<5:0>` 向量）
- 隐藏 B2: `hidden_b2.sx`（不同信号集，反硬编码）
- reference: `gen_probe_stim_ref.py`
- check.py: k=14 断言 a-n（subprocess 真跑候选在 B1/B2，check 内独立重算期望信号集）

## ⑥ 自验结果
（待填，见 jsonl test 字段）
