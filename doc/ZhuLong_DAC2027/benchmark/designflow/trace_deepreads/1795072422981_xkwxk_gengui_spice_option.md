# deepread xkwxk — junlingw GENGUI FineSim `.option` 块语法讲解 + GUI 改造

**trace**: junlingw @ hfeg0pkn005 (10.129.2.14), session 1795072422981_xkwxk.messages.json, mc=186, pdom=schematic_netlist, 741 msgs / 2.3MB
**深读时间**: 2026-11-23 (r1204)
**scp 路径**: `/home/junlingw/.snapshot/hourly-new.2026-11-22_2100/.cline/data/sessions/1795072422981_xkwxk/1795072422981_xkwxk.messages.json`（.snapshot 路径，非 live）

## 与 r1203 (2m9z2) 的关系
同一用户 junlingw、同一 `/proj/drvqa/V0/workdir/junlingw/GENGUI/` 代码库、同一套 FineSim/HSPICE 测试平台网表生成器。xkwxk (1795072422981) 与 2m9z2 (1795074908715) 是**两个不同 session**。前 ~25 轮用户指令高度重叠（学习→中文→3 GUI 变体对比→关联文件→"需要"清理→再检查→修语法坏文件→修 check_all.py→保留/删除清单），属同一任务族的前半段（代码审计与清理）。**xkwxk 的后半段（msgs 157-552）是 2m9z2 没有的全新意图**：大规模 GUI 行为改造 + FineSim SPICE 语法讲解，与 r1203 的 PyDepGraphAudit 内核（Python import 依赖审计）**不相交**。本 case 抽后半段的可离线判分内核。

## 真实意图（后半段，msgs 157-552 用户指令）
用户在 GENGUI 主程序 `finesim_tb_generator.py` 上逐轮要求：

- **GUI 布局/尺寸**（157-245）: "ui窗口太小了…窗口做大一点" → "里面参数窗口的尺寸太小了…现在是固定的，全屏也不会变大" → "process/lib下面全屏之后ui还是只有那么大" → "整体ui有点瘪，太矮了…表格右侧应添加滚动条" → "滚动条应做到表格内侧" → "缩小后ui没有同步缩小" → "表格排版没有同步缩小"。
- **GUI 控件语义讲解**（246-318）: "apply process params 和 add param 都是什么作用" → "为什么第三页的 add device 一点就卡住了" → "讲一下 sffm 和 am 这两个激励" → "source edit 页面没有确认和取消键" → "下面 steps 是做什么的" → "为什么我调 steps 图像形状变化巨大？…step 不是指我跑的精度吗，越小越好？" → "1000 点调到 2000 点都变化很大" → "出现重影了" → "am 0 1 1e9 0.5 1e12 还是不行"。
- **缺失控件补全**（320-396）: "power 这页没有按钮" → "ANALYSIS 这页也没有" → "option 这页是干嘛的…下面的按钮都是什么意思" → "为什么在 all 里点 Preset: Accuracy/Converge/SPFBA 效果都一样" → "analysis 这页是干什么的"。
- **ANALYSIS 页对勾改造**（397-453）: "目前里面是没有 AC 的…默认全是 yes…应该默认全是 no，然后我手动点 yes…把 enabled 这一栏改成对勾选项，初始默认只勾 tran" → "ac 没有加进去…on 这列对勾判定范围太大了，行内只弄一个小框挑勾…把 on 这列放到最后" → "把 tran 默认放到第一行，框有点太小了…只点到方框里才能勾上" → "对勾图标有bug，显示异常"。
- **tab 重排 + traceback 修复**（454-488）: 粘贴 `finesim_tb_generator.py line 697 self.at.configure(font=...)` 的 `_tkinter.TclError` traceback → "把 devices 挪到第二位，把 voltagecurrentsources 单开一个 topic 放在 analysis 左边第四位名字叫 source"。
- **★ FineSim `.option` 块语法讲解**（489-496）: 用户直接粘贴一段真实 `.option` 控制块：
  ```
  .option PARHIER = LOCAL
  .option scale = 1
  .option BRIEF = 0
  .option INGOLD = 2
  .option finesim_mode=promd
  .option finesim_model=3
  .option finesim_speed=1
  .option finesim_partition=1
  .option finesim_dvmax=0
  .option finesim_bisection_output=13
  .option finesim_pwrloadmodel=1
  *.option finesim_measout=1
  .option finesim_prbport=1
  .option finesim_maxicout=0
  .option finesim_output=fsdb
  .option finesim_subckt_dup_rule=0
  .option post
  *.option finesim_force_fsdb_version=5.1
  ```
  问"这些都是什么，为什么 option 里都没有？" → agent 逐条解释每个 `.option` 的含义（FineSim 专属 vs HSPICE 通用、`*` 注释行）。随后用户问"只适用于 promb，其他的模式就不适用了，该怎么得到其他类型仿真的模板"。
- **★ corner `.lib` 语句格式**（504-530）: 用户给出 corner `.lib` 语句的精确格式：
  ```
  .lib '/proj/drvqa/V0/model/current/model.sp' SS
  .lib '/proj/drvqa/V0/model/current/incFile_lp' bjt_ss
  .lib '/proj/drvqa/V0/model/current/incFile_lp' res_ss
  .lib '/proj/drvqa/V0/model/current/incFile_lp' nicap_ss
  .lib '/proj/drvqa/V0/model/current/incFile_lp' diode_ss
  ```
  说明 name 没问题，lib 内容应为路径，ff/tt 等只把最后的 ss 改为 ff 或 tt。
- **★ MOSFET 实例语句语法**（531-535）: 用户粘贴 `MMP0 Z A VDD VDD ptn w=3.8e-6 l=0.13u` / `MMN0 Z A VSS VSS ntn w=2.0e-6 l=0.13u`，问"这是什么语法你讲讲" → "把 device 这个 topic 整体删掉吧"。
- **topic 功能总览**（552）: "写一下每一个 topic 的功能"。

## 可离线判分内核（本 case 抽题）
GUI 改造/对勾/tab 重排/激励波形渲染都依赖 tkinter 显示，无法离线判分。**FineSim `.option` 块的逐行解析与分类**是纯文本处理，可离线判分，且是用户 msg 489 的真实意图。抽内核 `spice_option_audit.py`：读一个含 `.option`/`*.option` 行的网表片段 → 逐行识别选项行（正则 `^\s*(\*)?\s*\.option\b`，`*` 开头为注释选项）→ 按 token 切分（正则 `(\w+)\s*(?:=\s*(\S+))?`，支持 `key=value`/`key = value`/裸 `key=True`）→ 每条记录判 is_commented / is_finesim_proprietary（finesim_ 前缀）/ category（8 类 + unknown）→ 产出 option_audit.json（options 列表 + summary 计数）。

**与 r1203 PyDepGraphAudit 内核不相交**：r1203 = Python 模块 import 依赖图审计（读 .py 目录，行级正则抓 import，py_compile 语法判定，broken/entry/core/orphan 分类）；本 case = SPICE `.option` 块选项审计（读 .sp 网表片段，正则抓选项 token，finesim_ 前缀判定，sim_mode/model/speed/partition/convergence/output/power/generic/unknown 分类）。文件类型、正则、分类体系、输出结构完全不同。

**case_id**: EDA-Eval-DesignFlow-SpiceOptionAudit-001（domain=schematic_netlist, level=L1）
- A（可见，14 token）: 真实 .option 块的衍生采样（generic×2 + output×6 + sim_mode/model/speed/partition/convergence/power 各1，2 个 `*.option` 注释行）
- B1（隐藏，18 token）: 不同 .option 块（含 1 个 unknown 类键 finesim_experimental，3 个注释行，1 个空行 + 1 个 `* 普通注释` 非 .option 行测试 line_no 真实跳行），覆盖全 8 类 + unknown
- B2（隐藏，11 token）: 第三套结构（custom_opt=unknown，2 个注释行）
- k_check=15（①zip含脚本 ②B1 exit0+合法JSON含options/summary ③B1 options=18反A=14 ④每条含8字段 ⑤is_commented全匹配 ⑥is_finesim_proprietary全匹配 ⑦category全匹配(全8类+unknown) ⑧key+value全匹配(value str/True语义) ⑨line_no+token_index排序全匹配 ⑩summary total/active/commented/finesim_proprietary全匹配 ⑪by_category全匹配 ⑫确定性3次md5 ⑬B2 options=11反A/B1+by_category全匹配 ⑭B2 category+is_commented全匹配 ⑮B2 key+value+is_finesim_proprietary全匹配）
- §4.9 三假: print_only（打印 A 14 token）/empty_stub（空报告）/hardcode_a（硬编码 A）全 FAIL（B1 18 token + unknown 类，condition 3 拦截）
- 自验: reference 15/15 PASS + 3 负样本全 FAIL + negative_selftest PASS(BUG):0 + round-trip（从 case JSON 抽 test 字段重跑）全 PASS
