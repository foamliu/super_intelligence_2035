# 5kysh deepread — Verilog stdcell simlib similar-model matching analysis

- session: `1794362790365_5kysh/1794362790365_5kysh.messages.json`
- user: e0039602 @ hfeg0pkn005
- mc: 57 (1115 scan), domain: characterization (stdcell simlib/tb_family tooling)
- 156 msgs / 433KB / trace 在子目录 `1794362790365_5kysh/` 下

## 真实用户意图（原话 + 流向）

1. 「请你检查一下这里面这个相似model匹配的一个逻辑，并告诉我or4GSx2会在我们的库里匹配到哪个相似model」— 理解 simlib_ref_db.py 的相似匹配逻辑 + 对 or4GSx2 跑匹配。
2. 「你只通过tbfamily的名字判断是否是这个族，没有用这每个tb sv当中的实际代码对吧」— 确认族门控只用 tb_family 文件名，不读 tb sv 代码。
3. 「那实际上可以完全不利用这个tb_family对吗 ... 请你收集这个目录里tb_family的名字，用于匹配，然后再测试一下or2GSx2」— 从新目录 /home/wellesc/StdCellTB_Skill/StdCellTBSkill_V0 收集族名，测 or2GSx2。
4. 「or4GSx2和or4FSSx1会匹配到什么，还有现在是不是tbfamily这个文件夹完全不需要了，我可把它删了？」— 测两个目标 + 问 tb_family 能否删。
5. （frustration）「把新目录里所有的族都提取出来放到一个文件里，以后检索不依赖tbfamily」— 把族名提取到 src/family_names.txt，检索不再依赖 tb_family 目录。
6. 「后面的数字也一起提取出来啊，你只需要把前面的tb_去掉，后面的保留诸如or2 or3 or4这种的区分开，数字也能匹配上的就优先选数字也匹配上的」— 族名保留数字（or2/or3/or4 分开），数字相同候选优先。
7. 「我替换了一份simlib_drcoa_stdcells.sv，请你现在再看看能匹配到什么」— 换了参考库后重测。

agent 用 SimlibRefDB 实跑验证（写临时脚本跑 find_reference / _eligible_similar），给出族名单 + 匹配结果，改 `_build_family_bases` 优先读 `src/family_names.txt`，并改门控用 `_family_token`（字母+紧跟数字）+ 数字优先。

## 匹配算法（simlib_ref_db.py 真实实现，已确认）

- `_cell_part(name)`: 去开头单字母 role 前缀 `X_`（R_and7CSx→and7CSx）。
- `_family_letters(cell)`: 首段字母（`re.match(r'([A-Za-z]+)', cell)`），如 `and7CSx`→`and`，`bufB`→`bufB`（含变体后缀字母）。
- `_family_digit(cell)`: 字母后紧跟的数字段（`and3CSx`→`3`）。
- `_family_token(cell)`: `re.match(r'[A-Za-z]+[0-9]*')` → 字母+紧跟数字（`or4GSx2`→`or4`，`buf`→`buf`，`bufA2`→`bufA2`）。
- `_build_family_bases`: 优先读打包 `src/family_names.txt`（每行一个族名，含数字）；否则扫描 `tb_family/`（`sorted(os.listdir)`，`tb_` 前缀 + `.sv` 后缀去掉，保留数字）。
- `_eligible_similar(name)`: 
  1. t_token = family_token(cell_part(name)); 若 t_token 不在 family_bases → 返回 []。
  2. 遍历参考库模块（跳过 exact 同名），要求 `family_letters(cell_part(cand)) == t_letters`（完全相等）。
  3. dm = bool(c_digit) and c_digit == t_digit；按 `(-int(dm), order.index(cand))` 排序（数字匹配优先，再按文件序）。
- `find_reference(name, limit=1)`: exact（大小写不敏感）优先；否则 `_eligible_similar`[:limit]。

## 关键 quirks（决定判分「牙」）

- `bufB` 的 family_letters = `bufB`（含 B），与 `buf` 的 `buf` 不等 ⇒ target `buf` 在只有 `bufB` 模块的库里相似匹配返回空（null）。这是真实行为，naive 模糊匹配会错。
- exact 是大小写不敏感（index 用 lower key），优先于族门控（如 `invB` 即使 token `invB` 不在族名单，exact 仍命中）。
- 族 token 含数字，故 `or4` 需 tb_family 有 `tb_or4.sv`；`xor2` 无 `tb_xor2` ⇒ null。
- `oai21BX2` token = `oai21`，digit=`21`，候选 `oai21BX1`(digit 21, dm=True) 优先于 `oai22BX1`(22)。

## 合成（A 档 trace-faithful）

- case_id: `EDA-Eval-DesignFlow-SimlibMatchAnalyze-001`，domain=characterization，shard=B
- 任务：写 `simlib_match_analyzer.py(input_dir, output_dir)`，分析匹配逻辑 + 从 tb_family 提取族名（含数字，排序）+ 对 targets 跑匹配 + 判 tb_family 是否可删；产 `match_report.json`(12 顶层键) + `family_names.txt`。
- A 输入：真实 `simlib_ref_db.py` + 合成 simlib.sv(or2GSx2/or3GSx1/or4GSx1/and2CSx1/and3CSx1/nand2CSx1/nor2CSx1/inv/buf/mx2CSx1/mx3CSx1) + tb_family(or2/or3/or4/and2/and3/nand2/nor2/inv/buf/mx2/mx3) + targets(or2GSx2/or4GSx2/or4FSSx1/and3X2/nand5X1/nor2CSx1/mx2X1/xor2X1)。
- hidden B：不同 simlib(and2BX1/and3BX1/and4BX1/nand2BX1/nand3BX1/nor2BX1/nor3BX1/invB/bufB/oai21BX1/oai22BX1) + tb_family(and2/and3/and4/nand2/nand3/nor2/nor3/inv/buf/oai21/oai22) + targets(and4BX2/and6BX1/nand2BX1/nor3BX2/oai21BX2/oai23BX1/invB/buf)。
- check.py 独立 oracle 重算族名/模块/匹配，cross-input guard + A-leak guard(or 族/CSx1/GSx1/FSSx1) + 确定性 + 4 假提交回归。
- k_check == k_rationale == 32；ref 32/32 PASS + 4 negs 全 FAIL。
- 真实引擎 SimlibRefDB 与 oracle 在 A/B 两种输入上结果完全一致（已验证）。

## 台账

`mark 1794362790365_5kysh → case EDA-Eval-DesignFlow-SimlibMatchAnalyze-001`（r686 复活池变现 #65）
