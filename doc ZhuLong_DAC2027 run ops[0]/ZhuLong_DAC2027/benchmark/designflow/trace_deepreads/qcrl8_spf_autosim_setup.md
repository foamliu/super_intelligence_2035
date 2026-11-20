# trace_deepread: qcrl8 — SPF/autosim setup for 2P PEX M4B4/M4B1

- **session**: `1794529802472_qcrl8` · user `e0046686` · host `10.129.2.14` · mc=189
- **ts**: 2026-11-13 · 125 msgs / 760KB · agent `lead` (glm-5.3-flash)
- **keywords**: pex:2205;netlist:404;lvs:343;calibre:89;virtuoso:87;.gds:61;hspice:58;.def:32
- **deepread 轮**: r524 (2026-11-14) · **修正 r506-r523 七连 0-case 的误判**（qcrl8 被标 "cross-domain-tool inflation (PEX/LVS=C域)" 实为 **B域 characterization**）
- **claim**: ledger_B 已 claim (characterization) · 待合成（DEBT:1，下轮第一件事交付）

## 1. 用户原话（msg[0]）
`<user_input mode="act">按照TASK_EXTRA_SPF_M4B4.md分析执行</user_input>`

## 2. 任务文件 TASK_EXTRA_SPF_M4B4.md（msg[4] read_files 原文）
```
现有：拿的cad那边发的pex目录，在terminal跑的抽取2P的M4B4和M4B1在多个pvt下的spf，运行目录：
/proj/lacaa/TV1_FS/workdir/zlhou/2prf_work/pex/pex420/pex1024x72

对应工具或需要的额外参数：
Rev07的PEX已经发布了，经过测试可以正常使用。请使用廖建文路径下的lvs runset和PEX deck进行抽取，使用工具为GloryEX_2026.06_P010
配置路径：
/proj/lacaa/TV1_DBC_Virtuoso/workdir/jianwenl/simulation/current/pex_20261030/35H_PEX_FS_V0d1_Rev07_20261030/GloryEX_20261030_V0d1_Rev07_TYP/FS/
工具版本：
module load /rundata/lacaa/TV1_DBC_Virtuoso/simdir/finesim/workdir/jianwenl/simulation/current/glory_package/2026.06_P010

参考这个信息，如果在autosim工具下跑相同仿真，应该使用的入参是那些？如MeasureFile、TemplateFile、TimingTransition、PVT、Param这些；
以及autosim_script/spf_extractor/config/spf_extractor_config.json中涉及的fs_dir、dbc_dir、lvs_rule等入参应该如何配置，从已经跑的case中如何复制或复用；

先分析拆解，review确认后再执行
```

## 3. assistant 工具链（125 msgs）
list_allowed_files(project) → read_files(TASK.md) → list(autosim_script) → list(spf_extractor) →
read(spf_extractor_config.json / spf_extractor.py) → list(pex420/pex1024x72) →
read(cmd_param.log / run_pex.sh / run_lvs.sh / gxrc_cci_cmd) → list(pex420) → 找到 M4B1=pex32x72 →
read(AutoSim使用说明.md) → list(2prf_work/autosim) → read(temp.sp / autosim.cfg) →
read(spice_tools 默认配置) → list(jianwenl Rev07_TYP/FS) → read(sp_config.py resolve 逻辑) →
**合成** setup_2p_pex420.py (494 行, 幂等 patch) → run_approved_command → **60 OK / 0 FAIL** →
read 复核 spf_extractor_config.json / extract_spf.sh / PVT_LIST / instances.csv / config_path_M4B1

## 4. 交付物（reference truth，msg[119-123] readback 原文）

### 4a. spf_extractor_config.json 关键 patch（9 处替换）
```json
{
  "corner_map": {"tt":"TYP","ff":"CMAX","ffgnp":"CMAX","ss":"CMIN","sf":"RCMIN","fs":"RCMAX"},
  "fallback_corner": "TYP",
  "pex_config": {
    "version": "V0", "mode": "RC",
    "fs_dir":  "/proj/lacaa/TV1_DBC_Virtuoso/workdir/jianwenl/simulation/current/pex_20261030/35H_PEX_FS_V0d1_Rev07_20261030/GloryEX_20261030_V0d1_Rev07_TYP/FS/",
    "dbc_dir": "/rundata/lacaa/TV1_FS/simdir/finesim/workdir/peinie/pex_rule/DBC/",
    "lvs_rule":"35H_1P18M_18F1xa1x1xb1ya6y2yy2yx2z_LVS_Cal_V0d1_Rev06_Test08.lvs",
    "pin_file":     "CCI_Flow_for_CUI/35H_FS_PEX_GloryEX_V0d1_Rev07_device_pin_file",
    "query_cmd":    "CCI_Flow_for_CUI/query_cmd",
    "tran_map":     "CCI_Flow_for_CUI/35H_FS_PEX_GloryEX_V0d1_Rev07_tran.map",
    "hcell_list":   "CCI_Flow_for_CUI/hcell_list_V0d1_Rev07",
    "gxrc_cci_cmd": "CCI_Flow_for_CUI/gxrc_cci_cmd_V0d1_Rev07",
    "camx_captab_name":    "/apps/imctf/cad/runset/lacaa/tv1_fs/current/lpe_gxrc/GloryEX_20261106_V0d1_Rev07_3Corner/FS/CAPTAB/35H_FS_PEX_GloryEX_Encrypted_V0d1_Rev07_CMAX_ccworst.captab",
    "typical_captab_name": "CAPTAB/35H_FS_PEX_GloryEX_Encrypted_V0d1_Rev07_TYPICAL.captab",
    "cmin_captab_name":    "/apps/imctf/cad/runset/lacaa/tv1_fs/current/lpe_gxrc/GloryEX_20261106_V0d1_Rev07_3Corner/FS/CAPTAB/35H_FS_PEX_GloryEX_Encrypted_V0d1_Rev07_CMIN_ccbest.captab"
  },
  "gds_tiler_compilers": {"prefix":"MY_SRAM","sep":"[","leaf_gds_cfg":"config/LEAF_GDS.cfg",
    "compilers":{"1P":"gds_tiler_for_CAD/1.py","2P":"gds_tiler_for_CAD/1.py","SP":"gds_tiler_for_CAD/1.py"}}
}
```

### 4b. PVT_LIST（6 PVT = 3 corner × 2 temp，映射 terminal corner_file）
```
*** PVT corner list (PROCESS_VDDP_VDDC_TEMP)
*** 2P pex420 SPF/postsim: 3 PEX corner x 2 temperature (= terminal corner_file 6 corners)
*** corner_map: tt->TYPICAL, ff->CMAX_ccworst, ss->CMIN_ccbest
***   tt_0p75v_m40c  -> TYPICAL_-40      captab: ...Rev07_TYPICAL.captab
***   ff_0p75v_m40c  -> CMAX_ccworst_-40 captab: ...Rev07_CMAX_ccworst.captab
***   ss_0p75v_m40c  -> CMIN_ccbest_-40  captab: ...Rev07_CMIN_ccbest.captab
*** vdd in name is nominal 0.75V (PEX itself is voltage-independent)
***
tt_0p75v_m40c
tt_0p75v_125c
ff_0p75v_m40c
ff_0p75v_125c
ss_0p75v_m40c
ss_0p75v_125c
```

### 4c. instances.csv（2 实例 = M4B4 1024x72 + M4B1 32x72）
```
Instance,Vt,Process,OutputPath,Netlist,Vector
CXN4HC2PS1024X72M4B4C1R1W1BW1RE1_FS,SVT,FS,/rundata/.../project/2p-pex420/output_spf,,
CXN4HC2PS32X72M4B1C1R1W1BW1RE1_FS,SVT,FS,/rundata/.../project/2p-pex420/output_spf,,
```

### 4d. config_path_M4B1_32x72.txt（派生变体，$nw=1024→32, $bk=4→1）
```
$cm = 4
$bk=1
$nw=32
$nb=72
$cd=1
$cr=0
$rck_lbit=$cm/2
$rck_hbit=$cm/2+1
```

## 5. 域归属裁定（关键 · 修正 r506-r523 误判）
- **B域 (characterization) ✓**：任务是「terminal PEX 流 → autosim 入参/config 映射」，属 SPICE 表征流程编排（SPF=Standard Parasitic Format 是 FineSim 后仿的寄生输入）。pex:2205 高是因为 PEX 是表征子步骤（抽寄生 → 喂 FineSim sim），**不是** C域 physical_verify（C域是 DRC/LVS signoff 本身）。
- r516 (fj41f STC CRF) 先例已证：PEX-heavy characterization 案例可便携 L2 交付。
- **r506-r523 七连 0-case 的根因**：只用 keyword ratio 判域，把 PEX 一律归 C，漏掉 PEX-as-characterization-substep 的 B 域案例。**filter 缺陷**（见 discuss 建议：domain-tool-ratio threshold 须区分 "PEX-for-sim" vs "PEX-for-signoff"）。

## 6. case 设计（下轮合成 · 便携 L2 · A 档 trace-faithful）

**case_id**: `EDA-Eval-DesignFlow-SpfAutosimSetup-001` · domain=characterization · L2

**prompt（A 档 trace-faithful，用真实用户原话）**:
> 按照 TASK_EXTRA_SPF_M4B4.md 分析执行：参考 terminal 跑的 2P PEX M4B4/M4B1 多 PVT SPF 抽取（运行目录见 task），如果在 autosim 工具下跑相同仿真，应使用的入参（MeasureFile/TemplateFile/TimingTransition/PVT/Param）以及 spf_extractor_config.json 中 fs_dir/dbc_dir/lvs_rule 等如何配置。写一个 setup 脚本，读入 task 文件 + spf_extractor_config.json 模板 + terminal PEX run 信息，生成 PVT_LIST、instances.csv、patch 后的 spf_extractor_config.json、config_path 变体，打包 submit.zip。

**Input A（visible, assets/<id>/）**:
- `TASK_EXTRA_SPF_M4B4.md`（真实 task 原文）
- `spf_extractor_config.json`（patch 前模板：fs_dir 为旧值/placeholder，pin_file 等无 CCI_Flow_for_CUI/ 前缀，captab 为旧 Rev06 路径）
- `terminal_pex_info.json`（pex420 目录结构：5 个 M4B4 实例 + pex32x72=M4B1；cmd_param.log 关键参数；corner_file 6 corners = TYPICAL/CMAX_ccworst/CMIN_ccbest × -40/125；instance 命名 CXN4HC2PS{NW}X{NB}M4B{B}C1R1W1BW1RE1_FS）
- `autosim_param_spec.md`（AutoSim 使用说明节选：PVT 格式 PROCESS_VDDP_VDDC_TEMP、corner_map 语义、instances.csv schema、config_path 派生规则 $bk=M4B 数、$nw=字宽）

**Hidden B（assets/<id>/hidden/, 不进 SUT 沙箱）**:
- 不同 project：`TV2_DBC`（替换 TV1_FS）· 不同 Rev：`Rev08` · 不同 jianwenl 路径变体
- 不同实例：M4B2 512x8 (`CXN4HC2PS512X8M4B2C1R1W1BW1RE1_FS`) + M4B1 8x16 (`CXN4HC2PS8X16M4B1C1R1W1BW1RE1_FS`)
- 不同温度：`-40/85`（替换 -40/125）· 不同 VDD：`0p80v`（替换 0p75v）
- 不同 corner 包：`GloryEX_20261120_V0d1_Rev08_3Corner`
- OutputPath 用 B 的 project 路径

**deliverable**: `outputs/submit.zip`{`setup_spf_autosim.py`（生成器，读入输入目录，产出 4 类文件）}

**check.py（双参 check(deliverable, workdir)，subprocess 真跑候选 on B）· k=12 断言**:
1. zip 内含 `setup_spf_autosim.py` 可执行
2. 在 B 输入目录跑生成器，产出 `PVT_LIST` 文件存在
3. PVT_LIST 含 6 行 PVT（3 corner × 2 temp，B 的温度 85 替换 125）
4. PVT_LIST corner→PVT 映射正确（tt→TYPICAL, ff→CMAX_ccworst, ss→CMIN_ccbest）
5. PVT_LIST VDD 名为 B 的 0p80v（不硬编码 A 的 0p75v）
6. 产出 `instances.csv` 存在且 header = `Instance,Vt,Process,OutputPath,Netlist,Vector`
7. instances.csv 含 2 行 = B 的 2 实例名（512X8M4B2 + 8X16M4B1），不出现 A 的 1024x72/32x72
8. instances.csv Vt=SVT, Process=FS, OutputPath 含 B 的 project 路径
9. patch 后 `spf_extractor_config.json` 的 fs_dir 指向 B 的 Rev08 FS/ deck 路径
10. spf_extractor_config.json 的 pin_file/query_cmd/tran_map/hcell_list/gxrc_cci_cmd 均带 `CCI_Flow_for_CUI/` 前缀
11. spf_extractor_config.json 的 camx/cmin_captab_name 指向 B 的 3Corner 包 Rev08 captab（绝对路径），typical_captab_name 为相对 `CAPTAB/...Rev08_TYPICAL.captab`
12. **cross-input guard**：把生成器在 A 输入上重跑，产出 A 的正确值（1024x72/32x72, 0p75v, m40c/125c, Rev07）—— 证明未写死 B

**test_rationale（k=12 条断言）**:
`12 条断言：① zip 含 setup_spf_autosim.py 可执行 ② PVT_LIST 文件存在 ③ PVT_LIST 含 6 行 PVT（3 corner×2 temp，B 温度 85） ④ PVT_LIST corner→PVT 映射 tt→TYPICAL/ff→CMAX_ccworst/ss→CMIN_ccbest ⑤ PVT_LIST VDD 名=B 的 0p80v 非写死 ⑥ instances.csv 存在且 header 正确 ⑦ instances.csv 2 行=B 实例(512X8M4B2+8X16M4B1)非 A ⑧ instances.csv Vt=SVT/Process=FS/OutputPath 含 B 路径 ⑨ spf_config fs_dir=B Rev08 FS/ deck ⑩ spf_config 5 个 CCI 键带 CCI_Flow_for_CUI/ 前缀 ⑪ spf_config camx/cmin_captab=B 3Corner Rev08 绝对路径 + typical 相对 CAPTAB/ ⑫ cross-input guard：A 重跑得 A 正确值(1024x72/0p75v/m40c-125c/Rev07) 证未写死`

**negative（reference/<id>/negative/, ≥2 错解 + negative_selftest.py 全 FAIL）**:
- `fake_empty.py`（产出空文件）→ FAIL ②③⑥⑦
- `fake_hardcode_a.py`（写死 A 的 1024x72/0p75v/Rev07）→ FAIL ⑦⑧⑨⑪⑫
- `fake_print_expected.py`（只 print 期望串不写文件）→ FAIL ②⑥

**§4.9 三假提交**: (a) 空壳 zip → FAIL ①②; (b) 只 print 期望串 → FAIL ②⑥; (c) ref 删 config_path 生成段 → FAIL ⑫(partial) 或缺 config_path

## 7. 便携性裁定
- 全文本/config，**无需 EDA license**（不跑 calibre/gxrc/finesim，只生成 config + PVT/instance 清单）→ L2 便携 ✓
- 真实绝对路径保留（§1 不脱敏），Input A 用真实路径，Hidden B 用真实风格但取值全异（不同 project/Rev/实例/温度/VDD）
- 难度：参数映射 + 路径解析 + 派生规则（$nw/$bk），需理解 corner_map 语义 + config_path 派生 → 中等，符合 B 档 20-30% 目标

## 8. 下轮执行清单（合成，≤25 min）
1. 建 `assets/EDA-Eval-DesignFlow-SpfAutosimSetup-001/`：TASK.md + spf_config 模板(patch前) + terminal_pex_info.json + autosim_param_spec.md
2. 建 `hidden/`：B 变体 4 文件 + hidden_manifest.json
3. 写 `reference/.../setup_spf_autosim.py`（ref 生成器）+ `check.py`（12 断言）+ `negative/`（3 错解 + selftest）
4. 自验：ref on B → 12/12 PASS；§4.9 三假 FAIL；negative_selftest 全 FAIL
5. jsonl 追加 EDA-Eval-DesignFlow_B.jsonl + ledger mark case
6. 删 DEBT:1
