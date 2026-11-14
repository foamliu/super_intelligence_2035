# deep-read r549 g9gw3 — OPC/ddm 模型抽取 + mask.in 重建

## trace
- session: 1794376048465_g9gw3
- user: zhenglu @ hfeg0pkn001 (10.129.2.10)
- mc=104, keywords: calibre:476;pdk:133;rtl:8;virtuoso:2;pex:2;hspice:2;aether:2
- 185 msgs, 861KB
- domain: physical_verify (calibre OPC/ddm)

## user 意图演进
- U#0 (msg 0): "把 HL_LFD 目录下文件中的optical模型 ddm resist抽取出来保存成文本文件 AA_22nm_GL_optical 命名采用这种格式 层名 最后是模型名" — produce-task author-new-script
- U#9 (msg 17): "抽取 optical + ddm + resist 三个模型，分别保存为 AA_22nm_GL_optical / AA_22nm_GL_ddm / AA_22nm_GL_resist"
- U#23 (msg 45): "其他的文件也都完成 所有的都放在dtech_models目录里"
- U (msg 104): "原有的也给替换 然后readme中注明ddm是dark还是bright"
- U (msg 112): "m3d要完整的ddm 包括下面的数值"
- U (msg 139): "你可以根据ddm反推原来的mask.in吗 caliberwb" — mask.in 重建需求
- U (msg 141): 参考 calibre manual ddm 配置
- U (msg 168): "po的mask stack信息在哪里找的"
- U (msg 174): "po的光源文件就用目录下对应的路径你给改掉 输出到都在家目录下的po_modles文件夹 然后用caliberwb -a去完整建模"
- U (msg 179): "这几个文件可以看到实际的dose值是多大吗"

## assistant 工具链
- editor×37 + run_approved_command×32 + read_files×13 + list_allowed_files×6
- _search_optical.py: 扫描 .tbc.decrypt 文件 optical/ddm/resist 关键词计数
- _extract_models.py (msg 66, 3927 chars) — 核心抽取脚本：
  - match_brace(text, open_idx): 大括号深度配平
  - extract_optical/resist/m3d/src: 各模型块抽取
  - process(layer, fname): 找 optical_model_load/resist_model_load/ddm_model_load → 写 {layer}_22nm_GL_{optical,resist,ddm,m3d,src}
- _find_darkbright.py (msg 105): 搜 dark/bright/clearfield/Mask Type 关键词分类 ddm
- _extract_full_m3d.py (msg 119): 完整 m3d 抽取（version 行到闭合大括号）
- mask.{po,aa,m1}.in (msg 157/159): 重建 Calibre MaskSim DDM Library input file (wavelength/reduction_factor/film stack/Mask Type Bright-Dark Field/crosstalk/corner_model)
- _po_maskstack.py (msg 169): 定位 ddm 块头注释提取 mask stack 信息
- _recon_calibre.py (msg 175): 定位 calibrewb 二进制

## 真实产物
- AA_22nm_GL_optical: 920394 bytes, 31209 lines (optical_model_load OPT_0 {...})
- AA_22nm_GL_resist: 918 bytes, 27 lines (resist_model_load RESIST {...})
- AA_22nm_GL_ddm: 10202057 bytes, 514133 lines (ddm_model_load nomddm {...})
- dtech_models/ 目录: 各层 (AA/PO/M1/Mx) optical/resist/ddm/m3d/src
- maskin/: mask.po.in (Bright Field, stackslope 84) / mask.aa.in (Bright Field) / mask.m1.in (Dark Field)

## case 设计 (B档 synthesized, mock-behavioral)
- 核心算法保持忠实：大括号配平块抽取 + dark/bright 分类 + mask.in 重建
- mock PDK fixture (TCL-like 大括号语法) 替代真实 .tbc.decrypt（live calibre 不可离线沙盒）
- B (AA, Bright Field, stackslope 84, films Qz/bottom-MoSi/top-MoSi) / B2 (M1, Dark Field, stackslope 86, films Qz/MoN/Ta)
- 15 条件 a-o: 结构2 + B运行9(块抽取+配平+分类+mask.in重建) + B2 dark 1 + 防硬编1 + 确定性1
- 自验: ref 15/15 PASS, 4 neg all-FAIL, §4.9 三假全 FAIL, E2E roundtrip PASS
