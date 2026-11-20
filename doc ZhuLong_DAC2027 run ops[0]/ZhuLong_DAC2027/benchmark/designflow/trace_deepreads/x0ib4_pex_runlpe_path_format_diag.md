# Deepread: x0ib4 — PEX LPE runlpe.sh 跨工作目录硬编码 + DSPF-vs-SPF_RCC 输出格式诊断

- **session**: `1793685645025_x0ib4.messages.json`
- **user**: e0024852 @ hfeg0pkn004 (10.129.2.13)
- **fetched via**: subdir path fix (`/home/e0024852/.cline/data/sessions/1793685645025_x0ib4/1793685645025_x0ib4.messages.json`, 607KB, fetchable — confirms D-shard r263 NOFILE-parked was a path bug, fixed r971)
- **mc**: 116, keywords pex:940/lvs:290/aether:226/netlist:123/schematic:110/pyaether:98/.gds:66/calibre:48
- **structure**: 73 msgs / 42 user turns / 13 真实 user_input 轮（其余为 tool_result）

## 真实用户意图演进（13 真实 user_input 轮）

| idx | user_input | 类型 |
|---:|---|---|
| 0  | the difference of /proj/lacaa/V0/simdir/finesim/.../hd_CH252_bitcell_post_rev06 | (unclear — finesim sim dir "difference") |
| 13 | 提参需要给什么输入 | Q&A |
| 15 | "提参"指的是 PEX 寄生提取(ncrc/gxrc/lpe,即生成那条 .dspf 网表) | 用户澄清术语 |
| 17 | in /proj/lacaa/TV1_DBC/ver/pex_gxrc/e0012583/.../DBC which are inputs and which are output | Q&A: 输入/输出分类 |
| 27 | 版图 GDS/OASIS is where | Q&A |
| 32 | 从版图到gds 是不是还有一步 | Q&A |
| 34 | 有没有从版图到gds 的命令 | Q&A |
| 49 | the input of pex is what and where they arw | Q&A |
| 51 | tell me in chinese | lang |
| 53 | 电容表 CAPTAB / 层次映射 tran.map / 器件 pin 文件 / hcell 列表 这些可以不要吗 | Q&A: PEX 输入能否省略 |
| 60 | /proj/lacaa/TV1_DBC/ver/pex_gxrc/.../SRAM_TV0_.../lpe.config has what input | Q&A: 读 lpe.config |
| 65 | **run /rundata/lacaa/TV1_FS/.../e0024852/.../runlpe.sh if sucess where is the dspf** | ★core produce-task seed |

本案聚焦 U#65（用户唯一明确的 produce-task：跑 runlpe.sh 并定位 .dspf 输出）。

## Gold 诊断（assistant A#72）

助手 `run_approved_command` 被 agent-policy-engine 拒绝（filePath outside dynamicFileRoots），改读 runlpe.sh + lpe.config 给出 4 条确定性结论：

1. **跨工作目录硬编码**: runlpe.sh line 3 `cd /proj/lacaa/V0/ver/pex_gxrc/e0012583/hd_CH252_bitcell/lpe/hd_CH252_bitcell/`，line 15 `-config /proj/lacaa/V0/ver/pex_gxrc/e0012583/hd_CH252_bitcell/lpe/hd_CH252_bitcell/lpe.config`；lpe.config line 34-37 `cdl=.../e0012583/hd_CH252_bitcell.cdl`、`gds=.../e0012583/hd_CH252_bitcell.gds`。**与用户 invoke 的 `TV1_FS/.../e0024852/...` 不同** → 输出不会落入用户当前目录。

2. **输出格式错配**: lpe.config line 40 `mode = RCC` → 实际产出 `hd_CH252_bitcell.spf_RCC`，**不是 .dspf**。用户目录里已存在的 `hd_CH252_bitcell_rev03.dspf` 是之前 rev03 DSPF 流程的产物，本次 RCC 流程不会生成它。

3. **输出位置**: 
   - 主路径: `/proj/lacaa/V0/ver/pex_gxrc/e0012583/hd_CH252_bitcell/lpe/hd_CH252_bitcell/hd_CH252_bitcell.spf_RCC`
   - 软链（runlpe.sh line 17-22 `cd ../..` + `ln -sf lpe/hd_CH252_bitcell/hd_CH252_bitcell.spf_RCC .`）: `/proj/lacaa/V0/ver/pex_gxrc/e0012583/hd_CH252_bitcell/hd_CH252_bitcell.spf_RCC`

4. **修复路径**: (a) 把 runlpe.sh/lpe.config 硬编码路径改成用户本地 TV1_FS/e0024852 路径再提交；(b) 在能访问 /proj/lacaa/V0 且装了 glory/2026.03_P002 + ds/calibre/2023.3_14 的登录节点上跑（bsub -Is -q star -n 8 是 HPC 交互批处理）。

## reframe 为 case EDA-Eval-DesignFlow-PexRunlpePathFormatDiag-001

**档 B reframe**：A 档 gold = assistant free-text 诊断 prose（依赖 live /proj/lacaa 不可达，且无 ≥8 独立硬断言牙）→ reframe 为离线纯 stdlib 单文件 `pex_runlpe_diag.py`，CLI `<runlpe_sh> <lpe_config> <user_invoked_dir> <workspace_listing> <user_asked_format> [-o out.json]`，输出 24 顶层键结构化 JSON。

**visible A**：忠实 trace（V0/e0012583/hd_CH252_bitcell/mode=RCC/v0/2-up 软链/glory/2026.03_P002+ds/calibre/2023.3_14/preexisting hd_CH252_bitcell_rev03.dspf）。

**hidden B**：全反相（V1/e0024852/ampMacro_v9/mode=RC/v1/1-up 软链/glory/2025.12_P001+ds/calibre/2024.1_12/preexisting ampMacro_v9_rev07.dspf），10+ 轴全异防硬编 A。

**判分 k_check=20**（≥8 闸门）：a zip+stdlib / b B-run 24 keys / c runlpe_cd_path / d path_mismatch / e config_mode / f expected_output_format / g expected_output_filename / h expected_output_path / i symlink_levels_up / j expected_symlink_path / k config_version / l module_loads / m user_asked_format / n format_mismatch / o preexisting_dspf / p recommended_fix / q severity / r anti-hardcode A / s missing-path / t determinism。

**自验**：ref PASS（20/20）+ 4 neg FAIL distinct（a/r/f/c）+ §4.9 三假全 FAIL distinct（a/r/f）+ roundtrip sha16 3c822e7ae42dc79f ✓。

## 与已有 PEX cases 的正交性

C 域已建 6 个 PEX 相关 case，本案与它们正交：

| case | 子型 | 区别 |
|---|---|---|
| PexGxrcDiag-001 | gxrc 选项文件抽取失败根因（TRIO-0428 CapTab + multi-corner + runset 陈旧） | 配置层失败诊断 |
| PexBlCouplingCompare-001 | PEX coupling 对比 | 报告对比 |
| PexCharConfigReview-001 | PEX char config review | 配置审查 |
| PexFlowRunLogDiag-001 | PEX flow run log 诊断 | 日志诊断 |
| PexRccCdlPortMapFix-001 | PEX RCC CDL port map 修复 | 端口映射修复 |
| PexRccLayerMigrate-001 | PEX RCC layer 迁移 | 层映射迁移 |
| **PexRunlpePathFormatDiag-001**（本案）| **runlpe.sh 跨工作目录硬编码 + DSPF-vs-SPF_RCC 输出格式错配 + 软链位置解析** | **driver-script + config + workspace 三方对账** |

本案独特点：**driver-script（runlpe.sh）内部 cd 目标 vs 用户 invoke 目录的跨工作目录错配** + **用户口头问的格式（dspf）vs lpe.config mode 实际产出的格式（spf_RCC）错配** + **runlpe.sh 末尾软链创建模式的解析**，是 PEX 流程中「跑成功但找不到我要的文件」一类高频用户疑问的结构化诊断。
