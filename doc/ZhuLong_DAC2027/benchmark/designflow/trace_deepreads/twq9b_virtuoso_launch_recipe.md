# Deep-read: 1793237557021_twq9b — Virtuoso RHEL8 launch + LACAA SRAM Bitcell open

- **trace**: `1793237557021_twq9b` · user `e0030760` @ `hfeg0pkn004` (10.129.2.13) · mc=342 · 357 msgs · 860KB
- **tool breakdown**: 682 virtuoso + 387 schematic + 63 hspice + 50 netlist + 29 cellview + 17 calibre + 5 pyAether + 4 spectre + 2 dbGet (SKILL lang)
- **domain**: layout_virtuoso (Virtuoso IC6.1.7 GUI launch + schematic cellview open)

## 用户意图（两轮）
1. (msg 0) "帮我打开电路图查看软件" → 选择 Cadence Virtuoso IC6.1.7
2. (msg 133) "我想查看LACAA 的SRAM 电路" → 在 Virtuoso 中打开 LACAA SRAM Bitcell schematic

## assistant 工具链 & 根因诊断（关键知识）
**Phase 1 — Virtuoso 启动排障（msg 0–132）**：
1. **OA 平台不识别 RHEL8**：OA 22.50 `sysname` 返回 `unknown`（只内置 `linux_rhel50_gcc48x_64`，RHEL8 内核 4.18 落入 `check_global`）。修复：`export OA_UNSUPPORTED_PLAT=linux_rhel50_gcc48x`
2. **freetype 符号冲突**：`libfontconfig.so.1: undefined symbol: FT_Done_MM_Var` — Virtuoso 把 `libfreetype.so.6` 解析到 **INCISIVE 15.20.024 自带的旧版** (`/apps/cdsmgr/CRB/INCISIVE/15.20.024/tools.lnx86/python/64bit/lib/libfreetype.so.6`，不导出 `FT_Done_MM_Var`)。修复：`export LD_LIBRARY_PATH=/usr/lib64:$LD_LIBRARY_PATH`（系统新 freetype 导出该符号）
3. **VNC libnsl 32-bit**：`-nographinfo` 让 Virtuoso 走 `cdsXvncd`（32-bit），缺 32-bit `libnsl.so.1`。修复：**去掉 `-nographinfo`**，直接用远程桌面 X display `hfeg0plg55:1073.0`（已验证 `xdpyinfo` 可连）
4. **setsid 脱离会话**：`setsid nohup virtuoso ... &` 让进程脱离 agent 沙箱会话清理（SID=PGID=PPID 1）

**Phase 2 — LACAA SRAM 定位（msg 133–232）**：
5. `/proj/lacaa/V0` 是 LACAA V0 Virtuoso 设计数据（`cds.lib` + `lib.defs` + `libs/`）
6. **`lacaa_sram` 库**（1611 单元）只在 `lib.defs`（不在 `cds.lib`）；含 `Bitcell` 单元，有 **schematic + symbol + layout**（`sch.oa` 39KB）
7. 网表引用 `BitCell_FS_Simulation_CH336`（位单元仿真模型）
8. **`deOpenCellView` 用法**：本地脚本 `/proj/shdc/cad/skill/ut/IMCutDesignReview.il` 真实调用 `wid = deOpenCellView(libName cellName viewName "sch")`。用 `virtuoso -replay <skill.il>` 启动时执行

**Phase 3 — 静默退出根因（msg 234–356，最深层）**：
9. **ARGUS server.tcl 自动退出**：站点 `.cdsinit` 加载 `argus.il` → `ipcBeginProcess` 启 `server.tcl`，"ARGUS will close server"。但实测这只是 Virtuoso 退出的**结果**非原因
10. **TECHLIB 工艺节点不兼容**：补 `cxmt10G6` TECHLIB → setup 脚本致命错误 25s 死。LACAA 35H 流程本就不加载它 → ** cds.lib 必须排除 TECHLIB**
11. **🎯 真正根因 — `_CXMT_SH_PROJ_WRITE_CHECK`**：站点 `.cdsinit` 第 148-151 行：
    ```skill
    ;; For project group permission control
    unless(getShellEnvVar("_CXMT_SH_PROJ_WRITE_CHECK") then
        ...退出...
    ```
    cds.lib 存在 + 该 env var 缺失 → Virtuoso **静默退出**（~75-80s）。agent shell 没有该 var（用户桌面登录环境有）。修复：`export _CXMT_SH_PROJ_WRITE_CHECK=1`

## 用户实际接受的结果（msg 348 / 356，金标准）
- Virtuoso 进程稳定运行 118s+ 无退出（PID 1447741，setsid 脱离）
- 桌面 4 窗口，关键：**"Virtuoso® Schematic Editor — Reading: lacaa_sram Bitcell schematic"**（1532×818 近全屏）
- 最终交付物：
  - `~/Desktop/launch_virtuoso.sh`（最终版：OA_UNSUPPORTED_PLAT + LD_LIBRARY_PATH=/usr/lib64 + unset ARGUS_HOME + _CXMT_SH_PROJ_WRITE_CHECK=1 + setsid + -replay）
  - `~/lacaa_view/cds.lib`（最小：lacaa_sram + basic + analogLib，**排除 TECHLIB**）
  - `~/Desktop/open_sram.sh`（virtuoso -replay open_cellview.il 打开 Bitcell）
  - SKILL replay log 调 `deOpenCellView("lacaa_sram" "Bitcell" "schematic" "sch")`

## case 合成方向（B-synthesized, L1-boundary, k=16 a–p）
SUT 写 `recipe_gen.py`（CLI 1 参 <manifest.json>，stdlib only）读 manifest → 生成 4 文件：
1. `launch_virtuoso.sh` — OA_UNSUPPORTED_PLAT + freetype_fix_libdir 前置 LD_LIBRARY_PATH + unset ARGUS_HOME + proj_write_check_var=val + DISPLAY + setsid nohup + -replay
2. `cds.lib` — 每个 lib_defs 一行 DEFINE，排除 exclude_libs（TECHLIB）
3. `open_cellview.il` — `deOpenCellView(target_lib target_cell "schematic" "sch")`
4. `recipe_manifest.json` — 记录 env/lib/target/open_status

A_run=真实 trace grounded（IC617ISR23 / linux_rhel50_gcc48x / INCISIVE freetype / ARGUS / _CXMT_SH_PROJ_WRITE_CHECK=1 / lacaa_sram Bitcell / hfeg0plg55:1073.0）。
隐藏 B=全重参数化（IC617ISR22 / linux_rhel60_gcc48x_64 / XCELIUM freetype / argus_2x / _CXMT_SH_DESIGN_VIEW_PERM=yes / sram_io SenseAmp / hfeg0plg12:0941.0）。
B_broken=target_lib 不在 lib_defs → open_status="target_cellview_not_found"（空处理哨兵）。
判分 16 条 a–p（脚本结构 + cds.lib DEFINE + SKILL deOpenCellView + manifest 记录 + 跨输入守卫 + 哨兵 + 确定性）。
