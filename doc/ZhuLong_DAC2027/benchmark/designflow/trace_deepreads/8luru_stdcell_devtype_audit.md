# trace_deepread: 8luru (jiashengz@hfeg0plg92, mc386, schematic_netlist)

- session: 1794899301159_8luru.messages.json (259 msgs, 1.05MB)
- host: hfeg0plg92 (.75), user jiashengz, lib R1b3, tool Aether (pyAether live)
- domain: schematic_netlist (schematic:521, netlist:495, aether/pyaether/cellview dominant; lvs secondary)
- keywords: lvs:838;schematic:521;netlist:495;aether:228;pyaether:196;dbopencv:176;cellview:128

## 用户真实意图（逐字 user turns）
- U#2: 「扫描只要schematic和symbol」
- U#3: 「继续，xor的symbol为看你也画的不对」
- U#5: 「和xord还是不一样啊，xor2是xord组成的，还是画xord，不要画xor，此外继续执行其他stdcll的扫描」
- U#6: 「我是说stdcell里的xor是由xord和inv还有passage gate等标准单元组成的…现在只要xorddemo你画得和xord一样就行…对扫描出的这些进行绘制，并且对比与正确的差别，提炼出错的原因，固定为较为严格的规律，主要是symbol，schematic还是以我以后会话中提供的网表为准，pulsehi/lo、dlyrc这个不需要，dlyg=dlygate需要」
- U#7: 「你的xor不是少圆圈吗，提炼为泛性问题，以后不许发生」
- U#10: 「器件类型基本以LV为准 不要用L的，除非实在找不到，提炼进skill」
- U#12: 「更正一下 是找不到LV LVS IOLV后再降级为其他的器件类型」
- U#13: 「muxi是经过后反相，mux是经过后不反相」

## assistant 工具链
- read TECHLIB_cells.txt / stdcells_ac_cells.txt → pyAether scan symbol+schematic 指纹（Arc 数 / 管数）
- 建 skill `~/.cline/skills/stdcell-from-netlist/` + references/04_gate_family_map.md，升 v1.8.0
- dump 参考 xord2 symbol 逐 shape 几何，对比目标 XOR2_DEMO，找差异（少圆圈=少反相器）
- 归纳：每类门 symbol Arc 数 + schematic 管数当指纹；器件类型 LV 优先降级规则

## 合成 reframe（B 档 produce-task）
真实交付物=live Aether schematic/symbol（不可沙盒）→ reframe 为**离线网表审计**：
给定 stdcell SPICE 网表 + 器件类型偏好规格（LV>LVS>IOLV>L），产脚本审计每个 MOS 的 model 类型，
按「网表中存在的最高偏好类型为 best_available，任何 device 用比 best 更差的类型即非偏好降级」判据，
输出 JSON{cells,best_available,preferred_order,nonpreferred,summary}。
- 忠实 U#10/U#12（器件类型 LV 优先降级）+ U#6（对比差别/提炼规律）+ U#7（少反相器=结构缺）
- A: xord2/nand2d/invd，nand2d 的 Mn1 用 nL（LV 存在→降级）gold{total12,np1,best LV}
- B(hidden): nor2d/muxid/ao21d，muxid Mp2=pIOLV / Mn2=nL gold{total14,np2,best LV}
