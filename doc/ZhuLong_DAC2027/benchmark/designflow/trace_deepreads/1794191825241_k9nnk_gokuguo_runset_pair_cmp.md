# trace_deepread — 1794191825241_k9nnk (gokuguo @ hfeg0plg53) — runset/layermap 文件对比（只读）

## 元数据
- sid: `1794191825241_k9nnk`，user `gokuguo`，host `hfeg0plg53`，mc=123
- status: **completed**（94 msgs / 47 user-turns，多轮文件对比任务）
- domain: **layout_virtuoso**（Calibre LVS/PEX runset + Virtuoso layermap 文件比对，只读分析）
- 本轮选取来源：r328 pg_flag=0 layout-affinity 排序池（pg_layout fresh 已耗尽，回退 layout_virtuoso），fresh non-ledgered

## 用户 goal-turn（U#0 逐字）
> 「只阅读一下：/proj/lacaa/TV1_FS_Virtuoso/libs/35HFS/35HFS.layermap和/proj/lacaa/V0_FS_Virtuoso_test/libs/35HFS/35HFS.layermap，比较一下两者的区别，注意不要有任何删除的动作」

- 附件：**无**（U#0 纯文本路径）
- §A 选轮规则：U#0 = 提出需求（"比较一下两者的区别，不要有任何删除的动作"），用户未指出根因/未给修复方案 → 合格 A 档 seed。
- 关键约束："只阅读"+"不要有任何删除的动作" → 严格只读，成为本 case 的只读守卫来源。

## assistant 链路（真实 gold）
1. **第一对：layermap 完全相同**
   - 读两个 `35HFS.layermap`（各 2253 行）。
   - 写 `diff_layermap.py`：用 `difflib.SequenceMatcher` 逐行比对，输出差异行号与内容。
   - 写 `hash_layermap.py`：用 `hashlib` 算 MD5 + SHA1，做字节级校验。
   - 结论：两文件**完全相同**（0 处差异，MD5/SHA1 一致）。
2. **第二/三对：LVS/PEX runset（.sp / .lvs / hcell_list）**
   - 用同样 difflib + hashlib 方法对比 LVS runset（`*.sp` / `*.lvs` / `hcell_list`）。
   - 多数 runset 对**完全相同**。
3. **tran.map：3 行不同**
   - 对比 `tran.map` 文件对 → 发现 **3 行**内容不同（路径/标题行差异）。
   - difflib 精确枚举 3 处差异行（行号 + 旧/新内容）。
4. **缺失文件：大小写写错**
   - 一次对比中 `V0D1` vs `V0d1`（目录名大小写写错）→ 路径不存在 → 报错。
   - assistant 识别为"文件名大小写写错致路径不存在"，未崩溃，重新定位正确路径后继续。
5. 全程**严格只读**：从未以写模式打开输入文件，从未修改/删除任何输入。

## 改造为通用生成器（本 case）
- 真实 gold 模式：`difflib.SequenceMatcher` 逐行 diff + `hashlib` MD5/SHA1 字节校验 + 缺失文件优雅处理。
- 改造为 `cmp_runset.py <fileA> <fileB> <out_report.json>`，输出结构化 JSON 报告。
- 三种 verdict：`identical`（MD5 相同）/ `different`（逐行 diff 枚举）/ `error`（文件缺失，不崩溃）。
- 只读守卫：脚本绝不写/删输入文件 → check.py 跨输入 MD5 校验。

## 判分设计（14 条断言 a-n）
- A 对（可见，identical 46 行 layermap）：① 单文件 submit ② compile ③ exit0+合法JSON ④ verdict=identical ⑤ md5 匹配 ⑥ diff_count=0 ⑦ lines=46
- B 对（隐藏，3 行 diff runset）：⑧ verdict=different ⑨ diff_count=3 ⑩ diffs 精确枚举（反硬编码）
- B2（隐藏，fileB 缺失）：⑪ verdict=error+missing ⑫ exit 0（不崩溃）
- B3（隐藏，行数 diff 12 vs 15）：⑬ verdict=different+lines_a=12/lines_b=15
- 只读守卫：⑭ 所有运行后输入文件 MD5 不变

## §4.9 三假解 + 6 负样本（均须 FAIL）
- naive_hardcode（恒输出 identical）→ ⑧⑨⑩ FAIL
- print_only（只 print 不写文件）→ ③④ FAIL
- deleted_core（跳过哈希）→ ⑤ FAIL
- modify_input（违反只读，append 输入）→ ⑭ FAIL
- crash_on_missing（缺失文件崩溃）→ ⑫ FAIL
- wrong_diff_count（误计 diff_count=len(la)）→ ⑨ FAIL
- empty_shell（空 no-op）→ ③④ FAIL
- print_expected（print 答案不写文件）→ ③ FAIL
- name_only（只比文件名不比内容）→ ④⑤ FAIL

## 自检结果
- reference self-test: **14/14 PASS**
- negative_selftest: REFERENCE PASS + 9 negatives/fakes all FAIL → ALL OK

## 交付
- assets: fileA_A/fileB_A.layermap（可见 identical 对）+ hidden/（B/B2/B3 runset + manifest）
- reference: check.py（14 条，自包含从 literal 写隐藏文件）+ cmp_runset_ref.py + reference_submit.zip + negative/（6 neg + 3 fake）+ negative_selftest.py
- jsonl: EDA-Eval-DesignFlow_C.jsonl line 284，id=EDA-Eval-DesignFlow-RunsetPairCmpGen-001，k_check=14/k_rationale=14，track=faithful，domain=layout_virtuoso
- check_sha256=42a4ec9c4d0a2d0f3b2ef8f7b68baa70a17aaa723b526b2890e6bf8689e67f17，check_size=10378
