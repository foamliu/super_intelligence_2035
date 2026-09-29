# MEMORY_2B.md — BaiZe 2B 架构搜索（从零训练）运行时状态（不提交 git，重启用）

## 当前状态
- STAGE: S1 打通从零冒烟
- PHASE: env_check
- WAITING: 0
- ERROR_COUNT: 0
- BUDGET_USED（GPU·小时）: 0
- 当前运行实验: 无
- 下一步: env_check（验证 conda py310 + PYTHONPATH=/tmp/omegaconf_230 规避 + `import megatron.bridge` 成功）→ arch_prepare

## 数据检查结论（data_check 完成）
- 选用子集：`openbmb/Ultra-FineWeb-L3/data/ultrafineweb_en_l3/qa/`（618G，part-00000~...，每个 1.1G，约 519,627 行/part）。
- parquet 列：`uid` / `content`(正文) / `style`；切词取 `content`。
- 备选：`multi_style/`（554G）同样可用，暂不切。
- 磁盘估算：~1000 步 × ~4M tok/步 ≈ 4B tokens；每 part 文本约 ~275M tokens（DeepSeek 切词粗估），切 ~15~18 个 part 足够（数据 .bin/.idx 预计 ~16~20GB，两架构共用）。
- tokenizer 已确认：`/nas_train/app.e0031982/models/DeepSeek-V4.1-Flash/`（tokenizer.json + tokenizer_config.json）。
- MiniCPM5-2B config 已确认：42 层 / hidden 2048 / intermediate 6144 / 16 heads / 2 KV heads / head_dim 128 / silu / rope_theta 5e6 / vocab(原始) 130560（本任务改用 DeepSeek 129281→pad 129408）。

## 候选架构（固定）
- MiniCPM5-2B（42 层 Llama）：config 见 doc/BaiZe-ISEDA2027/MiniCPM5-2B.config.json
- Mamba2-hybrid 2B（56 层 hybrid）：代码见 BASE_DIR/mamba2_hybrid_2b/

## 关键决策（勿违反）
1. 两架构统一走 NVIDIA/NeMo recipe（随机初始化从零），统一 tokenizer=DeepSeek-V4.1-Flash（vocab 129281/pad 129408）
2. 训练口径对齐（seq4096/mb1/同超参/同数据/同seed），**两架构必须同卡数**（建议各 6 卡并行）
3. omegaconf 阻塞需 PYTHONPATH=/tmp/omegaconf_230 规避
4. 最终产出 HTML 报告 `doc/BaiZe-ISEDA2027/BAIZE_2B_ARCH_RESULT.html`

## GPU 资源（双节点）
- 10.239.2.29（8×H100，GPU0~7）；10.239.2.12（前 6×H100，GPU0~5）。两节点 ssh 免密已通。
- 建议：MiniCPM5-2B 用 2.29（GPU0~5）、Mamba2-hybrid 用 2.12（GPU0~5），剩余 2.29 的 GPU6~7 留冒烟/推理。

## git 提交（每 4~6 小时 push）
- 根目录 `/nas_train/app.e0031982/code/super_intelligence_2035`；remote foamliu/super_intelligence_2035（main）。
- PAT 已写入 `~/.git-credentials`（credential.helper=store），push 免交互；loop.sh 每 5 小时兜底 push。
- 只提交 `doc/` 文本（md/html/json/sh）；训练产物/checkpoint/.bin/.idx 在 git 外，不入库。

## 操作流水
| 时间 | 步骤 | 记录 |
|------|------|------|
| 2026-09-29 | init | ✅ 任务书 + loop.sh + 记忆文件初始化；PHASE=data_check |
| 2026-09-29 | data_check | ✅ 确认 qa 子集(618G, parquet 列 uid/content/style, 519627行/part)；tokenizer=MiniCPM5 config=Mamba2 dir 均就绪；PHASE→env_check |
