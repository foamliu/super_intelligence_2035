# trace_deepread: 1792552343391_748ox (johnl / hfeg0pfn119, mc=123)

- **session**: `/home/johnl/.cline/data/sessions/1792552343391_748ox/1792552343391_748ox.messages.json` (1.36MB, 189 msgs)
- **keywords**: netlist:402; calibre:384; aether:216; schematic:160; .cdl:78; .spi:56; synopsys:17; transistor:15
- **domain**: pnr_signoff (Calibre PEX / RCC parasitic extraction + LVS)
- **真实任务**: Calibre PEX RCC 抽取失败修复 — `/proj/drcoa/V0/ver/pex/johnl/T_IsmTop` 抽 IsmRCC 失败，CCI-LVS NOT Clean。

## 用户轮（A-档规则②筛选）
- **[0]**（提需求 + 根因 + 修复方向，规则②命中🚫）: "/proj/drcoa/V0/ver/pex/johnl/T_IsmTop 这个文件夹抽IsmRCC失败了 说是buffer底层没map vbn 到vss vbp到vcc 要改cdl你改下记得 对所有目录下到文件的修改都要比较修改前后确保合适修改没问题 修改并完成RCC抽取"
- [165] "搞好没"（催促，非任务轮）
- [177] "我不是很理解 什么是沙箱 你直接在本地执行命令不就和我自己执行是一样的吗"（澄清沙箱概念，非任务轮）
- **结论**: 无干净 A-档提需求轮 → 本 case 走 **B 档（synthesized）**。

## 助手诊断与金标（trace 真实产物）
1. 探查 `/proj/drcoa/V0/ver/pex/johnl/T_IsmTop`（aether.rc symlink / cdlOut.log / asOut.log / lpe/T_IsmTop/cci_lvs.log / star_cmd_RCC / lpe_RCC.rule）。
2. `SPICE_SUBCKT_FILE` 指向 `T_IsmTop.cdl`（3575 行，155 个 .SUBCKT）。`lpe.log` 报 `Terminate LPE running due to CCI-LVS result is NOT Clean !!`；`layout_top.lvs.rep` 报 INCORRECT。
3. 写 `inspect_cdl.py` / `scan_body.py` / `top_analysis.py` / `top_body.py` / `trace_trim.py` / `block_headers.py` / `final_check.py` 逐层分析：
   - 全 CDL 中 `vbn!`/`vbp!` 出现 105 处；多数 buffer/inverter/nand/mux 实例用 `vbn! vcc! vcc! vss!`（体端）。
   - 关键：`T_IsmCntClkGen` 的 `vbn!` 端口在 `T_IsmTop` 实例化处被 fed `vss!`（line 3571 `... vss! vcc! vss! / T_IsmCntClkGen`）→ 其内部 buffer 体端实际在 vss!，**正确**。
   - `T_IsmTrim1/2` 同理被父层 fed vss!/vcc! → 正确。
   - **唯一 bug**：`T_IsmTop` line 3249 `XI37 JudgeN<8> JudgeN_buff vbn! vbp! vcc! vss! / bufLx4` — 全 CDL 唯一一个把体端接到 `T_IsmTop` 顶层**悬空** `vbn!`/`vbp!` 端口的实例。其相邻 XI324/XI325 已正确用 `vss! vcc! vcc! vss!`。
4. **修复** = 单行改写：`XI37 ... vbn! vbp! vcc! vss! / bufLx4` → `XI37 ... vss! vcc! vcc! vss! / bufLx4`。
   - `fix_cdl.py` 备份 `T_IsmTop.cdl.bak_vbnfix`，apply，`precise_diff.py` 校验：**仅 1 行差异**，line count 3575→3575，.SUBCKT/.ENDS 155→155，md5 不一致仅该行。
5. **RCC 二进制无法跑**：登录节点 `VCO=aok` vs calibre 构建为 `VCO=aoi`，`calibre -lvs` 报 `Current execution environment is VCO=aok. Software tree is for environment VCO=aoi.`；改用 `bsub -q star` 提交（Job 264761）成功提交，但 star 节点 LSF res 环境初始化脚本崩（`/lib64/libc.so.6` 版本问题）→ 仍无法跑。助手如实告知用户：CDL 修复完成并验证，RCC 需在 star 队列正确环境由 `runlpe.sh` 跑。

## 合成 fixture 设计（真实 /proj/drcoa permission-denied，按先例合成忠实复刻结构）
- **A = `T_IsmTop_A.cdl`**：顶层 `T_IsmTop`（悬空 `vbn!`/`vbp!` 端口）+ 1 个 buggy buffer `XI37 ... vbn! vbp! vcc! vss! / bufLx4` + 2 个正确 buffer XI324/XI325 + 子模块 `T_IsmCntClkGen`（局部 `vbn`/`vbp` 端口，被 root fed vss!/vcc!，内部 buffer 用局部端口→不是 bug）+ invLx1。buffer `bufLx4` 端口序 `A Y vbn vbp vcc vss`（体端在 pos 3,4）。
- **hidden B = `T_PllTop_B.cdl`**：不同 root `T_PllTop`、不同体端名 `vbnw!`/`vbpw!`、不同 buffer `bufLx8` 端口序 `A Y vcc vss vbnw vbpw`（体端在 pos 5,6，**位置不同于 A**）、**2 个 buggy** XI400/XI402 + 正确 XI401 + 子模块 `T_PllClkGen`（局部 vbnw/vbpw）+ invLx2。验泛化：候选须解析 buffer 端口表定位体端位置（不能假定固定 pos 3,4），且不得硬编码 A 专属名。

## case 落库
- task_id = `EDA-Eval-DesignFlow-CdlBodyMapFix-001`，domain=`pnr_signoff`，track=`synthesized`，level=`L2`。
- 交付件 = `fix_cdl.py`（CLI `python3 fix_cdl.py <in> <out> <report_json>`，解析 .SUBCKT → 找 root（不被实例化 + 含体端端口）→ 在 root 体内对 buffer 实例按 cell 端口表定位体端位置 → 若体端 arg == root 悬空体端端口则改写为对应 supply（vbn*→vss, vbp*→vcc）→ 备份 + diff_report.json + 良构校验）+ `T_IsmTop_fixed.cdl` + `diff_report.json`。
- check.py **15 条断言 (a)-(o)**：subprocess 在 A + 隐藏 B fixture 上跑候选 fix_cdl.py（§4.2 L2 结构判分，不跑 calibre/StarRC）。**k_rationale=15=k_check=15≥8 GATE PASS ✓**。
- 自验：reference_submit.zip → check() PASS 15/15；4 negative（fake_empty→(c) / fake_print_expected→(l) / fake_core_deleted→(d) / naive_hardcode_a→(l)）全 FAIL，NEG_SELFTEST NEG_RC=0 ALL-FAIL；§4.9 (a)(b)(c) 三假覆盖。
- 防泄题：资产仅 prompt+brief+A fixture（0 判分器/答案/隐藏/B）；hidden B 不进 SUT 沙箱；判分独立 /tmp，check.py+hidden 从 reference/ 复制；anti-hardcode (o) 防 T_IsmTop/JudgeN/bufLx4/XI37/vbn!/vbp! 硬编码。
