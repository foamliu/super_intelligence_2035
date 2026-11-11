# sg86n 深读 — DDR5 array12Meg CSL→bank→WL 门控 (ruisongs)

- **session**: 1793343745263_sg86n.messages.json (ruisongs @ hfeg0pfn090 / 10.129.33.216, mc=82)
- **size**: 573KB / 70 msgs / 2 user prompts (单轮+1澄清, Oct 30)
- **kw**: verilog:803;cmos:213;netlist:39;systemverilog:12;analog:10;rtl:5;schematic:3;floorplan:2
- **claim**: r412 (digital)

## 用户意图（原话）
- U#0: "/proj/drvqa/V0/simdir/verilog/ruisongs/verilog.ddr5.drvqa.0922net 以这个环境为例，libs里的array.sv，现在array12meg 需要引入csl判断，该如何改，才能知道是array die对应的cmos die的csl变化了"
- U#1（澄清）: "需要用gate 条件改变 blamm的赋值，打个比方，active active read指令，第一个read csl开了怎么才知道是第一个wl相关，而不是给第二个wl的"

## 真实技术问题（DRVQA 仿真平台）
array12Meg_E_UW_dwl 模块的读逻辑 `always @(cslsec) if(|m0wle) for(i) if(m0wle[i]) bla_mm=e_mmrra[i]` —— **只看 `|m0wle`（有无 WL 开）+ cslsec 变化**，把所有激活 WL 都读出来写进 BLa。两条 ACT 拉起两个 WL 后，任一 READ 的 CSL 一来，两行一起出数 → 分不清是第一个还是第二个 WL。**根因：模型没把"这条 CSL 属于哪个 bank"和"该 bank 当前激活的 WL"关联起来。**

## agent 给出的落地改法（msg[46]/[56]/[69]）
两层现成信息链对上：

1. **CSL→bank**: `get_csl_ba(hier)` 按 CSL 层次 `YsDecX1112` 解出 `bank_id`；`real_cs_gen` 已把 fired CSL 写进 `csmonitors.real_col_q[bank_id]`。**bank_id = bg*4 + ba**。
2. **WL→bank→sec**: `array_table` (`proj_monitor/array_table.v`) 结构 `{sec, part, start_wl_id, stop_wl_id}`，把 WL 地址范围映射到 sec；`array_table_generate_ref(.pwl_add)` 返回 `{sec, die, wl_idx}`。`m0wle[i]` 本身不带 bank，需 `wl2bank(piece, bg, ba, wl_idx)`：先 `wl2sec(wl_idx)` 查 array_table → sec，再结合 `array_piece`(哪片 die U/L) + bg + ba 凑 bank_id。
3. **active_wl_of_bank[bank_id]** 关联数组：ACT 上升沿登记 `active_wl_of_bank[wl2bank(...)]=wl_idx`；PRE 清成 -1。
4. **gate bla_mm**: CSL 触发时 `cs_bank = get_csl_ba(hier)`；`sel_wl = active_wl_of_bank[cs_bank]`；仅当 `sel_wl>=0 && m0wle[sel_wl]==1` 才驱动 bla（把 `for(i) if(m0wle[i])` 换成"由 fired-CSL 的 bank 定位唯一 WL"）。
5. **array_piece 过滤**（本 die）: cs_piece 须匹配 ACT 的 piece 才算"本 die 对应的 cmos die CSL 变了"。
6. **CSL 变化检测块**（msg[46]）: `cslsec_prev` 寄存 + `cslsec_first` 首采样 guard；`changed_bits = cslsec ^ cslsec_prev`；`$display` 带 `%m`(实例名)/`array_piece`/`csl`/`changed_bits`。

agent 还写了 8+ 个 grep_*.py 搜索脚本定位 array.sv / proj_package.sv / array_table.v / proj_monitor 的 CSL 解码助手（real_cs_gen/get_csl_ba/get_csl_seg/cslbit2cp/pcs_idx）。工程目录只读，agent 未直接改 array.sv，给了两套可直接落地的代码（cell 内加 always / bind monitor ary_cslchk）。

## B档 synthesized case 设计（CslWlGateMap-001, digital L1 spec-driven-gen）
trace 是 consultation（"该如何改"），agent 给出改法 + 搜索脚本但未产出最终 array.sv patch。抽其**可离线检验的纯 Python 核心**做 deliverable：

**deliverable = `csl_wl_gate.py`**（纯 stdlib, `--spec <array_table.json> --scenario <events.json> --out <report.json>`）
- `wl2sec(wl_idx, array_table)` → sec（按 start/stop 区间查表）
- `bank_id = bg*4 + ba`（bank 编码）
- `wl2bank(piece, bg, ba, wl_idx, array_table)` → (piece, sec, bank_id)
- `active_wl_of_bank` 维护：ACT 登记 / PRE 清 -1
- `gate_bla(cs_piece, cs_bank, active_wl_of_bank, m0wle)` → (sel_wl, drive) 含 array_piece 过滤 + m0wle[sel_wl] 校验
- `csl_changed_bits(prev, cur)` → XOR + first-sample guard
- 输出 JSON: wl2bank / active_wl_of_bank / gate_decisions / csl_changes / summary

**check ≥12 条**：①zip 合法含 .py ②py_compile ③B 上 exit 0 + 可解析 JSON ④顶层键齐全 ⑤wl2sec 区间命中 ⑥wl2sec 边界(start/stop) ⑦wl2sec 越界→-1 ⑧bank_id=bg*4+ba ⑨ACT 登记 active_wl_of_bank ⑩PRE 清 -1 ⑪gate 命中本 die→drive=true/sel_wl 正确 ⑫gate piece 不匹配→drive=false ⑬gate 无 active WL→drive=false ⑭changed_bits=XOR 正确 ⑮first-sample guard ⑏"active active read" 场景：第一个 read 的 CSL(bank0) 只驱动 bank0 的 WL，不驱动 bank1（trace 核心诉求）

**A/B 差异**: A=4 sec 区间 + 2 ACT + 2 CSL_FIRE + 1 PRE；B=5 sec 区间(不同边界) + 3 ACT(3 bank) + "active active read" + PRE + re-ACT，piece/bg/ba/wl 全不同。

**negatives**: naive_empty / print_only / core_removed(去掉 piece 过滤或 gate 逻辑) / substring_match(用 `in` 代替精确键)。

**archetype**: spec-driven-gen（第 1 类，A 域主导）。与 r411 PatternTaskXref-001 同类但领域不同（DDR5 CSL 几何映射 vs 正则交叉引用）。
