#!/usr/bin/env python3
"""Update MEMORY_C for round 154: archive r153, bump heartbeat, add r154 entry."""
import re, os

MEM = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/MEMORY_DESIGNFLOW_C.md"
ARCH = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/MEMORY_C_archive.md"

lines = open(MEM).read().splitlines()

# 1) find & extract the r153 entry line (starts with "- **轮(153)")
r153_idx = None
for i, ln in enumerate(lines):
    if ln.startswith("- **轮(153)"):
        r153_idx = i
        break
assert r153_idx is not None, "r153 entry not found"
r153_text = lines[r153_idx]

# 2) append r153 to archive (batch 154)
arch = open(ARCH).read() if os.path.exists(ARCH) else ""
if "归档批次 154" not in arch:
    arch += "\n\n## 归档批次 154 (r154 轮归档 r153)\n\n" + r153_text + "\n"
    open(ARCH, "w").write(arch)

# 3) replace r153 line with 1-line pointer
lines[r153_idx] = "- 轮(153) 已归档→ designflow/MEMORY_C_archive.md（EDA-Eval-DesignFlow-PcellBasexEncloseAudit-001, layout_virtuoso；归档批次 154；详细见归档）"

# 4) bump heartbeat lines 1-9
new_heartbeat = [
    "WAITING: 0",
    "SHARD: C (physical_layout)",
    "DOMAINS: layout_aether, layout_virtuoso, pg_layout, physical_verify",
    "round: 154",
    "📊 trace 覆盖率：150/8598=1.7%（r154 交付 Nand3LefDeriveAudit-001 pg_layout；ledger 283:case 150·parked 133·claimed 0；mc30 池 8598/mc100 4615/mc300 1001）",
    "🎯 通过率: shard C 累计 150 case 已落 ledger（jsonl 149 行；pi/cline 实跑数见 cline_eval_status.jsonl，B 档目标 20–30%）",
    "🧾 断言: k_rationale=k_check ✓（150/150 达标；r154 新增 Nand3LefDeriveAudit-001 k=14/14 a–n）",
    "📦 体积：TASK≈17KB / MEMORY_C≈32KB（<32KB ✓，r154 归档 r153 到 MEMORY_C_archive 批次154）",
    "🛠 DEBT: 0（r153 已清零，r154 正常交付 1 case）",
    "",
    "",
]
# replace first 10 lines (indices 0-9) with new heartbeat (10 lines) — keep blank lines after
# original lines[0:10] are the 9 heartbeat + 1 blank. Replace exactly 10.
lines[0:10] = new_heartbeat

# 5) insert r154 entry right after the heartbeat (after the two blank lines at new_heartbeat end)
r154_entry = (
    "- **轮(154) 已交付 EDA-Eval-DesignFlow-Nand3LefDeriveAudit-001（pg_layout, B-档 faithful-seed-B-synthesized, L1-boundary）✓** —— "
    "trace=1792493511731_624js（johnl @ hfeg0pfn119, mc=80, active 75 msgs/120KB + archive 2882 msgs/8.8MB; tools 165 innovus 纯 innovus-dominant → pg_layout seed, fresh-user）。"
    "真实任务（archive USER idx699/761 原话逐字）「已确认的真值：源 OA prBoundary 为 (0,0)–(3.88,6.71) µm，DBU=10000…SIZE 必须为 3.88 BY 6.71；ORIGIN/FOREIGN…不再出现整数极值；Y 为 OUTPUT，vcc!/vss! 为 POWER/GROUND；原有引脚、OBS 和供电图形不得被错误平移或裁剪；不改源 OA/GDS/LEF/PDK，不启动 P&R」（用户给真值+约束, 未给方案→A-档合格 seed）。"
    "真实根因：ski-genlef(GenLEF) 日志 FINDBOUNDARY-INFO 读到 prBoundary=3.88x6.71@(0,0) src_OA，但 dbCreateRect 报 `Extra arguments` + `Cell 'nand3LVSx1' does not have layer '235:250'`，boundary rect 没建 → 产出 LEF 头部崩成**整数极值哨兵** `ORIGIN -214748.3647 -214748.3647` / `FOREIGN nand3LVSx1 214748.3647 214748.3647` / `SIZE 0.0001 BY 0.0001`（±214748.3647=INT32_MAX/DBU；退化回退值）。"
    "assistant 用 emyPRBoundary.find(cv.getTopBlock()) 确认真实 prBoundary，写 derive_lef.py 派生独立 LEF：坐标核对（vss! 轨 Y−0.41..+0.41 居中 0；vcc! 轨 Y6.30..7.12 居中 6.71；引脚 Y 0.78..5.711 全在 prBoundary 内）→ ORIGIN/FOREIGN=(0,0)；diff 仅改 SIZE/ORIGIN/FOREIGN 三行（−整数极值/+0.000 0.000 +SIZE 3.880 BY 6.710）；五项核验全 PASS（SIZE/ORIGIN/FOREIGN/Y OUTPUT/vcc!vss! 供电角色/几何 0 处不同/无整数极值）；交付 nand3LVSx1_derived.lef+derive_lef.py+prb_points.txt，用户接受。"
    "本 case 取**正交子主题**(GenLEF 丢失 prBoundary 的 LEF 头部派生修复, 与 r112 PaCfgMigrate/r139 RsRedFlowOrchestrator 等 pg_layout case 均正交): 给「坏」LEF(整数极值头+完整 PIN/OBS 体)+真实 prb.txt 写 derive_lef.py 做「派生修复」——CLI <input.lef> <prb.txt> <output.lef>, 解析 prb(xmin,ymin,xmax,ymax µm), 在 MACRO 块内定位 ORIGIN/FOREIGN/SIZE 三行**只改这三行**(SIZE=(xmax−xmin) BY (ymax−ymin)、ORIGIN=(xmin,ymin)、FOREIGN 引用点=(xmin,ymin), 3 位小数), 检测整数极值哨兵(|v|≥214748 或 SIZE<0.001)→sentinel_detected, 其余行原样保留行数守恒, stdout JSON 报告(macro/prboundary/size/origin/foreign/sentinel_detected/lines_changed/verdict)。"
    "A(nand3LVSx1, prb 0,0,3.88,6.71, 整数极值头, pins A/B/Y/vcc!/vss! Y=OUTPUT vcc!=POWER vss!=GROUND) 给 SUT；隐藏 B1(nand3LVSx1, prb 1.20,0.50,5.00,7.21 → SIZE 3.800 BY 6.710, ORIGIN/FOREIGN 1.200 0.500; **非零 min 暴露 size_h=ymax=7.21 与 foreign=(xmax,ymax)=(5.00,7.21) 两类 naive bug**) / B2(跨输入守卫 inv2xLVSx1, prb 0,0,2.40,4.00, pins IN/OUT/VDD/VSS, **输出不含 A 专属 token nand3LVSx1/'PIN Y'/vcc!/vss!**) / B3(malformed 无 MACRO→exit1) base64 内嵌 check.py 真跑。"
    "判分 14 条独立条件 (a–n): ①(a)zip+py_compile ②(b)CLI --help/-h/无参 ③(c)B1 exit0+写输出 ④(d)B1 SIZE==3.800 BY 6.710 ⑤(e)B1 ORIGIN==1.200 0.500 ⑥(f)B1 FOREIGN 引用点==1.200 0.500 ⑦(g)B1 头部无整数极值哨兵残留 ⑧(h)B1 PIN/OBS 保留(Y OUTPUT/vcc! POWER/vss! GROUND/RECT 行逐行一致) ⑨(i)仅 SIZE/ORIGIN/FOREIGN 三行改, CLASS/SITE/SYMMETRY 不变, 行数守恒 ⑩(j)B2 跨输入 SIZE 2.400 BY 4.000+ORIGIN/FOREIGN 0 0+FOREIGN cellname=inv2xLVSx1+无 A 专属 token ⑪(k)B2 PIN USE 保留(VDD POWER/VSS GROUND/OUT OUTPUT) ⑫(l)B3 无 MACRO exit!=0+stderr+不写输出 ⑬(m)确定性 B1 两跑 stdout+md5 一致 ⑭(n)反 naive B1 输出≠输入 md5 且 B3 exit!=0。"
    "自验：REF check() PASS 14/14；negative_selftest NEG_RC=0（5 fakes 全 FAIL）；§4.9 三假(empty/print-expected/core-deleted)全 FAIL；REF on A: size[3.88,6.71] origin[0,0] foreign[0,0] sentinel=True verdict=DERIVED；check.py md5 d8a4ad4a1fc1f5b47744b34ca5802483（disk==jsonl embedded test roundtrip ✓）；k_rationale=k_check=14>=8 GATE ✓；ledger mark 624js→case, covered 149→150, pg_layout case 20→21; jsonl 148→149。"
    "踩坑/笔记：summary.tsv 工具列对 innovus 计数偏少且 host 名含 'pgn' 会误匹配 grep 'pg'（须只对 $7 tools 列做 tolower 正则, 勿含 host 列）；624js active .messages.json 仅 75 msg(PT STA 续聊), 真正 PR/LEF 工作在 .messages.archive.json(8.8MB, 3 个 archivedAt 对象含 messages 数组, 共 2882 msg)——pg_layout 深读必须同时读 archive; trace 领域判定不能只看 mc/innovus 计数, 须读用户原话(nand3 prBoundary/GenLEF/SIZE 3.88 BY 6.71 = pg_layout PR-LEF 主题)。leakage 隔离 OK（B1/B2/B3 base64 内嵌 check.py，repo 无 hidden/ 暴露 SUT；SUT 只见 A.lef+prb_A.txt+prompt）。"
)
# insert r154 entry at index 11 (after new_heartbeat's two trailing blanks which are at idx 9,10)
# new_heartbeat has 11 elements (indices 0-10). Insert r154 at index 11, then a blank.
lines.insert(11, r154_entry)
lines.insert(12, "")

out = "\n".join(lines) + "\n"
open(MEM, "w").write(out)
print("MEMORY_C bytes:", len(out.encode()))
print("archive bytes:", len(arch.encode()))
print("round line:", [l for l in lines if l.startswith("round:")][0])
