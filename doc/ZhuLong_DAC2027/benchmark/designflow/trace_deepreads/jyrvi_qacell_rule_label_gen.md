# Deepread: 1793329833544_jyrvi (xxchen @ hfeg0pkn002)

- session: `1793329833544_jyrvi`，model=deepseek-v4-flash，status=failed
- cwd: `/home/xxchen/workspace/DRC_pattern_tool/0.4/device_rule1`
- match_count=417，domain=layout_aether，shard C round 170
- messages.json 275 条 (1.95MB) + archive.jsonl 2.6MB

## 真实任务
DRC_pattern_tool 里 enclose 类规则的「规则描述标签」(userSpecifyRuleDescription) 修复。
SKILL pcell (`enclosePass.il` 233-234 / `encloseFail.il` 1311-1312) 用 `dbCreateLabel` 在 pcell
边界写出规则描述字符串，形如：
```
patternString = sprintf(nil "%s" userSpecifyRuleDescription)
dbCreateLabel(cv lppText 0:borderTop-insideLayerShortSide*0.5 patternString "centerLeft" "R0" "roman" ...)
```
userSpecifyRuleDescription 文本丢失后需从 `qa_config_device.txt` (QACELL 格式) 重建。

## 关键用户轮 (4 个 user_input)
- U#21: enclose label missing，要求修复 userSpecifyRuleDescription
- U#128: goodPattern 补齐（pass 样本 pattern）
- U#241: auxRegion region 后缀（CORE / RLDEV;mark1）逻辑
- U#273/274: continue 收尾

## 核心逻辑（enclose_simple.py rule_label_text() lines 85-117）
- 输入：QACELL 配置，每行 `QACELL <rule_id> <rule_type> <source>-><target> <distance> {param val ...} ...`
- rule_id 后缀 `_c`=check/违规(is_pass=False)，`_p`=pass/合规(is_pass=True)，无后缀=None
- per-rule label: `<source> <rule_type> <target>: >= <distance:.4f>` + auxRegion 时 `, in region: <auxRegion;→_>`
- pair label (_c/_p 配对): `<source> <rule_type> <target>: >= <dist_c:.4f>/<dist_p:.4f>` + region 后缀
- `;`→`_` 仅在 label 文本里替换，params 里保留原值

## 合成 case
- ID: `EDA-Eval-DesignFlow-QaCellRuleLabelGen-001`
- 档位: B-档 synthesized, L1-boundary, domain layout_aether
- 范围: QACELL config parser + rule-description label generator (`qacell_rule_label.py`)
- 与 r169 ConvexEnclosePcellGen-001 区别：r169 是 pcell 几何 (dbCreateRect via/metal) 凸角 enclose；
  本 case 是配置解析 + 标签文本生成 (dbCreateLabel userSpecifyRuleDescription)，无几何。

## A/B 配置
- A (visible, `qa_config_A.txt`): 7 rules — DNW_ENC/DNW_S/DNW_W/DGX_ENC/DNW_F，auxRegion=CORE，pair _c/_p
- B (hidden, `qa_config_B.txt`): 7 rules 结构不同 — DGX_ENC/DGX_S/NW_O/DGX_ENC_021/M1_LS，
  auxRegion=`RLDEV;mark1`（测分号归一化），waivePattern 多 token list，insideLayerNotAllowedOutside bool

## check.py
14 条断言 (a-n)：zip+compile+stdlib / --help / B run+JSON / B 7 rules / DGX_ENC_018_00_c 字段 /
pair_label 格式 / auxRegion ;→_ / is_pass 标志 / params 类型 / 多 token list+bool / stats /
注释跳过 / 跨输入守卫 A≠B / 确定性 sha256。A/B 配置 gzip+b64 内嵌。

## 验证
- reference `qacell_rule_label.py` PASS 14/14
- 5 negatives 全 FAIL (fake_empty / fake_print_expected / fake_core_deleted / naive_hardcode_B / naive_skip_auxregion)，NEG_RC=0
- test==disk roundtrip OK
- 跨分片查重：A/B/D jsonl 无此 case id
