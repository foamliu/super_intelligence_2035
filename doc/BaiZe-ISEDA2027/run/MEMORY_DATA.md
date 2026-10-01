# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 1

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        phase5_isolation（base 已立闸）
已完成:       phase0_inventory（实测盘点 + DATA_LEDGER v0）；phase5 base（黑名单指纹 + 扫描脚本 + 冒烟 + CONTAMINATION_CHECK v0）
当前动作:     立闸完成；首波持续推进结束
下一步:       phase3（EDA 领域语料排查，轻 I/O）→ 其余评测快照(148/46/Updated102)纳入黑名单 → 等下载完成后 phase1/2/4
阻塞:         多模态下载未完成（>50%），phase1 全量校验 / phase2 分词 / phase4 打包均为重 I/O，按任务书 §5 避让
ERROR_COUNT:  0
```

## 运维问答

> 外部运维在 `BAIZE_DATA_TASK.md` 的「运维指令区」提问时，答案写在这里。

（暂无）

## 状态头

| 字段 | 值 |
|:---|:---|
| PHASE | **phase5_isolation**（phase0 已完成；黑名单/脚本/报告 v0 已就位） |
| WAITING | 1（异步阻塞：多模态下载未完成，重 I/O 阶段推迟） |
| ERROR_COUNT | 0 |
| 节点 | `10.239.2.29`（NFS：`/nas_inference` 只读源，`/nas_train` 产出） |
| 更新 | 2026-10-01 |

## 看板（按推荐执行顺序）

| 阶段 | 状态 |
|:---|:---:|
| phase0 inventory（实测盘点） | ✅ 完成（DATA_LEDGER v0） |
| phase5 isolation（**先立闸**） | 🟡 base 完成（黑名单+脚本+冒烟）；正式全量扫描待 phase2 前 |
| phase1 validate（完整性校验） | ⬜（重 I/O，待下载完成） |
| phase2 text（通用文本 .bin/.idx） | ⬜（重 I/O，待下载完成；复用 Round1 脚本已确认） |
| phase3 domain（EDA 领域语料排查） | ⬜（**下轮先做**，轻 I/O） |
| phase4 mm（多模态打包） | ⬜（待下载完成） |
| phase6 handoff（清单/报告/HTML） | ⬜ |

## 待确认（需要人工提供）

- [ ] **EDA 领域语料来源**（方案 §4.3）——`eda_fastmcp` 的 API 知识库能否导出为纯文本文档？（phase3 首查）
- [ ] 内部培训材料 / 脱敏 CAD 案例能否用于训练（授权）
- [ ] 多模态下载预计完成时间；`UltraData-SFT-2605/-Agent-2609` 具体存储格式（phase1 确认是否为 jsonl）

## 关键路径速查（供恢复）

- 训练仓库 `BASE_DIR` = `/nas_train/app.e0031982/code/BaiZe-ISEDA2027`（复用其 `mamba2_hybrid_2b/preprocess_data.py` + `data/tokenizer_eod` + `pretrain_launcher.py`）。
- 评测集（只读红线）：`/nas_train/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl`（158 任务，**无 canonical_solution 字段**）。
- 黑名单产物：`run/data_pipeline/blacklist/`（ngram_hashes.txt / meta.json / entry_points.sha256）。

## 操作流水

- 2026-10-01 —— 唤醒 1（首次）：phase0 inventory 完成（L3 616 文件/617.6GiB；Code 1121；Math 1823；SFT parquet=0；LLaVA EN5545/CN1512；en500k 25tar/68.59GiB；eval5k 1tar/1.27GiB）→ 写 DATA_LEDGER v0（差异 D1–D7）。
- 2026-10-01 —— phase5 立闸：build_blacklist.py + check_contamination.py + inventory.sh；生成黑名单 158 任务/191372 shingle；冒烟负控 0 命中、正控 158/158。写 CONTAMINATION_CHECK v0。WAITING 置 1（避让下载）。
