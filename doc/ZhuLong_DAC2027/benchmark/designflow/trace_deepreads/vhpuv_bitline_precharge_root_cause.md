# Deepread — vhpuv (houweip @ hfeg0plg97) — DRAM bitline precharge root-cause debug Q&A

**Session**: `1792751124319_vhpuv.messages.json` · 71 msgs · 1.4MB · mc=148 (waveform/schematic/netlist 混合)
**Model**: GLM-5.2 · **Domain**: waveform
**Case**: `EDA-Eval-DesignFlow-BitlinePrechargeRootCauseQA-001` (r823, 11-15 revival 第二十弹)
**Ledger prior state**: parked @ peek266 "unfit" (old rules pre-11-15) → revived per 11-15 reaudit mandate (Q&A/debug-Q&A/waveform 现在合法)

## 用户原始问题 (U#0 verbatim)
> Help me debug, find the reason why mat0_bla_tar<0> is forced to 475 mV at 25 ns

## trace 真实形态
DRAM sense-amplifier bitline 预充电电压根因调试多轮 Q&A。用户给：
- `Iso0.sp` 激励网表片段（.param pvad2=475mv / vvad2 vad2! 0 dc=pvad2 / 控制信号 PWL / .tran/.meas）
- `SA_unit` 子电路网表（.SUBCKT 端口 Bla Blb Csl Io IoN Iso NCS OcEn PCS PreEq inh_vad2 inh_vblhbk inh_vss）
- `XI37` 顶层例化片段（inh_vad2 端口接 vad2! 全局预充电电源）
- `pattern_power.sp` 参数

SA_unit 内 MOS 拓扑：
- **预充电 NMOS 对** XMMN6/XMMN72：栅=PreEq，漏=inh_vad2（共享漏=预充电电源端口），源=SaBlb<0>/SaBla<0>（内部节点）→ 预充电窗口把 SaBla/SaBlb 充到 inh_vad2 电压
- **offset-cancellation 交叉耦合开关** XMMN3/XMMN2：栅=OcEn，把内节点电平传到位线端口 Bla/Blb
- **隔离开关** XMMN5/XMMN4：栅=Iso
- NMOS/PMOS 锁存对

## 金标准 (assistant msg #70)
根因 = 预充电电源 `vad2!`（`.param pvad2=475mV` 设定）经 SA_unit `inh_vad2` 端口注入 → 预充电 NMOS 对（栅 PreEq）在预充电窗口把 SaBla/SaBlb 内部节点充到 475mV → offset-cancellation 交叉耦合开关（栅 OcEn）把该电平传到位线 → 使能撤销后位线浮空在预充电电压 → 故 25ns 观测 mat0_bla_tar<0>=475mV。

## A 档资产（从 trace 重建）
- `stimulus.sp`：Iso0.sp 激励片段
- `sa_netlist.sp`：SA_unit .SUBCKT + XI37 顶层例化 + 控制信号
- `question.json`：target=mat0_bla_tar<0>, obs=475mV @ 25ns
保留全部真实 trace 结构标识符。

## 隐藏 B 档（identifier-renamed + value-shifted）
- vad2→vdp2, pvad2→pvdp2, SA_unit→SnsAmpU, XMMN→XMn, XI37→XI38
- mat0_bla_tar→m0_bla_tgt, PreEq→preqG, OcEn→ocenG, Iso0→isoG
- SaBla→sAa, SaBlb→sAb, inh_vad2→i_vdp2, inh_vblhbk→i_vbh, Bla→blA, Blb→blB
- value-shifted: 475mV→525mV, 25ns→30ns, 98C→95C
- 17 A_ONLY_TOKENS 词边界校验零泄漏

## candidate_ref.py（通用 SPICE 根因分析器，无硬编码标识符）
CLI: `python3 candidate.py <asset_dir>`
pipeline:
1. `.param` mV 值匹配观测电压 → `source_param`
2. vsource `dc=` 引用 source_param → `source_net`
3. `.SUBCKT` MOS 解析找 SA 子电路（NMOS 栅为控制端口；预充电对=共享漏/源且为非位线电源端口；交叉耦合对/隔离对分类）
4. 顶层例化 `port_to_net_map` 确认电源端口接 source_net → `confirms_source_connected`
5. `root_cause` 文本接地电压 + param + net
输出 21 顶层键 JSON。

## check.py 13 断言 (a-m)
①zip 含 candidate.py+analysis.json ②py_compile ③A JSON 合法+11 必需键 ④B subprocess 跑通产合法 JSON ⑤B source_param 值匹配观测 525±3mV ⑥B source_net+sa_subckt 非空 ⑦B 预充电≥2 且电源端口接 source_net ⑧B 交叉耦合≥2 ⑨B 隔离≥2 ⑩B top_instance+target_port 位线+confirms=True ⑪B root_cause 接地电压+param/net ⑫反硬编码 B 输出零 17 A 专属 token ⑬3-run md5 确定性

## 自验
- ref 13/13 PASS
- 3 退化 FAIL distinct labels NEG_RC=0：
  - empty stub → c,d 失败
  - print-only A-hardcoded → e,g,h,i,k,l 失败（反硬编码 l 捕获 A token 泄漏）
  - core-logic-deleted → f,g,h,i,j 失败（SA 检测删后 sa_subckt/source_net=None）
- A≠B 证明非 canned（475 vs 525）
- 3-run md5 一致

## 工程教训
- **shared-drain vs shared-src**：初版 candidate 只识别预充电对 shared-src（漏接内节点、源接电源端口），但真实 SA_unit 是 shared-drain（漏接 inh_vad2 电源端口、源接内节点）—— 须两者都识别。
- **`.param` 空格容错**：`.param pvad2 = 475mv` 空格围绕 `=` 会使 `split('=')` 失败 → 须先 `re.sub(r'\s*=\s*','=',body)` 归一化。
- **A-only token 词边界**：`vad2` 是 `vad2!` / `inh_vad2` / `pvad2` / `vvad2` 的子串 → 反硬编码正则须用 `(?<![A-Za-z0-9_])` + `(?![A-Za-z0-9_])` 词边界，否则误判泄漏。
- **root_cause 接地校验**：k 断言要求 root_cause 文本含观测电压数字 + source_param/net 名，硬编码 A 输出会因含 475 而非 525 失败（双保险）。

## 落库
- D.jsonl 458→459 (line 459)
- ledger mark vhpuv → case
- coverage 451→452/24085 mc≥10
