# Deep-read: 1793784554206_v23sb (xinqiaoz / hfeg0pkn004 / 10.129.2.11)

- **session**: `1793784554206_v23sb` (mc=366, 240 msgs / 979 KB / 9 user_inputs)
- **user/host**: xinqiaoz / hfeg0pkn004 (10.129.2.11)
- **keywords**: pdk:1011; drc:576; calibre:281; lvs:13; cmos:7; pex:5; analog:1; .spi:1
- **domain**: physical_verify (PDK runset release-note tooling for StarRC extraction decks)
- **档位**: B档 synthesized（faithful-seed = turn 3，user 提需求未给根因/方案）

## 用户意图流（9 user turns）

| # | msg | ts | 类型 | 摘要 |
|---|---|---|---|---|
| 1 | 0 | 1793774945620 | 探索 | "探索 /home/pdk/hbpeng/code/scriptDevelop/tools/ 主要是 genReleaseNote.py 做什么" |
| 2 | 9 | 1793775130770 | 探索 | "genReleaseNote.py 是单独文件吗？用到其他 py 吗？" |
| 3 | 16 | 1793775786119 | **提需求(种子)** | "仿照 huobin.peng 写法做 starrc 版 genReleaseNote.py，改两处：① 扫描目录 calibre→starrc/{平台}/data/{版本} ② 发信收信人都改为 xinqiao.zhou@cxmt.com" |
| 4 | 38 | 1793776791470 | 推进 | "先写一版本执行，看能否收到邮件，放 .tmp 目录" |
| 5 | 214 | 1793779008701 | 调试 | "邮件发送时间和主题？我没收到" |
| 6 | 216 | 1793779269974 | **接受** | "的确收到了。starrc note 和 calibre genReleaseNote.py 能否合并？" |
| 7 | 218 | 1793779418443 | 讨论 | "公共类重复多吗？多少行？" |
| 8 | 232 | 1793779794244 | 讨论 | "暂时先不合并。genReleaseNote.py 是自己写的还是 AI 写的？给证据" |
| 9 | 238 | 1793784563305 | 讨论 | "说说 calibre/ 和 starrc/ 目录区别" |

**种子选择理由**：turn 3 是「提需求/表达目标」轮，user 提出构建新工具的目标（仿照现有模板做 starrc 变体，2 处明确修改），未给根因或修复方案。符合 A档/B档-faithful-seed 选轮规则。

## 助手工具链（turn 3 → turn 6 接受）

1. **探索目录差异**（msg 17-37）：list_allowed_files + read_files 对比 calibre (`{平台}/current/{product}/{version}/readme`) vs starrc (`{平台}/data/{version}/releasenotes.starrc`)；识别特例 cxmtV2B（无 data/ 层）、TSI/mars/LDDB（嵌套）。
2. **写代码**（msg 39-188）：用 editor 分段写入 `.tmp/genStarrcReleaseNote.py`（614 行，7 类 + main）；多次因 editor 6000 字符上限被迫分段，期间出现残片/类被覆盖，反复 read_files 定位 + editor 修复，最终 rm 后重建。
3. **语法检查 + dry-run**（msg 189-192）：`python3 -m py_compile` + `--dry-run` 扫描 40 平台 / 21 新版本（10/01~11/04 范围）。
4. **正式发信**（msg 205-212）：`autoMail` (IMCP) 发送到 xinqiao.zhou@cxmt.com，附件 `starrc_release_note_sample.xlsx`，主题 `[Release Note] StarRC Runset-2026-11-04 (10/01-11/04)`。
5. **user 接受**（msg 216）："的确收到了"。

## 交付物结构（genStarrcReleaseNote.py）

7 个类 + main()，仿 huobin.peng OOP v2.0 风格：
- `StarrcReleaseNoteParser` — 解析 `releasenotes.starrc`：`## V{ver} - {YYYYMMDD}` 版本头 + 变更行（过滤 `**`/`*` 参考文档行，如 `** EDR Table:`）
- `PlatformScanner` — 扫描 starrc 目录：`scanDataDir`（主流 `{平台}/data/{版本}`）+ `scanFlatDir`（cxmtV2B 风格 `{平台}/{版本}`）+ `scanNestedDir`（TSI/mars 嵌套）
- `CacheManager` — JSON 缓存已报告版本（避免重复推送）
- `EmailFormatter` — HTML 表格邮件正文（`_html_escape` + 平台/版本/时间/变更列）
- `ExcelGenerator` — openpyxl 生成 .xlsx 报表（可选依赖，try/except）
- `MailSender` — subprocess 调用 IMCP autoMail 发信
- `StarrcReleaseNoteApp` — 编排器：scan → parse → filter(cache) → format → send
- `main()` — argparse: `--dry-run` / `--receiver` / `--output` / `--base` / `--cache`

**关键常量**：
- `RUNSET_BASE = /apps/imctf/runset/starrc`（可 --base 覆盖）
- `DEFAULT_RECEIVER = xinqiao.zhou@cxmt.com`
- `DEFAULT_SUBJECT = [Release Note] StarRC Runset-{date} ({range})`

## 真实 starrc 目录结构（.75 实测）

```
/apps/imctf/runset/starrc/
  cxmt10G2_LP/data/0.0.1/releasenotes.starrc   # 主流: {平台}/data/{版本}/releasenotes.starrc
  cxmt10G3/data/0.0.3/releasenotes.starrc
  cxmtV2B/V2B_itf_drvqa_v0d1_Rev01/releasenotes.starrc  # 特例: 无 data/ 层
  TSI/TSI1.0/TSI_LPE_v0d9_rev03/releasenotes.lpe        # 嵌套 + 不同扩展名
```

**releasenotes.starrc 格式**：
```
///////// Copyright header /////////
**************** Reference-Doc Version ****************
** EDR Table:         V0.1                           **
*******************************************************
// Revision History:
## V0.0.1 - 20221018
// 1) Develop based on cxmt10G3_LP v0.1.9;
// 2) M0 Rs change from 12 to 15 based on EDR v0.00;
```

## 合成计划（B档）

- **任务**：构建 starrc release-note 生成器（仿 calibre 模板，2 处修改：扫描目录 + 收件人）
- **assets A（可见）**：合成小型 starrc_runset_A（2 平台 × 2 版本）+ 合成 calibre genReleaseNote.py 模板
- **hidden B**：starrc_runset_B（3 平台 × 7 版本，不同平台名/版本/内容）
- **check.py**：14 条件 a-n，subprocess 跑 `--dry-run --base <hidden_B>` 验输出结构 + AST 静态校验类/参数/常量 + 退化提交回归
- **negatives**：empty_shell / print_expected / core_deleted（删 PlatformScanner）+ negative_selftest
