# 深读笔记 · 1794557816641_mnzo8 · WaveView FSDB → PWL 提取脚本

- **trace**: `1794557816641_mnzo8` · user `guangmingz` · host `hfhds206` · mc=19 · 30 msgs / 90KB
- **keywords**: waveview:24;analog:17;netlist:12;spectre:4;synopsys:1;schematic:1
- **domain**: waveform（WaveView ACE Tcl 脚本编写）
- **深读日期**: 2026-11-14 (shard D r663)

## 对话流（3 个实质用户轮）

| # | 用户轮（逐字） | 性质 | assistant 行为 |
|:--|:--|:--|:--|
| U#0 | `waveview如何从FSDB中提取指定信号为pwl格式` | Q&A（问方法） | RAG_MCP search_apis → 找到 `sx_export_pwl` 系列 API → get_api_details → 给出 4 步流程 + 完整示例脚本（含误导性 `sx_release $garbage` 占位） |
| U#12 | `释放对象 sx_release $garbage ;是做什么的` | Q&A（追问脚本里那行） | 查 sx_release 详情 → 解释 `$garbage` 是占位符、sx_release 释放 ACE 对象内存、派生信号释放后不可再引用、一次性脚本不必手动 release |
| U#16 | `帮我写一个可用的extract_pwl.tcl文件，场景仅处理模拟信号，提取两个信号` | **目标轮（A-eligible，纯需求）** | list_allowed_files 找 FSDB（DSIM/test_primesim/Downloads 均无现成 .fsdb）→ editor 创建 `/home/guangmingz/extract_pwl.tcl` → read_files 回读确认 → SandBox run_code 验 Tcl 控制流语法 → 给出脚本说明（4 个顶部变量可改、仅模拟信号不用 pwl_level/slew、-netname） |

## 金标准产物

trace 末尾 assistant 产出的 `/home/guangmingz/extract_pwl.tcl`（read_files msg#26 全文已捕获），用户接受（assistant 验证通过后给出运行说明，无否定）。脚本结构：

1. 顶部 4 变量：`fsdb_file ./sim.fsdb` / `sig1 top.ana.in.vp` / `sig2 top.ana.out.vout` / `out_file ./output.pwl` + `t_begin begin` / `t_end end`
2. `sx_open_sim_file_read $fsdb_file` → `sx_current_sim_file`
3. `sx_find_wave_in_file` ×2（sig1/sig2 精确取信号对象）
4. 健壮性：任一信号未找到打印 WARNING；两个都找不到 `exit 1`
5. `foreach` 收集非空信号对象到 `sigs`
6. 配置：`sx_export_precision 6` / `sx_export_range $t_begin $t_end` / `sx_export_delimiter "/"`
7. `sx_export_pwl $out_file $sigs -netname`
8. **不调用** `sx_export_pwl_level`/`sx_export_pwl_slew`（模拟信号无需数字逻辑电平/斜率配置）

## 为何 B-grade synthesized reframe

- 私有 FSDB `./sim.fsdb` 不可复刻（用户工程文件，沙盒无）。
- 但交付件 = Tcl 脚本（文本），FSDB 仅在判分时由 mock 提供。
- **reframe**：把「写脚本」改成「写一个 `source signal_spec.tcl` 读参数的通用脚本」，使隐藏 B（不同信号名/路径/波形）可验反硬编码。
- 判分用 **WaveView ACE Tcl mock shim**（`wv_mock.tcl`）模拟 sx_* API，从隐藏 B 波形数据生成真 PWL，验证候选脚本的 API 调用序列 + 输出结构（§4.2 真跑候选脚本）。

## 关键 API（RAG 检索命中）

- `sx_export_pwl <out_file> <signal_obj|name> <-netname> <-savespnet>` —— 核心
- `sx_open_sim_file_read <path>` —— 打开 FSDB
- `sx_find_wave_in_file <file> <signame>` —— 精确取信号对象
- `sx_export_precision <n>` / `sx_export_range <b> <e>` / `sx_export_delimiter <d>` —— 配置
- `sx_export_pwl_level <hi> <lo>` / `sx_export_pwl_slew <rise> <fall>` —— **数字逻辑专用，模拟信号禁用**
- `sx_release` —— 释放对象内存（一次性脚本不必）

## 案件落库

- case_id: `EDA-Eval-DesignFlow-FsdbPwlExtract-001`
- domain: waveform · layer: L2 · difficulty: B · track: synthesized
- k_check = 15 (a-o)
