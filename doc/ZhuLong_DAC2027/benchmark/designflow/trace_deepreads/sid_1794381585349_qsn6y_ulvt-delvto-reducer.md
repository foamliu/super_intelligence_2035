# Deepread — sid 1794381585349_qsn6y (joeyl @ hfeg0plg74)

- trace_source: user=joeyl, host=hfeg0plg74, session_file=1794381585349_qsn6y.messages.json, mc=23
- scan keywords: netlist:196;spectre:34;hspice:18;cadence:12;opamp:7;aether:4;virtuoso:1;transistor:1
- domain: schematic_netlist (D)
- messages: 39 (1 non-empty user, multi-step assistant build)

## 用户原始任务（逐字）
「我想做个为netlist中的pulvt_ckt与nulvt_ckt减小vth的脚本，实现方式是，找到ulvt管，然后在最后加'_delvto=数值'，比如_delvto=-0.2就会把vth降低-0.2V。可以写个cfg文件来选择替换的netlist地址，与改变vth的值。在开工前，请注意文件BEFORE_STARTING_ANY_WORK,READ_ME」

用户给出实例变换（XNM18 nulvt_ckt … delvto_user=0 → 末尾追加 ` _delvto=-0.2`）。

## SUT 实际产出（joeyl 的 cline agent）
任务目录 `/home/joeyl/ulvt_delvto/`，交付 `reduce_vth.py`(290行) + `config.cfg` + test/ + AI_USAGE.md。
核心逻辑：
- 解析 cfg（netlist 路径、delvto 值、models 默认 pulvt_ckt,nulvt_ckt、in_place、require_x_prefix）
- 扫描 netlist，收集 `+` 续行构成完整语句
- 仅处理 X 开头实例行（跳过 .subckt/.ends/注释/空行/非 X 行）
- 命中 model token（精确匹配，小写）→ 在语句最后一条物理行末尾追加 ` _delvto=<值>`
  - 行尾 `$`/`//` 注释 → 插到注释之前（保留注释）
  - 语句已有 `_delvto=...`（边界感知）→ 替换其数值（幂等）
- 非原地模式输出 `<原名>_delvto<值>.sp`；原地模式首次留 .bak
- 报告修改器件数/匹配数/按模型统计/实例名
- 测试样本 7 情况：单行/续行(模型在首行)/续行(模型在续行)/已有_delvto/非目标nch/行尾$注释/.subckt定义
- 幂等性测试通过（已修改文件重复运行报告"无需修改"）

## case 化要点
- 真实任务 = 纯文本 netlist 变换 produce-task（无需 EDA 工具），适合 check.py 精确比对
- 简化接口为 `python3 reduce_vth.py <netlist> <delvto>` → stdout（去掉 cfg/原地/.bak 噪音，聚焦变换正确性）
- 可见输入 A 覆盖 10 情况（含子串陷阱 nulvt_ckt_extra / pulvt-only / .param / .subckt 定义 / 续行 / 行尾$注释 / 已有_delvto 替换）
- 隐藏 B（主）+ C（反硬编码）不同实例名/结构，金标准由 reference 生成
- ≥8 断言：zip 合法/含.py/退出0/行数/目标行追加/非目标行不变/已有值替换/续行末尾/行尾注释前插入/精确金标准B/反硬编码C/反硬编码A/幂等/空输入鲁棒
- 3 negative: empty / print_only(硬编码gold_B stdout) / hardcode_a(硬编码A的输出)
