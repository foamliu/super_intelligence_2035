# Deepread 7bg20 — addr_to_rowcol RTL→DRVQA stdcell 门级映射

- **session**: `1790650962650_7bg20.messages.json`
- **user/host**: fxian@hfeg0pkn002
- **match_count**: 221 (schematic_netlist domain, D)
- **grade**: B synthesized（私有 DRVQA catalog `/home/fxian/python/drvqa` 对 e0031982 不可读 → 复刻 trace 的映射阶段）

## 真实任务（trace 还原）
用户要求把 Verilog RTL `addr_to_rowcol`（地址 A → row/col/valid 映射）映射到 DRVQA 项目的标准单元门级原理图。agent 在 Aether（pyAether）里：

1. **全仿真 RTL 真值表**：对 296 个输入向量逐一仿真 `addr_to_rowcol`，拿到 (A → row, col, valid) 完整真值表。
2. **面积优化**：÷3（地址到行号）用**级联减法**替代除法器，省面积。
3. **门级映射**：用 DRVQA stdcell catalog（NAND2/AND2/OR2/INV/MUX2 等）把优化后的逻辑映射成门级网表，最终交付 `R_BADEC_ADDR2ROWCOL.v`（msg#190 附近）。

trace 主线是组合逻辑综合（RTL truth-table → stdcell gate mapping），属 schematic_netlist domain 的“网表映射”子类。

## 为什么 B-grade synthesized
- 真实资产（DRVQA catalog、原始 RTL、Aether 设计库）都在 fxian 私有目录 `/home/fxian/python/drvqa` 与 `/proj/.../fxian` 下，e0031982 无读权限（与 #408-#413 同因）。
- A-grade faithful（直接用真实 DRVQA catalog + 真实 RTL 跑映射）不可行。
- B-grade：忠实复刻 trace 的**映射阶段**——给一份迷你 case 风格 RTL（addr→row/col/valid）+ 一个 stdcell catalog JSON，让候选写**通用 mapper.py** 把 RTL 综合成门级 netlist.json，离线 subprocess 评分。

## 合成 case 设计（EDA-Eval-DesignFlow-AddrRtlGateMap-001）
- **A（可见）**：4-bit 输入 A，2-bit row，2-bit col，1-bit valid；3 个 region（[0-3]→row0, [4-7]→row1, [8-9]→row2），default(≥10)→row0/col0/valid0；catalog 8 cell（INV/NAND2/AND2/OR2/NOR2/XOR2/MUX2/AOI21）。
- **B（隐藏）**：5-bit 输入 A（32 向量），3-bit row，2-bit col，1-bit valid；4 个 region 各 5（[0-4]→row0…[15-19]→row3），default(≥20)→row0/col0/valid0；catalog 6 cell（drop MUX2/AOI21，只剩 INV/NAND2/AND2/OR2/NOR2/XOR2）。
- **A≠B 每维度**：输入宽度、输出宽度、region 数、region 边界（5 不对齐 2 的幂，逼真综合而非位模式硬编码）、catalog 子集全不同 → 反硬编码。
- **netlist.json schema**：module/ports(inputs,outputs)/instances[{name,cell,inputs,output}]/port_drivers{输出位→net}；net 名 = 顶层输入位 `A[i]` / instance 输出 / 常量 `1'b0`/`1'b1`。

## 12 条断言（check.py a-l）
a zip 含 mapper.py ｜ b subprocess 跑通产 netlist.json ｜ c 四字段齐 ｜ d cell 在 catalog 内无乘除模 ｜ e instance 名唯一+引脚匹配 ｜ f net 闭合无悬空 ｜ g 输出位唯一驱动 ｜ h 全 2^N 向量功能等价 ｜ i 越界 valid=0 ｜ j 3 次重跑确定 ｜ k cell 数在界(≤4×outbits+40) ｜ l ≥2 种 cell

## 参考解（reference/mapper.py）
- 通用：解析 case 风格 RTL → 真值表 → 每个输出位 Quine-McCluskey 最小化 SOP → 用 catalog 的 INV/AND2/OR2 综合（INV net 跨 product 共享）。
- B 跑出 40 instance（INV×4/AND2×27/OR2×9），row[2] 自动综合成常量 0（B 的 region 只到 row=3=011，row[2] 恒 0）→ QM 正确识别。
- A 跑出 13 instance，0 mismatch。
- 3-seed 确定性：run1==run2==run3。

## 自验
- ref submit.zip → check.py PASS 12/12。
- 三假：empty（b fail，c-l blocked）/ print-only（b fail）/ core-deleted 全输出 0（h+k+l fail）→ 全 FAIL。
- 两 neg：neg_hardcode_A（硬编码 A 4-bit 真值表，在 B 5-bit 上 g/h/i/k fail）/ neg_xor_shuffle（XOR2 乱接，h/i/l fail）→ 全 FAIL。
- byte-sync sha d4121e46 size 15549。

## 流水结论
- 7bg20 属 D 域 schematic_netlist 的“RTL→门级综合映射”子类，trace 真实、任务清晰、可 B-grade 复刻，符合选料标准。
- case 已 append EDA-Eval-DesignFlow_D.jsonl（228→229），ledger mark case。
