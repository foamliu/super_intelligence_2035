# trace_deepread: 1792114378643_rw7u9 — ERC -recon license 根因诊断

- **session**: `1792114378643_rw7u9.messages.json` — gokuguo @ hfeg0plg53 (10.129.35.69)
- **mc**=51 (279 calibre + 21 virtuoso + 9 schematic + 4 pyAether + 2 hspice)；44 msgs / 1 user turn
- **domain**: physical_verify (shard C)
- **A-档 seed (USER#0 逐字, 提出目标未给根因)**:
  > /proj/lacaa/.../MB2SDFQD1FSP51H204L6W35T6ULVT/erc.log，你先读取一下这个文件，看看为什么erc会报错。我的执行程序在 /home/gokuguo/Desktop/vir_setup_cant_remove/Batch_LVS 中，执行命令是 python3 batch_lvs.py lvs.json，需要你来帮我找一下执行程序哪里有问题。
- **assistant 工具链**: get_agent_policy_status + list_allowed_files(Batch_LVS) + read_files(erc.log) → read_files(batch_lvs.py/lvs.json/policy) → read_files batch_lvs.py 分段 (86-560, 156-460, 221-366=create_calibre_erc_script) → editor(grep_erc.sh) + run_approved_command(shell-runner) → tail erc.log → read_files(erc.log 11290-11330) → list_allowed_files(result dir) + list_allowed_files(LVS_20261016_092259 cell dir) → editor(grep_lvs.sh) + run_approved_command → editor(grep_src.sh) + run_approved_command (grep batch_lvs.py + batch_lvs_old.py) → editor(batch_lvs.py 修复) → editor(check_syntax.py) + run_approved_command(python-runner) → SYNTAX OK

## 真实根因 (trace #37/#38/#42 人工复核)
1. **erc.log** (11330 行) 末尾：
   - `CALIBRE_CMD_LINE='...calibre -recon -erc -hier -turbo 4 .../35H_...Test07.lvs'`
   - `// Applying licensing policy...` + 12 条 `calibreXXX license acquired.` (calibrehlvs/calibrelvs/calibrehdrc/calibredrc/calibreadp/calibreci 各 2 次)
   - `// ERROR: The following products could not be licensed sufficiently:`
   - `// ERROR: - LVS Recon ERC`
   → ERC 跑因 **license** 报错退出（不是规则错误、不是版图错误）。
2. **batch_lvs.py** `create_calibre_erc_script()` 第259行：
   `f'calibre -recon -{self.erc_mode} -hier -turbo {self.turbo} {extra} {local_erc_rule} 2>&1 | tee ./erc.log'`
   — `-recon` 开关让 Calibre 请求独立的 **LVS Recon ERC** 许可，该许可未授权 → 报错。
   `self.erc_mode='erc'` (第42行)，`self.turbo=4`，`self.erc_extra_flags=''`。
3. **LVS 跑通** (对比)：lvs.log line86 `//  Running ... calibre -lvs -spice layout.spi -hier -turbo 4 -hcell ...`，lvs.rep `CORRECT  MB2SDFQD1FSP51H204L6W35T6ULVT`。LVS 命令**无 -recon**，用标准 calibrelvs/calibreci license (已 acquired) → 成功。
4. **batch_lvs_old.py** 无 ERC 块（只做 LVS，line181 `calibre -lvs ... -turbo 1`）→ ERC 是 batch_lvs.py 新加功能，`-recon` 是新引入的 bug。
5. **修复 (#37/#42)**: editor old_text 第259行 `calibre -recon -{self.erc_mode}` → new_text `calibre -{self.erc_mode}` (移除 -recon)；check_syntax.py `SYNTAX OK`, line 259: `f'calibre -{self.erc_mode} -hier -turbo {self.turbo} ...'`。修复后 ERC 命令 = `calibre -erc -hier -turbo 4 ...`，用已 acquired 的 calibreci license。

## 资产保真
- erc.log: 含 `// OPTION 5 ... nwell_floating` 注释、`LAYOUT ERROR ON INPUT YES`、`LVS ABORT ON SUPPLY ERROR NO`、`#IFNDEF <switch> TRUE/FALSE` + `SVRF ERROR "...switch setting is wrong"` 块 (CASE_SENSITIVITY/ENABLE_SUBCUT_ISOLATION/ENABLE_FLICKER/ENABLE_WELL_TEXT/PARASITIC_*_CMP/TPA_THICK/RC_FLOW)、`--- STANDARD VERIFICATION RULE FILE COMPILATION MODULE COMPLETED`、`CALIBRE_CMD_LINE='... -recon -erc -hier -turbo 4 ...'`、`--- CALIBRE::HIERARCHICAL CIRCUIT EXTRACTOR`、12 条 license acquired、`// ERROR: ... LVS Recon ERC`。
- lvs.log: `//  Running ... calibre -lvs -spice layout.spi -hier -turbo 4 -hcell .../hcell_list_V0d1_Rev06_Test01 .../35H_...Test07.lvs` + CALIBRE_CMD_LINE (无 -recon) + `--- LVS COMPLETED`。
- lvs.rep: `CORRECT  MB2SDFQD1FSP51H204L6W35T6ULVT`。
- batch_lvs.py: BatchLVSRunner 骨架，__init__ (erc_mode='erc'/turbo=4/erc_extra_flags=''/run_erc=True)，create_calibre_lvs_script (calibre -lvs)，create_calibre_erc_script (buggy 第60行 calibre -recon -{self.erc_mode})，generate_script 调两者。
- lvs.json: project= lacaa / lvs_rule_file= /home/gokuguo/.../35H_...Test08.lvs / platform= virtuoso / virtual_connect= YES。

## 隐藏 B1/B2 (防硬编码)
- B1: cell=INVX1FSP51H204L6W35T6ULVT, rule=Test09, turbo=8, buggy line=66 (padding 6)
- B2: cell=NAND2X1FSP51H204L6W35T6ULVT, rule=Test11, turbo=2, buggy line=72 (padding 12)
- B1/B2 同 -recon -erc bug + 同 LVS Recon ERC license error + LVS CORRECT，但单元名/规则/turbo/行号全不同 → 候选必须 regex 搜 -recon 行，不能硬编码 A 的第60行。

## 合成决策
- gold = `diagnose_erc_recon.py` (stdlib-only, 确定性): 解析 erc.log (license ERROR + CALIBRE_CMD_LINE -recon -erc) + batch_lvs.py (regex 搜 -recon 行号 + 封闭 def + self.erc_mode) + lvs.log (calibre -lvs 命令, 无 -recon) + lvs.rep (CORRECT) → JSON 诊断 (error_type=license / failing_product=LVS Recon ERC / buggy_flag=-recon / buggy_line_no / buggy_function=create_calibre_erc_script / fix=移除 -recon / lvs_status=CORRECT / conclusion)。
- A-档 faithful 不可行 (live erc.log 11330 行 + live batch_lvs.py 在 /proj + 用户机，沙盒不可达) → B-档 synthesized L1-boundary。

## 正交性
与现有 physical_verify ERC/LVS case 正交：ERCFilter-001 (ERC AI-check 2.1-2.8 filter) / ERCBootPlan-001 (ERC run_all.sh follow 修复) / ERCFlowAether-001 (ERC_AI_CHECK aether flow) / LVSDiag-001 (LVS INCORRECT instances-count) / LVSLogFilter-001 (argus LVS log filter)。本案 = **ERC license-error 根因 + calibre 命令构造器 -recon flag 定位** (license 类失败, 非规则失败, 非 LVS 失败)。
