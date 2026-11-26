# r235 选料轮（shard C）· 0 case · DEBT:2 真外部阻塞

> 日期 2026-11-08；r234 选料轮 0 case DEBT:1，本轮补 DEBT 选料，遇跨 shard 撞库 + path bug，0 case。DEBT:2。

## 关键发现 ① path bug（推翻 r234「scan 陈旧」结论）
- scan summary 的 session_file（basename）→ 实际路径是**嵌套** `/home/<u>/.cline/data/sessions/<id>/<id>.messages.json`，不是根目录。
- r234 + r235 早期用根 glob `ls .../sessions/*.messages.json` 查 existence 全返回空（误判"session 已从 host 清理"）。
- 改用 `find .../sessions -name "*.messages.json"` 后发现大量 user session **仍在**：
  - hfeg0pkn002: lizwen 45·kaixuanx 11·adaml 27·tongni 28
  - hfeg0pkn004: e0039602 83·e0044587 47·lorikx 48·thomasz 36·xxchen 34·clarawu 30·jcgu 28·jiangbaol 15·e0014036 10·e0030760 14
  - hfeg0pkn005: rongjiez 77·e0046686 24·jinsongl 22·t0002987 34·e0045128 18·e0014566 262(saturated)·ellawu 50(saturated)
  - hfeg0plg37: miccao 56(saturated)·oshen 8
  - hfeg0plg65: e0030085 8·yan1zh 4·yuhzhu 5·stephens 3
- **r236 选料必须用嵌套 find 验 existence**。

## 关键发现 ② 跨 shard 撞库（748ox = shard A 的 case）
- top1 calibre 候选 **748ox**（johnl@hfeg0pkn001, mc=226, calibre=298 innovus=10, 1.36MB, 189 msgs, agent=lead）。
- 用户 U#1 原话：`/proj/drcoa/V0/ver/pex/johnl/T_IsmTop 这个文件夹抽IsmRCC失败了 说是buffer底层没map vbn 到vss vbp 到vcc 要改cdl你改下记得 对所有目录下到文件的修改都要比较修改前后确保合适修改没问题 修改并完成RCC抽取`。
- assistant 189 步：写 ~20 个 Python 脚本(inspect_cdl/grep_logs/analyze_spf/check_mtime/grep_lvs/analyze_layout/trace_buf/list_buf_inst/scan_body/top_analysis/top_body/trace_trim/block_headers/poll2/env_check/launch_lvs2/poll_lvs2/final_status/cleanup_junk/try_bsub/poll_bsub_test)→定位 root cause：`T_IsmTop` line 3249 `XI37 JudgeN<8> JudgeN_buff vbn! vbp! vcc! vss! / bufLx4` 是全 CDL 唯一把 body 接到顶层悬空 vbn!/vbp! 端口的实例→LVS INCORRECT(vcc!↔vbp!、vss!↔vbn! bulk mismatch)→RCC 被 "CCI-LVS NOT Clean" 中止→单行修复 `vbn! vbp!`→`vss! vcc!`+backup+line-diff 验证(155 subckts/ends balanced)→RCC 重跑被 star 队列 VCO=aoi 平台限制阻塞。
- **撞库**：deepread 完才发现 748ox = **shard A EDA-Eval-DesignFlow-CdlBodyMapFix-001**（且 CdlVbnBulkRemap-001 也同 session）。grep A/B/D/main jsonl trace_source 确认。
- C-only ledger 无法检测跨 shard 撞库。→ parked。
- **已建跨 shard 排除清单** `designflow/_excl_crossshard_r235.txt`（643 session，从 A/B/D/main jsonl 的 metadata.trace_source.session_file 抽取，去 .messages.json 后缀）。r236 选料必须 `grep -v -F -f` 此清单 + ledger_C。

## 关键发现 ③ lizwen skill-def（非有机任务）
- ym81m（mc=138, calibre=161 pyAether=160, 89 msgs）/ i2k9v（mc=81, calibre=113 pyAether=105, 52 msgs）title="DRC Testpattern Generator"。
- prompt 是 skill-def spec 式（"# DRC Testpattern Generator ## When to Use... 触发... 不触发..."），非有机用户任务。
- topic 与已交付 QaWidthPatternGen-001 / DrcQaWidthTypeGeom-001 / SwitchGatedSpacePatternGen-001 / PcellPatternGeoDiag-001 重叠。
- → parked（r236 distinctness eval）。

## johnl 其余 fresh session（全 wrong shard / non-seed）
- jtcvf/bm8t8：T_IsmTop PEX（同 748ox topic，dup 风险）
- nqj3w/n2lhr/ygrxp/aqapd：finesim 波形/sweep（simulation，wrong shard）
- c5gwq/i7eyp/1uxza/ph3ku：primelib_char dc_addr_to_region synth（synthesis，wrong shard）
- 10qhm：DDR5 SPICE 网表电路学习助手（Q&A/教学，无交付物）
- z2knw"你好"/ztom2"原始对话文件在哪"/n9550"agent 老是让我审批"/exwpt"/anasimpro-gui-start"：meta/config，non-seed

## r236 必须交付（🚫 禁连续 3 轮 0 case）
1. **嵌套 find 验 existence**：`find /home/<u>/.cline/data/sessions -name "*.messages.json"`（别再用根 glob）。
2. **grep -v 跨 shard excl（643）+ ledger_C（403）+ 饱和用户**（e0014566/xinqiaoz/miccao/ellawu/kenwang/yqlu/lvyy/jason17w/sinanz/alan3zh）。
3. **优先 NEW user on hfeg0pkn004/005**：e0039602(83)/e0044587(47)/lorikx(48)/thomasz(36)/xxchen(34)/rongjiez(77)/t0002987(34)/e0046686(24)/jinsongl(22)——查 11-05 scan calibre/innovus dominant，嵌套验 existence。
4. **选定后先查跨 shard excl 再 deepread**（避免重蹈 748ox 撞库）。
5. .75 rescan 捕获 11-06~08 新 session 仍待做（daily_eda_scan.sh）。
6. 96crr(e0044131 37M tok "项目实操") 仍可单独深读轮（需嵌套验 existence）。

## 台账
- parked +3：748ox（跨 shard dup）/ym81m/i2k9v（skill-def）
- ledger_C：403 已动过（case 228·parked 174·claimed 0·deepread 0）
