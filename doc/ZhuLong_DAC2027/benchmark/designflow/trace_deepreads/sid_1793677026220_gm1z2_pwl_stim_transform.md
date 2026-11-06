# trace deepread — sid 1793677026220_gm1z2 (hairuizh@hfeg0pkn002, 242 msgs, mc=193, spice_sim)

## 源
- session: `/home/hairuizh/.cline/data/sessions/1793677026220_gm1z2/1793677026220_gm1z2.messages.json`
- host: hfeg0pkn002 (10.129.2.11), scp 1.68MB, 242 msgs
- tools: 790 netlist / 502 schematic / 305 hspice → spice-dominant by absolute count (ratio 0.19 < 0.35 但绝对 hspice=305 高)
- 来自 11-05 19:28 fresh summary.tsv, 11-05 重扫令候选

## 用户轮（A-档选轮）
- **USER#0 (verbatim, A-档任务说明 = 本 case prompt)**:
  `@/proj/drcoa/V0/workdir/hairuizh/simulation/drcoa_array_XdecGapTop_DRCOA_schematic_ALPS/`
  1. 将该文件夹内的 inpattern_origin.pwl, 复制并改写为 inpattern.pwl；要求各 net 名称改成和文件夹内的 netlist 文件顶层信号所匹配的项；所有 pwl 波都需映射，记录映射关系
  2. 高电平接近 3.2 的信号，将其 PWL 的所有电压值都写成 x*pvwlp 的形式，比如 0.32 写成 '0.1*pvwlp'; 别忘了单引号；类似的，高电平接近 1.1V 的信号，所有值用 pvcc 表示
  3. pvwlp 的信号将所有值小于 0.1*pvwlp 的值改成 0，大于 0.9*pvwlp 的改成 pvwlp；pvcc 的也这样做
  4. 保留每一步的输出，分别命名为 inpattern_map.pwl, inpattern_map_vol.pwl, inpattern_map_vol_nonoise.pwl
  → **纯需求轮 ✓**（用户提出4步变换需求，未给根因/修复）
- USER#1 「继续」
- USER#2 修正映射: net22→PwrOn3Bot, fngidl_bga_b1→cm0_ro_GidlSec0, fngidlmode_bga_b1→cm0_ro_GidlModeSec0, cm0_ro_eblstrsentop_vdleq_l 删除
- USER#3 修正: cm0_ro_GidlModeSec0 应改成 cm1_ro_GidlModeSec0
- USER#4 补充 inpattern_origin_top.pwl（4个*Top信号），按流程加进 inpattern_map.pwl 等
- USER#5 第二个任务（不同路径 degnt, pvwlp/pvcc→pvintcore + *Bot 信号匹配 + 逻辑取反 + NO SOURCE MAPPING 标注）—— 不用，超出本 case 范围
- USER#6 *Top 信号全部删除
- USER#7 按 *** 注解设置 NO SOURCE MAPPING 信号

## assistant 工具链（关键）
- list_allowed_files / read_files(inpattern_origin.pwl, dump_pwl.tcl, netlist_org, netlist.mapping, XdecGapTop_DRCOA_io/_in/_out)
- editor 写 analyze_pwl.py（解析 PWL block: `Vname net 0 PWL(` + time-value 数据行）→ run_approved_command
- editor 写 cat_pwl.py / parse_io.py / parse_io2.py（分类 net family）
- ask_question（确认顶层信号命名约定）
- editor 写 transform_pwl.py（核心变换脚本）:
  - BOT_SINGLETONS dict（非 sec 单 net → *Bot camelCase）
  - BOT_BUS regex（_bga_b0<k> → *Bot<k>）
  - sec-family regex（cm0_ro_blcomensec<N> → cm0_ro_BLComEnSec<N>）
  - TOP_SINGLETONS（far_b02 → *Top）
  - SKIP set（cm0_ro_eblstrsentop_vdleq_l 删除）
  - rail 分类（RAIL_PVWLP=3.2 / RAIL_PVCC=1.1，按观测 max）
  - fmt_factor(v/rail, ".10g")
  - 4 输出: inpattern.pwl(abs) / inpattern_map.pwl(abs) / inpattern_map_vol.pwl('factor*rail') / inpattern_map_vol_nonoise.pwl(clip)
  - inpattern_map.txt（映射记录 src→tgt+rail）
- verify*.sh 验证 block count / 映射 / 裁剪 / 残留 token

## 金标准
- USER#0 的 4 步变换 = 可复用子流。trace 末尾用户持续修正映射并接受 assistant 产物（inpattern_map.pwl 等 4 文件 + inpattern_map.txt）。
- 本 case 抽取 **USER#0 verbatim** 作为 A-档任务说明，金标准 = 按4步规则变换后的 4 个 PWL 文件 + 映射表。
- 为可判分化简：net 映射表作为 asset 显式提供（net_mapping_A/B.json），rail 配置显式提供（rails.json），候选只需 parse+rename+classify+param+clip+write，不需猜测 camelCase 规则。
- L2: check.py 真跑 HSPICE 于 B 的绝对值 inpattern_map.pwl + dummy-load stub → job concluded。

## case 合成
- case_id: EDA-Eval-DesignFlow-PwlStimTransform-001
- domain: spice_sim, track: faithful, layer: L2
- A: inpattern_origin_A.pwl(8 block: 4 pvwlp~3.2 + 4 pvcc~1.1), net_mapping_A.json, rails.json(pvwlp=3.2/pvcc=1.1)
- hidden B: inpattern_origin_B.pwl(8 block, 不同 net/值), net_mapping_B.json, rails_B.json(pvwlp=2.5/pvcc=0.9) → 强制运行时读 rail
- 交付: pwl_stim_transform.py <src> <map> <rails> <out> → 4 PWL + txt + submit.zip
- reference: pwl_stim_transform_ref.py + check.py (k=12 a-l) + negative/(empty/print_expected/hardcode_a/no_clip/wrong_rail) + negative_selftest.py + reference_submit.zip
- 自验: ref 12/12 (本地 11/12 + .75 HSPICE k PASS job concluded), 5 negative 全 FAIL (NEG_RC=0), §4.9 三假全 FAIL
- 断言闸门: k_rationale=k_check=12≥8 ✓
