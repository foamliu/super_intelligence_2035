# trace deepread: ddo96 (e0024852 @ hfeg0pkn004, FineSim gxrc_t libdizo.so missing fix)

## 元信息
- sid: 1793944907619_ddo96.messages.json
- user: e0024852 · host: hfeg0pkn004 · mc: 218
- 时间窗: 2026-11-06 14:32 (mtime, fresh ≥ 11-06, 不在 11-05 summary.tsv)
- msgs: 61 · user turns: 8
- domain: spice_sim (FineSim SRAM bitcell DTCO gxrc_t)

## 用户轮逐字（A-faithful 选用 U#0，提需求无根因 ✓）
U#0: "in /rundata/lacaa/TV1_FS/simdir/finesim/workdir/e0024852/SRAM_bitcell_DTCO/Bitcell_FS/CH231_FS_guojing i run /rundata/.../GloryEX_2026.06_P010/tool/bin/gxrc_t -c gxrc_cci_cmd_V0d1_Rev07 and got error .../gxrc_t: error while loading shared libraries: libdizo.so: cannot open shared object file: No such file or directory how to fix it"
- U#0 提出需求（运行 gxrc_t 报错 libdizo.so 缺失），未指出根因 → A档 ✓

## assistant 工具链（金标准推导）
1. A#1 run_commands → 被禁（policy engine）
2. A#7-A#16 run_approved_command + list_allowed_files + read_files → 探查 P010/P004 目录
3. A#14-A#28 写 diag_dizo{,2,3,4}.sh 诊断脚本 → 发现：
   - P010 tarball 截断（gzip -t 报 unexpected end of file），仅 186/1349 库被解压
   - libdizo.so (86MB) 在 P004 有，P010 缺
   - gxrc_t RPATH = $ORIGIN/../lib/lib
4. A#36 写补库脚本（comm -23 全量复制）→ U#4 报段错误
5. A#38-A#49 diag_segv/diag_fix/diag_glibc → 发现：全量复制把 P004 自带 glibc（libc.so.6/ld-linux/libm/libpthread/librt/libdl/libgcc_s）拷进 P010，LD_LIBRARY_PATH 前置导致 libc 版本不匹配段错误
6. A#50-A#60 最终修复：
   - 删除误拷的 glibc 系统库
   - 仅补非系统缺失库（含 libdizo.so + libstdc++.so.6.0.33 GLIBCXX_3.4.33）
   - export LD_LIBRARY_PATH="$P010/tool/lib/lib:$LD_LIBRARY_PATH"
7. U#7 "now the gloryfx is ok" + A#60 "搞定就好 👍" → 用户接受

## 金标准（用户实际接受的结果）
fix_missing_libs.sh:
- 读 needed_libs.txt 逐行
- 跳过系统库（libc.so*/ld-linux/libm.so*/libpthread*/librt.so*/libdl.so*/libgcc_s*）
- 非系统库缺失则从 P004 复制到 P010/tool/lib/lib
- 生成 setup_env.sh: export LD_LIBRARY_PATH="$P010/tool/lib/lib:$LD_LIBRARY_PATH"
- 关键：不复制 glibc 系统库（否则段错误），保留 libstdc++.so.6（gxrc_t 需 GLIBCXX_3.4.33）

## 案例交付
- case_id: EDA-Eval-DesignFlow-SharedLibDeployFix-001
- domain: spice_sim · track: faithful (A) · level: L1
- A 资产: GloryEX_2026.06_P010 (8 .so, 缺 7 非系统) + GloryEX_2026.06_P004 (21 .so, 含 7 系统) + needed_libs.txt (18)
- hidden B: GloryEX_2026.06_P010 (6 .so, 缺 6 非系统) + P004 (18 .so) + needed_libs.txt (16) + gxrc_t 检查 libdizo/libsparse/libstdc++
- check.py 10 断言(a-j) + 3 negative(naive_copy_all/always_ok/hardcoded_A)
- 自验: ref PASS 10/10 ✓ + 3 negative 全 FAIL ✓ + §4.9 三假全 FAIL ✓ + 闸门 10==10≥8 ✓
