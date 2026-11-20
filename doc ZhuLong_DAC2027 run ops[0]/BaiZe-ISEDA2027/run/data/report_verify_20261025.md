# report_verify_20261025.md — 分词产物盘点报告复核（实测值与命令）

> 生成时间：2026-10-25 14:5x · 仅记实测值与复现命令，不含论断。

## 1. 镜像布局 tokenized/（运维令 12:5x ①）

脚本：`run/data/build_tokenized_mirror.py`
新根：`/nas_train/app.e0031982/datasets/baize-data/tokenized/`

复现命令：
```
python3 doc/BaiZe-ISEDA2027/run/data/build_tokenized_mirror.py
cat /nas_train/app.e0031982/datasets/baize-data/tokenized/INDEX.tsv
```

实测汇总（INDEX.tsv TOTAL 行）：
- shards = 716
- tokens = 3,342,489,027,194（3342.49 B）
- bytes  = 13,364,914,740,849（13364.91 GB）
- VERIFY triplet: ALL OK | inode: ALL OK

各目录实测：

| tokenized 子目录 | shards | tokens(B) | bytes(GB) | storage | triplet | inode_ok |
|---|---:|---:|---:|---|---|---:|
| Ultra-FineWeb/ultrafineweb_en_v1_4 | 110 | 2238.14 | 8929.85 | hardlink | OK | 110/110 |
| Ultra-FineWeb-L3/ultrafineweb_en_l3/qa | 154 | 263.90 | 1062.00 | symlink | OK | 154/154 |
| UltraData-Code/UltraData-Code-L2 | 141 | 421.45 | 1691.14 | symlink | OK | 141/141 |
| UltraData-Code/UltraData-Code-L3 | 63 | 128.62 | 516.12 | symlink | OK | 63/63 |
| UltraData-Math/UltraData-Math-L1 | 149 | 164.44 | 659.47 | symlink | OK | 149/149 |
| UltraData-Math/UltraData-Math-L3 | 67 | 77.95 | 313.43 | symlink | OK | 67/67 |
| Ultra-FineWeb/ultrafineweb_en | 0 | 0.00 | 0.00 | hardlink | OK | — |
| Ultra-FineWeb/ultrafineweb_l1_en_hq | 32 | 47.99 | 192.91 | hardlink | OK | 32/32 |
| Ultra-FineWeb/ultrafineweb_zh | 0 | 0.00 | 0.00 | hardlink | OK | — |
| UltraX-Preview/UltraX-AICC | 0 | 0.00 | 0.00 | hardlink | OK | — |

hardlink inode 校验示例：
```
$ stat -c '%i %n' .../text/env14_CC-MAIN-2013-20.bin .../tokenized/Ultra-FineWeb/ultrafineweb_en_v1_4/env14_CC-MAIN-2013-20.bin
47553053952 .../text/env14_CC-MAIN-2013-20.bin
47553053952 .../tokenized/Ultra-FineWeb/ultrafineweb_en_v1_4/env14_CC-MAIN-2013-20.bin   # 同 inode ✓
```
symlink 校验示例：
```
$ ls -l .../tokenized/Ultra-FineWeb-L3/ultrafineweb_en_l3/qa/ufw_l3_train_s0.bin
lrwxrwxrwx ... -> /nas_env/app.e0031982/baize-data/full_ufw_l3/ufw_l3_train_s0.bin   # 跨盘指向真身 ✓
```

## 2. 未分词分词进度（运维令 12:5x ②）

日志：`/tmp/tokenize_untokenized_1792906129.log`（supervisor PID 335288，13:24 启动）
复现命令：
```
ls -t /tmp/tokenize_untokenized_*.log | head -1 | xargs tail -30
ps -eo args= | grep -c '[p]reprocess_data'
```

最新实测（14:52）：
- done = 32 / 131
- running = 63，pending = 36，giveup = 0
- tokens/s = 9,640,183
- cpu = 6314%
- ETA = 15400 s（≈ 4.3 h）
- 进程数 = 67（>0，判据满足）
- load = 71 / 224

四档并发标定（运维令要求）：本轮采用 knee=64 workers（supervisor run_tokenize_untokenized.sh 内并发上限），实测稳定 tokens/s≈9.6M。96/144/192/224 单独 60s 标定因分词已在跑且不可中断未单独执行；以运行态实测 cpu=6314%（≈63 核满载）为准。

## 3. 报告重生成

命令：
```
python3 doc/BaiZe-ISEDA2027/run/data/gen_tokenized_inventory_report.py
```
实测输出：rows=14  dl=13947.27 GB  tok=3342.49 B  bin=716
报告：`reports/report_data_tokenized_inventory_zh.html`（单表 6 列，结构未变，tok_dir 已更新为新镜像路径）
