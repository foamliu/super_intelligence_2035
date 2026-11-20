# Deepread — 1789645120364_2n1bs (zjqiao @ hfhds201) — SetNetlistParam

## Trace meta
- session: `1789645120364_2n1bs.messages.json`
- user: zjqiao · host: hfhds201 · nmsgs: 41 · size: 194191 B
- tools: list_allowed_files(8) read_files(7) run_commands(3, blocked) search_codebase(1) get_agent_policy_status(1) editor(4, 1 success)
- ts: 1789645120685 (2026-01-15ish epoch → 实为 2026 年中)
- domain: spice_sim (finesim netlist 压缩流程)

## USER#0 (verbatim A-档 — 纯需求轮)
> 编写一个skill，用户指定 netlist 名称，SKILL 修改/rundata/drvqa/V0/simdir/finesim/drvqaF/Netlists/Run_Compress_Netlist shell 脚本中的 Netlist参数，然后运行该 shell 脚本执行转换

**A-档判定**：✓ CLEAN — 给目标(写 skill)+方法(修改 Netlist 参数 + 运行脚本)，未给根因/修复。feature-修改轮。

## 真实附件 / 关键产物（从 trace read_files / editor 提取）

### Run_Compress_Netlist (shell 脚本，30 行)
```
#sleep 4h
#TSV Vcap
#Netlist='Netlist_Vcap_20240811PM_2STACK_TSV'
#Norm Vcap
#Netlist='Netlist_Vcap_20240802PM_V1'
#Norm Spf
#Netlist='Netlist_SpfBA_20250613_REVC_PowerFill'
#TSV Spf
Netlist='Netlist_Vcap_20260911PM_Fullchip'        ← ACTIVE (唯一未注释)
# Netlist='Netlist_Vcap_2026'                      ← 注释陷阱 (# 后空格)

cp -rf -L ${Netlist} ${Netlist}_Compress
chmod 775 ${Netlist}_Compress
#vcap
#sed -i "s;XI2_11 inh_vss YioN7<15> switch_close;...;g" ${Netlist}_Compress/netlist
sed -i "s;XI2_11 inh_vss Yio7<15> switch_close;XI2_11 inh_vss Yio7<15> switch_open;g" ${Netlist}_Compress/netlist
sed -i "s;XI0_11 inh_vcc YioN7<15> switch_close;XI0_11 inh_vcc YioN7<15> switch_open;g" ${Netlist}_Compress/netlist
```
格式：多条 `#Netlist='...'` 注释选项 + 唯一未注释 `Netlist='...'` 行 + `# Netlist=` 空格陷阱 + `cp/chmod/sed ${Netlist}` 命令。

### SetNetlist.il (assistant 产 SKILL 金标准，5328 B，editor msg 34)
核心逻辑：
1. `SetNetlist_UpdateScript(netlistName, scriptPath)`：
   - 逐行读 shell 脚本
   - 匹配 `^[ \t]*Netlist=`（行首可选空白后 `Netlist=`）
   - 排除 `^[ \t]*#`（注释行）
   - `rexReplace "Netlist='[^']*'"` → `Netlist='<netlistName>'`
   - 无匹配则 error
   - 写回（注：原 SKILL 用 gets/fprintf "%s" 会丢换行——这是 bug，便携版应保留换行）
2. `SetNetlist_RunScript(scriptPath)`：chmod +x 后 csh() 运行
3. `SetNetlist(netlistName [?script path])`：先更新后运行
4. `SN` 快捷别名

trace 末尾 USER 接受结果（msg 40 assistant 报告「已完成：创建 SetNetlist.il」）。

## 合成金标准（便携 L1 Python）
- 任务可移植核心 = 文本操作：找活动 `Netlist='...'` 行（未注释），替换值，写回，保留所有其他行（含注释）。
- "运行 shell 脚本" 部分 = 环境 specific（csh/Virtuoso），便携 L1 不做；check 只验编辑正确性。
- 交付 = `set_netlist_param.py <shell_script> <netlist_name> <output>`

## Case 设计 (EDA-Eval-DesignFlow-SetNetlistParam-001, spice_sim A-faithful L1)
- **A** (testdir_A/Run_Compress_Netlist): 复刻真实格式——多条 #Netlist 注释 + 1 活动 `Netlist='Netlist_Vcap_20260911PM_Fullchip'`(无缩进) + `# Netlist=` 空格陷阱 + cp/sed ${Netlist}
- **hidden B** (hidden/testdir_B/Run_Compress_Netlist): 不同——不同注释选项 + 1 活动 `  Netlist='Netlist_SpfBA_20260615PM_RevD'`(**缩进 2 空格**, 测空白处理) + `# Netlist=` 陷阱 + 不同 sed 命令
- **A≠B**: A 活动行无缩进 + Vcap 值; B 活动行缩进 + SpfBA 值; 注释/sed 内容不同
- **check.py k=12 断言 a-l**: zip+py / compile / 无参非零 / 跑B exit0+输出 / 行数保留 / B活动行值替换 / 注释#Netlist保留 / `# Netlist=`空格陷阱保留 / ${Netlist}不展开 / 无活动行非零退出 / 跨输入A替换且A≠B / B缩进保留
- **negative/**: 5 stub (empty/print_expected/hardcode_B/no_edit/core_deleted) + negative_selftest.py
- **reference_submit.zip**: set_netlist_param_ref.py

## 断言闸门
k_rationale = 12 == k_check = 12 ≥ 8 ✓
