# r1074 深读 · y9bh6 · junlingw · FineSim TB Generator Corners 块生成器

## Trace 元数据
- session: `1795160534877_y9bh6`
- user: `junlingw` / host: `hfeg0pkn005`
- mc=211, keywords: `.lef:504;netlist:316;synopsys:77;hspice:76;pyaether:44;aether:39;schematic:31;mixed-signal:15`
- 文件: 2.84MB / 857 msgs (463 user / 394 assistant)
- 时间: Nov 20-21 2026

## 用户整体意图
junlingw 在 `/proj/drvqa/V0/workdir/junlingw/GENGUI/` 开发一个 **FineSim testbench GUI 生成器**（tkinter Python 工具 `finesim_tb_generator.py` + 生成引擎 `fengine.py`）。该工具把各 topic（Process/Lib, Netlist, Power, Source, Analysis, Options, Measure, Output, Corners, Preview）的 UI 配置编译成一段 FineSim SPICE testbench deck。

## 80 条真实 user 任务（按主题归类）
1. **入门** (msg 0-21): 给 GENGUI 路径让 agent 学习；要求中文输出。
2. **文件清理** (msg 25-132): 区分 finesim_tb_generator.py 相关/不相关文件；列保留清单/无用清单；删无用文件；fix_indent.py 路径问题；逐个复查。
3. **UI 尺寸** (msg 157-233): 窗口做大；参数窗口太小固定；表格内侧滚动条；全屏缩小同步问题。
4. **功能解释/bug** (msg 246-318): apply process params vs add param；add device 卡死；sffm/am 激励；steps 含义；step 1000→2000 变化大；am 0 1 1e9 0.5 1e12；power/analysis 页无按钮。
5. **Options 页** (msg 364-387): option 页按钮含义；Preset Accuracy/Converge/SPFBA 在 all 里效果一样（bug）；analysis 页用途。
6. **Analysis 页重做** (msg 397-454): enabled 列改对勾选项；默认只勾 tran；AC 没加进去；on 列判定范围太大；tran 放第一行；对勾图标 bug。
7. **崩溃修复** (msg 454): tkinter `_tkinter.TclError: invalid command name` traceback。
8. **Tab 重排** (msg 465): devices 挪第二位；source 单开 topic 放第四位。
9. **.option 学习/模板** (msg 489-491): 列 18 条 `.option finesim_*`；要求按 sim mode（promb/promd/...）给模板。
10. **Corner topic** (msg 504, 637, 663): ⭐ **本轮 reframe 核心** ⭐
    - msg 504: 给 `.lib '<path>/model.sp' SS` + 4 条 incFile `.lib '<path>/incFile_lp' bjt_ss/res_ss/nicap_ss/diode_ss` 例子；ff/tt 只改后缀。
    - msg 637: ① 第一列 name→corner ② 删 lib 列 ③ vdd→vvdd ④ temp/vvdd 列可编辑 ⑤ yes→勾选框 ⑥ 增 tt 行 ⑦ 顺序 ss ff tt fs sf ⑧ 默认只开 ss ⑨ 输出第一个勾选不加 .alter，其余加 ⑩ vvdd 输出 `.param vdd_core =`→`.param vvdd=`
    - msg 663: vvdd 默认值全改 0.94；vvdd 输出带单位 V（`.param vvdd = 0.94V`）；edit 弹窗不显示 on。
11. **Device topic** (msg 531-535): MMP0/BBN0 SPICE 语法讲解；后删 device topic。
12. **各 topic 功能清单** (msg 552): 写每个 topic 功能。
13. **蒙特卡洛/mismatch/cco** (msg 554-598): 搜 Synopsys finesim MonteCarlo tutorial；mismatch flag + cco flag；做成 process 页勾选项。
14. **Power 页** (msg 616): power 值改三种下拉 point/list/range。
15. **Netlist topic** (msg 674-760): 新建 netlist tab 放第二位；可视化打开文件夹导入网表；撤回/反撤回/保存；默认查看所有文件类型；路径 /rundata vs /proj bug（反复修）；可视化图标丢失。
16. **Power 链接** (msg 760): power 前加可视化读取链接文件，路径 /proj/drvqa/V0/setup/sim/sim_setup/Powervoltage/Pattern_Power.sp。
17. **Source 改名** (msg 774): source→stimulus。
18. **Param topic** (msg 784): 添加 param topic。
19. **Output/Probe** (msg 804-817): 给 9 条 `.probe` 语句；output/probe 按此改 + 勾选，默认只勾 tran v。
20. **Measure** (msg 832-855): 给 `.tran TDC_drqr trig v(D1)='V50P' rise=1 td=4n` + `targ v(CK1)='V50P' rise=1`；measure 按此改 + 勾选默认不勾；加 rf/fr + td 起始时间。

## Reframe 选择：Corner 块生成器（msg 637+663）

**为何选这条**：① 用户给了**精确的输出语义规约**（10 条改 + 3 条改），可机器验证；② fengine.py `_corners` 是**纯函数式生成**（无 EDA 依赖、无 GUI），可独立复刻；③ 真实 trace 溯源强（user 原话 + assistant 代码 + 实测输出三方对齐）；④ 隐藏输入 B 可构造结构异 A 的 spec（不同 base/corner 名/启用集/vvdd/温度），五重 anti-hardcode。

### 参考实现（assistant 实际 patch，msg 647 + msg 664）
`fengine.py` `_corners(self, L)` 最终形态（msg 647 first-flag 改 + msg 664 V 单位改）：
```python
def _corners(self, L):
    cc = [c for c in self.data.get("corners", []) if c.get("enabled", True)]
    if not cc: return
    base = self.data.get("corners_base", "/proj/drvqa/V0/model/current").rstrip("/")
    L.append("* === CORNERS ==="); L.append("")
    first = True
    for c in cc:
        n = (c.get("name") or "tt").lower()
        if not first: L.append(f".alter {c['name']}")          # raw name
        L.append(f".lib '{base}/model.sp' {n.upper()}")        # UPPER corner
        for suf in ("bjt", "res", "nicap", "diode"):           # 固定 4 顺序
            L.append(f".lib '{base}/incFile_lp' {suf}_{n}")    # lower corner
        L.append(f".temp {c['temp']}")                          # temp 必输出
        if c.get("vvdd"): L.append(f".param vvdd = {c['vvdd']}V")  # vvdd 空→跳过, 带 V 单位
        first = False
        L.append("")
```

### 输出格式（ss+tt 启用，msg 669 实测对齐）
```
* === CORNERS ===

.lib '/proj/drvqa/V0/model/current/model.sp' SS
.lib '/proj/drvqa/V0/model/current/incFile_lp' bjt_ss
.lib '/proj/drvqa/V0/model/current/incFile_lp' res_ss
.lib '/proj/drvqa/V0/model/current/incFile_lp' nicap_ss
.lib '/proj/drvqa/V0/model/current/incFile_lp' diode_ss
.temp -40
.param vvdd = 0.94V

.alter tt
.lib '/proj/drvqa/V0/model/current/model.sp' TT
.lib '/proj/drvqa/V0/model/current/incFile_lp' bjt_tt
.lib '/proj/drvqa/V0/model/current/incFile_lp' res_tt
.lib '/proj/drvqa/V0/model/current/incFile_lp' nicap_tt
.lib '/proj/drvqa/V0/model/current/incFile_lp' diode_tt
.temp 98
.param vvdd = 0.94V

```

### Case 设计
- **case_id**: `EDA-Eval-DesignFlow-CornerBlockGenProduce-001`
- **任务**: 写 `corner_block_gen.py <spec.json> <out.txt>`，读 spec（corners_base + corners[{name,temp,vvdd,enabled}]），按上述 `_corners` 语义生成 FineSim corner 块。
- **A** (visible): junlingw 真实 spec — base=`/proj/drvqa/V0/model/current`, 5 corners (ss/ff/tt/fs/sf), only ss enabled, vvdd=0.94, temps -40/125/98/98/98。
- **hidden B** (assets/hidden/, not in SUT sandbox): 结构异 A — base=`/proj/chip_t28/rel2.1/models/primitive`, 6 corners (typ/fst/slw/wcl/lt/ht), 4 enabled (typ/fst/slw/wcl), wcl vvdd="" (测 if-skip), vvdd 值 1.2/1.32/1.08/1.4/0.9/0.95, temps 27/125/-40/-55/-40/125。五重 anti-hardcode。
- **check.py 12 条**: a(zip+compile+size) b(B exit0+非空) c(header `* === CORNERS ===` 在) d(启用 corner 数==4) e(每启用 corner 有 `.lib '<base>/model.sp' <UPPER>`) f(每启用 corner 有 4 条 inc `.lib '<base>/incFile_lp' <suf>_<lower>` bjt/res/nicap/diode 顺序) g(第一个启用 corner 前无 .alter) h(后续启用 corner 前有 `.alter <raw_name>`) i(每启用 corner 有 `.temp <temp>`) j(有 vvdd 的启用 corner 有 `.param vvdd = <val>V`，空 vvdd corner 无 .param) k(禁用 corner 名不出现在任何 .lib/.alter/.temp/.param) l(anti-hardcode: A 的 base /proj/drvqa 不在 B 输出 + A 的 corner 名 ss/ff/tt/fs/sf 不在 B 输出) m(3-seed sha256 一致)。13 条。
- **3 negs**: neg_empty(空壳→a/b) / neg_print_only(硬编 A 输出串→d/e/f/g/h/l 多齿) / neg_core_removed(真解析 B 但 .alter 永远加/全跳过/vvdd 不带 V→g/h/j)。
