# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 1

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        R research ✅ + R2 LLM 侧 ✅ + R2 视觉侧 ✅（§0.4）+ phase5 isolation v0.3 + phase1/2 脚本就绪
已完成:       §0.3 8 源事实表满填·base vs L3 重叠 0%·P-8 三档 44/100/200B；§0.4 本地多模态 12 源逐条实测（图像形态+≤77 率）·13 HF 候选（7 URL-only 淘汰 / 6 bytes）·前 3 推荐；SFT-2605 重下已启动；⚠️ 校正 SFT-2605 总量=318.99GB/1504 jsonl（旧记 97.6GB 有误）
当前动作:     轻 I/O 维护：实测四路 HF 下载进度并回写记忆/流水、git 提交推送
下一步:       base(2.99TB) 与 SFT-2605(318.99GB/1504 jsonl) 下载完成后 → check_contamination.py 过闸 → phase2 分词（base-en 86:10:4）；SFT-2605 下满 1504/1504 后报实际字节/文件数与 HF 官方清单一致性
阻塞:         无硬阻塞；四路下载争带宽——SFT-2605 518/1504 jsonl（16.4G/318.99GB）·base 49/64624 parquet（50G/2.99TB）·gpic 626 tar·LLaVA 7592 parquet；重 I/O 继续避让
ERROR_COUNT:  0
```

## 运维问答

> 外部运维在 `BAIZE_DATA_TASK.md` 的「运维指令区」提问时，答案写在这里。

（暂无）

## 状态头

| 字段 | 值 |
|:---|:---|
| PHASE | **R research ✅ + R2 LLM 侧 ✅（8 源满填 / base vs L3 重叠 0% / P-8 86:10:4）+ R2 视觉侧 ✅（§0.4：本地 bytes 图文对实测 / 13 HF 候选 / 前 3 推荐）+ phase5 isolation v0.3 + phase1/2 脚本就绪** |
| WAITING | 1（base 2.99TB + gpic + LLaVA + SFT-2605 四路下载中：SFT-2605 518/1504 · base 49/64624 · gpic 626 · LLaVA 7592，重 I/O 阶段继续推迟） |
| ERROR_COUNT | 0 |
| 节点 | `10.239.2.12`（主机 `whag0pgpuap12`；NFS：`/nas_inference` 只读源，`/nas_train` 产出） |
| 更新 | 2026-10-02 |

## 看板（按推荐执行顺序）

| 阶段 | 状态 |
|:---|:---:|
| R research（🎯 只答 §0 两问） | ✅ 完成（DATA_RESEARCH v1.1：LLM 够/走路线A；Vision 换 GPIC short 消截断） |
| R2 LLM 数据侧调研（任务书两项优先） | ✅ 完成（DATA_RESEARCH R2 节：8 源事实表满填 / base vs L3 重叠实测 0% / P-8 三档 44B·100B·200B = base-en(86):code(10):math(4)；base 2.99TB 下载已启动） |
| R2 视觉侧调研（§0.4 去 HF 找通用图文对） | ✅ 完成（DATA_RESEARCH R2-视觉侧：本地 12 源图像形态+≤77 实测 / 13 HF 候选其中 7 URL-only 淘汰 / 前 3 推荐 CC12M≈11M + Amshaker≈6M + LLaVA≈1.15M，50 万→1800 万对 ×35，无需新下载） |
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
- [x] ~~`UltraData-SFT-2605` 重新下载~~ → **已启动（2026-10-01 夜）**：现 token `hf_lqLxH…`（用户 **foamliu**）`whoami-v2` 实测**有效**、gated resolve **通过**、单文件试下成功（`Code_no_think_part-001` 28M）。全量 **318,990,252,711 B ≈318.99GB / 1504 jsonl**（`no_think` 855 + `think` 649；⚠️ 2026-10-02 唤醒 13 按 HF 官方清单逐子目录求和校正，旧记「97.6GB/984 文件（978 jsonl）」系树 API 递归截断所致、已全部改正）后台下载中（`hf download` 进程存活），下完核验实际字节数+文件数与 HF 官方清单一致性。

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
- 2026-10-01 —— 唤醒 11（🎯 §0.4 R2 视觉侧 + ① SFT-2605 重下，两项均落地）：**① SFT-2605**：token `hf_lqLxH…` 实测 `whoami-v2`＝用户 **foamliu**（有效，非之前误判 401），gated resolve 通过、单文件试下成功 → **全量 97.6GB / 984 文件（978 jsonl）后台下载已启动**（进程存活，待下完核验一致性）。**② §0.4 视觉侧全完成**：本地 12 源逐条实测**图像形态 + ≤77 率**（`tar -tf`/`pyarrow` schema/`first-rows` 取证）：CC12M webdataset **bytes** 1100 tar/1.2T/≈11M 对 98%≤77 ✅；Amshaker Mobile-O **bytes** 2250 tar/3.7T/≈6M 对 100%≤77 ✅；BLIP3o **bytes** 但 0%≤77（长描述）⚠️；laion2B-en-aesthetic **URL-only**（schema=URL/TEXT/embedding）🚫；Recap-DataComp-1B URL-only 🚫。**13 个 HF 候选** first-rows 实测：7 URL-only 淘汰（DataComp/COYO/PixelProse/Recap/OBELICS/LAION-COCO/LAION2B）+ 6 bytes。**结论：可用对 50 万 → ≈1800 万（×35），前 3 推荐（CC12M + Amshaker + LLaVA）全本地、无需新下载**。`cimi-search`（api.bocha.cn）仍 SSL 阻断 → 用 HF 搜索 API + datasets-server 等价完成并列出请求。写 DATA_RESEARCH R2-视觉侧 + LEDGER §6 + 本文件；WAITING 保持 1（base/gpic/LLaVA/SFT-2605 四路下载中）。
- 2026-10-02 —— 唤醒 12（🎯 R2 已全部交付，轻 I/O 维护）：复核 BAIZE_DATA_TASK 运维指令**未变**（仍是「三次修订」① SFT-2605 重下 ② §0.3/§0.4 R2 ③ phase3_domain 取消）、无状态索取、无 STOP。R2 两项（§0.3 LLM / §0.4 视觉）已在唤醒 10/11 完成并推远端（data 最后一次 commit `12553d7`=wake 11）。本唤醒仅实测四路下载进度并回写记忆：**SFT-2605 179/978 jsonl（4.3G/97.6GB，~18%）· base 21/64624 parquet（26G/2.99TB，~0.9%）· gpic 1866 文件（843G）· LLaVA 7575 parquet**，4 个 `hf download` 进程存活（gpic / base / LLaVA / SFT-2605）。磁盘 `/nas_train` 剩 32T、`/nas_inference` 剩 21T、`/nas_user` 剩 29T，均够。phase1/2/4 重 I/O 继续避让，WAITING 保持 1。下一步 = 各下载完成后（尤其 SFT-2605 下完需报实际字节/文件数与 HF 官方清单一致性、base 落地后过污染闸）→ 污染扫描 → phase2 分词。
- 2026-10-02 —— 唤醒 13（轻 I/O 维护 + ⚠️ 校正 SFT-2605 总量）：复核运维指令未变（三次修订三件套）、无状态索取、无 STOP。**关键校正**（回应运维 ① 的「一致性」要求）：用 HF REST `/api/datasets`（siblings=1510）+ `/tree/main/<13 子目录>` 逐目录求和，权威总量 = **1504 jsonl / 318,990,252,711 B ≈318.99GB**（`no_think` 855 文件≈49GB：Chinese-general 50 / Code 300 / IF 20 / Knowledge 80 / Math 300 / Multi-lang-Knowledge 50 / Multi-lang-Math 55；`think` 649 文件≈270GB：Chinese-general 50 / **Code 279=177.5GB(体积主因)** / IF 20 / Knowledge 50 / Math 250=74GB）——旧记「97.6GB/978/984」系树 API 递归截断所致，**有误，已全部改正**（MEMORY/DATA_RESEARCH/DATA_LEDGER）。下载进度：SFT-2605 **315/1504 jsonl（8.57G/318.99GB）**·base **23/64624 parquet（30G/2.99TB，en part-0024/2048）**·gpic train **492/8000 tar（916G）**·LLaVA **7582 parquet**；4 个 `hf download` 进程均存活（gpic/SFT-2605/base/LLaVA）。磁盘 `/nas_inference` 剩 21T，319GB 无压力。phase1/2/4 重 I/O 继续避让，WAITING 保持 1。下一步 = SFT-2605 下满 1504/1504 后报「实际字节+文件数 vs HF 官方清单」一致性 → base 落地过 `check_contamination.py` → phase2 分词（base-en 86:10:4）。
- 2026-10-02 —— 唤醒 14（轻 I/O 维护，四路下载进度实测+回写）：复核运维指令未变（三次修订三件套）、无状态索取、无 STOP。实测四路均**存活且在推进**（mtimes 秒级更新）：SFT-2605 **461/1504 jsonl（12G/318.99GB，~30.7% 文件 / ~3.7% 字节）**，`no_think` 已下全 Chinese-general/Code/IF/Knowledge、正在下 Math（part-012/300），`think/`（尤其 Code 279=177.5GB 主体积）尚未开始——故字节进度远低于文件进度；base **36/64624 parquet（44G/2.99TB）**，en part-0037/2048（每片≈1.3GB，实测≈138s/片≈9.4MB/s）；gpic **625 tar（862G）**；LLaVA **7587 parquet（26T）**。磁盘 /nas_inference 剩 21T、/nas_train 剩 32T、/nas_user 剩 29T 均够。phase1/2/4 重 I/O 继续避让，WAITING 保持 1。下一步 = SFT-2605 下满 1504/1504 后报「实际字节+文件数 vs HF 官方清单」一致性 → base 落地过 `check_contamination.py` → phase2 分词（base-en 86:10:4）。
- 2026-10-02 —— 唤醒 15（轻 I/O 维护，四路下载进度实测+回写）：复核运维指令**未变**（三次修订三件套① SFT-2605 重下 ② §0.3/§0.4 R2 ③ phase3_domain 取消）、无状态索取、无 STOP。实测四路均**存活且在推进**（base `/tmp/base_dl.log` 秒级逐文件推进到 en part-0050/2048）：SFT-2605 **518/1504 jsonl（16.39G/318.99GB，~34.4% 文件 / ~5.1% 字节）**——`no_think` Chinese-general 50✓/Code 300✓/IF 20✓/Knowledge 80✓/Math 68/300（进行中），`think/`（尤其 Code 279=177.5GB 主体积）**尚未开始**，故字节进度仍远低于文件进度；base **49/64624 parquet（50G/2.99TB，en part-0050/2048）**；gpic **626 tar**；LLaVA **7592 parquet**。4 个 `hf download` 进程均存活（gpic/SFT-2605/base/LLaVA）。磁盘 /nas_train 剩 32T、/nas_inference 剩 21T、/nas_user 剩 29T 均够。phase1/2/4 重 I/O 继续避让，WAITING 保持 1。**带宽/ETA 注**：base 实测 ~9.4MB/s/路（138s/片×1.3GB），2.99TB 单路需 ~3.7 天，四路争用下更长；SFT-2605 待 no_think/Math 下完进入 think/ 后字节进度将明显加速。git：本地==origin 同步（工作区有 vision 侧 R8 在途改动 `models.py`/`r8_*`，**非本任务文件、不 touch**）。下一步 = SFT-2605 下满 1504/1504 后报一致性 → base 落地过 `check_contamination.py` → phase2 分词（base-en 86:10:4）。
