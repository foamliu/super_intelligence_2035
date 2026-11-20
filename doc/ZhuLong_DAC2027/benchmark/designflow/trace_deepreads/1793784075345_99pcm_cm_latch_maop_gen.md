# 深读笔记：1793784075345_99pcm — ruifan @ hfeg0plg36 — CM 锁存器 MA/OP 地址表生成 (CXMTseGetAllLatchInfo.il callback 复刻)

## trace 元数据
- user: ruifan · host: hfeg0plg36 (.75) · session: 1793784075345_99pcm.messages.json
- size: 1.1MB · msgs: 379 · domain: layout_virtuoso (Cadence Virtuoso SKILL)
- match_count: 69 (skill/dbGet/dbCreateRect/cmStautsTable/CmLatch/MA/OP/cm2/ERROR4 信号)
- mtime: 2026-11-06 (CSV 11:26 仍空, 用户未明确接受最终交付)
- NEW user: ledger 中 ruifan 0 prior (shard A/B/C 任一)

## USER 轮（verbatim 摘要）
- 用户在 dejoa 项目的 dejoa_digital 库（工艺 cxmtG4B_CIP）跑现成 SKILL 脚本 `CXMTseGetAllLatchInfo.il` 的 `CXMTseGetAllLatchInfo(mainForm)` 回调，从 CM 锁存器 cell 抽取 MA/OP 地址表，目标产物 `allCMAdr_MAandOP_<date>.csv`（真实参考文件 `/proj/dejoa/V0/workdir/ruifan/allCMAdr_MAandOP_20261104.csv`，458386 bytes，11/04 16:45）。
- assistant 复刻 callback 后处理逻辑生成 `allCMAdr_MAandOP_20261106.csv`，但 11:26 CSV 仍为空，session 取消，用户未明确接受最终 artifact。

## A-档 CLEAN 判定
- 用户给的是"跑现成 SKILL 抽地址表"的需求，未给后处理逻辑的根因/修复 → 纯需求轮 ✓
- trace 末尾 CSV 仍空、用户未接受最终交付 → **不适用 A-档**（无干净 accepted artifact）
- → 取 **B-synthesized**：grounded on 真实 `CXMTseGetAllLatchInfo.il` SKILL callback 后处理逻辑（assistant 在 trace 中 read 出完整源码 1-445 行）

## trace assistant 工具链 / 产物
1. read_files 多段读 `/apps/imctf/cad/init/settings_cdns/skill/special/se/CXMTseGetAllLatchInfo.il`（1-300, 300-445 行），抽出完整源码：
   - `CXMTseGetAllLatchInfo_GUI`（GUI 表单定义）
   - `CXMTseGetAllLatchInfo(mainForm)` callback（核心后处理）
   - `CXMTseGetAllLatchInfo_ByCell`
2. 复刻 callback 逻辑生成 CSV，但调试中 CSV 仍空（MA 装配/编码/cmStautsTable/cm2/ERROR4 任一环节未跑通）

## 原 SKILL callback 后处理逻辑（关键，用于同构重建 reference）
- **CSV 表头固定**：`MA(O),MA(H),OP,Category,Module Name,CM Name,CM Block`
- **MA bit 装配**：每个 latch instance，inputs 按 template 顺序对应 bit0..bitN（**LSB-first**，端口号 = bit 号），bit 值 = `getNetNum(net)`（net 名尾部整数，无数字则 0）；MA = sum(bit_i * 2^i)
- **MA(O)/MA(H) 编码**：MA(O) = octal(MA) 左侧零填到 **MALen**；MA(H) = hex(MA) 左侧零填到 **3**（小写 hex）
- **MALen** = 所有 instance MA 的 octal 串长度最大值（min 1）；**MAFullLen** = 511（MALen<=3）或 1023（MALen>3）
- **testmodeInfoTable**：key = MA(O)（填到 MALen）；每 key 按 outputs 顺序存每 testmode 槽 (cellnames, term, tmFullName=net, module)
- **cmStautsTable（按 project 区分）**：
  - 通用：ag→Analog, cl→Column, fc→Function, id→IDD, io→IO, ro→Row, ts→Test, sp→Spare
  - 仅当 project ∈ {ddcpb, ddjoc, degpa, degnt} 追加：gc→GlobalFunction, rf→Refresh, sc→Scrc, ta→TimingAdjust
  - 取 tmFullName 按下划线切分，第 2 段（index 1）是 status key；key=="sp" → "Spare" + spNum（正则 `cm([0-9])` 大小写不敏感在第 1 段匹配，取数字，无则空串）；表中不存在的 key → 空串
- **extract_sel=="Yes"**：i 从 0 到 MAFullLen，MA(O)=pad(octal(i),MALen)、MA(H)=pad(hex(i),3)；在表中 → 每 testmode 槽输出一行（槽空填 `NA,NA,NA,NA`）；不在表中 → 每 testmode 槽输出 `NA,NA,NA,NA`。OP = testmode 槽序号（0-based）
- **extract_sel=="No"**：只对表中存在的 MA(O)（排序）输出，槽空同样填 NA
- **cm2 行**：对每 cell 的 cm2_info 每个 cm2 串：按 "_" 切分取第 2 段 = cm2Type；cm2Type=="sp" → cm2Category="Spare2"，否则查 cmStautsTable；cm2Module 用正则 `(.*)<[0-9]*>` 剥掉尾部 `<N>`（不匹配则原串），**首个唯一名保留、后续重复 → 空串**。输出行：`NA,NA,NA,cm2Category,cm2Module,cm2,cell`
- **ERROR4**：每个 instance 若有名为 "CmOp" 的 output conn，其 net 名应等于 `CmOp<%d:0>` % (len(outputs)-1)；不等 → 日志写一行 `[ERROR4] <cell>/<inst> CmOp<...> connection is incorrect`
- **块名校验**：cm_latch_blocks 每个 name 必须匹配 `^CM[a-zA-Z]*$`（大写 CM 开头，后跟字母，无数字/下划线）；不匹配 → 优雅退出（非零退出码 + stderr 报错，不抛 traceback）

## 合成任务设计
- SUT 写 `cm_latch_maop_gen.py`，CLI 接 1 参 `<config.json>`，离线 Python 复刻上述后处理逻辑（不依赖 Virtuoso/SKILL 运行时），仅标准库
- 资产 A（可见）：dejoa/dejoa_digital 6-bit MA（CmLatchX6L 6in/3out，ma_0/ma_1 net，blocks CMCenter+CMLeft+CMRight，extract_sel=Yes，无 cm2_info，无 ERROR4）→ 1537 行 CSV（MALen=2, MAFullLen=511, 512×3 + 表头）
- 隐藏 B（重参数化）：ddjoc 7-bit MA（CmLatchX7L 7in/3out，blocks CMCenter+CMRight+CMsp，gc/rf/sc/ta 扩展分类，4 cm2_info[CMCenter_gc_sub<0>/CMCenter_sp/CMCenter_rf/CMCenter_rf<3>]，CMsp/I2 CmOp<5:0> 不匹配触发 ERROR4）→ 1541 行 CSV（MALen=3, MAFullLen=511, 512×3 + 4 cm2 + 表头）
- B_broken（哨兵）：块名 "CM2Bad"（含数字，不匹配 ^CM[a-zA-Z]*$）→ 优雅 exit2 + stderr（无 traceback）
- B 与 A 全重参数化（project/MA 位宽/blocks/分类表扩展/cm2/ERROR4/date 全不同）击穿硬编码 A

## 关键 gotcha（ref 实现踩坑）
- **cm2 split on "_"**：cm2 串 "CMCenter_sp<1>" split "_" → ["CMCenter", "sp<1>"]，cm2Type = "sp<1>"（**不是 "sp"**），→ category 查表失败得 ""。要让 sp→Spare2 路径生效，cm2 串须是裸 "CMCenter_sp"（无 <N> 后缀）或 "CMCenter_sp_1"（<N> 用下划线分隔）。B 的 cm2_info 据此设计：用 "CMCenter_sp" 测 Spare2，用 "CMCenter_rf" 测 Refresh（首现保留 module），用 "CMCenter_rf<3>" 测去重（<3> split 后 cm2Type="rf<3>"→空 category，但 module 经正则剥 <N> → "CMCenter_rf" 与首现重复 → 置空）
- **MAFullLen 对 7-bit MA 仍是 511**：7-bit MA max=127=octal"177"（3 字符）→ MALen=3 → MAFullLen=511（不是 1023）。要 MAFullLen=1023 需 MALen>3（MA≥512，需 10+ bit）
- **sp→Spare+cmN**：tmFullName "CMsp_sp_Tm0" → 第 1 段 "CMsp" 正则 `cm([0-9])` 无数字 → spNum="" → "Spare"（不是 "Spare0"）；"CM2_sp" 才给 "Spare2"

## 判分（k=16 条 ①–⑯ a–p）
- (a) zip 合法含 cm_latch_maop_gen.py (b) py_compile + 仅标准库 (c) B exit0 + csv + log (d) B 表头精确 (e) B MA(O) pad 宽度==3 (f) B 末行 MA(O)==777/MA(H)==1ff（MAFullLen=511）(g) B 总行数==1541 (h) MA 005→GlobalFunction/ModC1（ddjoc gc）(i) MA 077→Refresh/ModR0（rf）(j) MA 170→Scrc/ModR1（sc）(k) MA 021→空 category（zz 不在表）(l) cm2 CMCenter_sp→Spare2 (m) cm2 去重 CMCenter_rf 保留 / CMCenter_rf<3> 空 (n) errlog [ERROR4] CMsp/I2 (o) 跨输入守卫 A-prime（dejoa 6-bit 无 cm2）：exit0 + 1537 行 + pad 宽度 2 + MA 01→Test + errlog 空（杀硬编码 B）(p) B_broken 哨兵：非零退出 + stderr + 无 traceback
- k_check=16=k_rationale≥8 ✓；ref PASS 16/16；3 §4.9 fake 全 FAIL；3 negative 全 FAIL；3-seed determinism md5 稳定

## 交付
- EDA-Eval-DesignFlow_C.jsonl 第 211 行（test 字段 = check.py 源，与 disk 同步）
- assets/$CID/{prompt.txt, task_brief.md, config.json, hidden/{config_B.json, config_B_broken.json, hidden_manifest.json}}
- reference/$CID/{check.py, cm_latch_maop_gen_ref.py, negative/{naive.py, always_a.py, stub.py}, negative_selftest.py}
- ledger 99pcm → case + layout_virtuoso（第 351 行）
- MEMORY_C round 214→215, layout_virtuoso 47→48, coverage 210→211
