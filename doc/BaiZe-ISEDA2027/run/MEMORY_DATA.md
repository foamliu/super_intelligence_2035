# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 1

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡（pretrain loop 踩过这个坑）。

---

## 📊 进度快照（**固定格式，每次唤醒必须更新**，供外部远程巡检）

```
PHASE:        phase0_inventory
已完成:       （无 —— 任务刚创建）
当前动作:     尚未启动，等待首次唤醒
下一步:       读 BAIZE_DATA_TASK.md + BAIZE_DATA_PREP_PLAN.html → 执行 phase0 实测盘点
阻塞:         无
ERROR_COUNT:  0
```

## 运维问答

> 外部运维在 `BAIZE_DATA_TASK.md` 的「运维指令区」提问时，答案写在这里。

（暂无）

## 状态头

| 字段 | 值 |
|:---|:---|
| PHASE | **phase0_inventory**（任务已创建，等待首次唤醒） |
| ERROR_COUNT | 0 |
| 节点 | `10.239.2.29`（NFS：`/nas_inference` 只读源，`/nas_train` 产出） |
| 创建 | 2026-10-01 |

## 看板（按推荐执行顺序）

| 阶段 | 状态 |
|:---|:---:|
| phase0 inventory（实测盘点） | ⬜ |
| phase5 isolation（**先立闸**） | ⬜ |
| phase1 validate（完整性校验） | ⬜ |
| phase2 text（通用文本 .bin/.idx） | ⬜ |
| phase3 domain（EDA 领域语料排查） | ⬜ |
| phase4 mm（多模态打包） | ⬜ |
| phase6 handoff（清单/报告/HTML） | ⬜ |

## 待确认（需要人工提供）

- [ ] **EDA 领域语料来源**（方案 §4.3）——`eda_fastmcp` 的 API 知识库能否导出为纯文本文档？
- [ ] 内部培训材料 / 脱敏 CAD 案例能否用于训练（授权）
- [ ] 多模态下载预计完成时间

## 操作流水

- 2026-10-01 —— 任务创建（外部运维）。loop 脚本 `baize_data_loop.sh`、任务书 `BAIZE_DATA_TASK.md`、方案 `BAIZE_DATA_PREP_PLAN.html` 就位。**尚未启动。**
