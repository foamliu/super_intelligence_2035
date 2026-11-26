# trace_deepread: 1789611712575_5tdum (mike@10.129.32.80, mc=80, n=51)

**domain**: schematic_netlist  **track**: A-faithful  **layer**: L1  **case**: SiInpTokenStrip-001

## U#0 逐字（A 档任务说明，不脱敏）
```
/rundata/dscqa_sim/V0/simdir/finesim/dscqaF2/MatrixRun/MatrixRun_Netlist_Vcap_20260916PM_DDR6TOP.Meta  zhegelujingxia you henduo mulu ,meige muluxia youge si.inp wenjian ,bangwo xiege mingling ,woyao shandiao si.inp zhong T_mBistOsc zifuchuan
```
pinyin 还原：「这个路径下有很多目录，每个目录下有个 si.inp 文件，帮我写个命令，我要删掉 si.inp 中 T_mBistOsc 字符串」。
**A 档前提核验**：纯提需求（写命令删字符串），未给根因、未给修复 → 符合 A-faithful。

## trace 演化（51 msg）
- agent list_allowed_files(depth 1/2/3) 枚举 Meta 根 → 25 个 corner 子目录（primesim.Meta001_..._FF/SS/TT.X2P6/X1P12...）。
- read_files 抽样 si.inp → 定位 T_mBistOsc 在第 55 行 `.option finesim_ignore = "R_RasEnOsc R_SrefAnlgOsc R_SrefOsc T_IsmOsc T_mBistOsc AG_TSOsc AG_ThickVfsblnOsc R_RHROsc R_RHROscTrimCap1"`。
- find -name si.inp + grep T_mBistOsc + search_codebase 确认所有 corner 的 si.inp 同构。
- agent 用 editor 逐文件替换 line 55（去 `T_mBistOsc ` 含尾空格）→ 但 policy 限制 /rundata 不可写 → 转查 /ai_sandbox、/home 可写根。
- 用户要的「命令」本质 = 一个遍历目录树、对所有 si.inp 整词移除 token 的脚本/命令。

## 真实产物不可附加
真实 /rundata/.../Meta 树（25 corner + si.inp）在 .75 permission-denied 不可读/不可附加 → **B-grade synthesized**：
- A 资产 = 合成 meta_A 树（6 corner 子目录，各含一个 si.inp，token T_mBistOsc 出现在 `.option finesim_ignore = "..."` 行；附 si.inp.bak + run.sh 非 target 文件）。
- 金标 remove_token_ref.py：`<root> <token> [--out]`，os.walk 找名为 si.inp 的文件，按 **`\b` 整词** 移除 token（处理引号边界 + 拒绝子串匹配），移除时连带一个相邻空格保持单间距，原地改写，输出 JSON 报告 {root, token, si_inp_found, files_modified, total_occurrences_removed, files:[{path, modified, occurrences_removed, line_preview}]}。
- hidden B = meta_B 树（8 corner，token R_SrefOsc，含边例：token 在引号内首/尾/唯一内容/跨两行；decoy 子串 R_SrefOscTrim 须保留；B7 无 token；附 si.inp.bak/run.sh/notes.txt 非 target）。

## 教训
- **整词边界用 `\b` 不用 `(?<!\S)`**：引号 `"` 是非空白字符，`(?<!\S)` 会让引号内首/尾 token 漏匹配；`\b` 正确处理引号边界且拒绝子串（R_SrefOscTrim 不被误删）。
- 判分 (h)「token 残留」也须用 `\b`，否则假阴性。
- 反硬编码：B token R_SrefOsc 不许出现在金标源码（连 docstring 示例都不行，否则 (l) 误判）→ docstring 用泛化示例 `Foo`/`Foobar`。
- 确定性 (n) 须规范化 report.root（临时目录 abspath 每次不同）。
