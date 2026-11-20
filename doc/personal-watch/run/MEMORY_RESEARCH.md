# MEMORY_RESEARCH.md — 观察哨 · **research agent** 运行时记忆

WAITING: 1

> ⚠️ `WAITING:` **只在顶部出现一次**（`watch_research_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它决定睡眠时长）。
> 语义（**2026-10-07 起节律改为每天 2 次 · 06:00 / 18:00 本地时区**，由 `watch_research_loop.sh` 时窗强制）：`1` = 常态（字段保留仅供人读，**已不影响唤醒节律**）；`0` = 有近期待办（**仅回退模式**：`WATCH_SCHEDULE_HOURS=` 置空时 `0`→短睡 **60s** 续跑 / `1`→睡 **30min**）。
> 纪律：**正文/快照/流水里绝不再出现以 `WAITING:` 开头的行**。

---

## 📊 进度快照（**每次唤醒必须更新**）

```

PHASE:        双轨（A 最新论文 50% / B 经典论文 50% + 作者关系网 + 研究者言论投料）；loop 按 0,3,6,9,12,15,18,21 八时窗唤醒
已完成:       [r227 · 本地 2026-11-21 06:0x · 06:00 时窗：A 轨 0 新收（今日 5/5 已满）＋ B 轨 +3 → 307 ＋ 作者网 +2 → 287 ＋ 发信 3（累计 125）＋ 回信率 0/125 ＋ voice_ready 1]
  ① 网络：`cat:cs.CL&max_results=40`（`https` 直连 `--noproxy '*'`）`200` / **109,971 B / 40 entry** / `application/atom+xml; charset=utf-8`；`published` 上界 **`2026-11-19T18:57:25Z`**（连续第 7 窗未前进，仍在 72h 内，截止 11-22 18:57Z）。`x.com` 直连 `000`、代理 `127.0.0.1:7897` **`200`**；单条推文 `200` / 125,980 B。
  ② A 轨 **0 新收**（今日 5/5 已满，不凑第 6 篇）；候选 `2611.26084` / `2611.26059` / `2611.26069` / `2611.25588` / `2611.26275` 继续登记。
  ③ B 轨 **+3 → 307**：Mask DINO `2206.02777`（**911**，CVPR 2023）/ ViT-22B `2302.05442`（**965**，QK-norm）/ PaLM 2 `2305.10403`（**2,439**，配比 > 规模）；arXiv `id_list` 单批 `200` + atom + abs 3/3 `200` + OpenAlex 3/3 `200`；先查重剔除 Position Interpolation `2306.15595` / InternVL `2312.14238`（已在表内）。
  ④ 作者网 **+2 → 287**：#286 Ryan Hanrui Wang **B** `wang@nebius.com`（arXiv HTML 脚注，420,247 B）/ #287 Feng Li **A** `fliay@connect.ust.hk`（本人主页 `mailto:`，24,341 B）；**#274 Weisen Jiang 待跟踪 → 已发信**；X 保持 107（补抓 `_onurmutlu_` / `RichardSSutton`，未 follow）。
  ⑤ 发信 **3 封**（累计 125，今日 9/12）：#123 VR-SparseQuant 中文 153 字 / #124 Mask DINO 中文 225 字 / #125 MetaMath 中文 163 字，`SENT OK 06:04:11 / 06:04:15 / 06:04:18`；地址发前当场复核 3/3 `200`；三封开头句与问句零共用、各含只对该论文成立的技术细节；落款两行其后无行。
  ⑥ 回信率 **0 / 125**，**0 封到期**（最早 2026-11-25，#1–#7）；`replies/` 仍只有 README 与诊断；通道只发不收。
  ⑦ voice_ready **1**：Richard Sutton（2026-11-07，「Brute force computation is not enough…」，主页 JSON × `og:description` 双源逐字一致）/ news_ready **0**（三条经典均无事件点）。
  ⑧ 交付：`daily/2026-11-21.html`（06:00 节：B 轨表 + voice_ready + 作者段 + 信件段 + news_ready 0 + 6 线建议 + 附录；div 17/17、table 14/14、tr 81/81、td 183/183、th 59/59、0 script、49,437 B）+ `daily/index.html` 当日行改写（307 / 287 / 125 / voice 2）+ `research/2026-11-21.md` 06:00 节 + `PAPERS.md` #305–#307 + `AUTHORS.md` #286–#287 + `发送记录.md` §06:0x + #123–#125 行 + drafts/bodies 各 3。

当前动作:     ✅ 06:00 时窗闭环：A 轨 0 新收（今日 5/5 已满，不凑数），B 轨 +3（统一检测分割头 / QK-norm / 配比报告），作者网 +2（A 级 1 / B 级 1），发信 3 封（全中文），voice_ready 1（Sutton）。
下一步:       ① 09:00 时窗：A 轨 0 新收（额度已满）＋ B 轨候选 HBM/JEDEC 一手 / QK-clip 实现报告 / DINO-X 核 ID / EVA-02 或 InternViT-6B / NTK 位置编码对照；② 11-25 首批到期 → #1–#7 转 `无应答(>14d)`；③ voice_ready 继续 1 条双源核验；④ 运维：改发件显示名 / SMTP 只发不收 / 任务书 44 KB 超红线；⑤ 推送：先 `pull --rebase` 再 push。
本轮新增:     A 轨 0（今日 5/5）· B 轨 +3（307）· 作者网 +2（287）· 作者信 3（125）· voice_ready 1 · news_ready 0 · 回信率 0/125 · X 已核验 107
阻塞:         ① 🔴 发件显示名 `AI+EDA 招聘 · 自动`（最可能的 0 回信原因），需运维改配置；② 发件通道只发不收（无 IMAP/POP3）⇒ 回信可能已到但读不到；③ `WATCH_RESEARCH_TASK.md` 44 KB 超红线且 agent 只读 ⇒ 需授权；④ 无新增其他阻塞。
ERROR_COUNT:  118（本轮 0 新增）


```

## 🗣 运维问答（supervisor 提问 → 本线回答）

> supervisor 可在任务书运维指令区「状态索取」写入问题；本区**先答该问题**再干活。

- **Q（运维第 2 批登记）**：是否要**给论文作者发邮件**做学术交流/技术沟通？
  **A（本线）**：**已登记为未来职能，本批只登记、不实施**。启用**前提（须用户明确批准）**：① 发件邮箱/身份/署名；② 邮件模板；③ 频率上限；④ 每封是否需用户先审。
  **红线**：**未获批准，绝不自动发送任何邮件**。当前各线上均**无任何发信动作**。

- **Q（运维第 3 批 B 节 · 视频线）**：`V3`（把口播稿变成成片）什么时候能启动？需要用户/环境确认什么？
  **A（本线）**：**V1/V2 已交付**（选题表 + 3 份口播稿，纯文本）；**V3 会用到运行机可能没有的工具链**，故**本批不做**，先把**待确认清单**摆出来，获批后再动：
  ① **TTS / 配音**：用哪个引擎（系统 `espeak`？本机有无可用的中文 TTS？还是要用户自录口播）；② **文生图/画面**：运行机是否可访问图像生成服务（**HF 本机不可达**，需另定；否则退化为**纯自绘 SVG/图表**）；
  ③ **剪辑**：有无 `ffmpeg`；成片**>20MB 不入 git**（走外部目录 + 清单）；④ **栏目名**：本线**须自起**（避免与已有知名频道「两分钟论文」混淆）；
  ⑤ **发布**：B站/抖音账号、实名与平台规则在**用户侧**，**发布由用户本人执行**。
  **红线**：**不盗用论文原图、不夸大、不曲解**；未获确认**不擅自生成/发布成片**。
- **Q（运维指令 2026-10-12 · 📨 每日论文日报）**：选 3–5 篇 → PDF → 邮件发 `paul.liu@cxmt.com`，是否已执行？
  **A（现行口径）**：旧「每日论文日报邮件」职能已由 **2026-11-07 10:50 用户令**停止 —— 日报唯一出口 = `research/daily/<YYYY-MM-DD>.html` + `daily/index.html`；历史发送细节（第 1–23 封、分包、PDF 体积）已归档到 `WATCH_RESEARCH_TASK_ARCHIVE.md` 与 `daily-memories-research/`，此处不再复述。**作者请教信**是另一职能，口径见 `RESEARCH_MAIL_SPEC.md`（免审直发、每轮 ≤3 / 每日 ≤12）。


---

## 1. 状态头

- **线**：research（arXiv 论文采集/整理）
- **任务书**：`WATCH_RESEARCH_TASK.md`（只读）
- **产物**：`research/<YYYY-MM-DD>.md`（日报）· `research/SEEN.md`（去重台账，主键 arXiv ID）· `research/INDEX.md`（索引）· `research/papers.jsonl`（结构化台账）· `research/ARXIV_API.md`（R1）· **`research/TOP_K.md` + `research/TOP_K.jsonl`**（精选排序；源 `TOP_K_notes.md` + **`TOP_K_takeaways.json`**）· **`research/TAKEAWAYS.md`**（第 3 批 A 节：≤5 条可借鉴结论）· **`research/video/SHORTLIST.md` + `research/video/scripts/<arXiv_ID>.md`**（第 3 批 B 节：视频线 V1/V2）
- **工具/回归**：`research/arxiv_fetch.py` + `research/test_arxiv_fetch.py`（49/49）· **`research/top_k.py`（含 `--takeaways-json`）+ `research/test_top_k.py`（25/25）**
- **日流水**：`daily-memories-research/<YYYY-MM-DD>.md`
- **关注领域**：LLM · SLM · 多模态 · agent harness（+ 邻域，见任务书 §1）
- **采集节律**：⏰ **每天 8 个时窗 · 0/3/6/9/12/15/18/21（本地时区）**（`RESEARCH_MAIL_SPEC §3` 与 loop 现行口径；`WAITING` 字段保留仅供人读、**已不影响唤醒节律**）；回退：`WATCH_SCHEDULE_HOURS=` 置空 ⇒ `WAITING=1` 睡 **30min** / `WAITING=0` 短睡 **60s**
- **上次采集窗口**：`2026-11-20 18:0x`（**第二百二十二轮 · 18:00 时窗**：`cat:cs.CL` `200` / 109,971 B / 40 entry；最新 `published` **`2026-11-19T18:57:25Z`**（与 15:00 相同）；B 轨第七十六轮 +4 → 292）
- **TOP-K 窗口（第 2 批专用，第 3 批沿用）**：`2026-09-03 ~ 2026-10-01`（**≤30d / 720h**，`window_mode=override`；候选池 **1118** 篇 → TOP-20）
- **累计收录**：`363` 篇（11-20 A 轨 +5：`2611.24849` / `2611.24844` / `2611.24071` / `2611.24809` / `2611.24540`；`SEEN.md` 为唯一防重台账）
- **B 轨（经典论文 · 2026-11-11 新增）**：`research/classic/PAPERS.md`（滚动清单，**292 篇**，8 字段 + OpenAlex 单源被引 + arXiv `comment` 会议口径 + 首次收录日；**七十三轮累计，必读清单 37/37 全覆盖**）· `research/classic/AUTHORS.md`（**260 人**关系网 + X 只读证据 + 待 follow 清单 + 发信记录 + 言论台账 V1–V34）；**B 轨不占 5 篇额度、不进 `SEEN.md`**。作者信草稿 `research/mail/drafts/<arXiv_ID>.md`；正文一律落 `research/mail/bodies/`


---


## 2. 流水（倒序，保留最近 ~20 条）
- **2026-11-21（本地 06:0x · 06:00 时窗 · 🅰 A 轨 0 新收（今日 5/5 已满）＋ 🅱 B 轨第八十轮 +3 → 307 ＋ 作者网 +2 → 287 ＋ 3 封中文信（累计 125）＋ 回信率 0/125 ＋ voice_ready 1）** —— **第二百二十七轮**：① 网络：`cat:cs.CL&max_results=40` 直连 `200` / **109,971 B / 40 entry** / atom；`published` 上界 **`2026-11-19T18:57:25Z`**（连续第 7 窗未前进）；`x.com` 直连 `000`、代理 `127.0.0.1:7897` **`200`**（推文页 125,980 B）。② A 轨 **0 新收**（5/5 已满，不凑第 6 篇）。③ B 轨 **+3 → 307**：Mask DINO `2206.02777`（**911**，CVPR 2023，DOI `10.1109/cvpr52729.2023.00297`；query embedding × 高分辨率像素图点积出掩码）/ ViT-22B `2302.05442`（**965**，QK-norm 压注意力 logit 过大）/ PaLM 2 `2305.10403`（**2,439**，配比 > 规模、深窄）；`id_list` 单批 `200` + atom（9,772 B / 3 entry）+ abs 3/3 `200`（42,570 / 47,645 / 64,215 B）+ OpenAlex 3/3 `200`；**先查重剔除** Position Interpolation `2306.15595` / InternVL `2312.14238`（已在表内）。④ 作者网 **+2 → 287**：#286 Ryan Hanrui Wang **B** `wang@nebius.com`（arXiv native HTML 脚注 `Correspondence to:`，420,247 B）/ #287 Feng Li **A** `fliay@connect.ust.hk`（本人主页 `mailto:`，24,341 B）；**#274 Weisen Jiang 待跟踪 → 已发信**（MetaMath 一作学生邮箱判失效 ⇒ 该论文唯一一封）；X 保持 **107**（补抓 `_onurmutlu_` / `RichardSSutton`；无登录态 ⇒ 不 follow、不假称已 follow）。⑤ 发信 **3 封**（累计 **125**，今日 9/12）：#123 VR-SparseQuant 中文 **153** 字 `SENT OK 06:04:11` / #124 Mask DINO 中文 **225** 字 `06:04:15` / #125 MetaMath 中文 **163** 字 `06:04:18`；地址发前当场复核 3/3 `200`；开头三样、问句句式互不相同；专属细节分别为「两条 2:4 稀疏流共享同一 FP4 预算 + 离线 scale-ratio 校准」「query embedding × 像素图点积、54.5 AP / 59.4 PQ」「多视角改写不改答案、GSM8K 66.4% / MATH 19.4%」。⑥ 回信率 **0 / 125**，**0 封到期**（最早 11-25，#1–#7）；通道只发不收。⑦ voice_ready **1**：Sutton 2026-11-07「Brute force computation is not enough for intelligence…」（主页内嵌 JSON × `og:description` 双源逐字一致；风险 3 条已标）；news_ready **0**（三条经典均无事件点）。⑧ 交付：`daily/2026-11-21.html`（06:00 节；div 17/17、table 14/14、tr 81/81、td 183/183、th 59/59、0 script、49,437 B）+ `daily/index.html` 当日行（307 / 287 / 125 / voice 2）+ `research/2026-11-21.md` + `PAPERS.md` #305–#307 + `AUTHORS.md` #286–#287 + `发送记录.md` §06:0x + #123–#125 行 + drafts/bodies 各 3。⑨ 记忆维护：把 11-20 的 09:0x / 06:0x / 03:0x 三条长流水 fold 至 `daily-memories-research/2026-11-20.md`（原文不改）。
- **2026-11-21（本地 00:3x · 00:00 时窗补轮 · 🅰 A 轨 3→5（今日 5/5）＋ 🅱 B 轨 +2 → 301 ＋ 作者网 +2 → 282 ＋ 0 封（累计 119）＋ 回信率 0/119）** —— **第二百二十五轮（补轮）**：① 网络：`cat:cs.CL&max_results=60` 直连 `200` / **158,680 B / 60 entry** / `application/atom+xml; charset=utf-8`；`published` 上界 **`2026-11-19T18:57:25Z`**（连续 5 窗未前进）；`x.com` 直连与代理均 **`200`**（较 00:00 轮的 000 已恢复），未做推文双源核验 ⇒ voice_ready 0。② A 轨补 2：VR-SparseQuant `2611.25717`（FP4 + 元素级 2:4 稀疏，两条稀疏流共享同一 FP4 预算 + 离线 scale-ratio 校准；30B-A3B 上 WikiText-2 **6.85 → 5.57**；VRFP4 kernel 对 BF16 **3.1× GEMM / 2.7× MoE**，加速绑死 Vera Rubin 指令）/ G-MTP `2611.25813`（单头多 token 预测草稿器 + target 激活注入 + 零拷贝 KV 跨注意力 + 聚类词表投影；Gemma 4 上 **3.1×** 服务端 / **2.3×** H100 / **2.2×** 手机 GPU；域迁移微调少 **1.83×** target 前向）；abs 2/2 `200`（41,408 / 42,383 B），两 ID 在 SEEN / papers.jsonl / 近 7 天 daily **0 命中**。③ B 轨 **+2 → 301**：Megatron-LM SC'21 `2104.04473`（**1,754**，SC 2021；交错 1F1B 吞吐 +10%、3072 卡 1T 参数 502 petaFLOP/s、单卡 52% 峰值）/ EVA `2211.07636`（**1,182**，CVPR 2023；掩码重建对齐特征、10 亿参数、初始化巨型 CLIP 视觉塔更稳）；`id_list` 批量 **`200` / 13,938 B / 5 entry**，其中 DINO `2104.14294` / `2209.14389` / `1909.08053` **已在表内** ⇒ 先查重后剔除；OpenAlex 2/2 `200`。④ 作者网 **+2 → 282**：#281 Deepak Narayanan **B** `dnarayanan@nvidia.com`（`deepakn94.github.io` `200` / 10,161 B 页内明文；`mailto:` 被 JS 混淆；无 X 链接 ⇒ 未找到）/ #282 Samir Khaki **未找到**（4 个候选主页 404/403 ⇒ 不猜）；X 保持 **107**。⑤ 发信 **0 封**（本时窗 3/3 已满，不跨窗借额度）。⑥ 回信率 **0 / 119**，0 封到期（最早 2026-11-25）。⑦ voice_ready 0 / news_ready 0（两篇均方法类，无大众事件点）。⑧ 交付：`daily/2026-11-21.html`（补到 5 篇；div 15/15、table 9/9、tr 51/51、td 111/111、th 42/42、0 script）+ `daily/index.html` 当日行改写 + `research/2026-11-21.md` 补轮节 + `SEEN.md` / `papers.jsonl` +2（JSON 校验通过）+ `PAPERS.md` #300–#301 + `AUTHORS.md` #281–#282。
- **2026-11-21（本地 03:0x · 03:00 时窗 · 🅰 A 轨 0 新收（今日 5/5 已满）＋ 🅱 B 轨第七十九轮 +3 → 304 ＋ 作者网 +3 → 285 ＋ 3 封（累计 122）＋ 回信率 0/122 ＋ voice_ready 1）** —— **第二百二十六轮**：① 网络：`cat:cs.CL&max_results=60`（`https` 直连 `--noproxy '*'`）`200` / **158,680 B / 60 entry** / `application/atom+xml; charset=utf-8`；`published` 上界 **`2026-11-19T18:57:25Z`**（连续第 6 窗未前进，仍在 72h 内）。`x.com` 直连与代理 `127.0.0.1:7897` 均 `200`（184,188 B），单条推文 `200` / 141,310 B。② A 轨 **0 新收**（今日 5/5 已满，不拿旧批凑第 6 篇）；候选登记 `2611.26084`（RLVR 成功覆盖阈值）/ `2611.26059`（Complete-SVD）/ `2611.26069`（SheetAlign）/ `2611.25588`（judge 刻度方向偏差）/ `2611.26275`（dLoop）留待 06:00。③ B 轨 **+3 → 304**：Large-Batch `1812.06162`（**543**，梯度噪声尺度 / 临界批量；预印本）/ RNN 训练困难 `1211.5063`（**5,097**，梯度范数阈值裁剪；预印本）/ Decision Transformer `2106.01345`（**2,596**，return-to-go 序列建模、无自举；`biblio.volume 34`）；arXiv `id_list` 2 批 + abs 5/5 `200`（43,826 / 41,068 / 43,191 B）+ OpenAlex 3/3 `200`（均 `type=preprint`）；**先查重剔除** GShard `2006.16668` / LoRA `2106.09685` / DINOv2 `2304.07193`（均已在表内）。④ 作者网 **+3 → 285**：#283 Aditya Grover **A** `adityag@cs.ucla.edu`（`aditya-grover.github.io` 的 `mailto:` percent-encoded 解码，`200` / 17,742 B）/ #284 Mathieu Salzmann **B** `mathieu.salzmann@epfl.ch`（EPFL 官方人员页 `200` / 36,341 B）/ #285 Sam McCandlish **未找到**（`mccandlish.github.io` 404、`anthropic.com/people/sam-mccandlish` 404 ⇒ 不猜）；**#281 Deepak Narayanan：只建档 → 已发信**；X 保持 **107**。⑤ 发信 **3 封**（累计 **122**，今日 6/12）：#120 DT（英文 **161** 词，`SENT OK 03:04:43`）/ #121 HiSA（**法文称谓问候 + 英文正文 190 词**，`03:04:47`）/ #122 Megatron-LM SC'21（英文 **179** 词，`03:04:51`）；三地址发前当场复核 3/3 `200`；落款两行其后无行、正文无项目名；开头句三样、问题句式互不相同；专属细节分别为 return-to-go 无自举 / RoPE 分解静态 hidden-dim 稀疏 + 约 1/3 QK 乘积 / 交错 1F1B +10% + 单卡 52% 峰值。⑥ 回信率 **0 / 122**，**0 封到期**（最早 2026-11-25，#1–#7）；`replies/` 仍只有 README 与诊断；通道只发不收。⑦ voice_ready **1**：Karpathy HackerTube（2026-11-01，`og:description` × 页内 `full_text` 双源逐字一致；43M HN 评论 → 6,454 视频；风险三条已标）/ news_ready **0**（三条经典论文均无大众事件点）。⑧ 交付：`daily/2026-11-21.html`（03:00 节：B 轨表 + voice_ready + 作者表 + 信件段 + news_ready 0 理由 + 6 线建议 + 附录）+ `daily/index.html` 当日行（304 / 285 / 122 / voice 1）+ `research/2026-11-21.md` 03:00 节 + `PAPERS.md` #302–#304 + `AUTHORS.md` #283–#285 + `发送记录.md` §03:0x + #120–#122 行 + drafts/bodies 各 3。⑨ 记忆维护：把 11-19 21:0x 长流水原文 fold 至 `daily-memories-research/2026-11-19.md`，MEMORY 保持 **25.9 KB**（<32 KB）。




- **2026-11-21（本地 00:0x · 00:00 时窗 · 🅰 A 轨 +3（今日 3/5）＋ 🅱 B 轨第七十八轮 +3 → 299 ＋ 作者网 +4 → 280 ＋ 3 封（累计 119）＋ 回信率 0/119）** —— **第二百二十四轮**：① 网络：`cat:cs.CL`（`https` 直连 `--noproxy '*'`）`200` / **109,971 B / 40 entry** / `application/atom+xml; charset=utf-8`；`published` 上界 **`2026-11-19T18:57:25Z`**，与 11-20 的 15:00 / 18:00 / 21:00 逐字相同 ⇒ 公告批本窗未前进；`x.com` 经 `127.0.0.1:7897` **`000`**，Mihomo `systemctl is-active`=active 但出口不通 ⇒ voice_ready 0。② A 轨 **+3（今日 3/5）**：AutoMaster `2611.26510`（Skill-FT 用自然语言技能抑制教师轨迹坏习惯，AutoMaster 闭环；4B/9B × Terminal/Search/SWE 比 vanilla SFT 平均 **+1.42–8.99 pp**，且 SFT 保留 skill 前缀在六个设置全部更好）/ MemFolder `2611.26427`（RecordFolder 实体锚点折叠 + ContextFolder 紧凑编码；Mem0 上 **50% 记录保留 99.0%** 平均性能、比最强基线 +1.9 pp）/ HiSA `2611.26363`（按 token 位置静态无参规则做 RoPE 隐藏维稀疏，只算约 **1/3 q·k**，训练不降反升，FA3 kernel + 代码开源）；三 ID 在 `SEEN.md` / `papers.jsonl` / 近 7 天 `daily/` **0 命中**。③ B 轨 **+3 → 299**：Horovod `1802.05799`（**1,619**，预印本；ring-allreduce + TF 最少改写）/ Deformable DETR `2010.04159`（**8,952**，`comment`=ICLR 2021 Oral；参考点稀疏采样、少 10× epoch、小目标更好）/ SigLIP 2 `2502.14786`（**1,832**，预印本；caption + 自监督 + 在线治理、原生宽高比/多分辨率）；arXiv `id_list` 单篇 3/3 `200` + atom + OpenAlex 3/3 `200`（查询日 2026-11-21）；PDF 30 s 内未下完 ⇒ 数字用 arXiv 摘要并标「未做 PDF 逐页复核」。④ 作者网 **+4 → 280**：#277 Xizhou Zhu **B** `zhuwalter@sensetime.com`（ar5iv HTML `200` / 267,916 B 脚注；2020 年地址疑失效 ⇒ 只建档不发）/ #278 Michael Tschannen **未找到**（`tschannen.github.io` `404`）/ #279 Xiaohua Zhai **未找到**（`xiaohuazhai.com` `000`）/ #280 Alexander Sergeev **未找到**（论文无邮箱）；**X 保持 107**（代理 000，不猜 handle）。⑤ 发信 **3 封**（累计 **119**）：#117 NeRF（`me@bmild.com`，英文 **181** 词，`SENT OK 00:04:19`）/ #118 Faster R-CNN（`ross.girshick@gmail.com`，**178** 词，`00:04:21`）/ #119 Quiet-STaR（`eric@humansand.ai`，**182** 词，`00:04:24`）；三地址发前当场复核（`bmild.github.io` 12,088 B / `~rbg/` 7,882 B / `ezelikman.github.io` 19,986 B，均 `200` + `mailto:` 明文）；落款均两行其后无行、正文无项目名、开头句与问句句式互不相同。⑥ 回信率 **0 / 119**，**0 封到期**（最早 2026-11-25，#1–#7）；`replies/` 只有 `README.md` 与诊断文档；通道只发不收。⑦ voice_ready **0** / news_ready **0**（X 000；三篇 A 轨均方法类、无大众事件点）。⑧ 交付：`daily/2026-11-21.html`（3 篇 + B 轨表 + 作者表 + 信件表 + 6 线建议 + 附录；div 11/11、table 7/7、tr 34/34、td 75/75、th 32/32、0 script、**19,289 B**）+ `daily/index.html` 当日行（tr +1 / td +5，平衡实测）+ `research/2026-11-21.md` + `SEEN.md` +3 + `papers.jsonl` +3 + `PAPERS.md` #297–#299 + `AUTHORS.md` #277–#280 + `发送记录.md` §00:0x + #117–#119 行。⑨ 记忆维护：把 11-20 15:00 的长流水原文 fold 至 `daily-memories-research/2026-11-20.md`（原文不改），MEMORY 保持 **28.6 KB**（<32 KB）。

- **2026-11-20（本地 18:0x · 18:00 时窗 · 🅰 A 轨 0 新收（今日 5/5 已满）＋ 🅱 B 轨第七十六轮 +4 → 292 ＋ 作者网 +2 → 271 ＋ 0 封信（今日 12/12 满，备 11-21 两封）＋ 回信率 0/116）** —— **第二百二十二轮**：① 网络：`cat:cs.CL`（`https` 直连 `--noproxy '*'`）`200` / **109,971 B / 40 entry** / `application/atom+xml; charset=utf-8`；`published` 上界 **`2026-11-19T18:57:25Z`**，与 15:00 **逐字相同** ⇒ 本窗未前进。② A 轨 **0 新收**：新批前 12 条 `SEEN.md` 全 0 命中；另用 `id_list` 核出其中 7 条标题（`2611.26514` 马拉地语政务检索 / `2611.26509` GLiDE 蒸馏决策模型 / `2611.26492` 胸片报告多模态纠错 / `2611.26398` 水务治理知识 / `2611.26358` Beam 技术报告 / `2611.26336` 孟加拉语幻觉基准 / `2611.26317` 目标语言抽取）⇒ 多为低相关，11-21 仍优先 agent / 长上下文 5 条。③ B 轨 **+4 → 292**：ELECTRA `2003.10555`（**5,109**，`comment`=ICLR 2020）/ Faster R-CNN `1506.01497`（**80,700**，TPAMI 39(6):1137–1149, 2017）/ Mask R-CNN `1703.06870`（**7,047**，TPAMI 42(2):386–397, 2020）/ SAC `1801.01290`（**13,567**，`comment`=ICML 2018、OpenAlex biblio pp. 1861–1870）；arXiv `id_list` 4/4 `200` + atom（**9,733 B / 4 entry**）+ OpenAlex **4/4 `200`**；四 ID 此前只在候选池注释 ⇒ 转正无重复。④ 作者网 **+2 → 271**：#270 Georgia Gkioxari **A** `georgia.gkioxari@gmail.com`（`gkioxari.github.io` `200` / 44,977 B，页内明文 Caltech 职衔）/ #271 Ross Girshick **A** `ross.girshick@gmail.com`（`www.rossgirshick.info` `200` / 7,882 B；机构未核到 ⇒ 不写现雇主）；未找到（不猜）：Dollár（`404`）/ Luong（停放页）/ K. Clark（无明文邮箱）/ Manning（`000`）/ Haarnoja / A. Zhou / S. Ren。⑤ 发信 **0 封**（今日 **12/12** 满），备 11-21 **两封**：`drafts/2003.08934.md`（Neural 5D 辐射场，181 词）+ `drafts/1506.01497.md`（候选框成本，**178** 词）；落款均两行其后无行，正文无项目名，开头句与问句句式互不相同。⑥ 回信率 **0 / 116**，**0 封到期**（最早 11-25）；`replies/` 只有 `README.md`；通道只发不收。⑦ 交付：`daily/2026-11-20.html`（+18:00 节；div 75/75、table 39/39、tr 188/188、td 366/366、th 192/192、0 script、106,944 B）+ `index.html` 当日行 + `research/2026-11-20.md` §25–§28 + `PAPERS.md` #289–#292 + `AUTHORS.md` #270–#271 + draft/body 各 1。
- **2026-11-20（本地 12:0x · 12:00 时窗 · 🅰 A 轨 0 新收（今日 5/5 已满，但公告批 8 窗后首次前进）＋ 🅱 B 轨第七十四轮 +4 → 284 ＋ 作者网 +5 → 265 ＋ 2 封（累计 116）＋ 回信率 0/116）** —— **第二百二十轮**：① 网络：`cat:cs.CL`（`https` + `--noproxy`）`200` / **98,779 B / 40 entry** / atom，`published` 上界由 `2026-11-18T18:56:12Z` 前进到 **`2026-11-19T04:26:13Z`**（`http` 端点 `301`）；B 轨 `id_list` 三批全 `200` + atom（9,914 B / 6,252 B / 2,359 B）。② A 轨 0 新收：新批 20 ID 在 `SEEN.md` 0 命中，但今日 5/5 已满 ⇒ 不超额不替换，登记 4 个 11-21 候选（`2611.25433` RoCoKV / `2611.25429` Evolve Where It Matters / `2611.25289` / `2611.25191`）。③ B 轨 +4 → 284：PaLM-E `2303.03378`（**4,143**）/ 3DGS `2308.04079`（**12,239**，ACM TOG）/ Magicoder `2312.02120`（**416**，<500 按「方法论常青」）/ SGDR `1608.03983`（**11,502**，ICLR 2017）；OpenAlex 4/4，数字取自 arXiv 摘要，未做 PDF 逐页复核。④ 作者网 +5 → 265（#261 Driess A / #262 Kerbl A / #263 Drettakis A / #264 Yuxiang Wei A / #265 Hutter 无地址不发）；X 仍 106。⑤ 发信 2 封 → **116**（今日 12/12 满）：#115 **德语称谓 + 英文 178 词** `12:04:38` / #116 **中文 221 字** `12:04:44`；落款两行其后无行、正文无项目名、同轮零共用。⑥ 回信率 **0/116**，0 封到期（最早 11-25）；新增观察：两封对象均已换机构（Ji Lin→OpenAI、Yuxiang Wei→Meta）⇒ 下轮起台账加「地址新鲜度」列。⑦ voice 0 / news 0。⑧ 交付：`daily/2026-11-20.html`（+12:00 节；div 59/59、table 27/27、tr 124/124、td 280/280、th 126/126、0 script、0 残留 `**`，79,279 B）+ `index.html` + `research/2026-11-20.md` §17–§20 + `PAPERS.md` #281–#284 + `AUTHORS.md` #261–#265 + `发送记录.md` §12:0x + drafts/bodies 各 2。⑨ 更正 2 处 ID：PaLM-E `2403.03378`→`2303.03378`；SpeechT5 `2010.00718` 为无关统计论文 ⇒ 本轮未收。

- **2026-11-19（本地 21:0x · 21:00 时窗）** —— 第二百一十五轮（B 轨 +4 → 264 / 作者网 245 / 信 0）；原文已 fold 至 `daily-memories-research/2026-11-19.md`「归档 · MEMORY 滚动（第七十九轮折出）」。



- **2026-11-18（本地 12:1x · 12:00 时窗）** —— **第二百零三轮**：B 轨 +3 → 222 / 作者网 203 / 信 90 / H4 启动；细节已 fold 至 `daily-memories-research/2026-11-18.md`。

- **更早轮次（2026-11-12 ~ 2026-11-16，r152–r183）**：原文已按 §5 滚动归档 → `daily-memories-research/` 各日文件的「归档 · MEMORY 滚动」段（2026-11-13 / 14 / 15 / 16 等），此处只留指针，勿以指针替代结论。

## 3. 记忆维护（硬性）

- **上限 ≤ 32KB**；超限把**较早的流水条目**（保留最近 ~20 条）**追加**到 `daily-memories-research/<条目日期>.md`（原文不改），再从本文件删除。
- **顶部必须保留**：① `WAITING:` 行 ② 「进度快照」 ③ 「运维问答」 ④ 最近 ~20 条流水。
- **归档不改变任何结论**。
