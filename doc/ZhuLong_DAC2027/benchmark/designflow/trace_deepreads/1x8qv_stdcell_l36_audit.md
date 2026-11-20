# trace deepread — vincentz @ hfeg0pkn005 session 1794894357170_1x8qv (r950)

- **user**: vincentz  **host**: hfeg0pkn005  **session**: 1794894357170_1x8qv
- **mc**: 10652 (summary.tsv 11/21 00:51 scan)  **spice**: hspice:4986 ratio=0.47
- **file**: `/home/vincentz/.cline/data/sessions/1794894357170_1x8qv/1794894357170_1x8qv.messages.json` (52KB, 16 msgs, 3 user)
- **ledger**: claimed r950 (B, spice_sim), fresh (ledger_hits=0 cross-shard)

## 用户意图（原话）
- U[0]: `/proj/drgqa/V0/workdir/vincentz/simulation/drgqa_top_WOWTOP_schematic_ALPS/netlist帮忙看下这个网表里有多少个stdcell用到了L=36nm的器件`
- U[2]: `请帮我继续`（session 截断，未给最终计数）

任务形态：HSPICE stdcell 网表 L=36nm 器件使用审计（analysis/parse 类，11-15 重审后合法 spice_sim 真实意图）。

## agent 工具链
1. `list_allowed_files` → 确认 netlist 是文件不是目录（路径 `/rundata/drgqa/V0/simdir/finesim/...` 映射）
2. `read_files` netlist:1-80 → 确认 AETHER-SE HSPICE 格式：`*WOWTOP` header + `.subckt switch_close`/`parasiticRC2`/`brknet`/`brknetTMA`/`TDVPrc` 等
3. `editor` 写 `explore_netlist.py`：join `+` 续行 → 516256 raw / 458139 logical lines → 找 M 开头 MOSFET 行（顶层 0 个，器件在 .SUBCKT 内）→ L= 分布
4. `editor` 写 `explore_netlist2.py`：首字符分布 + 搜 `L=36` 模式（36e-9/3.6e-8/36n/36nm）→ session 在此截断

## 关键洞察（造题用）
- 续行 `+` 必须先 join，否则 M 行与其 `+ L=...` 续行分离，L= 取不到
- L 单位归一化：`36e-9`/`36n`/`36nm`/`0.036u`/`3.6e-8` 五种写法都 == 36nm；`360n` 是 360nm（子串 "36" 陷阱）
- `*` 注释行 `L=36nm ref` 不是器件 L=，必须跳过
- X 调用 subckt（只 `Xxxx ... child`）本身不算「用了 L=36nm」——器件物理在 child 内，统计 M 行所在 .SUBCKT 块

## 造题产物 (EDA-Eval-DesignFlow-StdcellL36Audit-001)
- A 档 trace-faithful：用户原话 U[0] + 真 /proj/drgqa/V0/... 路径 + 真 AETHER-SE HSPICE 格式
- 资产 netlist_A.sp：紧凑忠实复刻（15 subckts），因 516256 行原网表过大含内部路径故重建
- hidden netlist_B.sp：异 stdcell 名 + 异 L 分布 + 异 total(14) anti-hardcode-A
- check.py：17 条独立断言（a-q），ref 17/17 PASS，4 negs 全 FAIL（§4.9 三假 + hardcode-A）
- B 真值：total=14, count_l36=6, names={AND2x1,CKLNx1,DELAYx1,LATCHx1,OR2x1,SPLITB}
- 陷阱覆盖：续行(SPLITB)、注释(NOTE36)、360n(BIGTRAP)、X调用-only(XCALLB)、单位 5 写法
