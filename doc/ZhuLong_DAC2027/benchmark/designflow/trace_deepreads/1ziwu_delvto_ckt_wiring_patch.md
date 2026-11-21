# 1ziwu delvto-ckt-wiring-patch 深读笔记

## trace_source
- user: hairuizh  host: hfeahpc502 (10.129.33.25)  session: 1795224598668_1ziwu.messages.json
- mc=119  scan: ssh_eda_search_20261121_151844/summary.tsv  domain: spice_sim
- keywords: hspice:535;netlist:367;pdk:279;transistor:169;cmos:46;schematic:40;synopsys:9;lvs:8
- 917388 B / 140 msgs / 8 user_input

## 用户真实意图（8 条 user_input 流）
- **U[0]** how-to Q&A：分析两个 model 文件 `/proj/m2701/V0_DDR2/model/current/model.sp`（实指 HL22 22HK cl022ul v0p12 库）与 `/apps/imctf/models/V2B/.../V2B_HK_Model_D5_v0d1_Rev02_t01.sp` 里 `delvtrand_ntn` 参数（用来模拟晶体管 vtshift）的对应项。
- **U[27]** debug-Q&A：用户改了 GL22 的 `delvto`，仿真结果完全没变。要求按 `DEGNT_vtshft_base.sp` 逐级追查改动是否在仿真中被应用。
- **U[52]** 澄清：用户只改了 `/proj/degnt/V0_CMOS/.../vcc2vdleq_row/.../netlist`，给器件实例加了 `delvto=vtshft_*` / `delvto_user=0`。
- **U[56]** 主交付决策：「方案A吧，但是要把所有调用的文件都 copy 到当前文件夹的 local_files/ 内，然后修改文件调用路径，只修改 local_files 内的文件」。
- **U[63]** 「你可以用 cp 命令啊，笨」（agent 误判无写权限）。
- **U[88]** 指出漏文件：`topusage_hlmc_cl022ul_io25_spice_v0p12_0d10_for_vodka_shrink0d855.lib`（model.sp 用原文件名做段自引用）。
- **U[114]** 「我服了，是缺了 infile，实在不行你就把人家 model 文件夹整个 copy 过来呢」。
- **U[127]** 报错：`DEGNT_vtshft.lis` 里 `syntax error at or before "=" "0" "+delvto_user" "=" "0"`（agent 把 `+delvto=0 +delvto_user=0` 拼在 `.subckt (...)` 同一行，HSPICE 要求每个 `+param=val` 独占续行）。

## 根因链（agent 定位）
1. **delvto 不生效根因**：ckt 包装子电路 `nuhvt_ckt`/`puhvt_ckt`/`prvt_ckt` 头部无 `delvto`/`delvto_user` 默认参数；内部晶体管调用 `main d g s b <model> ... delvto = _delvto` 只用 subckt 自身默认 `_delvto`，丢弃 netlist 实例传入的 `delvto=vtshft_*`。
2. **方案 A 接线修复**：subckt 头加 `+delvto=0` + `+delvto_user=0`（默认值）；内部晶体管调用 `delvto = _delvto` → `delvto = '_delvto+delvto+delvto_user'`（让 netlist 传入值累加生效）。
3. **多实例**：`nuhvt_ckt` 有 2 个晶体管实例（L128781/L144482），需全部补接线（agent 首轮只改 1 个，后补）。
4. **漏文件**：model.sp（=topusage 库副本）用原文件名做段自引用 `.lib 'topusage_..._v0p12..._shrink0d855.lib' <段>`，重命名后 HSPICE 按原文件名 open 失败 → 解：整盘拷 model 源目录（187 文件 117MB）。
5. **HSPICE 语法**：`.subckt name (d g s b) +delvto=0 +delvto_user=0` 同行双 `+` 报 syntax error；每个 `+param=val` 必须独占续行。

## reframe（harness-for-teeth）
one-off debug+部署 → 参数化 **delvto_ckt_patch.py**：给 model lib + config（目标 ckt 子电路名表 + 累加表达式 + 默认值），自动：
- 给每个目标 subckt 头补 `+delvto=<d>` + `+delvto_user=<d>` 两条独立续行（语法正确）
- 内部 `delvto = _delvto` → `delvto = '<expr>'`（累加 netlist 传入值）
- 多实例全覆盖、幂等、报 JSON report
打包 submit.zip。layer L2（真 HSPICE model 文本处理，无 EDA 二进制）。

## asset 设计
- **A-faithful**：model_A.lib 重建 trace 结构 = nuhvt_ckt(2 实例)/puhvt_ckt(1)/prvt_ckt(1)，头无 delvto 默认，内部 `delvto = _delvto`；netlist_A.sp 器件实例传 `delvto=vtshft_*`；config_A.json 目标 ckt 名表 + expr `_delvto+delvto+delvto_user` + 默认 0/0。
- **hidden B**：nch_hvt_ckt(3 实例)/pch_hvt_ckt(1)/pch_svt_ckt(2)，名/数量/晶体管 model 名全异，anti-hardcode-A；netlist_B.sp 传 `delvto=vth_*`；config_B.json。
- 两 trace bug 转 check 齿：① 同行 `+p=v +p=v` 语法错（齿：header 续行独立）② 多实例漏补（齿：RAW=0 全实例改写）。

## check 齿（k≥8）
a zip/compile/run-on-B · b header `+delvto=` 续行独立 · c 无同行双 `+p=v` · d 内部 `delvto=` 含累加 expr · e 无残留 raw `delvto = _delvto` · f 幂等(二跑 identical) · g report JSON 结构 · h anti-hardcode-A(B 输出无 nuhvt_ckt/puhvt_ckt/prvt_ckt) · i netlist 不被改 · j 3-seed 确定性 · k 多实例全覆盖(B 的 nch_hvt_ckt 3 个全改) · l 累加 expr 值匹配 config
