# Deepread: 1794968173766_dap8v (ynbai @ hfeg0pkn004, mc=81, characterization)

## trace_source
- user: ynbai (original, unmasked)
- host: hfeg0pkn004 (10.129.2.13)
- session_file: 1794968173766_dap8v.messages.json (NMSGS=189, dict, 6 keys)
- match_count: 81
- keywords: netlist:4738; lvs:80; hspice:37; ... (spice-ratio 0.997, B-pure characterization)

## real_task_summary (USER 原话)
1. (msg 0) "查看 /home/ynbai/DDR5/DRVQA/sim_setup/Bin/runBiasTrimAccuracy 脚本，该脚本对网表文件进行处理输出，识别 /proj/drvqa/V0/simdir/finesim/drvqaF/Netlists/Netlist_Vcap_20261117PM_Fullchip/netlist 文件，当前脚本为什么识别不出 R_dlybiasn1000ps_custom cell，修改脚本，让工具可以识别出 R_dlybia* 文件"
2. (msg 78) "当前网表里所有的 R_dlybias*_custom* 都能被识别到吗"
3. (msg 90) "增加选项，添加 R_*_vdly_new 的 cell，识别当前网表存在那些 cell"
4. (msg 120+) 后续是 si.out 仿真速度对比分析 (WRAP SS vs WRP_AP vs Golden TT/SS) — 不同主题，本 case 不用。

## root cause + fix (assistant 实际做的)
- 脚本 `runBiasTrimAccuracy` (python3) 的 `is_keep_subckt()` 对 `R_` 前缀子电路有特殊分支，只保留:
  `'VdbiasDly' in name` / `'VbiasDly' in name` / `startswith(('R_trimand','R_trimbuf','R_trimnand'))`。
- `R_dlybiasn1000ps_custom` 以 `R_` 开头 → 进入该分支 → 不满足任一条件 → 被过滤掉。
- 通用规则 `dlybias*ps` 也匹配不到 (因为有 `R_` 前缀)。
- **Fix #1** (msg 38/54): R_ 分支新增 `or subckt_name.startswith('R_dlybias')`。
- **Fix #2** (msg 103): R_ 分支新增 `or subckt_name.endswith('_vdly_new')`。
- 网表实测 R_dlybias* 唯一 .SUBCKT 共 14 个 (R_dlybiasn_gut_custom_1000ps / R_dlybiasn500ps_custom / R_dlybiasn500ps_custom_small / R_dlybias_gut_custom_1000ps / R_dlybias250ps_custom / R_dlybiasn1000ps_custom_small / R_dlybiasn1000ps_custom / R_dlybiasn250ps_custom_small / R_dlybiasn250ps_custom / R_dlybias500ps_custom / R_dlybiasn750ps_custom / R_dlybiasn_gut_custom_2000ps / R_dlybiasn2000ps_custom / R_dlybiasn1500ps_custom)，全部 startswith('R_dlybias') ✅。
- R_*_vdly_new 唯一 .SUBCKT 共 2 个 (R_NcTiming210_vdly_new / R_OcOffDlyNcs210_vdly_new)，全部 endswith('_vdly_new') ✅。
- 18 + 31 测试用例全 PASS。

## script structure (runBiasTrimAccuracy, 完整)
```python
#!/apps/local/bin/python3
import re, shutil, os

def is_keep_subckt(subckt_name):
    # Rule 1: skip AG_/AF_/IO_/PWY_/T_ prefix
    if subckt_name.startswith(('AG_','AF_','IO_','PWY_','T_')): return False
    # Rule 2: skip containing 'Spdly'
    if 'Spdly' in subckt_name: return False
    # Rule 3: R_ branch
    if subckt_name.startswith('R_'):
        return ('VdbiasDly' in subckt_name
                or 'VbiasDly' in subckt_name
                or subckt_name.startswith(('R_trimand','R_trimbuf','R_trimnand'))
                or subckt_name.startswith('R_dlybias')        # FIX #1
                or subckt_name.endswith('_vdly_new'))          # FIX #2
    # Rule 4: dlybias*ps
    if subckt_name.startswith('dlybias') and subckt_name.endswith('ps'): return True
    # Rule 5: trimbuf_*
    if subckt_name.startswith('trimbuf_'): return True
    # Rule 6: trimnand2_*
    if subckt_name.startswith('trimnand2_'): return True
    return False

def process_netlist(input_file, output_file):
    # Checker 1: input validity (exists / readable / non-empty)
    # regex: re.compile(r'\.subckt\s+(\w+)', re.IGNORECASE)
    # read lines, skip empty + '*' comment lines, match .subckt → sub_name
    # if is_keep_subckt(sub_name): matching_words.add(sub_name)  # set dedup
    # Checker 2: empty result warning
    # sorted_words = sorted(matching_words)
    # processed_lines = [f'.option finesim_mode = "{word}:spicemd"' for word in sorted_words]
    # Checker 3: output dir write permission
    # write processed_lines to output_file, each + '\n'
    # print [SUCCESS] Process completed, N valid subcircuits exported

input_file = 'netlist'
output_file = 'BiasTrimAccuracy'
if __name__ == "__main__":
    process_netlist(input_file, output_file)
```

## case reframe (design_flow, produce-tool)
- trace 意图 = use-tool (用户让 fix 现成 runBiasTrimAccuracy 脚本)。
- case 交付 = produce-tool：fix 原始 buggy 脚本 (补 R_dlybias / _vdly_new 两条规则) + 在 netlist_A 上跑出 BiasTrimAccuracy 输出，打进 outputs/submit.zip。意图零偏移 (仍是让脚本识别 R_dlybias* / R_*_vdly_new 子电路)。
- asset_fidelity = A-faithful：netlist_A 是 ynbai 网表 .SUBCKT 片段的忠实重建 (14 R_dlybias* + 2 R_*_vdly_new + 现有规则 cell + 排除 cell + instance ref + 注释 + 重复定义)；runBiasTrimAccuracy (buggy 原版) 文本便携。
- hidden B = 不同命名/不同数量的 netlist (5 R_dlybias* + 3 R_*_vdly_new，名字全不同，count 不同) → 验防硬编码 A。
- layer = L1 (纯 python 文本处理，不启 EDA 二进制)。
- §4 牙：hidden-B cross-input + 3-seed 随机 netlist + subprocess 候选独立运行 + ref_keep 独立复算。

## check.py 计划 (k=11)
a unzip+find script / b py_compile / c is_keep_subckt callable / d R_dlybias* keep (含非 A 变体) / e R_*_vdly_new keep (含非 A 变体) / f 现有规则保留 (5) / g 排除规则保留 (7) / h 可见 A process_netlist 输出精确匹配 (sorted/deduped/格式) / i 3-seed 随机 netlist 输出==独立复算 (防硬编码) / j 确定性 3 run 字节一致 / k 输出格式精确 (regex + 排序 + 无 dup + 无 excluded)。

## negatives
- neg_hardcode_a.py: is_keep_subckt 只对 A 的 24 个确切名字返回 True → i (随机 B) FAIL。
- neg_overbroad.py: R_ 分支 always True (过度宽松) → g (AG_/T_/R_random 排除) FAIL。
- neg_print_only.py: 只 print 不写文件 → h/c FAIL。
- neg_core_removed.py: is_keep_subckt always True + 不真正过滤 → g + h FAIL。
- negative_selftest.py: 全部须 FAIL。
