# Deep-read: sid 1786014142309_pgaur — PG flow runDir/workDir 默认值

- **trace**: `1786014142309_pgaur` (e0014566 @ hfeg0pkn005, mc=129, 74 msgs, 677KB)
- **domain**: pg_layout (RsCalc + AutoVia + PowerFill 电阻优化 flow)
- **scanned**: 2026-11-07 shard C round 190
- **case**: EDA-Eval-DesignFlow-PgRundirDefault-001 (A-档 faithful, L1-boundary)

## 项目结构
`/home/e0014566/test_layout_rscalc_flow_7/` 包含三个 virtuoso runner：
- `virtuoso-rscalc-runner/` — 电阻计算（rscalc），assets/run_rscalc_nogui.il
- `virtuoso-autovia-runner/` — 自动加 via（autovia），assets/run_autovia_nogui.il
- `virtuoso-powerfill-runner/` — power fill cell 生成，assets/run_powerfill_nogui.il
- 顶层：rscalc.config / run_autovia_config.il / run_powerfill_config.il / common.config / adaptive_tuner.py / prompt_flow.md / gen_final_report.py

## 用户原话（msg#0，逐字，A-档 intent seed）
> 我看配置文件里面都有个 wordir rundir 这样的东西，配置起来比较麻烦，能不能每个给定一个合适的默认值。参考rscalc.config

纯需求表达，未指根因未给修复 → 合格 A-档 seed。

## 真实问题
三个配置文件的 `runDir`/`workDir` 原硬编码用户特定路径：
- `rscalc.config`: `runDir = "/proj/train/AI_Virtuoso/ver/rscalc/e0014566"`
- `run_autovia_config.il`: `runDir = "/proj/train/AI_Virtuoso/ver/autovia/austin_rscalc2/testa"`
- `run_powerfill_config.il`: `workDir = "/proj/train/AI_Virtuoso/workdir/e0014566"`（getWorkingDir 替代）

换用户/项目时必须手改，配置麻烦。`rscalc.config` 已有「留空 (`""`) 即用默认值」模式（pwrNets/metalOption 等可选参数），用户要求 runDir/workDir 也照此办理。

## assistant 真实修复（trace msg#41-73）
1. **配置文件**：3 个 runDir/workDir 改为 `""`（msg#42-44 editor diffs）
2. **SKILL nogui 脚本**：3 个脚本加 `unless(runDir == "" ...)` 默认逻辑（msg#45 editor）
3. **prompt_flow.md**：bash 段加 `if [ -z "$RSCALC_RUNDIR" ]; then ... fi` 空值回退（msg#46-48）
4. **adaptive_tuner.py**：
   - 加 `_read_config_value(config_path, param)` helper（正则匹配 `param = "value"`，返回去引号值或 None）
   - main() 中 `rscalc_run_dir` 空时按公式 `/proj/<project>/<version>/ver/rscalc/<USER>` 计算默认（project←common.config, version←rscalc.config 回退 v0, USER←$USER）（msg#50, 596-607）
   - 加 `_read_config_value(ccfg, "cellName")` 取 cell 名（msg#50, 610）
5. **SKILL.md**：3 个 runner 的参数表更新 runDir/workDir 默认值说明（msg#51-52）
6. **验证**（msg#57-71）：
   - `py_compile` adaptive_tuner.py 语法 OK
   - 3 个 generator（gen_rscalc_agent.py / gen_autovia_agent.py / gen_powerfill_agent.py）用空 runDir 跑通，产出的 agent .il 含默认逻辑（`getShellEnvVar("USER")` 等）
   - `_read_config_value` 默认计算：project=train, version=AI_Virtuoso, USER=e0014566 → `/proj/train/AI_Virtuoso/ver/rscalc/e0014566`（与原硬编码值一致 ✓）
   - bash 空值回退逻辑跑通

## 默认公式（gold）
| 工具 | 参数 | 公式 | 回退 |
|------|------|------|------|
| rscalc | runDir | `/proj/<project>/<version>/ver/rscalc/<USER>` | version→v0, USER→unknown, project→"" |
| autovia | runDir | `/proj/<project>/autovia/<libName>/<cellName>` | project/libName/cellName←common.config |
| powerfill | workDir | `<CWD>` | --cwd 或 os.getcwd() |

## case 设计（L1-boundary）
- **候选**: `resolve_rundir_defaults.py`（纯 stdlib），CLI `python3 resolve_rundir_defaults.py <config_dir> [--user <USER>] [--cwd <PATH>]`，stdout 输出 JSON `{rscalc:{runDir,source}, autovia:{runDir,source}, powerfill:{workDir,source}}`
- **可见 A**: 4 个真实配置文件（runDir/workDir 全空，触发默认）
- **隐藏 B1**: project=ddgoa, version=TapeoutV2, lib=pg_analog_blk, cell=vref_buf_top；rscalc 空→默认, autovia 非空→原样, powerfill 空→CWD（混合测全路径）
- **隐藏 B2**: project=iejoad, 无 version 键→v0 回退, USER 未设→unknown 回退；三工具全空→全默认（边界）
- **判分 14 条 ①–⑭ a–n**: zip+py_compile+stdlib+无 B 字面量(a) / B1 rscalc 默认(b) / B1 autovia 原样 source=config(c) / B1 powerfill CWD(d) / B2 rscalc v0+unknown 回退(e) / B2 autovia 默认(f) / B2 powerfill CWD(g) / B1 source 字段(h) / B2 source 全 default(i) / JSON schema(j) / 反硬编码 B1≠A(k) / 反硬编码 B2≠B1(l) / 确定性 3x sha256(m) / 源码无 B 字面量(n)
- **自验**: ref PASS(14/14); 5 negatives(empty/print_expected/core_deleted/naive_always_default/hardcode_a) ALL FAIL NEG_RC=0; §4.9 三假全 FAIL; k=14=k_check=14≥8 GATE PASS; jsonl 嵌入 test 抽出再跑 ref PASS+neg FAIL
