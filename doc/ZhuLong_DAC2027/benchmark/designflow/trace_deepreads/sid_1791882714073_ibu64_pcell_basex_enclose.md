# 深读笔记 · trace 1791882714073_ibu64 · pcell basex enclose bug

- **session**: `1791882714073_ibu64` · user `yzwang` · host `hfeg0pkn001` · mc=113
- **tool 命中**: 656 dbCreateRect · 10 calibre · 3 pyAether（layout 绘图密集 = layout_virtuoso seed）
- **model**: deepseek-v4-flash · 90 msgs · 942 KB · status failed (stale session)
- **cwd**: /home/yzwang · provider cxmt-deepseek-flash

## 用户真实意图（逐字原文，USER#0，纯意图 A-档合格 seed）

> 我在/home/pdk/yzwang/06_AI_workspace/test5放了一个叫Metal3DEncloseOneSideLand_F.il的文件，这是一个pcell,我只勾选exclose short/long side same value这个开关，正常来说针对最后一个pattern，OPC01_mark1这层应该生成在via layer和metal layer靠右侧中间的位置，但是当填写某种数值时，OPC01_mark1的位置偏了，请你分析并作出改动.

用户报告症状（OPC01_mark1 位置偏移），要求"分析并作出改动"——未给根因/修复方案 ⇒ A-档 seed 合格。

## 对话流

- USER#0：报告 bug（上文）。
- ASST#1–#38：反复 read_files / search_codebase 阅读 `Metal3DEncloseOneSideLand_F.il`（1997 行），定位 Pattern 10-1/10-2/10-3（withEncloseLong/Short/Enclose 三个并行分支）。识别 bug：`withEncloseShort` 与 `withEnclose` 分支的 `basex` 重新赋值错误多加 `+ encloseShort` / `+ enclose`，而参考分支 `withEncloseLong` 无此 enclose 项 → 整个 pattern（含 OPC01_mark1 / highlight mark）右偏一个 enclose 量。
- USER#52「你来修改。」→ ASST 因可写根受限（`/home/pdk/...` 不可写，仅 `/home/yzwang/`），改在可写区创建 fixed 版。
- USER#60「你改得没有问题，但是我希望在我只勾选withEncloseShort或只勾选withEnclose时，最后一个图形也改成这样，请继续帮我修改。」（扩展 scope，仍为目标非根因）
- USER#64「已执行，请进行修改。」→ ASST 用 Python 脚本 `fix_pcell.py` 逐行 patch（line 1239/1253/1258 删 `+ encloseShort`，line 1274 删 `+ encloseShort`，line 1280/1281 修 `1.2*metalWidth→metalWidth`）。
- ASST#83：三 pattern 风格统一，对比表确认 basex/metal 左边缘一致。
- USER#84（晚期，根因/方案轮，**不作 A-档任务说明**）：同事反馈 `metalWidth` 变量名语义不准（举例 viaSize1Long=1/viaSize1Short=0.22/metalWidth=5/enclose=1.89 → 生成 7.11×7.89 矩形），建议改名或重算。→ 转入另一个子主题（变量命名/公式重算），本轮不取。

## 金标准（用户实际接受的结果）

ASST 的 `fix_pcell.py` 删除 `withEncloseShort`/`withEnclose` 分支 basex 重新赋值中的多余 `+ enclose*` 项，使三分支 basex 公式一致（无 enclose 项）。用户 USER#60 明确「你改得没有问题」 ⇒ 此修复被接受。

## 取的子主题（正交于既有 AutoVia/DrcPat/Dummy 等）

**pcell basex enclose 一致性审计 + 修复**：给一个含 `withEnclose*` 多分支的 SKILL pcell 片段，写 Python 审计器，定位 `basex = basex + <rhs>` 重新赋值行中"只在部分分支出现"的 enclose 族裸变量加项（spurious），输出 JSON 报告 + 修复后 .il（删 spurious 项）。与 r152 LayCvPreserveAudit（dbCopyCellView textDisplay/pin 保留）、r133 AutoViaPwrFillRemove 等均正交。

## 本轮 case 设计（B-档 synthesized, L1-boundary）

- A(audit input)：化简 pcell 片段 `pcell_basex_A.il`，三分支，vars encloseLong/encloseShort/enclose，withEncloseLong 干净，withEncloseShort +encloseShort（buggy），withEnclose +enclose（buggy）。
- 隐藏 B1：3 分支，var 名换成 encLong/encShort/encL（同 bug 结构，不同名）。
- 隐藏 B2（跨输入守卫）：4 分支，仅 withEncloseShort +encShort buggy，其余干净；var 名 encL/encShort/encW/encX + m1Width，无 A 专属 token（encloseShort/enclose/metalWidth）。
- 隐藏 B3（malformed）：有分支但无任何 `basex = basex + ...` 重新赋值 → 候选须 exit 1。
- 判分 14 条独立条件 (a–n)：zip+py_compile / CLI / B1 exit0+写输出 / B1 JSON 键 / B1 total==3 / B1 两 buggy 分支含正确 spurious 项 + 参考分支干净 / B1 buggy_count==2+verdict FAIL / B1 patched basex 行删项+参考行不变 / B1 行数守恒 / B2 跨输入守卫(仅 1 buggy + 无 A token) / B2 patched 仅 buggy 分支改 / B3 exit1+stderr+不写输出 / 确定性 md5 / 反 naive(patched≠input + B3 exit1)。
- gold = `basex_enclose_audit_ref.py`；negatives = 5 fakes（empty/print-expected/core-deleted/naive-always-pass/naive-hardcode-A）+ negative_selftest。

## leakage 隔离

SUT 沙箱只放 prompt + task_brief + pcell_basex_A.il；B1/B2/B3 .il 以 base64 内嵌 check.py（在 reference/，不进 SUT 沙箱）；check.py / gold / negatives 均在 reference/，不进 assets。
