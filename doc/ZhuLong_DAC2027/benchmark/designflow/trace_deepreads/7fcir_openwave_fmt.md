# trace_deepread: 3jb3i → 7fcir (OpenWaveFmt)

- **session**: 1789881196637_7fcir.messages.json — rongjiez @ hfeg0plg98 (mc=16, 51 msgs)
- **domain**: waveform (L1-boundary: offline Perl script generates waveview tcl from waveform file listings; no real WaveView run)
- **track**: A-faithful (trace-faithful)

## U#0 (verbatim, 提需求轮 — user提出需求，未指出根因/未给修复方案 ✓)
> openWave.pl 这个脚本实现了对目录下ModelQA_0920111317文件夹下的idvd和idvg目录下的所有#.sw0文件进行读取，生成一个tcl文件。这种波形文件格式是finesim的。对于primesim的输出波形文件在ModelQA_0920111543下idvd和idvg下有ntn_w2.400u_l0.190u_nf1_wdf和ptn_w1.640u_l0.180u_nf1_wdf文件夹，下面有dc0_a1.dc dc0_a2.dc等文件，现在我需要你把penWave.pl增加支持这种格式，生成对应的tcl文件，注意不需要增加输入仿真器变量，因为这两种情况同时只会出现一种dc0_a0.dc不需要分析

## assistant 工具链
1. `list_allowed_files` / `search_codebase` 找 openWave.pl → `/home/rongjiez/jira_dev/mpqa/mp_1/scripts/openWave.pl`
2. `read_files` 读 openWave.pl + 两个 ModelQA 目录的 openSignal.tcl 样例
3. `list_allowed_files` 探 primesim 目录结构 → `idvd/<dev>_wdf/dc0_a1.dc..dc0_a4.dc`（含 dc0_a0.dc）
4. 分析两格式：FineSim `glob $waveDir/*/*#*.sw0`（sweep dir = dirname(file)）；PrimeSim `glob $waveDir/*/*_wdf/dc0_a*.dc`（sweep dir = parent of _wdf，跳过 dc0_a0.dc）
5. `editor` 写扩展版 openWave.pl 到 `/home/rongjiez/.cline/scripts/data/openWave.pl`（目标路径 policy 只读）
6. 清理未用 `$findName` 变量；trace 两格式逻辑确认 PANEL/WV 划分正确

## 关键产物（金标准 = 用户接受的结果）
扩展版 openWave.pl（finesim+primesim 自动识别）：
- 入参：`$waveDir`（如 ModelQA_0920111543）
- 自动识别：先 glob `*/*#*.sw0`（finesim），elsif `*/*_wdf/dc0_a*.dc`（primesim）
- `getSweepDir`：finesim→dirname(file)；primesim→dirname(dirname(file))（_wdf 的父目录 = idvd/idvg）
- primesim 跳过 `dc0_a0.dc`（DC 工作点）
- 生成 `$waveDir/openSignal.tcl`：`after 5 destroy .` 头；每文件 `set dbFile`+`sx_open_sim_file_read`；sweep 切换时（`i % count == 1 and i != 1`）`sx_new_wv`+`++$j`+`$i=1`；`sx_display [sx_signal "*.isub(d*)"]`；`wv_select_waveview $j`；`wv_press_key Down 973 404`；`wv_select_wv_item WV$j.PANEL$i:1.HEIGHT`；`wv_set_size ... 150`
- count = sweep dir 内文件数（finesim `find -name "*#*.sw0"|wc -l`；primesim `find -name "dc0_a*.dc" ! -name "dc0_a0.dc"|wc -l`）
- `chmod 755` + `wv -ace_gui $tclScript`

## 物理/工程要点
- FineSim 输出 `<sweep>/<dev>#<n>.sw0` 直接在 sweep 目录下；PrimeSim 输出在 `<sweep>/<dev>_wdf/dc0_a<n>.dc` 多一层 _wdf 子目录
- dc0_a0.dc 是 DC 工作点，不分析；只分析 dc0_a1..a_N
- 两种格式互斥（一次只出现一种），故不需增加仿真器输入变量，靠 glob 自动识别
- PANEL 按 sweep dir 内文件数分组，sweep 切换开新 waveview（WV），`sx_new_wv` 次数 = sweep_dir 数 − 1

## 合成降级
- L1-boundary：候选提交通用 openWave.pl，check 在隐藏 B 上 `perl` 跑（dummy `wv` no-op），校验生成的 openSignal.tcl 结构（PANEL/WV 划分、格式自动识别、dc0_a0 跳过、跨输入护栏）
- 资产 A（可见）：baseline openWave.pl（finesim-only）+ ModelQA_0920111317（finesim 16 .sw0）+ ModelQA_0920111543（primesim 20 .dc）+ prompt(U#0) + task_brief
- 隐藏 B：ModelQA_0925012015（finesim 12 .sw0，2 dev×3×2）+ ModelQA_0925012088（primesim 24 .dc，2 dev×(a0+5)×2）— 设备名/数量/时间戳目录名均不同
- check.py 16 条件 a–p
