# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 1

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        R research ✅（两问已答 v1.1）+ R2 LLM 数据侧调研 ✅（8 源事实表满填 / base vs L3 重叠实测 0% / P-8 三档 44B·100B·200B）+ phase5 isolation v0.3 + phase1/2 脚本就绪
已完成:       R2 调研产出并写入 DATA_RESEARCH.md R2 节 + DATA_LEDGER D9/D10 + token 实测（Code 411B/Math 303B/L3 690B/base 1.12T）；Ultra-FineWeb base（2.99TB）下载已启动
当前动作:     R2 收尾：回写记忆/清单、git 提交推送；确认 base 下载进程存活（轻 I/O）
下一步:       base 下载完成后 → check_contamination.py 过闸 → phase2 分词（base-en 86:10:4）；SFT-2605 等有效 token 轮换后重下
阻塞:         SFT-2605 gated 重下缺有效 HF token（现 token hf_lqLxH… whoami 401 已失效）；base 2.99TB 下载中（~3 天空窗，与 gpic/LLaVA 争带宽）
ERROR_COUNT:  0
```

## 运维问答

> 外部运维在 `BAIZE_DATA_TASK.md` 的「运维指令区」提问时，答案写在这里。

（暂无）

## 状态头

| 字段 | 值 |
|:---|:---|
| PHASE | **R research ✅（两问已答 v1.1）+ R2 LLM 数据侧 ✅（8 源事实表满填 / base vs L3 重叠 0% / P-8 三档 base-en(86):code(10):math(4)）+ phase5 isolation v0.3 + phase1/2 脚本就绪** |
| WAITING | 1（base 2.99TB + 多模态仍在下载，重 I/O 阶段继续推迟；SFT-2605 等有效 token） |
| ERROR_COUNT | 0 |
| 节点 | `10.239.2.12`（主机 `whag0pgpuap12`；NFS：`/nas_inference` 只读源，`/nas_train` 产出） |
| 更新 | 2026-10-01 |

## 看板（按推荐执行顺序）

| 阶段 | 状态 |
|:---|:---:|
| R research（🎯 只答 §0 两问） | ✅ 完成（DATA_RESEARCH v1.1：LLM 够/走路线A；Vision 换 GPIC short 消截断） |
| R2 LLM 数据侧调研（任务书两项优先） | ✅ 完成（DATA_RESEARCH R2 节：8 源事实表满填 / base vs L3 重叠实测 0% / P-8 三档 44B·100B·200B = base-en(86):code(10):math(4)；base 2.99TB 下载已启动） |
| phase0 inventory（实测盘点） | ✅ 完成（DATA_LEDGER v0） |
| phase5 isolation（**先立闸**） | ✅ 完成（v0.3：536 任务 + NFKC/Unicode 归一化 + 8-gram 兜底 + **SFT 嵌套 jsonl 目录同闸扫描**，全快照正控 100%） |
| phase1 validate（完整性校验） | 🟡 校验脚本已备（validate_data.py），全量跑待下载完成后 |
| phase2 text（通用文本 .bin/.idx） | 🟡 分词打包 wrapper 已备（preprocess_text.sh + 污染闸门），跑待下载完成后 |
| phase3 domain（EDA 领域语料排查） | 🚫 **已取消**（运维 2026-10-01 夜：评测 prompt 由 docstring 生成、与语料天然同源，入库无意义）；但 EDA-Eval 158 任务黑名单红线**依然有效、继续执行** |
| phase4 mm（多模态打包） | ⬜（待下载完成） |
| phase6 handoff（清单/报告/HTML） | ⬜ |

## 待确认（需要人工提供）

- [x] ~~EDA API 知识库能否导出纯文本~~ → **已确认可行**：`eda_fastmcp/docs/` 本就是 md/json 纯文本（≈45MB，见 DATA_LEDGER §5）。
- [x] ~~EDA 语料入库授权~~ → **整条线已取消**（运维 2026-10-01 夜）：评测 prompt 由 docstring 生成、与语料天然同源，"把测试集放进训练集"无意义 → phase3_domain 不再调研/入库。**但 EDA-Eval-PyAether 158 任务黑名单红线照常执行。**
- [x] ~~内部培训材料 / 脱敏 CAD 案例能否用于训练~~ → 随 phase3_domain 一并取消。
- [ ] 多模态下载预计完成时间
- [x] ~~`UltraData-SFT-2605/-Agent-2609` 具体存储格式~~ → **已实测**：Agent-2609 = **jsonl**（50 shard / 51 GiB，2GB/shard）；**2605 = 落盘为空**（仅 179 个 `.lock` 缓存文件 / 22.4KiB，无数据，需重下）
- [ ] **🔴 新数据缺口**：`UltraData-SFT-2605` 需重新下载（当前盘上只有 HF 下载缓存，`data/no_think/*` 目录为空）
- [ ] **🔴 SFT-2605 重下阻塞 = 缺有效 HF token**（运维 2026-10-01 夜已在 HF 网页点"同意条款"，但下载仍需有效 token）：本机**无缓存 token / 无 HF_TOKEN 环境变量**，唯一已知 token（gpic 进程参数暴露的 `hf_lqLxH…`）`whoami` 返回 401（`Invalid username or password`）、SFT-2605 resolve 仍 **HTTP 401** → **需运维在 `10.239.2.12` 配置有效 token（`huggingface-cli login` 或 --token），同时轮换/撤回 gpic 里暴露的同一失效 token**。

## 关键路径速查（供恢复）

- 训练仓库 `BASE_DIR` = `/nas_train/app.e0031982/code/BaiZe-ISEDA2027`（复用其 `mamba2_hybrid_2b/preprocess_data.py` + `data/tokenizer_eod` + `pretrain_launcher.py`）。
- 评测集（只读红线）：`/nas_train/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl`（158 任务，**无 canonical_solution 字段**）。
- 黑名单产物：`run/data_pipeline/blacklist/`（并集 6 快照 536 任务 / 193,295 `ngram_hashes.txt` / 10 `short_ngram_hashes.txt` / meta.json / entry_points.sha256）。
- 校验/打包脚本：`run/data_pipeline/validate_data.py`（phase1 完整性校验，默认轻 I/O）+ `preprocess_text.sh`（phase2 分词打包，复用 Round1 `preprocess_data.py` + 污染闸门）。

## 操作流水

- 2026-10-01 —— 唤醒 1（首次）：phase0 inventory 完成（L3 616 文件/617.6GiB；Code 1121；Math 1823；SFT parquet=0；LLaVA EN5545/CN1512；en500k 25tar/68.59GiB；eval5k 1tar/1.27GiB）→ 写 DATA_LEDGER v0（差异 D1–D7）。
- 2026-10-01 —— phase5 立闸：build_blacklist.py + check_contamination.py + inventory.sh；生成黑名单 158 任务/191372 shingle；冒烟负控 0 命中、正控 158/158。写 CONTAMINATION_CHECK v0。WAITING 置 1（避让下载）。
- 2026-10-01 —— 唤醒 2：phase5 升级为 **6 快照并集黑名单**（536 任务 / 191,718 ngram），`build_blacklist.py` 支持多 `--eval-jsonl`；正控 `-46`=46/46、`cuhk`=21(+59 短跳过)；API 参考文档粗扫 0 命中。**phase3**：确认 `eda_fastmcp/docs/` 有 ≈45MB API 参考文本（来源材料，红线内允许侧）。写 DATA_LEDGER §5、CONTAMINATION_CHECK v0.1。多模态 7500 parquet（基线 7057，仍在增）→ WAITING 保持 1。
- 2026-10-01 —— 唤醒 3（phase5 修 bug → v0.2）：定位 `normalize()` 的 `[^a-z0-9_]` 会丢弃**所有非 ASCII 字符（含中文）**，导致 cuhk 80 任务中 59 条中文 prompt 丧失指纹。改为 `NFKC + Unicode \w`（NFKC 先把 Kangxi 部首兼容字 ⼀ U+2F00→一 等映射回标准 CJK）；对 NFKC 后仍 <13 字的 4 条（CUHK-012/037/042/052）加 **8-gram 兜底**（新增 `short_ngram_hashes.txt` 与扫描侧短 tier）。重生成黑名单：536 任务 / 193,295 13-gram（+1,577 全来自修复的中文）/ 4 短任务 / 10 8-gram。冒烟：cuhk **80/80**（原 21）、v20260311 158/158、148=148、46=46、Updated102=102、TEST=2、负控 L3 1500→0。多模态 7506 parquet（obelics EN 仍在增）→ WAITING 保持 1。
- 2026-10-01 —— 唤醒 4（补齐 phase1/2 脚本 + 实测 SFT 落盘格式）：补齐 §7.3 验收所需但此前缺失的两类可复现脚本——`validate_data.py`（phase1 完整性校验：parquet/tar/jsonl/shards/census 五子命令，默认轻 I/O 只读 footer/成员名/前 N 行）与 `preprocess_text.sh`（phase2 分词打包 wrapper：复用 Round1 `preprocess_data.py` + 内置 `--with-contam` 污染闸门）。语法与实跑自测：`py_compile`/`bash -n` 通过；`shards` 自测 en500k 25 个 shard **0..24 连续无缺号**；`census` 自测 Code-L3/py = 147 parquet/148.4GiB。**关键实测**：`UltraData-SFT-Agent-2609` = jsonl（50 shard / 51GiB，2GB/shard，`data/Code_Agent` 等）✅；`UltraData-SFT-2605` = **落盘为空**（152K，仅 README+LICENSE，`data/no_think/*` 目录空，179 个 `.lock` 缓存），与任务书"已下载"不符 → 需重下（新数据缺口，已上报待确认）。下载仍进行中（LLaVA 7510 parquet）→ WAITING 保持 1。
- 2026-10-01 —— 唤醒 5（修 SFT 同闸目录-jsonl 扫描 + 校正 LLaVA 目录命名）：发现 **check_contamination.py 目录分支只 glob parquet、漏掉嵌套 jsonl**（Agent-2609 实为 `data/{Code,General,Search,Tool}_Agent/*.jsonl`），"jsonl 模式直接可扫"对**目录输入不成立** → 会让 SFT 目录语料被静默扫 0 文档。修复：目录递归收集 `*.jsonl`(rglob) + 新增 `_extract_jsonl_text`（支持 Agent-2609 的 `messages` list<{role,content}> 多轮对话，实测单文档 40KB）+ `_flatten` 加 content 回退。冒烟回归全过：正控 v20260311 **158/158**；Agent-2609 单文件 30 文档 / 目录 10 文档均 **0 命中**（短兜底 0 → 证明 messages 非空）。另校正 LLaVA 计数：**coyo 中文在 `Language-CN` 目录（436 parquet，非 `CN`）**，phase0 误记 coyo CN=0 → 修正总数 ≈7519（EN 5571 / CN 1948）；inventory.sh 同步覆盖 Language-CN。下载仍进行中（LLaVA≈7519 / gpic 687G）→ WAITING 保持 1。
- 2026-10-01 —— 唤醒 6（🎯 R 阶段：只答 §0 两问，产出 DATA_RESEARCH v1，废弃旧 8 主题稿）：用 HF REST API + 本地 open_clip/DeepSeek tokenizer **逐条实测**。**Q1**：L3 4 config = 1764 parquet 与 HF 逐文件一致（en_qa 616/en_multi 552/zh_qa 310/zh_multi 286）、Code 1121、Math 1823 均下全；SFT-2605 落盘空（gated=auto）需重下；MiniCPM5 另有的 Ultra-FineWeb base/UltraX-Preview/RL-2609 本地无但 BaiZe 计划不用。token 实测外推 ≈**690B**（en 467B/zh 223B；README 自述 600B+）→ **判定「1.8T tokens」写错**（1.8T=磁盘字节 1.8TiB=HF parquet 1898GB；论文 §4 还误写「English subset」）。**配比建议走 A**（复用 MiniCPM5 源 + BaiZe 已消融 86:10:4）。**Q2**：LLaVA 85M recaption 实测 **99.7–100% >77 token 被截断**（en 均值 ~202–228/zh 498）；GPIC `tag/short/medium` 实测 **0% 截断**（11/20/46 token，仅 long 100% 截断）→ 换 GPIC short 即消截断。**Q2 配比**建议 caption 用 GPIC short。写 DATA_RESEARCH v1 + 备份旧稿为 DATA_RESEARCH.md.bak-8topics。WAITING 保持 1（多模态下载进行中）。
- 2026-10-01 —— 唤醒 7（R 阶段复核 → DATA_RESEARCH v1.1，轻 I/O）：`fetch_web_content` 可直连 HF 但 arxiv/github/bocha 仍不可达。逐条复核 URL 事实后**修订 3 处**：① Q1(1) 补官方 config 全名 `*-Synthetic`（320/378/157/204M 行 ↔ 本地 en_qa 616/en_multi 552/zh_qa 310/zh_multi 286），并加 HF 官方 `1,058,535,126 rows / 1.9 TB`(=1898GB≈1.8TiB) 佐证「1.8T=字节」；② Q1(3) 更正 arxiv:2602.09003 身份 = **UltraData《Tiered Data Management》立场/框架论文**（宣称「2.4T open tokens」= 全 Ultra* 平台，**非** MiniCPM5 模型技术报告），结论「MiniCPM5 逐源配比=未找到」不变；③ Q2(1)/(4) 补 GPIC **gated 状态**（需同意共享联系信息，MIT 许可但访问 gated）+ Q1(2) 抽样口径透明化。下载仍进行中（gpic train 406→417）→ WAITING 保持 1。
- 2026-10-01 —— 唤醒 8（R 阶段已收敛，轻 I/O 维护）：复核 BAIZE_DATA_TASK 运维指令未变（仍「只答 §0 两问」）、无状态索取、无 STOP。确认 `DATA_RESEARCH.md` 已 tracked 且推远端（最新 commit `60af7fb`=v1.1；`git status -sb` 我方文件干净，仅 pretrain 在途文件 `EXPERIMENTS_PRETRAIN_2B_ROUND2.md`/`MEMORY_PRETRAIN_2B.md` 有改动 → **不碰**）。实测下载进度（⚠️ 用 `find -name '*.parquet'` 而非顶层 `ls`：L3/LLaVA 的 parquet 在 `{subset}/{lang}/partNN/` 嵌套子目录，顶层 `ls` 只看到 partNN 目录会严重低估）：LLaVA 85M = **7549 parquet**（EN **5601** = imagenet50+laioncn430+datacomp1b439+coyo1504+mint553+obelics**2625**；CN **1948**；sa1b/zero250m 仍缺）；GPIC train **430/8000**、test 128/128。2 个 `hf download` 进程仍存活（gpic 与 LLaVA）→ phase1/2/4 重 I/O 继续避让，WAITING 保持 1；R 阶段无需新调研。
- 2026-10-01 —— 唤醒 9（🎯 R 阶段已收敛，轻 I/O 维护）：复核运维指令未变（仍「只答 §0 两问」）、无状态索取、无 STOP。git `## main...origin/main` 干净、`DATA_RESEARCH.md` v1.1 已在远端（`46a3f8d`=v1、`60af7fb`=v1.1）。下载进度（`find -name '*.parquet'` / `ls|wc -l` 口径）：LLaVA 85M = **7556 parquet**（较唤醒 8 的 7549 +7，全在 obelics/EN；sa1b/zero250m 仍未开始）、GPIC train **439/8000**（+9）、test 128/128；2 个 `hf download` 进程存活 → phase1/2/4 继续避让、phase3 待 EDA 授权，WAITING 保持 1。
- 2026-10-01 —— 唤醒 10（🎯 R2 LLM 数据侧调研，两项优先任务全完成）：① **8 源事实表满填**（逐源 HF REST `/api/datasets`+tree+`datasets-server` `/size` 实测）：base 1,290,261,453 行/2.99TB/en 2048+zh~62576 文件、UltraX 113,789,578 行/487GB/5 config、L3 1,058,535,126/1.9TB、Code 348,083,481/1.22TB、Math 181,186,453/552GB、SFT-2605 gated ~97.6GB/1000+ jsonl、SFT-Agent-2609 ~500K 样本/51GB、RL-2609 20 jsonl/187.63GB（4 config）；**token 实测**（`r2_local_sample.py`）：Code ≈411B（L2 355+L3 56）、Math ≈303B（L1 184+L2p 32+L3 87）、L3≈690B、base ≈1.12T。② **base vs L3 重叠实测**：由于 L3 = base 的 Q&A/多风格合成改写（README），实测 base 48 vs L3 696 文档 verbatim **0.00%**、5-gram Jaccard 均值 **0.0000** → **下 base = +1.12T 净新增 raw web，非重复劳动**。③ **P-8 三档**：44B/100B/200B = base-en(86):code(10):math(4)，主体由 L3 改判 base；base 2.99TB（apache-2.0 公开）**下载已启动**（写入 `/nas_inference/.../Ultra-FineWeb/`，进程存活）；UltraX（与 base 重叠）与 RL-2609（Stage v）**不下载**。④ **配比来源复核**：MiniCPM5 模型卡 + 8 数据集卡 + arxiv 2602.09003 均 **未公开逐源百分比** → 建议配比 86:10:4（复用 S4 消融）。⑤ **HL 阻塞**：SFT-2605 重下缺有效 token（现 token `whoami` 401）→ 上报待轮换。写 DATA_RESEARCH R2 节 + DATA_LEDGER D9/D10 + 本文件；WAITING 保持 1（base 下载中）。
