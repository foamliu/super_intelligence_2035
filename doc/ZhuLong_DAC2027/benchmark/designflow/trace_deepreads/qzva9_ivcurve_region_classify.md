# 深读笔记 · 1793843116422_qzva9 (thqu @ hfeg0plg99, mc=253, waveform)

## 会话概要
- 用户 thqu 在 hfeg0plg99 用 Aether/HSPICE 做 ntn (native NMOS) 管子的 IV 特性仿真与绘图。
- n_msgs=324, n_user=7。工具以 read_files/list_allowed_files/run_approved_command(pyrunner)/editor 为主，hspice 真跑。
- 工具命中：212 hspice / 168 schematic / 146 netlist / 18 virtuoso / 16 pyAether / 12 spectre / 10 cellview / 3 calibre。

## 用户轮（逐字原文）
1. TECHLIB库中ntn管子的阈值电压这些要怎么查看
2. 你找一下spice model在哪里
3. 打开这个xlsx文件
4. 怎么仿真这个管子的IV特性曲线呢
5. 你能直接帮我仿吗
6. 你绘制一下这个IV特性曲线
7. 这个vg的电压是不是太少了，是不是要多跑几组啊，这组个怎么跟网上经典的IV曲线不宜样，而且要在途中标注出线性区，截至区饱和区这些

第 7 轮是「提出目标+要求标注工作区」的 refine 轮（要更多 Vg + 标注线性/截止/饱和区），属 A 档可用意图轮。

## 真实工作流（assistant）
1. 用 aether-tool-qa skill + search_codebase/read_files 在 Aether 手册里查 ntn 阈值/Vth 查看 -> 给出 Schematic 里按 Q 查 CDF 等方法。
2. 定位 SPICE model：`/proj/ddgoa/V0/model/current` -> `/apps/imctf/models/G6/model_local/V1_HK_Model_L5_v0d9_Rev02_t02/`，主文件 `V1_HK_Model_L5_v0d9_Rev02_t02.sp` + `incFile_V1_HKMG`（5w+ 行，含 .model ntn 卡，corner tt/ff/ss/...）。
3. 解析 `V1_LP_PDK_SPEC_TABLE_v0d9_Rev02_t02.xlsx`（openpyxl，9 sheet：device list / mos_instace_range 等，几何范围 W/L/NF，ntn W 上限 2.0u）。
4. 写 HSPICE deck `ntn_iv.sp`（Id-Vg，Vd=0.05V 线性区，提取 Vth）+ `ntn_idvd.sp`（Id-Vd 曲线族，Vg 外扫描/Vd 内扫描）+ `ntn_idvg.sp`（细 Vg 步）。
   - 首次 W=5u 超范围报错 -> 改 W=2u L=0.1u nf=1。
   - `.PROBE` 语法错 -> 改用 `.PRINT`。
   - `.sw0` 二进制 -> 用 `.PRINT` 输出到 `.lis` 文本。
5. 真跑 hspice (`/apps/synopsys/SRB/hspice_V-2023.12-SP1-1/hspice/bin/hspice`)，解析 `.lis`：
   - Id-Vg @ Vd=0.05V：用于 max-gm 线性外推 Vth。
   - Id-Vd 曲线族：数据结构 = Vd 外扫描(95 步) × Vg 内扫描(15 步)，每段 15 行；后扩到 Vg 0-0.9V step 0.05 = 19 条曲线 × 95 Vd 点。
6. plot：matplotlib 绘 Id-Vd（19 曲线，虚线/点划线/实线区分 Vg<Vth/Vg≈Vth/Vg>Vth）+ Id-Vg，标注 CUTOFF/LINEAR/SATURATION 三区。产出 `ntn_iv_curves.png/pdf`。

## 金标准/产物
- 脚本：ntn_iv.sp / ntn_idvd.sp / ntn_idvg.sp / run_hspice.py / parse_idvd2.py / analyze_vth.py / plot_clean.py。
- 数据：ntn_iv.lis / ntn_idvd.lis（Id-Vd 曲线族，Vd 外 Vg 内）/ ntn_iv.sw0 / ntn_idvd.st0。
- 图：ntn_iv_curves.png / .pdf（带线性/截止/饱和区标注）。
- 用户最后接受 IV 曲线绘制结果（19 Vg 曲线 × 95 Vd 点，三区标注）。

## 造题映射（B-grade synthesized L2, waveform）
私有 model + hspice 二进制 + /ai_sandbox 产物不可复刻 -> B-grade synthesized 自包含：
- 可见 A：`sim_out/idvd.lis`（Id-Vd 曲线族，`* vg=` 块头 + `vd id` 行）+ `sim_out/idvg_lin.lis`（线性区 Id-Vg，`vg id` 行）。square-law MOSFET 模型生成 + 微小噪声。
- 隐藏 B：不同器件(ntn2/ss)、不同 Vth(0.38 vs 0.30)、不同 Vg/Vd 扫描范围与步长、不同点数。
- SUT 任务：解析 .lis -> (Vg,Vd,Id) + (Vg,Id) -> max-gm 线性外推 Vth -> 分类 cutoff/linear/saturation -> 输出 iv_regions.csv + summary.json。
- 判分：check.py 独立从 B 重解析 + 重提取 Vth + 重分类，14 条独立条件（a..n），反硬编码(A 重跑 + A Vth!=B Vth) + 3-seed byte-stable。

## 域归属
waveform（IV 特性曲线仿真 + 工作区分类）。shard D。
