# 深读笔记 · 1789644585939_3e35z · zjqiao @ hfhds201 · spice_sim

## trace 元信息
- session: `1789644585939_3e35z.messages.json`
- user: zjqiao · host: hfhds201(.75) · size 894KB · 85 msgs · spice_kw 计数 sp=48
- ledger: claimed → case (EDA-Eval-DesignFlow-CompressNetlist-001)
- 触发：11-07 21:3x 重扫令持续履行，hfhds201 fresh rescan since 21:10 = 0 fresh（周六晚间），转 hfhds201 local spice-dominant 重建 37 cand → diff ledger_B(normalized anchor) → 8 unscouted local → peek 4 top(sp≥30)：rkdu8/3e35z/y91i6/mrmfn → **3e35z CLEAN A-档**（余 3 待下轮 peek：rkdu8/y91i6/mrmfn，及 4 低 sp：zlqaz/qyroq/vefeh/racxm）。

## 用户对话流（A-档选轮）
- **U#0**（逐字拼音 + 附件）：`gaiweijian1shiyonglaijiangwangbiaozhuanhuanweicompresswangbiaode1` = 「该文件1是用来将网表转换为compress网表的1」+ 附件 `Run_Compress_Netlist`（1.2KB shell 脚本）。→ 说明附件用途，非任务轮。
- **U#32**（意图轮）：「你能否编写一个skill，基于该文件夹中的修改netlist的代码，将文件夹中的指定的网表转换为compress netlist」→ 表达目标（编写 skill 转换 netlist → compress netlist）。
- **U#73**（澄清）：「需要说明的是，指定转换的网表并不一定是Netlist_Vcap_20260915PM_Fullchip，也可能是其他日期的最新网表，我需要你能够允许用户在使用skill时选择网表，然后你去修改相应的shell脚本参数，将最新的netlist转换为compress netlist」→ 用户可指定 netlist，改 shell 脚本参数。
- **U#75**（任务说明轮，**逐字用作 prompt**）：「注意，我不是要将最新的netlist进行转换，而是希望用户在调用skill时可以指定netlist，然后你去将相应的参数改为用户指定的netlist，然后运行脚本进行转换」→ 明确：指定 netlist → 改参数 → 运行脚本。属「表达目标」轮（非根因/非修复方案），合规 A-档。
- **U#79**（澄清，**不入 prompt**）：「这个skil完善一下，当用户输入网表名称例如Netlist_Vcap_20240811PM时，即可进行转换」→ 模糊匹配（用户输入部分名即可）。用作 hint 设计 hidden B 与 check（条件 l 前缀扩展、m 歧义、n 无匹配）。

> A-档规则：任务说明 = 表达目标轮逐字原文；澄清轮（U#73/U#79）不入 prompt，仅用作金标准/check 设计依据。U#75 既表达目标又含可执行子流（指定→改参数→运行），与 check 行为直接映射，故选 U#75 为 prompt。

## assistant 工具链
list_allowed_files(12) → read_files(10) → RAG_MCP_Server__search_apis(10, skill API) → search_codebase(4) → RAG_MCP_Server__get_api_details(4) → editor(4, 全被 policy 拒) → run_approved_command(1, profile owner mismatch) → get_agent_policy_status(1)。policy `writableRoots` 阻止所有写文件，最终 SKILL 代码以文本输出在响应里。

## Run_Compress_Netlist shell 脚本逻辑（msg 31 verbatim 引用）
1. **网表选择**：5 种 Netlist= 配置用 `#` 注释切换：
   - `#Netlist='Netlist_Vcap_20240811PM_2STACK_TSV'`（TSV Vcap）
   - `#Netlist='Netlist_Vcap_20240802PM_V1'`（Norm Vcap）
   - `#Netlist='Netlist_SpfBA_20250613_REVC_PowerFill'`（Norm Spf）
   - `Netlist='Netlist_Vcap_20260915PM_Fullchip'`（**TSV Spf，当前激活**）
2. **复制**：`cp -rf -L ${Netlist} ${Netlist}_Compress; chmod 775 ${Netlist}_Compress`（-L 跟随符号链接）
3. **核心转换**：sed 替换 `switch_close`→`switch_open`，3 套按模式注释切换：
   - vcap：`XI2_11 inh_vss YioN7<15>` / `XI0_11 inh_vcc Yio7<15>`（YioN7/Yio 方向）
   - Spf：`XI2_11 vss! YioN7<15>` / `XI0_11 vcc! Yio7<15>`（vss!/vcc! 供电）
   - TSV module（**激活**）：`XI2_11 inh_vss Yio7<15>` / `XI0_11 inh_vcc YioN7<15>`（Yio 方向与 vcap 相反）
4. 用途：DDR5 Compress 测试模式隔离特定测试路径，vecgen 基于改后网表生成压缩测试向量。

## 金标准（msg 82 SKILL 文本输出，用户接受）
`compressNetlist.il` 9 节：
1. `FindNetlistDirs(dir)` — 扫 Netlist_* 目录，按名降序（嵌日期 newest first）
2. `FuzzyMatchNetlist(userInput,dir)` — 精确匹配优先，否则正则子串匹配，无匹配返 nil，多匹配返全列表
3. `AutoInferMode(netlistName)` — 按名关键字推断 TSV_Vcap/Norm_Vcap/Norm_Spf/TSV_Spf（TSV+VCAP→TSV_Vcap；VCAP→Norm_Vcap；TSV+SPF→TSV_Spf；SPF→Norm_Spf；FULLCHIP→TSV_Spf；2STACK→TSV_Vcap；default→TSV_Spf）
4. `ScriptSetNetlist(name,scriptPath)` — 读 shell，正则替换激活 `Netlist='...'` 行，写回
5. `ScriptSetMode(mode,scriptPath)` — 按 mode 注释/取消注释对应 sed 块（3 套 sedBlockPatterns + activeBlocks 映射）
6. `ScriptRun(scriptPath)` — `csh` chmod +x 并执行
7. `RunCompressNetlist(userInput,?mode,?script,?dir)` — 主入口：模糊匹配→推断 mode→ScriptSetNetlist→ScriptSetMode→ScriptRun
8. `RunCompress` shortcut / 9. `ListNetlists` helper

## case 合成（A-档 spice_sim L1）
- **任务说明**：U#75 逐字原文（assets/A/prompt.txt）
- **资产 A**：Run_Compress_Netlist_A.sh（5 netlist, TSV Spf Fullchip 激活）+ netlists_A.txt（5 目录）+ config_A.json（user_input=Netlist_Vcap_20240811PM）+ task_brief.md（交付接口 ≤3 行）
- **隐藏 B**：run_compress_template_B.sh（不同 netlist 名 / Norm_Spf 激活 / vss!vcc! sed 块）+ netlist_dirs_B.json + config_B.json（partial_name=Netlist_SpfBA_20250613）+ hidden_manifest.json（expected_matched=Netlist_SpfBA_20250613_REVC_PowerFill, a_tokens_forbidden=[Netlist_Vcap_20260915PM_Fullchip]）
- **交付**：gen_compress_netlist.py 读 cwd 的 config.json/netlist_dirs.json/run_compress_template.sh → outdir/Run_Compress_Netlist(改写后shell) + compressNetlist.il(SKILL文本) + manifest.json
- **reference**：gen_compress_netlist.py（前缀模糊匹配：精确→前缀 startswith；0 命中 exit 1；>1 命中 exit 2 歧义；改写 Netlist= 行 + 注释其余 + 保留非 Netlist 行逐字 + 生成 SKILL 文本）
- **check.py 14 断言(a-n)**：见 jsonl metadata.test_rationale
- **自验**：ref PASS 14/14 ✓ · 4 negative(fake_empty/fake_print_fixed_A/fake_core_deleted/naive_no_fuzzy) 全 FAIL @ c,d ✓ · negative_selftest PASS ✓（修 hidden/B 目录 copy bug）· §4.9 三假(空壳/print固定A/删核心)全 FAIL ✓
- **断言闸门**：k_rationale=14 == k_check=14 ≥ 8 ✓
- **修复**：negative_selftest.py 第 45 行 `shutil.copy` 对 hidden/B 目录报 IsADirectoryError → 加 `if not os.path.isfile(src): continue` 跳过目录

## 备注
- 本 case 产物（assets/reference/check.py/gen_compress_netlist.py/negative）于 2026-11-04 07:2x 由前轮合成但未落 jsonl；本轮 21:3x 复核自验通过 + 断言闸门 + 修 negative_selftest bug + 追加 EDA-Eval-DesignFlow_B.jsonl + mark ledger，闭合为正式交付。
- trace 附件 Run_Compress_Netlist 已被 /tmp/cline-attachments 清理，从 msg 31 verbatim 引用重建（assets/A/Run_Compress_Netlist_A.sh 与原脚本一致）。
