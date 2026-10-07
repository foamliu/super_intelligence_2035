# INDEX_FILES — news/signal 文件清单（第11批 · R1）

> 由人工/脚本登记。体积纪律（2026-10-05 修订）：**单文件 ≥ 5 MB → 🚫 不入 git**（改走网盘）。
> 「存放位置」= `git` 或 `本地/未上云`。本目录**全部 < 5 MB ⇒ 入 git**。
> 登记列：路径 / 行数 / 大小(B) / sha256(前16) / 存放位置。

| 路径 | 行数 | 大小(B) | sha256(前16) | 存放位置 |
|:--|--:|--:|:--|:--|
| `signal/lag_corr.csv` | 23941 | 4018511 | `83d3bf349be52251` | git |
| `signal/prices/`（38 个 JSON，合计） | — | 2560273 | `c711347086cd3e05`¹ | git |
| `signal/fetch_prices.py` | 306 | 13836 | `2716603285212c33` | git |
| `signal/lag_corr.py` | 546 | 24745 | `961a423b3905381c` | git |
| `signal/PREREG.md` | 139 | 10346 | `967d7a43619c26c2` | git |
| `signal/SOURCE_TEST.md` | 55 | 5074 | `bc23d4ef5eded7af` | git |
| `signal/LAG_CORR.md` | 86 | 6177 | `777c237df23c91e5` | git |

> ¹ `prices/` 的 sha256(前16) = **对 `prices/*.json` 逐文件 sha256 排序后再 sha256**（目录级指纹），共 38 个文件。
> `lag_corr.csv` / `LAG_CORR.md` 为**生成物**，随 `lag_corr.py` 每次运行覆盖（sha 会变）；此处记录 R1 首版指纹。
