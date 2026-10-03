# ENDPOINTS.md — 历史端点勘察表（A1 产物）

> **状态：⬜ 未开始**（等 archive 线首轮唤醒）。
> 要求：逐个实测并**贴 HTTP 码 + Content-Type + 条目数/样本 URL**；403/405/WAF **如实记录**（含响应片段），**不要绕**。

## supervisor 的种子实测（2026-10-03，需本线复核）

| 源 | 端点 | 能否枚举 | 实测 |
|:--|:--|:--|:--|
| 中新网 | `https://www.chinanews.com.cn/scroll-news/{YYYY}/{MMDD}/news.shtml` | ✅ 待复核 | **200 text/html**（173–378 KB）；条目链接 `/{频道}/{YYYY}/{MM-DD}/{id}.shtml` |
| 新华网 | 日期路径 `http://www.news.cn/politics/2016-01/01/` | ❓ | **403** |
| 新华网 | 检索 `https://so.news.cn/getNews?...` | ❓ | **405** + WAF 反爬页 |
| 央视网 | `https://news.cctv.com/2016/01/01/` | ❓ | **403** |
| 新华网 | 首页 / 时政频道 | ✅ 可达 | **200**（但未验证"能否按历史枚举"） |
| 人民网 | ? | ❓ | 未测（注意：其 RSS 是**死源**，停在 2021/2024） |

## 待试候选（A1）

- **新华网**：频道分页（`/{channel}/index_2.htm`）· 日期变体（`/{channel}/{YYYYMMDD}/`）· 站内检索 XHR · `sitemap.xml` / `robots.txt`。
- **人民网 / 央视网**：同上各试一轮。
- **中新网**：复核 + 边界（月末 / 跨年）+ 分页 `news_2.shtml`。
