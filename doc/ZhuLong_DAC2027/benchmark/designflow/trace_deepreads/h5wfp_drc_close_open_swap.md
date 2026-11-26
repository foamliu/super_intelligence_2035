# Deepread: 1790564208899_h5wfp (weizhao @ hfeg0pkn004, mc=42)

## Session overview
- User: weizhao, host: hfeg0pkn004, session: 1790564208899_h5wfp
- mc=42, domain: physical_verify (Calibre DRC layer-map close/open swap)
- 58 msgs; user提出需求（A-faithful 合格：提需求，未给根因/修复方案）
- Live path (dir-based): /home/weizhao/.cline/data/sessions/1790564208899_h5wfp/
- Reference deck: /apps/imctf/runset/calibre/cxmtG5_CIP/current/drcoa/G5_CIP_package_drcoa_v0d5_Rev07/calibreDRC.rule

## Key user turn (verbatim, U#0)
"帮我写一个脚本 用于替换calibreDRC.rule中关于 LAYER MAP定义中的 XXX_close XXX_open
案例为
LAYER   MAP   88   DATATYPE   16     8516
LAYER   M1_CLOSE                     8516
LAYER   MAP   88   DATATYPE   17     8517
LAYER   M1_open                      8517变更为
LAYER   MAP   88   DATATYPE   16     8516
LAYER   M1_CLOSE                     8517
LAYER   MAP   88   DATATYPE   17     8517
LAYER   M1_open                      8516"

= 互换成对 XXX_CLOSE / XXX_open 的内部层号，LAYER MAP 行不变。

## Assistant tool chain
- search_codebase (timeout) → list_allowed_files → read_files calibreDRC.rule 分段读取
- editor 创建 swap_close_open.py + test_input.rule + test_expected.rule + test_swap_close_open.py
- run_approved_command 被 policy denied（hello_world profile uid 不匹配）→ 脚本未实跑但逻辑完整
- 末轮交付总结：11 对 CLOSE/open（CT/M1/V1/M2/V2/M3/V4/M4/RDL/M5 + MT2），脚本原理说明

## Gold = assistant 实际产物
- swap_close_open.py: 正则 `^(LAYER\s+)(\S+?)_((?:CLOSE)|(?:open))(\s+)(\d+)\s*$` (IGNORECASE)
  匹配 LAYER <name> 行（非 LAYER MAP），成对互换层号，不成对 skip+warn，exit 0=有交换/2=无配对
- 关键不变量：LAYER MAP 行永不修改；仅 LAYER <name> <num> 行尾数字互换

## Real deck CLOSE/open pairs (faithful A asset source)
sed -n '1029,1267p' 真实 deck 节选含 6 对：CT(8487/8488) M1(8517/8518) V1(8542/8543) M2(8562/8563) V2(8584/8585) M3(8604/8605) + decoy 层（M1_term/M1_SL_DUMMY/M1_voltage_txt/M2_term/M1_RNODE ...）

## Case synthesis (EDA-Eval-DesignFlow-DrcCloseOpenSwap-001)
- A档 faithful: prompt = U#0 逐字原文；A=合成 calibreDRC_sample.rule(3 对 M1/CT/V1, 9510-9631)
- 通用化: swap_close_open.py <input.rule> <output.rule> 互换成对 _CLOSE/_open 尾层号
- 隐藏 B (3 文件, 结构/层名/层号/配对数/大小写/不成对均不同):
  - B1: 3 对 AA/GT/MK (7210-7456)
  - B2: 5 对 P1-P5 大小写混合 close/OPEN (3101-3149) + 非 CLOSE 行 POLY 9001
  - B3: 1 对 XX + 1 不成对 YY_CLOSE (4201-4205) + DUMMY 4300
- check.py 10 条件 a-j（k_check=k_rationale=10≥8）: zip/compile/B1 run/3对互换/MAP不变/B2 run+5对(大小写)/B2非CLOSE不变/B3 run+XX互换/B3不成对YY不变/B3非CLOSE+stderr告警
- 5 negatives: hardcode_a / no_swap(空壳=§4.9a) / print_expected(§4.9b) / ref_core_deleted(§4.9c) / swap_map_too + 3 格式 fakes
- 自验: ref PASS 10/10 ✓; 5 negatives + 3 fakes 全 FAIL ✓; test 字段 == check.py 字节同步 sha256=051844de… size=6732 ✓

## Coverage impact
- physical_verify: 107 → 108 (+1)
- Total: 286 → 287 cases (jsonl_C 286→287)

## 注
本 case 由并发 session 落 jsonl_C + assets/reference（完整），本轮(r331)补齐 ledger mark + §4.9 (b)(c) 两 negatives + MEMORY/daily/deepread 收尾。
