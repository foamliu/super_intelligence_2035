# Deepread: okq91 — easont@hfeg0pkn004 — SPICE 网表对比报告

## trace 概况
- session: `1793102773959_okq91` (easont@hfeg0pkn004, mc=654)
- 415 msgs (224 user / 191 assistant), 13 user_input turns
- 工作流: DRAM 温度传感器(TempHalfWL) FineSim 仿真 + FSDB 波形分析 + SPICE 网表优化
- 工具: waveview-fsdb-readerV2-2 skill (FSDB 读取), read_files, editor, run_approved_command (python-runner)
- 仿真路径: /rundata/ddgoa/V0/simdir/finesim/.../ddgoa_cmos_digital_TempHalfWL_schematic_ALPS_sim/cosim/

## 用户轮 A-eligible 判定
- U#0 "can you read .../finesim.fsdb" — 纯目标(minimal) ✓
- U#8 "有fsdb相关的MCP server吗" — 工具询问 ✓
- U#17 "使用上面的skill读取...finesim.fsdb；根据波形说明signal的功能" — 纯目标 ✓★
- U#63 "读取.../netlist_AI,结合上面的fsdb分析，说明模块功能" — 纯目标 ✓★
- U#97 "分析当前netlsit是最简逻辑吗，是否有优化方案，直接输出优化后的网表" — 含 fix 方向(输出优化) 边界
- U#204 "仿真波形有问题，自己分析后迭代netlist" — 用户指出根因(波形有问题)+fix(迭代netlist) 🚫 NOT A-eligible
- U#234 "结构参考这个来，你生成的都是错的" — 指出错+fix 🚫 NOT A-eligible
- U#278 "你理解下这个网表...直接在netlist上修改" — 含 fix(修改) 🚫 NOT A-eligible
- **U#383 "对比修改后的网表和原先的网表，生成markdown形式的报告"** — 纯目标(对比+生成报告) ✓★ **选定**
- U#392 "分析文件夹...；说明整体仿真流程" — 纯目标 ✓ (asset 在 /rundata 不可恢复)
- U#401/U#412 "分析...finesim.fsdb，将分析结果用markdown输出" — 纯目标 ✓ (fsdb 不可恢复)
- U#414 "读取...finesim.fsdb,分析RowControl模块的行为" — 纯目标 ✓ (fsdb 不可恢复)

## 选定 U#383 理由
- 纯目标(A-eligible), 无根因/fix 方向
- 资产可恢复: netlist_pro_final(37 单元, /home/easont) + netlist_pro_clean(15 单元, /home/easont) 均可 ssh cat 恢复
- gold = assistant msg#391 markdown 对比报告(39840->24951 字节, 802->431 行, 37->15 单元, 22 删除, TopDes 一致)
- netlist_AI(用户原引用) 在 /rundata 权限拒绝; netlist_pro_final 是 assistant 本地工作副本, 与 netlist_AI 同构(同 37 单元集), 作为"原先的网表"资产

## gold 报告 (msg#391) 结构
1. 文件大小: 字节/行数 + %变化
2. 单元格定义: 原始 37 / 优化保留 15 / 删除 22
3. 删除的 22 个未使用单元格定义 (aoi21, dlyg*, invhiz, nand*, nor3*, oai21*, or*, switch_*)
4. 保留的 15 个单元格定义 (inv, bufLx4, invLx*, nand2*, nor2*, nand3, xnord2, gfilt, inv_org, invhiz_org)
5. 保留的核心逻辑 (selN26/TempN 缓冲/14 路阈值比较器/输出级/12 路区间检测/毛刺滤波器)
6. 温度阈值验证 (FSDB 实测翻转时间)
7. 结论: 仅删除死代码, TopDes 完全相同, 功能等价

## 资产可恢复性
- netlist_pro_final: /home/easont/netlist_pro_final (40814 字节, 819 行, 37 .SUBCKT) ✓ ssh cat 恢复
- netlist_pro_clean: /home/easont/netlist_pro_clean (24951 字节, 431 行, 15 .SUBCKT) ✓ ssh cat 恢复
- netlist_pro_v2: /home/easont/netlist_pro_v2 (3960 字节, 90 行, 破坏性优化) — 备用
- netlist_AI: /rundata/ddgoa/.../netlist_AI (39840 字节) 🚫 权限拒绝; netlist_pro_final 同构替代
- TopDes 区域: netlist_pro_final 与 netlist_pro_clean 的 **TopDesStart..**TopDesEnd 完全一致(均 18147 字符)

## 合成计划 (本轮交付)
- task_id: EDA-Eval-DesignFlow-NetlistCompareReport-001
- domain: eda_other (SPICE 网表结构对比工具)
- track: faithful (A 档, 用户原话 U#383)
- 难度: L1-static + subprocess (离线 Python 解析网表文本, check 在 B 上真跑候选)
- 交付: compare_netlist.py (config-driven 读 config.json{original_netlist, optimized_netlist}) + report.md + report.json
- A (可见): original_netlist.sp (netlist_pro_final 37 单元) + optimized_netlist.sp (netlist_pro_clean 15 单元)
- 隐藏 B: relabel(反转单元名 inv->vni 等) + 原始加 3 dummy + 优化加 1 dummy => 40->16 单元, 24 removed
- 隐藏 B' (交叉输入守卫): relabel only => 37->15 单元, 22 removed (非 B 的 40/16/24)
- gold: compare_netlist.py 通用解析 .SUBCKT + TopDes X-instance, 反硬编码无 A 专属字面量
- check.py 14 conds a-n: a zip b py_compile c [B]exit+keys d-g [B]bytes/lines h,i [B]cell counts j [B]removed names k [B]kept names l [B]topdes m 反硬编码 n [B']交叉守卫
