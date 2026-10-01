# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 1

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        phase3_domain（来源已确认）+ phase5_isolation（6 快照并集已立闸）
已完成:       phase0_inventory；phase5 isolation（全评测快照并集 536 任务黑名单 + 冒烟 + CONTAMINATION_CHECK v0.1）
当前动作:     phase3 排查完成（API 参考文档 ≈45MB 纯文本已找到）；更新清单/报告/记忆
下一步:       EDA 语料授权确认（需运维）→ cuhk 短 prompt 8-gram 兜底 → 等下载完成后 phase1/2/4
阻塞:         多模态下载未完成（7500 parquet > 基线 7057，仍在增），重 I/O 阶段避让；EDA 语料授权待运维确认
ERROR_COUNT:  0
```

## 运维问答

> 外部运维在 `BAIZE_DATA_TASK.md` 的「运维指令区」提问时，答案写在这里。

（暂无）

## 状态头

| 字段 | 值 |
|:---|:---|
| PHASE | **phase3_domain + phase5_isolation**（phase0 完成；6 快照并集黑名单 536 任务 + 报告 v0.1；phase3 来源已确认） |
| WAITING | 1（多模态下载未完成，重 I/O 阶段推迟） |
| ERROR_COUNT | 0 |
| 节点 | `10.239.2.12`（主机 `whag0pgpuap12`；NFS：`/nas_inference` 只读源，`/nas_train` 产出） |
| 更新 | 2026-10-01 |

## 看板（按推荐执行顺序）

| 阶段 | 状态 |
|:---|:---:|
| phase0 inventory（实测盘点） | ✅ 完成（DATA_LEDGER v0） |
| phase5 isolation（**先立闸**） | ✅ 完成（6 快照并集黑名单 536 任务 + 冒烟 + 报告 v0.1） |
| phase1 validate（完整性校验） | ⬜（重 I/O，待下载完成） |
| phase2 text（通用文本 .bin/.idx） | ⬜（重 I/O，待下载完成；复用 Round1 脚本已确认） |
| phase3 domain（EDA 领域语料排查） | 🟡 来源已确认（API 参考文档 ≈45MB），待授权 + 入库 |
| phase4 mm（多模态打包） | ⬜（待下载完成） |
| phase6 handoff（清单/报告/HTML） | ⬜ |

## 待确认（需要人工提供）

- [x] ~~EDA API 知识库能否导出纯文本~~ → **已确认可行**：`eda_fastmcp/docs/` 本就是 md/json 纯文本（≈45MB，见 DATA_LEDGER §5）。
- [ ] **EDA 语料入库授权**（🔴 关键）：`eda_fastmcp` 是 ZhuLong 内部项目，其 API 参考文档能否作为训练数据入库需负责人确认。
- [ ] 内部培训材料 / 脱敏 CAD 案例能否用于训练（授权）
- [ ] 多模态下载预计完成时间；`UltraData-SFT-2605/-Agent-2609` 具体存储格式（phase1 确认是否为 jsonl）

## 关键路径速查（供恢复）

- 训练仓库 `BASE_DIR` = `/nas_train/app.e0031982/code/BaiZe-ISEDA2027`（复用其 `mamba2_hybrid_2b/preprocess_data.py` + `data/tokenizer_eod` + `pretrain_launcher.py`）。
- 评测集（只读红线）：`/nas_train/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl`（158 任务，**无 canonical_solution 字段**）。
- 黑名单产物：`run/data_pipeline/blacklist/`（并集 6 快照 536 任务 / 191,718 ngram_hashes.txt / meta.json / entry_points.sha256）。

## 操作流水

- 2026-10-01 —— 唤醒 1（首次）：phase0 inventory 完成（L3 616 文件/617.6GiB；Code 1121；Math 1823；SFT parquet=0；LLaVA EN5545/CN1512；en500k 25tar/68.59GiB；eval5k 1tar/1.27GiB）→ 写 DATA_LEDGER v0（差异 D1–D7）。
- 2026-10-01 —— phase5 立闸：build_blacklist.py + check_contamination.py + inventory.sh；生成黑名单 158 任务/191372 shingle；冒烟负控 0 命中、正控 158/158。写 CONTAMINATION_CHECK v0。WAITING 置 1（避让下载）。
- 2026-10-01 —— 唤醒 2：phase5 升级为 **6 快照并集黑名单**（536 任务 / 191,718 ngram），`build_blacklist.py` 支持多 `--eval-jsonl`；正控 `-46`=46/46、`cuhk`=21(+59 短跳过)；API 参考文档粗扫 0 命中。**phase3**：确认 `eda_fastmcp/docs/` 有 ≈45MB API 参考文本（来源材料，红线内允许侧）。写 DATA_LEDGER §5、CONTAMINATION_CHECK v0.1。多模态 7500 parquet（基线 7057，仍在增）→ WAITING 保持 1。
