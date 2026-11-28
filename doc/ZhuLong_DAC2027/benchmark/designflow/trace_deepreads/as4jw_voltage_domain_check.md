# deepread: 1795757563423_as4jw (zqzhan@hfeg0pkn005, mc=233)

- trace: hfeg0pkn005:/home/zqzhan/.cline/data/sessions/1795757563423_as4jw/ (live 1.21MB 308msgs, agent=lead)
- domain: schematic_netlist (aether:481+schematic:435+pyaether:412+netlist:267 dominant)
- real user: zqzhan, DRAM `drcpa_digital/R_RasBnkLogic` schematic (330 inst / 353 net / 216 port)

## 用户意图
层次化电压域检查工具：对 schematic 全层次做只读检查，找出**跨电压域直连而没有 level shifter**的违例。
- 规则：vcc→vdly 直连合法；vdly→vcc 必须加 level shifter（`R_lvlshftVdly2Vcc...`），否则违例。
- 用户配置项：lib/cell、allowed 跨域直连白名单（空=任何跨域都报）、顶层输入信号电压域（全局 + 个别 pin 覆盖，个别优先）。
- netlist 版做不了（单元端口无方向信息，启发式不可靠）→ 必须用 pyAether 读 schematic 真实端口方向。

## 核心算法 (voltage_domain_gui.py DomainChecker.analyze)
递归 analyze(lib,cell,env,top,skip_check) -> {ports:{port:{drive:set,load:set}}}:
1. 建 net→domain 映射 nd：power_names[net]（vcc!/vcc...）；若 net 有继承表达式 `[@prop:%:def]` 则沿 env 的 instance assignment 链向上解析（_resolve_pwr）。
2. 实例分类：
   - basic/TECHLIB → skip
   - leaf_libs(stdcells_ac) → 叶门：domain=vcc pin 接的 net 的域；非电源 instTerm 按 direction(output=drive/input=load) 累积到 net_dr/net_ld
   - level-shifter（_is_ls：ls_prefixes 或 cell 名 `<A>2<B>` 正则 anchored on domain vocab）→ 合法桥：claimed=parse name；internal=recurse(skip_check) 取 In 端口 load 域 / Out 端口 drive 域；若 claimed∉internal → ls_mismatch；In net 加 src(load)、Out net 加 dst(drive)
   - else 子电路 → recurse，子端口 drive/load 经 instTerm direction 传播到本层 net
3. top：input terminal → net_dr += (top_specific[name] or top_global)
4. 端口累积：net.terms → port_dr/port_ld（电源 net 跳过）
5. 违例检测：每条非电源 net，drs×lds，need_shift(d,l)=d≠l 且 (d,l)∉allowed → violation(cell,net,drivers,loads,bad_pairs)

## 关键判分点（断言素材）
- parse_ls_domains：`R_lvlshftVdly2VccInv_DRCOA`→(vdly,vcc)，前缀/后缀不被吞（domain vocab 锚定）
- need_shift：src==dst→no；(src,dst)∈allowed→no；else yes。allowed={(vcc,vdly)} ⇒ vcc→vdly 合法、vdly→vcc 违例
- LS claim vs internal mismatch：名声称 vcc→vwlp 但内部实际 in={vdly}/out={vdleq} ⇒ mismatch
- 顶层输入：specific 覆盖 global（RasEnBnk=vwlp 而非全局 vcc）
- 继承连接：vcc! 在子电路有 `[@PWRX:%:vcc!]`，父实例 assignment PWRX=vdly! → 解析为 vdly（不是默认 vcc）
- 叶门域 = 其 vcc pin 接的 net 的域（inv 接 vdly! → 域 vdly）
- LS 合法桥：经 level-shifter 的路径不报违例（In/Out net 同域）

## case 设计（synthesized-reframe，LIVE-NA judge [L0,L1]）
spec-JSON 驱动纯 python 检查器 `vdcheck(spec)->{valid,violations,ls_mismatches,stats,errors}`。
- A(visible): drcpa_digital/R_RasBnkLogic，allowed=[(vcc,vdly)]，top_global=vcc, top_specific={RasEnBnk:vwlp}。
  GT violations: n_drv_vdly(vdly,vcc) / n_bad_out(vwlp,vdleq,LS-mismatch 下游) / n_amp_out(vdly,vcc,继承依赖) / rasenbnk(vwlp,vcc,top_specific)。
  GT ls_mismatches: R_lvlshftVcc2Vwlp claimed(vcc,vwlp) internal_in=[vdly] internal_out=[vdleq]。
  非违例: n_drv_vcc(vcc,vdly)allowed / n_ls_in,n_ls_out(LS合法桥,同域) / n_bad_in(同域) / n_amp_in(allowed) / rasin(同域)。
- hidden B(token-structurally 不同): periph_lib/PwrCtrl，domains vcore/vio/vaux/vgb，allowed=[(vcore,vio)]，top_specific={EnableN:vaux}，不同 LS(LS_mismatch R_lvlshftVcore2Vgb)、不同继承、违例数不同(5 vs 4) ⇒ A 硬编码器在 B 全错。
- 反硬编码：A 硬编码 violation 列表 → B GT 不匹配；B .py 无 A-only token。
