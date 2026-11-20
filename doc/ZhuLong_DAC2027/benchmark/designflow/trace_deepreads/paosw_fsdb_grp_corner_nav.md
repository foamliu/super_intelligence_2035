# deepread — paosw · kaixuanx@hfeg0pkn002 · waveform

- sid: 1792460001779_paosw
- user/host: kaixuanx / hfeg0pkn002
- mc=31, model deepseek-v4-flash, status completed, cwd /home/kaixuanx/ai_project/tspc_dff
- domain: waveform (waveview:260 dominant)

## 任务原话 (U#1)
> waveview中对于fsdb.grp文件的波形，我想只看其中一个比如alter=30的波形，把其他的隐藏起来，看完这个corner，再继续看下一个

## agent 流程 (18 msgs, 7 user turns 多为 tool_result)
1. U#1 → load skill `waveview-fsdb-readerV2-2` (Read hierarchy signals from finesim FSDB via WaveView ACE Tcl backend `wv -ace_no_gui`)
2. RAG search_apis "WaveView open fsdb graph group corner show hide waveform alter" → 命中 tcDisplayTechGraphForm 等(无关)
3. search_codebase fsdb.grp/alter/corner
4. load skill `waveview-ace-batch` (Generate & run WaveView ACE Tcl for batch waveform analysis)
5. list_allowed_files 两个 skill 目录; read ACE cheatsheet; read reader 脚本 + wv_tmp/wv_s_*.tcl
6. 最终纯文本解释(fsdb.grp 结构 + 三种导航方法)：
   - **核心结论**：finesim 多 corner 跑 `-o xx.grp` 时，**每个 corner(每个 .alter/run)各自生成独立 .fsdb**，再生成一个 `.grp` 汇总文件(仅引用路径/描述)，WaveView 打开 .grp 时把每个 corner 当独立 simulator 一起加载，`alter=30` 即第 30 个 corner 那组波形。
   - 方法 A：直接只 Open 对应 corner 的单个 .fsdb，看完用 File→Open "Replace current" 换下一个。
   - 方法 B：载入全部后手动 hide/show。
   - 方法 C：用 ACE Tcl 脚本遍历 corner(open 一个 / hide 其他 / 下一个)。

## 关键技术点 (用于 B-grade synthesized)
- **fsdb.grp = 文本引用清单**：每行引用一个 per-corner .fsdb 路径 + corner 标签 + alter 编号。
- **corner 导航 = 按 alter 顺序逐个 open/hide**：可程序化生成 WaveView ACE TCL 实现自动化遍历。
- WaveView ACE Tcl 后端：`wv_open_file` / 信号 hide/show / panel select / corner label。

## B-grade synthesized 案例方向
真实任务是 advisory(解释 fsdb.grp 结构 + 导航方法)，无私有 /rundata 可复刻。提取核心技术操作 → 合成工具 `gen_corner_nav.py`：
- 解析 fsdb.grp 文本清单 → 提取有序 corner 列表(name/alter/path)
- 生成 `corner_manifest.json`（corner 列表按 alter 升序）+ `corner_nav.tcl`（WaveView ACE 逐 corner 导航脚本，每 corner 一个 open/hide/show/label 块）
- 判分：在隐藏 B grp(8 corner，name/alter 与 A 6 corner 全不同)上验证 manifest+tcl 正确性 + 反硬编码(也跑 A，A count=6 != B count=8)

## 操作差异度
与已有 D case 区分：
- PwrCornerSweep-001(kaixuanx)：从波形算功耗 per corner(before/after mA)→ 计算类，非导航类。
- AvcPatternCompare-001：AVC 文件结构 diff → 非 grp 解析。
- 本例：fsdb.grp 文本解析 + WaveView 导航 TCL 生成 → 全新操作(无 grp 解析/TCL 生成类先例)。
