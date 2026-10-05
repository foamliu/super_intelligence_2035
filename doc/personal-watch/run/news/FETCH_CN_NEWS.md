# FETCH_CN_NEWS.md — 中文权威源统一入口 `fetch_cn_news()`（T10）

> 交付物位置：`news/mcp_web_search_free.py`（并入原免 key MCP 模块，**新增** `fetch_cn_news()` / `cn_news_report()` + MCP 工具 `cn_news` + CLI `--cn-news`）。
> 目的（第 6 批运维指令 T10）：把**已实测的中文「活/死源」名单固化成统一入口**，避免每轮现拼；**CLI 直调是一等公民**（当前 MCP 未装进 cline）。
>
> 🆕 **第 10 批 A 线更新**：`web-search` / `web-search-free` **已装进 cline**（详见 `news/MCP_INSTALL.md`）。但**新增的 `mcp_ddgs` 免费搜索后端 8/8 被墙、本机不可用** → **日常取数仍以本文件 `cn_news` + 官方 RSS 为一等公民**；`fetch_cn_news()` 的调用方式与口径**不变**。
> 相关：`news/API_COMPARISON.md`（源调研）、`news/2026-10-03.md`（第三轮中文真新闻）、`WATCH_NEWS_TASK.md`（§0.1 判据 + T8/T9/T10）。

---

## 1. 用法（3 种调用方式）

### 1.1 CLI 直调（**首选**，MCP 未装进 cline 时）

```bash
# 人类可读：条目 + 各源新鲜度 + 丢弃原因
python3 news/mcp_web_search_free.py --cn-news --limit 30

# JSON（含 meta：各源 status / content_type / kept / dropped）
python3 news/mcp_web_search_free.py --cn-news --limit 30 --json

# 自定义新鲜度窗口（默认 72h）
python3 news/mcp_web_search_free.py --cn-news --limit 50 --max-age-hours 24
```

### 1.2 MCP 工具 `cn_news`（装进 cline 后）

```jsonc
// 并入运行机 cline 的 cline_mcp_settings.json 后，可调用：
//   工具：cn_news
//   参数：{ "limit": 30, "max_age_hours": 72 }
```

### 1.3 Python 直调（供其它脚本复用）

```python
import sys; sys.path.insert(0, "news")
import mcp_web_search_free as m

res = m.fetch_cn_news(limit=30)          # → {"items": [...], "meta": {...}}
for it in res["items"]:
    print(it["published"], it["source"], it["title"], it["url"])

print(m.cn_news_report(limit=30))                     # 人类可读报告字符串
print(m.cn_news_report(limit=30, as_json=True))       # JSON
```

---

## 2. 返回结构（统一、可直接落盘）

```jsonc
{
  "items": [
    {
      "title": "OpenAI披露澳大利亚又一政府机构遭入侵",
      "source": "央视网",                          // 媒体名（中新网 / 联合国新闻 / 央视网）
      "url": "https://news.cctv.com/2026/10/03/ARTI3jDXniV5jQDx59hwBf6y261003.shtml",
      "published": "2026-10-03T01:14:00+00:00",    // ISO8601（UTC）
      "lang": "zh",
      "type": "news",
      "snippet": "当地时间10月2日，美国开放人工智能研究中心（OpenAI）披露…"  // 便于落盘摘录
    }
  ],
  "meta": {
    "generated": "2026-10-03T06:08:01.366581+00:00",
    "per_source": [ { "source": "...", "url": "...", "kind": "rss|cctv-jsonp",
                      "status": 200, "content_type": "...", "kept": 30, "dropped": ["原因…"] } ],
    "dropped_total": 83
  }
}
```

- **排序**：按 `published` **倒序**；**去重主键** = `url`（去 query）。
- **`source` 写媒体名**（非域名）；`lang` 固定 `"zh"`；`type` 固定 `"news"`。

---

## 3. 源清单（固化的「活 / 死」名单）

### 3.1 ✅ 活源白名单（`CN_LIVE_SOURCES`，只接这三类）

| 媒体名 | 源 | 类型 | 说明 |
|:--|:--|:--|:--|
| 中新网 | `https://www.chinanews.com.cn/rss/scroll-news.xml` | rss | 即时（当日持续更新） |
| 中新网 | `https://www.chinanews.com.cn/rss/world.xml` | rss | 国际 |
| 中新网 | `https://www.chinanews.com.cn/rss/finance.xml` | rss | 财经 |
| 联合国新闻 | `https://news.un.org/feed/subscribe/zh/news/all/rss.xml` | rss | ⚠️ **URL 必须写死正确值**（`news.un.org/zh/rss` 会 **404 返回 HTML**） |
| 央视网 | `https://news.cctv.com/2019/07/gaiban/cmsdatainterface/page/news_1.jsonp` | cctv-jsonp | 站内接口（页面 JS 渲染，数据源在此） |
| 央视网 | `https://news.cctv.com/2019/07/gaiban/cmsdatainterface/page/tech_1.jsonp` | cctv-jsonp | 站内接口（科技） |

### 3.2 🔴 死源黑名单（`DEAD_SOURCES`，**永不请求**）

| 源 | 实测内容停更 |
|:--|:--|
| 新华网 `www.xinhuanet.com/{tech,politics,world}/news_*.xml` | **停在 2022** |
| 新华网 `www.xinhuanet.com/english/rss/*` | **停在 2017/2018** |
| 人民网 `www.people.com.cn/rss/*.xml` | **停在 2021/2024** |
| 央视 `www.cctv.com/program/rss/*` | **停在 2006/2007** |

> 🧠 **核心教训**：**「接口 200」≠「有新闻」** —— 死源照样返 200 / 300 条。本入口**内建 `pubDate ≤ 72h` 校验 + `Content-Type` 校验**，从机制上杜绝旧闻充数。
> （新华 / 人民 / 央视若要实时内容，须走「网页列表页 / 站内接口」并校验页面日期 —— 央视网已按此法接入。）

### 3.3 📎 补充：中文 dated 源（**不入本入口**，供常态采集用 `rss_latest` 单独取）

| 媒体名 | 源 | 说明 |
|:--|:--|:--|
| 量子位 | `https://www.qbitai.com/feed` | AI 纵深报道；**2026-10-03 实测 `200` + 带 `pubDate`**（WordPress RSS）。 |
| IT之家 | `https://www.ithome.com/rss/` | 科技产业；**实测 `200` + 带 `pubDate`**（首发轮即已用）。 |

> ⚠️ 依 **T10** 规定，`fetch_cn_news()` **只准聚合三类已实测活源**（中新网 / 联合国新闻 / 央视网），
> 故上表两源**不并入 `CN_LIVE_SOURCES`**；常态采集时以 `rss_latest(...)` 单独取得，用于**中文补强（T6）**。

---

## 4. 内建硬规则（写进代码）

1. **死源黑名单** → **永不请求**（`DEAD_SOURCES` 仅作文档 / 输出提示用）。
2. **`pubDate ≤ 72h` 校验**：超龄 → **丢弃**；**解析不到日期 → 丢弃**（🚫 **不许用「抓取时间」冒充发布日期**）。
3. **`Content-Type` 校验**：RSS 源须为 `application/rss+xml` / `text/xml` / `application/xml` / `application/atom+xml`，否则（拿到 HTML / 404）**判源失败并记录**（🚫 不许静默当"无新增"）。
   - 央视网 JSONP 源 `Content-Type` 为 `text/html`（正常）→ 改以 **「能否解析出 `JSONP.data.list`」** 作校验；解析失败即判源失败并记录（**等价**达到校验目的）。
4. **UA**：`Mozilla/5.0 (compatible; PersonalWatch/1.0)`（通用防御性措施）。
5. **单源失败降级**：每个源各自 `try/except`，失败写进 `meta.per_source`，**整轮绝不因一个源卡死**。

---

## 5. 自测证据（T10「必交证据」· 真实跑一次）

**命令**（2026-10-03）：

```bash
cd /home/liuyang/super_intelligence_2035/doc/personal-watch/run/news
python3 -m py_compile mcp_web_search_free.py && echo 'COMPILE OK'
python3 mcp_web_search_free.py --cn-news --limit 30
```

**原始输出（节选 · 前 5 条）**：

```text
COMPILE OK
[cn_news] 生成 2026-10-03T06:08:01.366581+00:00 ｜ 新鲜度窗口 ≤72h ｜ 活源 6 个
命中 30 条（按发布时间倒序）：

1. 新业态催生"文旅+"新玩法 "花样"新场景绘就假日新消费图鉴
   🔗 https://news.cctv.com/2026/10/03/ARTIrwkq3qk0aUcrMrnEYYXP261003.shtml
   🏷 来源：央视网 ｜ 发布：2026-10-03T06:00:01+00:00 ｜ lang=zh type=news
   摘要：在贵州、广东、新疆、山西等地，国庆假期，景区陆续迎来游客高峰。…

2. 第九届纽约中国当代音乐节开幕
   🔗 http://www.chinanews.com.cn/tp/hd2011/2026/10-03/1206857.shtml
   🏷 来源：中新网 ｜ 发布：2026-10-03T05:57:48+00:00 ｜ lang=zh type=news

3. 假日服务台·出行 | 假期第三天旅游出行热度居高不下 客流持续高位运行
   🔗 https://news.cctv.com/2026/10/03/ARTIYTOydYEWtDGdbWxFJlJl261003.shtml
   🏷 来源：央视网 ｜ 发布：2026-10-03T05:51:12+00:00 ｜ lang=zh type=news

4. 文化"圈粉"、"进货式"旅游 中国游"立体化出圈"吸引海外游客
   🔗 https://news.cctv.com/2026/10/03/ARTI3bc7T76ztASRfA6GeXRR261003.shtml
   🏷 来源：央视网 ｜ 发布：2026-10-03T05:49:10+00:00 ｜ lang=zh type=news

5. 澳大利亚发生汽车冲撞人群事件致9人受伤
   🔗 https://www.chinanews.com.cn/gj/2026/10-03/10707443.shtml
   🏷 来源：中新网 ｜ 发布：2026-10-03T05:46:17+00:00 ｜ lang=zh type=news
   …
```

**原始输出（节选 · 各源状态 / 新鲜度 / 丢弃）**：

```text
—— 各源状态 / 新鲜度 / 丢弃 ——
• 中新网 <rss>        status=200 ct='text/xml'                           kept=30 dropped=0
• 中新网 <rss>        status=200 ct='text/xml'                           kept=30 dropped=0
• 中新网 <rss>        status=200 ct='text/xml'                           kept=30 dropped=0
• 联合国新闻 <rss>    status=200 ct='application/rss+xml; charset=utf-8' kept=18 dropped=12
    - 超龄 90.1h>72h：'人权高专谴责缅甸若开邦市场致命空袭'
    - 超龄 90.1h>72h：'产权组织全球创新指数：瑞士、瑞典、美国等位居前列'
    - 超龄 90.1h>72h：'难民署：830万人面临失去关键援助风险'
    - 超龄 90.1h>72h：'刚果（金）东部冲突外交努力仍在进行 局势依然严峻'
    …
• 央视网 <cctv-jsonp> status=200 ct='text/html'                          kept=80 dropped=0
• 央视网 <cctv-jsonp> status=200 ct='text/html'                          kept=9  dropped=71
    - 超龄 76.4h>72h：'"雪龙"号、"雪龙2"号凯旋！中国第16次北冰洋…'
    - 超龄 88.5h>72h：'我国科学家研发出单光束多维光存储新技术'
    - 超龄 89.6h>72h：'我国生成式人工智能用户规模突破7亿人！最新报告发…'
    …

丢弃合计：83 条（原因见上）
死源黑名单（永不请求）：www.xinhuanet.com/{tech,politics,world}/news_*.xml（内容停在 2022） ；… ；www.cctv.com/program/rss/*（停在 2006/2007）
```

**结论**：6 个活源 **全部 200**；**≥1 条带 ISO8601 日期的真实新闻**（共 30 条）；**各源新鲜度**与**被丢弃条数 / 原因**均已如上列出。

---

## 6. 本轮实跑用于采集的产出

- 从上述 30+ 条中按 **§0.1** 筛出**中文权威源真新闻 4 条**（央视网 2 + 中新网 2），落盘于 `news/2026-10-03.md` **「三、第三轮 · 中文权威源真新闻（T9）」**。
- 与第三轮 2 条英文真新闻合计 → **中文 ≥ 英文**（T9.5 配比要求达成）。