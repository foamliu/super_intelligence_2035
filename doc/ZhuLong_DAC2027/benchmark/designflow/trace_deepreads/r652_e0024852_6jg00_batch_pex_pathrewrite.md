# r652 deepread — 6jg00 (e0024852 @ hfeg0plg85) — BatchPexGdsPathRewrite-001

## trace 元数据
- session: `1794537778378_6jg00` (e0024852 @ hfeg0plg78 = 10.129.8.123)
- file: `/home/e0024852/.cline/data/sessions/1794537778378_6jg00/1794537778378_6jg00.messages.json` (331,647 bytes / 101 msgs / 3 user-text turns)
- scan keywords: lvs:404;calibre:310;pex:117;netlist:84;.cdl:34;.gds:23;schematic:4;pdk:3 — 强 C-signal (physical_verify)
- match_count: 134 (mc≥10 ✓)
- domain: physical_verify (PEX 提取流程脚本路径修复)

## 用户意图（3 real user turn）
- **U#0 (msg0)**: `修改 /rundata/.../CH336_FS_guojing/batch_pex.py  gds 的路径在 gds 文件夹下面 文件路径都用当前路径下的名字 提取寄生` — 提出需求型，未给根因/方案（仅给目标：GDS 取自 gds/ 子文件夹 + 配置文件用当前目录名）
- **U#1 (msg66)**: `tell me in chinese`
- **U#2 (msg68)**: 运行 `python batch_pex.py` 的输出 `Total GDS files: 1 / [1/1] Processing: CH336_HC_Bitcell_FS_PIN / LVS: FAIL lvs.rep not found (1.9s)` — **用户测试运行**，脚本找到 GDS（路径修复生效），但 LVS 下游失败

## assistant 工具链
1. read_files 原 batch_pex.py（msg3，分段读取）
2. editor 多轮重写为 `batch_pex.py.new`（msg29-35）：
   - `WORK_DIR = os.path.dirname(os.path.abspath(__file__))` (当前目录锚)
   - `GDS_DIR = os.path.join(WORK_DIR, "gds")` (GDS 取自 gds/ 子文件夹 ✓)
   - `LVS_FILE/GXRC_FILE/CDL_FILE/QUERY_CMD` 均按 basename 置于 WORK_DIR ✓
   - `TOPCELL = "CH336_HC_Bitcell_FS_PIN"` / `SOURCE_PRIMARY = "CH336_bitcell_FS"` (硬编码常量)
   - `modify_lvs_deck(gds_path)`: regex `LAYOUT PATH ".*?"` → `LAYOUT PATH "{gds_path}"`
   - `modify_gxrc_cmd(gds_basename)`: regex `NETLIST_FILE{ FILE_NAME\t...` → `./output/{basename}.dspf` + `COUPLING_CAP_REPORT\t...` → `./output/{basename}.cc.rep`
   - `run_calibre_lvs` / `run_cci_query` / `run_gxrc` / `validate_cc_rep` / `validate_dspf`
   - `main()`: glob gds/*.gds 排序迭代 + clean_workspace + LVS+CCI+gxrc + 校验 + collect all_dspf + summary
3. py_compile 验证 + 部署到 target + cleanup（msg44-52）
4. 用户运行后 LVS FAIL → assistant 转 debug **Calibre VCO 环境**（msg81-100）：机器是 aok VCO 但系统只装 aoi build calibre → VCO mismatch 拒绝运行 → 搜索 aok/aoj calibre → msg100 find /apps SIGKILL 超时，session 截断未恢复

## gold 状态（关键）
- **路径修复 gold 达成**：用户 U#2 运行后脚本找到 GDS（"Total GDS files: 1, Processing: CH336_HC_Bitcell_FS_PIN"）= 用户隐式接受路径修复生效
- **下游 LVS 失败 = 正交环境问题**：Calibre VCO aoi/aok 不匹配，非脚本 bug；assistant 转去 debug 环境未恢复
- ⇒ 本 case 金标准 = **路径解析逻辑**（WORK_DIR/GDS_DIR/config-basename/topcell + deck-modify 替换目标），用户已验证 GDS 找到；LVS 环境失败在 real_task_summary 如实记录
- 对比 r651 wy27j（AutoViaV4Dir3DY，U#3「没有办法生成V4」=核心任务失败 0-gold）：本 case 核心任务（路径修复）=用户已验证生效，下游失败是另一问题

## r652 处置：CASE DELIVERED — BatchPexGdsPathRewrite-001
- **B档 mock-behavioral reframe**（承 r650 CutLayerIdxBugFix / r645 AntennaRuleFamilyExtract 模式；新子型 `pex-batch-script-path-resolution-reframe`，distinct vs r650=cut-layer-name whole-token 匹配 / r645=SVRF antenna rule family extract / r634=nonascii-sanitize / r642=via-enclosure-r90-force：本 case=PEX 批量脚本路径解析修复 modify-existing reframe）
- 真实 batch_pex.py 在 /rundata（沙盒不可达 + e0031982 无权限）→ 合成紧凑可运行 mock workspace 作 asset A（gds/ + lvs deck + gxrc cmd + cdl + query_cmd + pex_config.json + buggy batch_pex_orig.py 作上下文）
- deliverable = `batch_pex.py` dry-run 路径解析器：`python batch_pex.py <workspace>` → stdout JSON{work_dir, gds_dir, topcell, source_primary, config_files{4}, gds_files[{basename, short_name, gds_path, lvs_layout_path, gxrc_netlist_file, gxrc_cc_report}], total_gds}
- check() 16 条件 a-p：跑 hidden B（workspace_B, CH231_HDT_Bitcell_DBC_WiPin, 3 gds, 不同 config basename）+ B2（workspace_B2, CH180_SRAM_Bitcell, 1 gds）反硬编码 + 确定性
- **自验**：gold ref PASS 16/16 ✓；7 negatives（neg1 hardcode-A / neg2 no-gds-subfolder / neg3 unsorted / neg4 hardcode-count / fake_empty / fake_print_expected / fake_core_deleted）全 FAIL ✓，6 distinct first_fail labels（c/d/e/f/l/m）≥3 ✓；§4.9 三假全 FAIL ✓；test==disk check.py 字节同步 sha 38baa028401f70c3 ✓；k_rationale=k_check=16>=8 GATE PASS ✓

## 教训（承 r651 SOP 应用）
- r651 教训「选料前 grep ledger 排除已 case」：本轮先 grep ledger 验证 6jg00 仅 parked 非 case ✓
- r651 教训「deepread 先看 trace 末尾 5-10 条消息（倒序省 80% 时间）」：本轮先 peek 末 20 msgs 确认用户运行结果（U#2 GDS 找到）+ session 末环境 debug 截断 ✓
- r651 判据收敛验证：revival 候选可造与否取决于 **trace 末尾用户接受 artifact**；6jg00 用户 U#2 运行确认路径修复生效 = 可造（对比 r651 wy27j 0-gold）
- r557 parked reason「thin PEX orchestration, budget-limited」复核：路径解析逻辑足够 structured（WORK_DIR/GDS_DIR/4 config-basename/regex-subst 2 处/glob 排序/short_name/total）支撑 16 独立 teeth，非 thin
