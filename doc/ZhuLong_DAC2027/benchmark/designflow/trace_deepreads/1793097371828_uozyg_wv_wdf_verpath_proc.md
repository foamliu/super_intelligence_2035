# Deepread: 1793097371828_uozyg — WvWdfVerPathProc

## trace_source
- session: `1793097371828_uozyg.jsonl` (kanban streaming log, 300KB, 2170 chunks)
- user: e0023936 @ 10.129.32.75 (.75 本机)
- mc=21, keywords: waveview:52;cadence:12;virtuoso:10;pyaether:5;rtl:1;pex:1
- domain: waveform (Custom WaveView ACE Tcl API)

## 用户意图（从 chat_reasoning 流还原，kanban 无独立 user_text stream）
用户要求编写一个 Tcl proc `get_version_and_filepath {file_path}`，需要：
1. 打开仿真波形文件进行读取
2. 获取 Custom WaveView ACE 版本字符串
3. 获取打开文件的磁盘路径
4. 关闭文件
5. 返回 `{version_string file_path_string}` 列表
6. 如果文件无法打开则返回空列表 `{}`

（A-faithful 判定：这是"提出需求"轮，用户未指出根因或修复方案 → 可作 A 档；本轮按 B-grade synthesized 落库。）

## agent 工具链
1. `list_allowed_files /home/e0023936 depth=2` — 探目录
2. `search_apis "open simulation waveform file for reading" lang=tcl` — 查 sx_open_sim_file_read
3. `search_apis "get Custom WaveView ACE version string" lang=tcl` — 查 sx_version
4. `search_apis "get file path of opened waveform file" lang=tcl` — 查 sx_wdf_info
5. `get_api_details [sx_open_sim_file_read, sx_version, sx_wdf_info, sx_close_sim_file]`
6. `find /home/e0023936 -maxdepth 4 -iname '*.wdf'/'*.fsdb'/'*.vcd'/'*.tb'` — 找波形文件
7. `run_code tcl "sx_version"` — 实测版本 → `P-2019.06-SP2 {Nov 30, 2019 11:01:57} {RHEL64 v5.7}`
8. `run_code tcl "sx_open_sim_file_read /home/e0023936/devops/frequency.wdf"` — 实测打开
9. `run_code tcl` 测 open-failure 行为（不存在文件 → 抛 Tcl 错误，错误信息为空）
10. `editor /home/e0023936/tcl_code/get_version_and_filepath.tcl` — 写 proc
11. `run_code tcl` 运行 proc 验证

## API 实测要点（pyAether get_api_details 确认）
- `sx_open_sim_file_read <file>` → 返回单个句柄(hex 字符串)；文件不存在**抛 Tcl 错误** → 必须 catch
- `sx_version` → 返回多元素列表 `{version {date} {platform}}`，`lindex 0` 取版本号
- `sx_wdf_info <fh> -path` → 返回文件路径；必须带 `-path`/`-waveforms`/`-title` 之一
- `sx_close_sim_file <fh>` → 关闭文件

## 金标准 proc（逐字，/home/e0023936/tcl_code/get_version_and_filepath.tcl）
```tcl
proc get_version_and_filepath {file_path} {
    if {[catch {set fh [sx_open_sim_file_read $file_path]} err]} { return {} }
    if {$fh eq ""} { return {} }
    set ver [lindex [sx_version] 0]
    set path ""
    catch {set path [sx_wdf_info $fh -path]}
    catch {sx_close_sim_file $fh}
    return [list $ver $path]
}
```

## B-grade A/B/C 不相交设计
- A(visible): prompt 描述任务（无具体 version/path 值，SUT 写通用 proc）
- B(hidden): mock_B.tcl — sx_open 返回 "_b_handle_8821_void_pp", sx_version 返回 "P-2024.11-SP2 ...", sx_wdf_info -path 返回 "/tmp/wv_hidden_B_8821.wdf"
- C(anti-hardcode 嵌入 check.py): mock_C — version="Z-2018.03-Beta", path="/data/wv_anti_C_5512.fsdb"
- A/B/C version + path + handle 全不相交
- 额外: mock_fail_open(sx_open 抛 error) + mock_empty_handle(sx_open 返回 "") 验错误路径

## 维度正交论证（vs 现有 waveform cases）
- WvEyeSelect-001: .rep 文本解析 + 眼宽选点 → 本 case = Tcl API orchestration proc，机制不同
- WvVecCmpXTolAudit-001: vec 文本 + X 容差扩展 + shift 对比 → 本 case 无 vec/shift
- OpenWaveFmt-001: Perl→Tcl 波形格式转换 → 本 case 无格式转换
- FMFreqVsT/FmInstFreq: Tcl ACE FM 信号处理 → 本 case 无信号处理
- SineZeroCrossFreqPeak/CosWaveWdf: 波形生成 → 本 case 无波形生成
- IddMeasPostProcess: CSV 后处理 → 本 case 无 CSV
→ 非 dup ✓

## check.py 15 条件 (a-o)
静态(文本): a zip含.tcl / b proc 1参 / c sx_open $file_path / d 失败处理+返回{} / e sx_version / f sx_wdf_info -path / g sx_close_sim_file / h return [list] / i 无B/C硬编码 / m 无禁模式
动态(tclsh subprocess): n 解析无语法错 / j mock_B→{B_VER B_PATH} / k mock_fail_open→{} / l mock_empty_handle→{} / o mock_C→{C_VER C_PATH}

自验: ref 15/15 PASS + 4neg(empty/print_only/hardcode/core_removed) 全FAIL + §4.9三假全FAIL + 3-seed(B/C/seed3) 一致
