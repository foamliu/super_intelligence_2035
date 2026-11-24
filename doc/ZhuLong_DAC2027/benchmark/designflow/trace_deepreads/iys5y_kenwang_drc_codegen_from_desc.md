# Deepread: iys5y (kenwang@hfeg0pkn004, mc=59, 89 msgs, 908KB)

**Session**: `/home/kenwang/.cline/data/sessions/1795416159128_iys5y/1795416159128_iys5y.messages.json` on 10.129.2.13
**cwd**: `/home/kenwang/zl`
**Keywords**: drc:779;calibre:574;.def:220;analog:3 (pure physical_verify, DRC deck codegen)

## 真实任务 (msg 0)

kenwang 整理了 `DBC_H280_update.ev`（377 行，~80 条规则，每条只有 `@description` 没有code），要求 agent：
1. 根据 description 开发 SVRF code
2. 参考 `FS_H240.ev`（同类已开发规则，了解代码风格/派生层命名）和 `calibre_n5.drc`（n5 deck，找相似 rule）
3. 优先复用已有派生层/变量；无法开发的跳过并说明原因
4. 优先保证开发质量

## Agent 工作流

1. **上下文收集** (msg 3-28): 读 DBC_H280_update.ev（发现 377-496 行与 253-376 行重复，CM2A/CM2B_S_4/S_5 数值冲突 0.012/0.013 vs 0.018）；读 FS_H240.ev（前 890 行 + 890-1372 行，掌握模式：`CM1A_H = ANGLE (CM1A INSIDE BS_6) == 0` + `INT CM1A_H < v1 ABUT < 90 OPPOSITE REGION`）；发现 DBC_H280_update.ev 用 BS_6/MPRP_6 家族而 FS_H280.ev 用 FS_7/MPRP_7
2. **检索脚本** (msg 20-30): 写 `h280_grep_refs.sh` grep V05_coding_rebuild 目录，发现 `4_5_5_DBC_H180.ev` 有完全同族 DBC_H180_* 规则（M0_L_1 到 MPRP_R_2 全套）——最佳参考
3. **三轮检索** (msg 38-52): 确认全局层 `M2A_all/M2B_all/M3CA/M3CB/M2_24_up/SQR_BV0/MPRP_5_Zone/BS_5_RING/M1_20/M0C_H/BCM1H/ALL_GT_HW_LE6_CHK` 在 `1_4_global_layer_same.ev` 存在；n5 same-color 用 CA/CB 双色；`M0_PWR_BREAK_280 = CCP_10 NOT M0CAii` 命名法；CUT 在 n5 有使用
4. **代码生成** (msg 52-55): 用 editor 写 `DBC_H280_update.ev.new`，Part 1 (M0/M0C/V0G/V0D/M1) + Part 2 (CM1A/CM1B/VIA1/M2/CM2/M3/BV0/BM1/MPRP + 重复块处理 + #ENDIF)
5. **安装+校验脚本** (msg 56-78): 写 `h280_install_check.sh`：
   - 备份原文件 → 替换
   - CHECK 1: 花括号配平（非注释行 { 和 } 计数）
   - CHECK 2: 块结构（每个 { 行在下一个 { 前关闭）
   - CHECK 3: 重复检查块名（活动块）—— 用 `grep ^[A-Za-z][A-Za-z0-9_.]* *{` sort uniq -d
   - CHECK 4: 层引用完整性 —— 收集 in-file 定义（file-level `^name =` + block-local `^[ \t]*name =`）+ 已知全局层 + SVRF 关键字，comm -23 找未知标识符
   - 重复块注释：`////====` 到 `#ENDIF` 之间非注释行加 `//` 前缀
6. **校验 bug 修复** (msg 60-78): CHECK 3 暴露 30 个重复块未注释（`////====` 标记匹配错）→ 修 `index($0, "////====") == 1`；块内局部定义缩进未抓 → 修 `^[ \t]*[A-Za-z]`；补充全局层 CM3A/CM3B/VIA2；补充关键字 ANGLE1/ANGLE2/ENCLOSURE/HORIZONTAL/VERTICAL
7. **最终交付** (msg 88): 885 行，209/209 花括号配平，94 个活动检查块无重名，层引用零未知

## 关键 SVRF 模式（从 FS_H240.ev / DBC_H180.ev 提取）

```
# Width 规则: @Vertical width of <L> [INSIDE BS_6] = v1, v2
<L>_H = ANGLE (<L> INSIDE BS_6) == 0
INT <L>_H < v1 ABUT < 90 OPPOSITE REGION
INT <L>_H > v1 < v2 ABUT < 90 OPPOSITE REGION

# Space 规则: @Space of <L> ... >= v
EXT <L> < v ABUT < 90 OPPOSITE REGION

# Area 规则: @Area of <L> ... >= v
AREA <L> < v

# Enclosure 规则: @Enclosure of <L> ... >= v
ENC <L> < v ...
```

## 可计算子意图（本 case 取这个）

**DRC deck codegen-from-description + 静态校验工具**：给定一个 .ev 文件（规则只有 `@TYPE:layer=v1,v2` 描述，body 空），一个 patterns 文件（按 TYPE 给出代码模板 with {layer}/{v1}/{v2} 占位符），一个 globals 文件（已知层名 + SVRF 关键字）：
1. 对每个描述块，按 TYPE 查模板，代入 layer/v1/v2，写 code body
2. 注释掉重复段（`////====` 到 `#ENDIF` 之间非注释行加 `//`）
3. 校验：花括号配平、无重复活动块名、无未知标识符
4. 输出 output.ev + report.json

判分核心：模板代入正确性（数值出现在 code body）、重复段注释完整性、校验报告与文件实际状态一致、反硬编（B2 不同数值/层名）。

## 区别

与 DrcDeckStructureAudit-001（解析 DRC deck 提取 switches/layer_map/variables 生成审计 JSON）：本 case 是 **codegen**（从描述生成代码）+ **validator**（注释重复+校验），产物是 .ev 文件 + report.json，不是审计报告。
与 DrcDeckStructureAudit-001 / DrcResultsItemCollect-001：完全不同子型（codegen vs 解析）。
