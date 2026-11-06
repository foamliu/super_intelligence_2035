# 深读笔记: wn9jo (1793869749395_wn9jo) — PDK 库文件定位

- **trace_source**: user=t0002965, host=hfhds201, session=1793869749395_wn9jo.messages.json, mc=109
- **agent**: cline lead (deepseek), 172 msgs (93 user / 79 assistant), 967KB
- **真实任务**: 用户在 PDK 服务器 (hfhds201/hfeg0pkn002) 上为 DC 逻辑综合寻找 TSMC 22ULL 标准单元库的 5 个 .db 文件，从 PDK 树定位 + 拷贝到综合机
- **col6 tools**: 60 synthesis + 18 schematic + 6 hspice + 3 calibre + 1 pyAether (digital-dominant, dig_share=0.64)

## 关键用户轮 (act)
- ACT#1 (idx0): 「/proj/train/AI_Virtuoso/libs/TECHLIB这个路径下，以及父路径，有没有PDK 文件呢？就是那些适合逻辑综合的文件」— 初始探索
- ACT#6 (idx97): 「但是我只做逻辑综合，应该不用整个PDK 打包呀」— 收窄到最小子集
- ACT#7 (idx99): 用户给出关键约束 — operating condition `ssg0p72vm40c`、时钟门控 cell `CKLNQSGD12BWP30P140`、dont_use `*SGD*BWP30P140*`、5 个 .db 文件、T22 库
- **ACT#8 (idx168) — 最具体需求轮**: 给出 5 个 .db 文件的精确规格（变体名 + 文件名 + 子目录 + 用途），路径模式 `T22/1P10M_5X2Y2Z/<版本>/Digital/ips/tsmc_ip/digital/Front_End/LVF/CCS/<variant>_110b/`，文件名模式 `tcbn22ullbwp30p140<variant>ssg0p72vm40c_hm_lvf_p_ccs.db`。**但此轮含 find+scp 命令=部分解决方案 → 不作 A-faithful 任务说明**
- ACT#9 (idx169): 「注意不要再往tmp_22中写入大文件，继承...这个会话，给出接下来的解决方案」— 收尾需求

## 5 个目标 .db 文件 (变体 → 文件名)
1. sghvt → tcbn22ullbwp30p140sghvtssg0p72vm40c_hm_lvf_p_ccs.db (target SG-HVT)
2. sg → tcbn22ullbwp30p140sgssg0p72vm40c_hm_lvf_p_ccs.db (target SG)
3. pmsghvt → tcbn22ullbwp30p140pmsghvtssg0p72vm40c_hm_lvf_p_ccs.db (target PM-SG-HVT)
4. mbsghvt → tcbn22ullbwp30p140mbsghvtssg0p72vm40c_hm_lvf_p_ccs.db (target MB-SG-HVT, LIB_MAX operating 库)
5. sglvt → tcbn22ullbwp30p140sglvtssg0p72vm40c_hm_lvf_p_ccs.db (仅 link, SG-LVT)

## assistant 工具链 (关键发现)
- 探索 /proj/train/AI_Virtuoso (Virtuoso OA 库, 非综合 PDK) → /apps/imctf (PDK 发布点)
- 找到 28HK12T_STD (CXMT/Image Design 28nm 库) → 但用户要的是 TSMC 22ULL (bwp30p140 后缀)
- 误找到 22ULP (tcbn22ulp...) → 用户纠正要 22ULL (tcbn22ull...)
- 关键教训: 22ull vs 22ulp 命名混淆; corner ssg0p72vm40c (单电压) vs ssg0p81v0p72vm40c (双电压 level-shifter)
- trace 在 idx170 中断 (editor 校验失败), 无最终接受的交付件 → B-synthesized: 合成 PDK 树 + 定位+验证脚本

## case 设计 (B-synthesized, L1-static, digital)
- **交付**: submit.zip 含 `locate_libs.py` (参数化: `<pdk_root> <out_manifest>`) + manifest.json (对 A 的产物)
- **check**: 在隐藏 B PDK 树上 subprocess 跑 locate_libs.py → 解析 manifest.json → 16 条件 a-p
- **隐藏 B 结构反转**: 版本目录 v3.1.0_20250320 (vs A current); 5 valid + 6 decoys (22ULP/wrong-corner/.lib/lvllvt-no-CKLNQ/tar.gz/wrong-path-depth)
- **反硬编**: B 版本目录与 A 不同; check 用 B 路径/sha 独立校验
- **真跑候选 §4.2**: check subprocess 跑 locate_libs.py 于 B (非文本相似)
