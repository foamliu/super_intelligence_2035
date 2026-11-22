# r1017 深读笔记 — t61yg (max7c@hfeg0pkn005) — LPDDR6 commands.txt dedup by -sr name

## Trace 来源
- session: `1795252307591_t61yg.messages.json` (子目录 `1795252307591_t61yg/`)
- user: max7c, host: hfeg0pkn005, mc=79
- keywords: verilog:567; .def:15; analog:6; cmos:4 (clean A-pure verification, nA=567 vs nC=0 vs nBD=10)
- scp e0031982@hfeg0pkn005 (group-readable, 459KB / 41 msgs / 3 干净用户输入 act-mode)
- fresh-diff vs 4-shard ledger(4221 normalized sids) verified absent — t61yg 是 max7c 的 NEW session（max7c 已有 6 个 ledgered sessions，但本 sid 不同，无 intent-dup）

## Session 3 子任务（单一文件 commands.txt，递进去重）
文件: `/rundata/decqa/V0/simdir/verilog/max7c/verilog.lpddr6.decqa.Nov09/async_scripts/commands.txt` (420 行)

### U#0 — 格式转换 (reformat)
用户原话: "这个文件前三行为目标模板，把其他行按前三行的格式改"
- 前 3 行已是 `./bin/vsim -sr <name> ... &` 模板格式（列对齐：name 域宽 26, --regnameb 域宽 36, -d 域宽 72, & 固定第 150 列）
- 其余 ~375 行是 `system("..."); system("sleep 5");` 包装格式
- agent 写 convert_commands.py: 剥 system 包装 + 路径替换 + unescape + 列对齐 + 保留 --rannum/-b
- 结果: 375 行转换, 45 行(空行/注释)保留, 0 失败

### U#19 — 单名去重 (本 case 提炼点)
用户原话: "遍历一下这个文件，看下有没有重复的类似用例，比如 Safety_10_M_Meta_L_DAAP Safety_10_M_Meta_L_DAAP ... 这种的话就保留第一条，其他条注释掉（开头加#）"
- 规则: 按 `-sr <name>` 全文件遍历, 同名用例保留第一条, 后续重复行开头加 `#`
- agent 写 dedup_commands.py (gold msg#20, 2431B):
  - `ACTIVE_RE = re.compile(r'^\./bin/vsim -sr (\S+)')`
  - 遍历: 首次见 → 记 line no + 保持; 重复 → `out.append("#" + line)`
  - 已注释/空行/section header 不动不注册
  - sanity: `assert len(out)==len(lines)` + `assert b==a or b=="#"+a`
  - 备份 .bak2 + 原位写回 + 报告(active kept / dup commented / dup names + 每名 keep:ln comment:ln1,ln2)
- 结果: 291 kept, 73 commented, 37 dup names (本 case 用 419 行重构版: 292/75/38)

### U#29 — 系列级极端去重 (不用于本 case)
用户原话: "其实可以再极端一点，比如 Safety_* 整个系列只保留第一条"
- agent 写 family_dedup_commands.py: 按测试名系列前缀分组(如 Safety_* 全归 Safety 系列), 每系列只留首条活跃, 其余注释
- 结果: 39 系列, 注释 204 行, 剩 87 活跃

## 本 case 提炼 (U#19 单名去重 → produce-task)
- 通用化: `dedup_commands.py <commands_file>` 读 argv[1], 去重, 原位写回 + 备份 + 报告
- A (visible): 真实 LPDDR6 commands_A.txt (419 行, post-reformat, 含 ROC_check/Safety_*/meta*/link_ecc 等重复名)
- B (hidden): 合成 DDR5 controller commands_B.txt (47 行, ddr5_* 名, 5 个重复名 7 行重复: ddr5_write_bl8@16,27 / ddr5_refresh@19 / ddr5_zqcal@20,28 / ddr5_link_ecc@36 / ddr5_link_edc@38)
- ref solution = 参数化版 gold (argv[1] 替换硬编码 SRC), A/B 上均与 gold 输出 byte-for-byte 一致
- check.py 21 断言 (k=21≥8): 见 test_rationale
- 验证: ref PASS 21/21 + 3 neg (empty/print-only/core-deleted) 全 FAIL + §4.9 三假 FAIL ✓ + E2E (harness layout) PASS ✓
