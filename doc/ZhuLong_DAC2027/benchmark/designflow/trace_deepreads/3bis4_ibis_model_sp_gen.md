# Deepread: 1795055873026_3bis4 (alan17z @ hfeg0pkn004)

- **sid**: 1795055873026_3bis4
- **user/host**: alan17z / hfeg0pkn004
- **match_count**: 167 (netlist:379; hspice:228; cmos:15; .spi:7; schematic:6 — netlist+hspice dominant, B-domain spice_sim)
- **trace size**: 261 msgs / 1019338 B
- **fetched**: r892 via eda_flow ssh cat (subdir path `.../<sid>/<sid>.messages.json`)
- **case**: EDA-Eval-DesignFlow-IbisModelSpGen-001 (reframe: spec-driven DQ-driver model .sp generator)

## 用户真实意图（按 msg 顺序）

- **[0]/[1] Context summary + act**: 合并 3 个 IBIS 抽取相关 skill（`ibis-t2b-gen` / `ibis-zq-calib` / `ibis-zq-sim-gen`）为一个端到端 skill `ibis-extract`，实现 source → t2b 交付完整自动化（hspice 直接跑 ZQ 校准，t2b 用户手工抽取）。状态汇报：新 skill 已建（SKILL.md + 7 scripts），run_sims.py 用 `LD_PRELOAD= bsub` 绕开 agent 旧 libstdc++ 注入，gen_t2b.py 参数化生成 4 t2b 配置实测逐字节一致，ZQ 校准 6 码误差 ±0.34Ω。
- **[2] act**: 「删了旧目录，流程符合预期，验证文件在 AI_verify 中，从 0 开始完整验证，不依赖之前记忆，完全利用 skill」
- **[44] act**: 「corner 文件之前没给，现已补充，把生成的 zq 校准文件都删了，从头重新验证」
- **[149] act**（关键 reframe 锚点）: 「生成的模型文件（odtoff.sp 等）格式和内容有问题，参考文件已放 t2b_extraction。**核心就是 CIO 和 ODT 下仍然需要配置驱动管电压，只是为 0**；然后格式也统一一下」
- **[214] act**: boostoff 下电压配置也有问题（stimulus 里定义了 VDATAFOOTEREN/VVFOOTOUTEN* 等，top 文件要对应）
- **[229] act**（gen_top 逻辑）: 「gen_top 逻辑可能有问题，核心是 **top 文件中的电压要跟 stimulus 中的对应**，不是单纯 footer 使能行；初步模板只要 stimulus 中的电压在模板中已定义就不用管，没定义就要在 top 文件中补充」

## 关键产物（真实参考 .sp 文件，自 .75 /rundata/SIPI 抓取）

`odtoff.sp` (16 行, 263B):
```
** Drive Strength Setup **
.param pdqpudrv2	=0
.param pdqpudrv1	=0
.param pdqpudrv0	=0

.param pdqpddrv2	=0
.param pdqpddrv1	=0
.param pdqpddrv0	=0


** ODT Setup **
vodten			odten			0	dc='1*pvcc'
.param podt2		=0
.param podt1		=0
.param podt0		=0
```

`odt40.sp`: 同结构，podt2/1/0 = 1/1/1（drive 仍 =0，vodten 仍 =1*pvcc）
`pu40_pd40.sp` (boost/Tx): drive =1，vodten dc='0*pvcc'，podt2/1/0 = 1/1/1
`odt240.sp`: drive =0，podt = 0/0/1

**两段式布局 + mode-driven drive_strength + mode-driven vodten_dc + per-file podt 三位** 是核心可断言核。

## 为什么 reframe（不可便携性证据）

- 真实流程依赖 `/rundata/SIPI/alanzhang/SI/1_IBIS_extract/AI_verify/` 内网 PDK 文件（model.sp / incFile_lp / incFile_G5_CIP / netlist / RCC / corner.txt）
- hspice 跑 ZQ 校准需 `bsub -q SIPI "source /rundata/SIPI/setup.sh; hspice ..."` 提交 6 作业，绕开 agent `LD_PRELOAD` 污染
- 261 msgs 的 skill-merge + multi-round-fix 流程不可整体移植
- **可移植核**：模型 .sp 文件格式是纯文本、确定性 I/O（spec → .sp），可参数化为生成器，判分牙来自逐字段独立复算 + 反硬编码 A + anti-stub B2

## reframe 形态

script-build portability-reframe 第四例（r889 skill 生成器 / r890 plan-HTML 生成器 / r891 metric-dir 生成器 / r892 model-.sp 生成器）：
- 输入 spec.json（label / mode / podt 三位）
- 输出 <label>.sp（两段式 + mode-driven drive_strength + vodten_dc + per-file podt）+ manifest.json
- check.py 在隐藏 spec_B（结构性反向：boost + 4 files + 不同 podt + 不同 label）和 anti-stub spec_B2 上真跑生成器，逐字段解析 + 独立复算 + 反硬编码 A + 确定性 3-run sha256

## k_check / k_rationale

k_check = k_rationale = 16（a-p）：a 候选存在 / b 4 文件生成 / c drv 头 / d odt 头 / e pdqpudrv==mode drive / f pdqpddrv==mode drive / g vodten_dc==mode / h podt==spec / i vodten 行格式 / j .param 可解析 / k 反硬编码 A (boost drive==1) / l anti-stub B2 / m 确定性 3-run / n py_compile / o manifest 4 label / p 文件名 == <label>.sp

## 自验

- ref 16/16 PASS（本地 + .75 双跑）
- 5 neg（empty / print-A / hardcode-A / core-deleted / always-pass）全 FAIL → NEG_RC=5/5
- 确定性 3-run sha256 一致（修正 manifest 不写绝对路径后通过）
