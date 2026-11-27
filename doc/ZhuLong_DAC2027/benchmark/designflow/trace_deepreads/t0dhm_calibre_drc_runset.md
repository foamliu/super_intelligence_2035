# Deepread: 1795395353963_t0dhm — felixw Calibre/Argus DRC via runset on Aether

- **session**: `1795395353963_t0dhm.messages.json` (28.9 MB, 338 msgs, 175 user turns)
- **user/host**: felixw @ hfeg0pkn004
- **match_count**: 399 · **domain**: physical_verify (C shard)
- **keywords**: drc:8630 calibre:1187 pdk:500 aether:167 pyaether:109 lvs:62 .gds:165 lib.defs:108
- **tools used**: SandBox_MCP_Server__run_code×81, editor×31, read_files×30, run_approved_command×17
- **claimed**: r1451 (2026-11-28), ledger row `1795395353963_t0dhm.messages.json felixw hfeg0pkn004 399 physical_verify claimed`
- **status**: DEBT — deepread done 2026-11-28 r1451, case synthesis pending (next round)

## 真实用户意图（一句话）

在 Aether 平台上把指定 cell 的 layout stream out 成 GDS，用 calibre（及 argus）通过 **runset** 方式跑 DRC（而非命令行拼 rule），修好 runset 字段并丢 LSF 运行，最后把整套流程沉淀成 skill.md + HTML 培训文档给其他 tool owner。

## 用户逐轮意图（U0–U10+）

| # | 用户要什么 |
|---|---|
| U0 | 跑 calibre DRC，产物放 `/proj/drgqx/V0/agentdir/felixw/DRC_test`；cell=`test1`@lib`A_felixw_test`；先用 `asOut` stream out GDS（`asOut -lib $lib -cell $cell -view $view -gds $gds -logFile … -convertPinTo geometry`） |
| U1-2 | 提供 runset 文件 + calibre DRC rule；runset 通过 aether DM python console `leGlobalVariables.projRunsetPath` 取 runset path，用其下 `drcRunset.sh` 生成真正的 drcRunset 文件，输出到 DRC 运行目录 |
| U3 | **纠正 runset 字段**：① 用 `-runset` 方式跑 DRC（不是命令+rule）；② `drcLayoutPath` 错→应 `drcLayoutPaths`；③ 新增 `drcRunDir`（值=运行路径）；④ `drcLayoutGetFromViewer`/`drcLayoutPrimary` 保留 |
| U4 | 为什么 DRC job 不能丢 LSF？给原因+方案。用户在 debug 目录验证 `calibre -gui -drc -runset drcRunset -batch` 可丢 LSF 跑通 |
| U5 | 把「抽 gds → calibre -gui -drc -runset -batch → 丢 LSF」总结成 `skill.md` 放 DRC_test 目录 |
| U6 | 同样流程换 **argus** 跑 DRC：运行路径 `DRC_test_argus`（权限 775），runset 用 `argus_Runset.sh` 生成 `argus_drcRunset` |
| U7 | 继续进行（argus 流程） |
| U8 | 把 argus DRC 内容补进既有 `skill.md` |
| U9 | 整理成 HTML 培训文档（目标：给其他 tool owner 做分享，开发并迭代 skill 让 agent 调 EDA 工具） |
| U10 | 用 argus rule 在 `DRC_test_argusrule` 目录跑对照实验 |

## 关键技术细节（run_code 命令序列）

1. **GDS stream-out**: `asOut -lib A_felixw_test -cell test1 -view layout -gds test1.gds -logFile strmOut.log -convertPinTo geometry`
2. **lib.defs 定位**: `find /proj/drgqx -name lib.defs -maxdepth 4`；`A_felixw_test` 定义在 `/proj/drgqx/V0/lib.defs`
3. **runset path**: `leGlobalVariables.projRunsetPath` → `/apps/imctf/cad/runset/drgqx/v0`
4. **drcRunset.sh**: 读 `/apps/imctf/cad/runset/drgqx/v0/drcRunset.sh`，执行后生成 `drcRunset` 文件
5. **runset 字段修正**（用户硬纠正，case 判分核心）:
   - `*drcRulesFile: .../calibreDRC.rule`
   - `*drcLayoutView: layout`
   - `*drcLayoutPrimary: test1`
   - `*drcLayoutPaths: /path/to/test1.gds`  ← 必须是 Paths（复数），用户纠正点
   - `*drcRunDir: /proj/drgqx/V0/agentdir/felixw/DRC_test`  ← 用户要求新增
   - `*drcLayoutGetFromViewer: ...`（保留）
6. **calibre batch 调用**: `calibre -gui -drc -runset drcRunset -batch`（cwd=DRC_DIR）
7. **LSF 提交**: bsub 包装上述 calibre batch 命令
8. **argus 平行流程**: `argus_Runset.sh` → `argus_drcRunset`；argus rule 对照实验在 `DRC_test_argusrule`

## 交付物候选（case 合成方向）

**任务形态**：给 agent 一个 cell（lib/cell/view）+ 一份 calibre DRC rule 模板 + runset 生成脚本（drcRunset.sh），要求产出：
1. 一个 Python 编排脚本 `run_calibre_drc.py`，能够：
   - 调 `asOut` stream out GDS（或给定 GDS）
   - 执行 `drcRunset.sh` 生成 drcRunset
   - **修正 runset 字段**：`drcLayoutPaths`（复数）、`drcRunDir`、`drcLayoutPrimary`、`drcLayoutView`、`*drcRulesFile`
   - 以 `calibre -gui -drc -runset <runset> -batch` 运行
   - 解析 DRC 结果（results db / summary），输出结构化 JSON（规则名×违例数×坐标）
2. LSF 提交脚本 `submit_drc_lsf.sh`（bsub 包装）
3. `skill.md` 流程文档

**判分核心（check.py ≥8 断言方向）**：
- runset 文件存在且字段齐全
- `*drcLayoutPaths`（复数 s）正确——拼成 `drcLayoutPath` 必 FAIL（用户硬纠正点）
- `*drcRunDir` 存在且=运行目录
- `*drcLayoutPrimary` = 顶层 cell 名
- `*drcRulesFile` 指向给定 rule
- batch 调用形如 `calibre -gui -drc -runset … -batch`（解析脚本里的 subprocess 调用，不能缺 `-batch`/`-runset`）
- LSF 脚本含 `bsub` 且包装的是上述 calibre batch 命令
- DRC 结果解析：能在 mock/真实结果 db 上抽出「规则名→违例计数」结构（不是文本相似）
- 随机化：在 hidden B 上换 cell 名/路径，3 seed 结论一致

**真跑候选**：calibre 在 .75 PATH（`/apps/mentor/calibre/2020.1_36/.../bin/calibre`），可走 L2.live——check_live 在 .75 跑候选脚本对真实 GDS+rule 抓 DRC 结果结构。需确认 .75 有可用的 calibreDRC.rule + 一个小 GDS（可用 pyAether 建 OA layout stream out，参考 OaLayoutM1RectEdit-001 的 techSetTechLibName 法挂 018um_PDK tech.db）。

**负样本方向**：
- naive: 只 print 期望的 runset 字段串，不实际生成文件
- always-pass stub: runset 写对形状但 `drcLayoutPath`（单数，用户纠正的错误形）
- 删核心: 缺 `drcRunDir` 字段

## 溯源

- `metadata.trace_source = {user:"felixw", host:"hfeg0pkn004", session_file:"1795395353963_t0dhm.messages.json", match_count:399, real_task_summary:"在 Aether 平台 stream out GDS 后用 calibre/argus 通过 runset 方式跑 DRC（修正 drcLayoutPaths/drcRunDir 字段）、丢 LSF 运行，并沉淀 skill.md+HTML 培训文档"}`
- 不脱敏：路径 `/proj/drgqx/V0/agentdir/felixw/...`、用户名 felixw、runset path `/apps/imctf/cad/runset/drgqx/v0` 全保留

## 下轮 ETA

r1452 合成 `EDA-Eval-DesignFlow-CalibreDrcRunset-001`：assets（mock GDS + calibreDRC.rule 模板 + drcRunset.sh 桩）、hidden B（换 cell/路径）、reference 参考解、negative×3、check.py（≥8 断言 + check_live）、SKIP_RUN 自验 + .75 L2.live 实跑。
