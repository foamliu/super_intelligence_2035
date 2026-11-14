# trace_deepread: 1789889776686_se4uf (miccao, mc106, physical_verify)

- **session**: `1789889776686_se4uf` @ hfeg0plg37 (10.129.32.47), 836KB, 125 msgs, 6 user turns
- **keywords**: .gds:566;drc:314;netlist:148;calibre:110;lvs:73;schematic:62;pdk:46;.cdl:43
- **tool counts**: list_allowed_files:17, read_files:17, editor:17, run_approved_command:14, skills:1
- **peek channel**: pyAether `run_code(host=aether)` 可读 `/home/miccao/.cline/data/sessions/<sid>/<sid>.messages.json`（r583 发现的新通道，推翻 r571-r582 九轮 0-case 枯竭判断）

## 用户轮（原话）

- **msg#0/#1**：`<user_input mode="act"># AutoCell TCL Flow Generator ...` = autocell-tcl-flow-generator skill 的系统级 prompt（skill 注入，非用户自然语言）
- **msg#2**（assistant skills 调用 args，实际用户任务）："Create AutoCell flow: netlist /home/miccao/autocell/ddcpc/netlist/train_proplus_decqa_20260903/netlist_dir_20260807/blcnand2PF47x1.cdl, constraints from /home/miccao/autocell.1.2026.7/g5_ddcpc/config/cell_constraints_template.txt, GDS output /home/miccao/autocell/black/gds, install /apps/proplus/autocell.1.2026.8" —— **A档合格 produce-task**（提需求+输入路径，未给根因/方案）
- **msg#80**："jixu"（continue）
- **msg#84**："你生成的gds中，有些层和这个gds里的不一样，你参考/home/miccao/autocell/decqa/gds/blcnand2PF47x1.gds，可以看/home/miccao/autocell/lvl/decqa/blcnand2PF47x1里面的lvl结果，告诉我是什么原因导致里面的图形有差异" —— **produce-task author-new-script**（让助手写 GDSII 比对工具定位差异）
- **msg#85/121**："继续"（continue）

## assistant 行为

1. **Create flow → 实为 run-existing + validate/fix**：发现 `/home/miccao/autocell/black/blcnand2PF47x1_flow/` 已存在完整 8 文件 TCL flow（planar NAND2，ZPower 电源引脚 vccz!/vss!，体偏置 vbn!/vbp!，器件 ptn_lv/ntn_lv）。assistant 读 references（pipeline.md/profile-planar.md/validation.md）+ validate_flow.py 静态校验（0 errors/15 warnings）+ run_2026_8.sh 跑 AutoCell 1.2026.8 → GDS 写入、内部 LVS 通过、外部 DRC (nano_verify) 返回 code 1。
2. **GDS diff 分析（msg#84 的核心 produce）**：author 一系列 GDSII 二进制比对脚本——
   - `gds_3way.py`：三路比对 black/decqa/ddcpc，忽略时间戳 record（BGNLIB 0x01/BGNSTR 0x05），逐结构比较 record 序列 + 按 layer 统计 boundary 计数
   - `gds_structdiff.py`：逐结构定位差异单元
   - `gds_m0u_ctx.py` / `gds_pcul.py`：dump M0U/PCU SREF 上下文
   - **结论**：A(black/generated) == C(ddcpc) 逐记录一致；A ≠ B(decqa reference)，差异全部在 `blcnand2F47x1_gut` 中间单元内部（Y 网 PCU_L 通孔变体/位置 18295_25190 vs 18555_25290 + M0U/MT2 布线走向），顶层结构完全相同。
3. editor 17 次多为**辅助分析脚本**（flow_grep.py/run_validator.py/log_inspect.py/gds_check2.py/cmp_gds.py/cmp_gds_geom.py/gds_3way.py/gds_structdiff.py/gds_m0u_ctx.py/gds_pcul.py），非 TCL flow 本身。

## 算法核心（用于 B档 mock-behavioral 重构）

GDSII record 流解析 + 时间戳忽略 + 按结构分组 + 按层统计 + 逐结构比对 → 结构化 diff 报告。纯 Python 标准库即可，无需 mock pyAether（算法本身即纯 Python 二进制解析）。

## case 落地

- **case_id**: `EDA-Eval-DesignFlow-GdsLvlStructDiff-001`
- **domain**: physical_verify（GDSII LVL 结构化比对，C 域 novel——无既有 case 做 GDSII 二进制 diff）
- **tier**: L2-boundary · B档 mock-behavioral · synthesized
- **k_check = k_rationale = 12**（a-l）：结构2 + B运行1 + identical1 + 结构数1 + diffStructures1 + match dict1 + layerCountsA1 + layerCountsB1 + firstDiffIndex1 + totalDiff1 + 时间戳忽略(B_ts identical)1 + B2反硬编1
- **自验**：ref GOLD 12/12 PASS ✓；§4.9 三假(empty/print/core-deleted)全 FAIL ✓；3 neg(always-identical/hardcode-B/count-timestamps)全 FAIL ✓；distinct first-fails=5 ≥2 ✓
- **隐藏输入**：B 对（4 结构/4 结构，3 差异：INVx1_gut/VIA_B_001/VIA_B_002）+ B_ts 对（仅时间戳不同，须 identical=True）+ B2 反硬编对（3/2 结构，2 差异：BUFx2_gut/DUMMY_B2）
- C.jsonl 355 → 356
