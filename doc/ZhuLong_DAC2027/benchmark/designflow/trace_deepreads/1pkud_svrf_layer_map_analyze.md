# deepread: 1pkud · e0047695 · Calibre SVRF DRC rule deck 剖析 → LAYER MAP 分析器

- **session**: `1794981622005_1pkud.messages.json`
- **user**: e0047695 @ hfeg0plg58 (10.129.35.244)
- **mc**: 76 (kw drc:266/calibre:134/lvs:120/virtuoso:60/pdk:34/pex:10)
- **size**: 88 msgs / 3 real user_input turns
- **domain**: physical_verify (Calibre DRC rule deck 结构剖析)

## 用户原话（逐字）
1. "/apps/imctf/cad/runset/lacaa/tv1_dbc_virtuoso/current/calibre_DRC_DBC_IP.rule 帮我详细研究剖析这个rule，形成一套知识体系，后续我会让你帮我解决与这个相关的问题"
2. "继续，以后只要timeout就继续"
3. "继续" / "好了吗"

## 用户真实意图
把一个 17 万行的 Calibre SVRF DRC rule deck（`calibre_DRC_DBC_IP.rule` → `35H_DRC_Cal_V0d1a_Rev13_..._encrypt_IP.drc`，含 `#DECRYPT/#ENDCRYPT` 加密段）剖析成可复用的知识体系，重点搞清 GDS layer/datatype/texttype 如何映射到 Calibre 内部 layer。

## 助手 gold 链
- `list_allowed_files` + `read_files` 遍历 rule deck（17 万行，部分加密）
- `editor` 写多个分析脚本（13 次 editor）：
  - `analyze_rule.py`..`analyze_rule5.py`（5 次精化）— 最终 `analyze_rule5.py`：两遍解析
    - pass1: `^\s*LAYER\s+(\S+)\s+(\d+)\s*$` → `name_by_num[num]=name`
    - pass2: `^\s*LAYER\s+MAP\s+(\d+)\s+(DATATYPE|TEXTTYPE)\s+(\d+)\s+(\d+)\s*$` → row(line, gds, dt, src, name_by_num.get(num,"?"))
    - 输出 `layer_map_35H_full.tsv`（2547 行）+ distinct gds→name 汇总
  - `probe_drf.py`/`probe_drf2.py`/`probe_drf3.py` — 探 .drf
  - `35H_DBC_DRC_IP_知识体系.md` — 知识体系 markdown（editor 写入但文件未落盘成功，远端 ls 报 NOFILE，可能 unicode 文件名编码问题）
  - `rename_kb.py`
- `run_approved_command` 14 次（python-runner 跑分析脚本）

## 真实 SVRF 语法样例（来自 deck 实测）
```
LAYER MAP        6         DATATYPE     0  8000
LAYER DNW_drawingi     8000
LAYER MAP        6         TEXTTYPE   251  8004
LAYER MAP        6         DATATYPE   251  8004     <- 同一 calibre_num 8004 有 TEXTTYPE+DATATYPE 两条映射
LAYER  NW_pini     8011                         <- 名字前可有额外空格
```
- 行注释 `//`，块注释 `/* ... */`
- `LAYER MAP` 行尾无注释；`LAYER <name> <num>` 行尾无注释
- 174246 行，5037 个 `LAYER` 语句，2547 个 `LAYER MAP`

## reframe（档 B）
真实 gold 跑 17 万行真实 deck（含加密段 + 不可复现的 PDK 路径）→ reframe 为 **fixture 驱动的离线 SVRF LAYER MAP 分析器**：
- 候选交付 `svrf_layer_map.py <rule_file> [-o out.tsv]`
- 可见 fixtureA/rule_A.svrf（合成 SVRF deck，DNW_*/NW_* 层）
- 隐藏 B（嵌入 check.py，AA_*/MS_*/MS2_* 层，含未命名 calibre_num 9008→'?'，含 // 注释掉的假 LAYER MAP dt=99）
- check.py 15 teeth（a-rand）+ 3-seed 随机子集

## 落库
- case_id: EDA-Eval-DesignFlow-SvrfLayerMapAnalyze-001
- domain: physical_verify / layer: L1 / grade: B / track: A-faithful-seed-synthesized-reframe
- k_check = k_rationale = 15
- C 域 physical_verify SVRF LAYER MAP 分析 reframe 子型首例（与 DrcRunsetAutoConfigAnalyze(runset 模板复制机制)/LvsSvdbRepDirStat(.rep 目录统计) 正交：本案=对 SVRF rule deck 的 GDS→Calibre layer 映射表抽取）
- 自验: ref solve.py PASS 15/15；3 negatives (empty_stub→c / print_expected→f / delete_core→e) 全 FAIL distinct；§4.9 (a)(b)(c) 三假提交全 FAIL
