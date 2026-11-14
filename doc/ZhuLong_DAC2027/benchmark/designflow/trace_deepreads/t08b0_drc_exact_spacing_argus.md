# trace_deepread: t08b0 — DRC SVRF exact-spacing rule modify for Argus

- **session**: 1792647973145_t08b0
- **user/host**: sherlock @ 10.129.33.137 (hfeg0pkn003-area)
- **mc=43**: drc:173;calibre:56;lvs:31 (physical_verify dominant)
- **size**: 137KB, 32 msgs, 8 user turns
- **domain**: physical_verify (Calibre/Argus SVRF DRC deck authoring)

## 意图演进（user turns）
- U#0 (msg 0): "解释一下这一段DRC deck BLR_S_004_00{ @Min - Space between BLR and AGT ... EXT BLR AGT < _BLR_S_004_00_ ABUT<90 SINGULAR INSIDE ALSO REGION  BLR INTERACT AGT }" = **explain Q&A** (not produce-task)
- U#1 (msg 5): "如何把这条规则改为检查BLR与AGT之间的精确间距，并且只需要一条边符合即为通过" = **A档合格 produce-task modify-existing** (提需求：改为精确间距 + 一条边符合即通过；未给根因/方案) ← A档任务说明用此轮
- U#2 (msg 7): "更倾向与情况A" = refine (选 OPPOSITE facing-edge 方案)
- U#3 (msg 9): "这种写法会把正确的情况认为是错误的，请优化代码" = refine (指出 EXT == 会把正确情况报错 → 需 existential one-edge-pass 语义)
- U#4 (msg 11): "添加这一行代码 'EXT BLR AGT > _BLR_S_004_00_ + _TOL_ OPPOSITE' 后, Argus DRC 提示 Failed to compile rule file" = debug (给症状：Argus 编译失败)
- U#5 (msg 27): "你找错了，我是用的deck是 BLR_S_004_00{ EXT BLR AGT < _BLR_S_004_00_ OPPOSITE  EXT BLR AGT > _BLR_S_004_00_ OPPOSITE  BLR INTERACT AGT }" = correction (给真实 deck)
- U#6/U#7 (msg 29/30, duplicated): "EXT BLR AGT > _BLR_S_004_00_ OPPOSITE 会报 Failed to compile rule file 错误" = debug (定位：`>` 运算符本身 Argus 不支持，不只是 `+ _TOL_` 算术)

## assistant 工具链
- skills (argus-tool-helper) ×2 (msg 1, 12；第一次 args 类型错误被拒)
- read_files ×3 (msg 17 读 PCT_AGT_DRC.rule / argus / gen_drc.sh；msg 24 读修改后片段)
- editor ×2 (msg 21 改 PCT_AGT_DRC.rule：加 PCT_AGT_MIN_SPACE/MAX_SPACE 预算变量 + 替换 Check_002 内联 `0.15 ± TOLERANCE` 为变量)
- search_codebase ×1 (msg 15, timed out)
- list_allowed_files ×1 (msg 16, 发现 Documents/PCT_AGT_DRC.rule)

## 真实算法 / 关键技术点
1. **原规则**：`EXT BLR AGT < _BLR_S_004_00_ ABUT<90 SINGULAR INSIDE ALSO REGION` = min-space check (间距 < 值 报错)。
2. **目标**：改为**精确间距**（spacing 必须等于 target，带容差 ±tol），且 **one-edge-pass**（任意一条 facing edge 符合 → 该检查通过，不报违例）。
3. **OPPOSITE**：只检查正对（facing）的边对，去掉 ABUT<90/SINGULAR/INSIDE/REGION。
4. **Argus 限制（核心 trap）**：
   - `EXT ... > value`（max-space / 大于间距）**Argus 不支持** → "Failed to compile rule file"（msg 29/30 确认：去掉 `+ _TOL_` 后 `>` 仍编译失败）。
   - `EXT ... < value + _TOL_` 内联算术**也不支持**（msg 11 报错根因之一）。
5. ** SIZE-based workaround**（msg 31 assistant 思路，被截断）：用 SIZE 扩张 + NOT TOUCH 实现 "too far" 检测，绕过 `>` 限制。
6. **容差实现**：把上下界 `target ± tol` **预计算成变量**（如 `_BLR_AGT_MIN_SP = 0.149`, `_BLR_AGT_MAX_SP = 0.151`），EXT 里直接用变量，避免内联 `X + Y`。
7. **overlap**：`BLR INTERACT AGT` 保留，重叠独立报违例。

## case 建模决策（B档 mock-behavioral）
- 把 "SVRF exact-spacing + one-edge-pass + Argus-safe" 重构为纯 Python 几何评估器（mock Argus/SVRF 引擎，核心算法保留）：
  - 输入 layout deck（BLR/AGT 多边形 = rect 复合）+ spec（target/tol/layer1/layer2）
  - 逐对 (blr_poly, agt_poly)：
    - 任一 constituent rect 重叠 → overlap violation（跳过 spacing）
    - 收集所有 facing edge gaps（轴对齐 rect：x 方向 facing 需 y 投影重叠，y 方向 facing 需 x 投影重叠）
    - **one-edge-pass**：任一 facing gap ∈ [target-tol, target+tol] → 该对 PASS
    - 否则：closest gap < min → too_close；closest gap > max → too_far
    - 对角分离（无投影重叠）→ 无 facing 边 → 非邻接 PASS
  - 输出 report.json（total_pairs / overlap_violations / too_close_violations / too_far_violations / passing_pairs / conforming_edges / violations 列表）
- **陷阱**（判分核心）：
  1. one-edge-pass：复合多边形一条边符合 → 整对 PASS（naive "任一边不符即报错" FAIL）
  2. 容差边界：gap == min_b / max_b 算 conforming（naive 严格 < FAIL）
  3. overlap 独立：重叠对跳过 spacing（naive 对重叠对算 spacing FAIL）
  4. 非邻接（对角分离）：无 facing 边 → PASS，不算 too_far（naive "远即 too_far" FAIL）
  5. mixed → too_close：复合多边形既有 <min 又有 >max 边、无 conforming → 按 closest 归类
  6. B2 反硬编：不同 target/tol/位置 → 不同计数
- **Argus `>` 限制**化作 prompt 背景动机（"不能用裸 `>` max-space，改用上下界 + one-edge-pass 语义"），deliverable 是 Python 评估器（非 SVRF 文本，因 SVRF 语法约束难在 Python 判分）。
- dual-hidden-fixture：B（10 对，target=0.15 tol=0.01）/ B2（7 对，target=0.20 tol=0.02）。

## 谱系
- produce-task 第十四子型 drc-exact-spacing-argus-safe（承 r536 EncloseSide2Good5 / r535 PctAgtSpacingDeck DRC-deck 族 + r556 InvCellCreate / r562 DupOriginRotate 几何评估族），anti-hardcode dual-hidden-fixture（B 10对 / B2 7对）。
- A档 task 说明 = U#1 原话（提需求未给根因/方案）。
