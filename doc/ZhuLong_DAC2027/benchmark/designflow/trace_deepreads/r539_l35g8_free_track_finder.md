# r539 deepread — l35g8 (t0002038 @ 10.129.2.12, mc=90, layout_aether)

## trace
- sid: 1794468352049_l35g8, user t0002038, host hfeg0pkn003, ip 10.129.2.12
- mc=90, kw: pyaether:588;cellview:192;dbshape:141;aether:138;rtl:32;dbopencv:32;dbget:22
- 92 msgs, 757KB
- USER#0 (逐字原文): "PyAether 脚本生成指令 — 空 Track 标记器...请生成一个完整、可直接运行的 PyAether Python 脚本，功能是：扫描当前打开的版图，在指定金属层上找出所有空置的 track 段，在版图上用高亮标记层可视化出来，并同时在终端输出一份每层 track 占用率报表"

## 选料判定 (r527 动词法)
- 动词=生成(generate), 宾语=完整 PyAether Python 脚本 = **author-new-script produce-task** ✓
- 域: layout_aether (pyAether 版图几何遍历 + track 区间运算)
- 与 r536 peek 同批 (aether/layout-dominant 筛选, aer>=50 aer>veri aer>=drc)
- r537 计划"扩 aether/layout-dominant 筛选, 优先 produce-task 用户" → 本轮执行

## assistant 工具链
1. RAG_MCP_Server__search_apis ×8 + get_api_details ×4 (检索 dbShapeQuery/dbShapeQueryEx/aeGetCurDesign/emyBox/emyPointF/SleHierData/emyDesignDBUPerUu)
2. list_allowed_files/read_files (发现 free_track_finder.py 旧损坏版本)
3. editor ×15 分片写入 + run_approved_command 构建脚本 (拼接+编译验证)
4. run_approved_command 离线自检 (19/19 PASS, 修 1 断言)
5. SandBox_MCP_Server__run_code (pyAether 沙箱未启动, 验证错误路径)
6. 清理辅助文件, 交付 free_track_finder.py (941 行)

## 金标准 (assistant 实际产物)
- /home/t0002038/free_track_finder.py, 941 行, 38KB
- 纯算法层: merge_intervals / subtract_intervals / _track_centers / compute_layer_free_tracks / LayerResult
- pyAether 交互层: _import_pyaether / connect_layout / get_design_bbox_um / dbShapeQueryEx 层次遍历
- 高亮层: FreeTrack_HL / dbCrtRect
- 自检: --self-test 19 cases (区间减法/track 中心线/空段过滤)
- 算法核心: 排序+最小堆扫描线 O(B log B + T log B), eff_half=(width+min_spacing)/2+via_enclosure

## 合成 (B档 synthesized)
- case: EDA-Eval-DesignFlow-FreeTrackFinder-001 (layout_aether, L2-boundary, k=16 a-p)
- 把"连接当前 Aether GUI"重构为"读 layout.json 几何 fixture + config.json track 配置" (核心区间算法不变, 数据源从 live GUI 改为 fixture 文件, 离线可判)
- 资产 A: config_A.json (M2/M4) + layout_A.json (可见样例)
- 隐藏 B: area 0,0,1,1, M2(H 7 tracks 密集部分占用) / M3(V) / M5(空层) → longest_free=0.15/0.20/1.0
- 隐藏 B2: area 0,0,1.2,1.2, M6(H 3 tracks) / M7(V) → longest_free=0.30/0.25 (防硬编 dual-hidden)
- bad_config: direction=DIAGONAL → error path (exit 非零)
- check.py 16 条件: a-p (结构 3 + B 运行 7 + B2 3 + 空层 1 + error 1 + 防硬编 1 + 确定性 1)
- 负样本 4: naive_empty(b) / print_expected(i) / core_deleted(f) / naive_wrong_algo(f)

## 自验
- ref GOLD B+B2 PASS 16/16 ✓
- 4 neg NEG all-FAIL (NEG_RC=0) ✓
- §4.9 三假 (empty/print/core-del) 全 FAIL ✓
- k_rationale==k_check==16≥8 ✓
- test==disk check.py roundtrip ✓

## 谱系
- produce-task 第八子型 author-new-script (r524 author-new / r529 format-convert / r526 pipeline-build / r531 optimize-modify / r535 author-new-spacing-NE / r536 author-new-adjacent-side2-good5 / r534 bug-fix-gate / **r539 author-new-script**)
- C 域首个"纯算法脚本生成"子型 (前 7 子型为 deck/GDS 图案/几何工具, 本子型为 track 占用区间算法)
- anti-hardcode: dual-hidden-config (B+B2, 承 r536 双隐藏配置族)
