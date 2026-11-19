# trace_deepreads/pzo1r_rowred_b64_restore.md — shard A r819

## session
- slug: `1793873712084_pzo1r` · user `johnl` @ `10.129.2.10` · mc5 · domain **digital**
- keywords (scan): A-pure (digital: verilog/rtl/primelib row-redundancy)
- file: `/home/johnl/.cline/data/sessions/1793873712084_pzo1r/1793873712084_pzo1r.messages.json` (subdir, 53923B, 3 msgs, mtime Nov 5) — ALIVE on 10.129.2.10
- ledger: r794-parked-ALIVE (2026-11-19 12:47) → r819 claim+mark case `EDA-Eval-DesignFlow-RowredB64RestoreProduce-001`

## 用户原话 (verbatim, msg 0)
`/home/johnl/.cline/scripts/data/primelib_char_T_IsmTop/dc_addr_to_region/rtl/rowred_behavioral.v  这是base64 压缩文件  还原`

## 意图
用户在 DDR5 primelib 字符化流程 `char_T_IsmTop/dc_addr_to_region/rtl/` 目录下有一个以 **base64 + gzip** 压缩存放的 Verilog 文件 `rowred_behavioral.v`（行冗余行为模型），想把它还原成原始 RTL。压缩文件内容是一整段 base64 文本（头 `H4sIAAAAAAAC` = gzip magic 的 base64 形态）。

## trace agent 行为
- msg 0 (user): 上面的还原请求
- msg 1 (assistant): thinking「用户说这个 .v 文件是 base64 压缩文件，要还原」+ tool_use `read_files` 读 `/home/johnl/.cline/scripts/data/primelib_char_T_IsmTop/dc_addr_to_region/rtl/rowred_behavioral.v`
- msg 2 (user/tool_result): cline read_files 回显文件前 571 行 base64（带 `  N | ` 行号前缀），尾注 `[Showing lines 1-571 of 3380. Use start_line/end_line to read other sections.]` —— 即原始压缩文件共 3380 行 base64，trace 只残留前 571 行
- session 在此结束（仅 3 条消息，agent 还没来得及还原/写出）

## 原始文件可达性
- `ssh 10.129.2.10 ls /home/johnl/.cline/scripts/data/primelib_char_T_IsmTop/dc_addr_to_region/rtl/rowred_behavioral.v` → **No such file**（文件已在主机蒸发）
- trace 残留的 571 行 base64 经清理后 `Invalid base64 (43457 chars, mod4=1)` 且只有 571/3380 行，**无法逐字复原原始 RTL**
- sibling `addr_to_rowcol_region.v`（satf4/akfxu 同目录，git "staged changes" Q&A）也已蒸发

## 判定
- **可造**：真实用户意图（还原 base64+gzip 压缩文件）= 真实 produce-task，交付物明确（还原脚本 + 还原后的 Verilog），check 可写「有牙」（解码确定性 → 隐藏 B/B2 逐字节比对 + 反硬编 + 双输入泛化）
- **档 = B 档 synthesized**：A 档（用真实压缩文件）不可行——原始文件已蒸发 + trace 仅残留 571/3380 行 base64 无法逐字复原。按 2026-10-31 归档令「B 档须说明 A 为何不可行」执行。忠实保留：真实任务形态（还原 base64+gzip 压缩的 Verilog）+ 真实 trace_source（johnl/10.129.2.10/pzo1r/mc5 + 用户原话）+ 真实路径语境（DDR5 primelib char_T_IsmTop/dc_addr_to_region/rtl）。资产 = 按 DDR5 primelib `dc_addr_to_region` 语境合成的同结构压缩文件（rowred/colred/addrmap 三个行为模型，均为 base64+gzip 压缩的 Verilog）。

## 候选筛审 (r818 flag 的 4 候选 @ 10.129.2.10)
- **pzo1r** (johnl mc5 54KB) ✅ 选定 —— 还原压缩文件 produce-task，check 牙齿最强（解码确定性 → 逐字节比对）
- satf4 (johnl mc7) —— 「addr_to_rowcol_region.v staged changes是什么意思」git 概念 Q&A；与 akfxu 逐字重复（dup）。新标准下 Q&A 合法但 check 牙齿弱（概念解释，无独立可验交付物，反硬编难构造）
- akfxu (johnl mc5) —— 与 satf4 同句 dup，跳过
- vqefw (e0029495 mc5) —— 「siliconsmart你知道userguide在哪」doc-search Q&A；agent 查 AskEDA KB 给 SolvNetPlus 链接。新标准下合法，但证据在私有 KB 不可复现，check 牙齿中弱
- 结论：pzo1r 的 produce-task 形态最满足 §4.2(subprocess-on-B) + §4.9(anti-hardcode) 硬闸门

## 合成资产 (B 档)
- A (SUT 见): `assets/.../rowred_behavioral.v` = base64(gzip(rowred_behavioral Verilog))，688 字节
- hidden B (judge-only): `hidden/colred_behavioral.v` = base64(gzip(colred_behavioral Verilog))，608 字节，模块名/端口/标识符全异（列冗余 vs 行冗余）
- hidden B2 (judge-only): `hidden/addrmap_behavioral.v` = base64(gzip(addrmap_behavioral Verilog))，436 字节，第三模块（地址映射），双输入泛化防单输出 stub
- 三个 Verilog 均为 DDR5 primelib `dc_addr_to_region` 语境下的行为模型（行冗余 / 列冗余 / 地址映射），结构同构、标识符全异

## check.py 10 条独立断言
① restore.py 存在+py_compile ② 在 B 上运行 exit0+非空 ③ B 输出合法 Verilog(module+endmodule) ④ B 模块名==colred_behavioral(反硬编A) ⑤ B-only>=3 且 A-only==0(跨输入反硬编) ⑥ B 输出 sha256==ground-truth(逐字节一致) ⑦ B2 也正确解码+模块名+sha256(双输入泛化) ⑧ 确定性 3 runs ⑨ 反退化(无 H4sI/非空壳/非拷贝输入) ⑩ 无 hidden 路径泄漏

## 自验
- ref PASS 10/10
- 4 neg 全 FAIL 命中 4 不同断言组（neg_empty→②、neg_print_only→⑥、neg_core_deleted→③、neg_hardcoded_a→④）→ 独立性证实
- §4.9 (a)empty (b)print-only (c)core-deleted 全 FAIL
- 3x 确定性 sha256 一致
- e2e: 从 A.jsonl test 字段抽出 check.py 独立跑 ref submit → PASS
- k_rationale = k_check = 10 ≥ 8 GATE PASS
