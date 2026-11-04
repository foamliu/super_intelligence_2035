# trace_deepread: 1793607437978_fzngm (yazhuok@hfeg0pkn002, mc=972, schematic_netlist)

## 选料
- 来源：Nov daily eda_trace logs (eda_trace_2026110{1..5}.log) → fresh_D_nov_256.tsv rank ~36 (mc=972)
- cands_257.tsv batch-1 peek (peek_257b.py) resolved via 10.129.2.11
- session 路径：`/home/yazhuok/.cline/data/sessions/1793607437978_fzngm/1793607437978_fzngm.messages.json` (2.0MB, NMSGS=194, cline v3 目录结构)

## 用户意图轮（A-faithful 任务说明候选）
- **U#0（提需求，选作 prompt）**：「你是一位aether仿真专家，请根据我附件中的两个网表，查找SWD_out<7> net电气连接通路上电容和电阻分布的区别」+ 附件 all_netlist / simple_netlist
- U#33「Tier_M取值53，请再比较一下」(补参数)
- U#39「连接到晶体管栅级的最远段RC分布是否也是一样」(追问分析)
- U#49「如果只有SWD_out<7>这根net开启，其他都是vwln，分布一致吗」(追问)
- U#51「为什么仿真tWL时简化网表 SWD_out<7> 的 10-90% 上升时间与 50-50% 延迟都更长」(根因追问)
- U#57/U#63/U#64 补 Tier_T/Tier_B 取值 + 电路地址
- U#86「pyaether沙箱环境如何启动」(环境)
- U#140/U#169 补 fsdb 波形文件路径
- U#173 换 Tier_T/M/B=61/33/5 重做 bottom 层

按 A 档规则只取「提需求/表达目标」轮 ⇒ **U#0**（U#33+ 是补参数/追问根因/给电路地址，不另作任务说明）。

## agent 工具链
shell 被禁（`run_commands is disabled; use run_approved_command`）→ 全程用 `editor` 写 python 分析脚本 + `run_approved_command` (python-runner profile) 跑。写了 12+ 脚本：
explore.py(统计元件类型) → struct.py(.SUBCKT 结构) → extract7.py/extract7b.py(bit-7 路径 dump) → cmp7.py(bit-7 r/c 元件按含 subckt 分组) → final.py(TopDes 标记/SWD_out<7> 定位) → params.py(.param/Tier 定义) → gate_seg.py(各 bit-7 gate 节点的 r/c) → layer1.py(per-bit cap count) → mid7.py(VWL_L<7> storage 耦合) → cmp_mid.py(按 tier 集合 diff) → verify_path.py(LWL_mid_0 位置/subckt 归属) → rp_quant.py(R_CWL_pSC 段数/系数)。

## 关键物理（金标准依据）
- SPICE 元件行 `r*`/`R*` = 电阻，`c*`/`C*` = 电容；bit-7 路径 = 行含 `<7>` 的 r/c 元件
- tier 分组：元件名含 `top`/`mid`/`bot` → 对应 tier，否则 `other`（rSWD/cSWD/rCWL_pSC/rVWL2CWL 等）
- all_netlist 含 top+mid+bot 三层 + CWL 耦合(rCWL_pSC/cCWL_pSC)；simple_netlist 只含 mid + top-level rSWD/cSWD
- diff = all 名集合 − simple 名集合 → only_in_all（top/bot 层 + CWL 耦合元件）；only_in_simple 通常为空
- VWL 串联 R 系数 = Tot_tier − Tier_X（用户给定 Tier_T/M/B）

## 交付形态判断
trace gold = **prose 诊断**（agent 解释简化网表缺 top/bot tier + CWL 耦合 → tWL 上升时间更长）。prose 不满足 §4.2 (subprocess 在 B 上跑候选脚本断言输出结构)。
⇒ 采用 **B 档 L1-boundary**：把「比较两网表某 net 通路 R/C 分布」固化为可运行交付件 `netlist_rc_diff.py`（Python CLI，输出 JSON 报告），金标 = 通用解析器（对任意网表+bit 通用，无硬编码）。A 档 prompt = U#0 逐字；task_brief 只写交付接口（≤3 行）。

## 合成
**EDA-Eval-DesignFlow-NetRcPathDiff-001**（schematic_netlist, L1-boundary, track=faithful）
- A 资产：all_netlist（bit 7, top+mid+bot+CWL 耦合, R=7/C=7）/ simple_netlist（bit 7, mid+top-level, R=3/C=3）
- hidden B：all_B.sp（bit 3, WLDRV_TOP/MID, top R=3/mid R=3/other R=3, +rVWL2CWL<3> 耦合, R=9/C=6）/ simple_B.sp（bit 3, mid+top-level, R=3/C=3）
- check.py：16 条件 a-p（zip/py_compile/JSON/keys/总R/C/per-tier/diff lists/delta/cross-guard/确定性）
- 6 negative（empty/print_fixed_A/count_only_R/wrong_diff/no_tier/syntax_err）+ negative_selftest
- 自验：REF PASS 16/16；6 neg ALL-FAIL（c/e/f/l/i/b）；§4.9 三假（empty=c, print_fixed_A=e, wrong_diff=l）distinct=3 ✓；test==disk sha ✓；k_rationale=k_check=16 GATE PASS

## 教训
1. cline v3 session = 目录 `sessions/<id>/<id>.messages.json`；daily log probe 只记 basename，peek 须重建 `sessions/<id>/<id>.messages(.archive).json` 路径
2. home automount：dedup 取 max-mc 的 ip 可能非用户 home 节点；fallback ip 列表 + 6 个候选 ip 试错
3. SRAM 字线 netlist RC-path 比较是 schematic_netlist L1-boundary 可行范式：grep `<bit>` 的 r/c 元件 + 按 tier 名分组 + 双网表集合 diff，对任意网表通用
4. 分析/诊断类 trace（「查找…区别」「分析原因」「总结」）纵使 mc 高，gold=prose 不满足 §4.2；须 B 档固化为可运行交付件
5. cross_guard B_must token 须用脚本输出实际出现的 B 专属元件名（rVWL2CWL<3> 等），勿用 subckt 名/param（WLDRV_TOP/Tot_tier 不在 JSON 输出中，会误判 ref FAIL）
