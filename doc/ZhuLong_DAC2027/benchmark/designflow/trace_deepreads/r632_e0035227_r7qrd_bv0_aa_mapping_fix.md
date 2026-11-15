# r632 deepread — r7qrd (e0035227@hfeg0plg55, layout_virtuoso, mc46)

**session**: 1793352312599_r7qrd.messages.json (subdir layout), 120 msgs, 796KB, 12 real user turns
**host IP**: 10.129.35.74
**user**: e0035227, foundry layout engineer
**task domain**: layout_virtuoso (pyAether/SKILL place-and-route config for DBC180→DBC280/FS280 layout migration)

## 背景

e0035227 有一套 pyAether/SKILL 版图迁移脚本 `Copy_instance/`（原 204nm→280nm），现要改造成 180nm→280nm 迁移（DBC 180 → DBC 280）。核心配置文件 `place_config.il` 定义各层 instance 的坐标映射函数（Xform*）和规则表（gPlaceRules）。

## 用户轮逐字

- **UI#1 IDX0**: "帮我解读下面路径下的脚本：/home/e0035227/Templates/Copy_instance/" — 解读脚本
- **UI#2 IDX14**: "现在我要参考这一套脚本把另一套工艺库的版图迁移，把DBC 180的迁移到DBC 280，原来这套脚本是204nm到280nm，现在是180到280，帮我分析一下做版图迁移这些脚本哪些地方需要改动" — 分析 180→280 迁移需改动哪些地方
- **UI#3 IDX16**: 4 点具体改动（gOutputDir/gInputDir/gPlaceConfigFile 路径改当前目录；place_config.il 等输出 read_instance.il 后再改；ReplaceTEM("FS280_Porting_All_20260930" "Template_cell_FS280_40_51_40")；本次执行后做数据分析：统计每类别 cy/cx 离散值分布反推 180 轨道和行位置，设计 place_config.il 的映射：基于 PDK 数值 + 分布，重写各 Xform* 函数里的数字，重写规则表和 pin 名单）
- **UI#4 IDX27**: "我的数据已导出，帮我解析然后修改place_config.il，完成映射设计"
- **UI#5 IDX73**: 报错 `dbOpenCellViewByType: Invalid character ' ' in input name:  DBC280_SVT_ALLtest`（目标库名前导空格）
- **UI#6 IDX75**: **"这里的BV0要在目标位置AA的Y轴中间，帮我把BV0的纵坐标调整一下"** — BV0 Y 坐标调整到目标 AA 的 Y 轴中间
- **UI#7 IDX85**: **"这个结果还是有问题，读取原180的坐标关系，看一下原来AA的位置和BV0的对应位置，AA的映射关系没问题，BV0参考原对应关系映射修改一下"** — 结果还是错，读原 180 坐标关系，AA 映射没问题，BV0 参考原对应关系映射修改
- **UI#8 IDX109**: **"这里参考的不是AA 器件 TEM_AA25_SVT：0.09 → 0.10（XformTrackRepitch）；BV0应参考AA 标记 AA25_SINGLE 等（devAA）：XformAACenter 保持 0.045/0.135/0.225/0.315，BV0分别对应到这四个Y 轴坐标位置CY一致，按照此映射关系帮我修改"** — BV0 不参考 AA 器件 TEM；BV0 应参考 AA 标记 devAA，XformAACenter 保持 4 中心 0.045/0.135/0.225/0.315，BV0 对应到这 4 个 Y 位置 CY 一致
- **UI#9-11 IDX115-117**: "继续" x3
- **UI#12 IDX119**: "你好"

## 关键 produce-task：BV0↔AA 坐标映射修正（UI#6→UI#8 三轮迭代）

### 源数据（DBC180）实测（agent 写 bv0_aa_offset.py 全库统计，IDX90-93）
- AA 器件 `TEM_AA25_SVT` cy 直方图: {0.09: 6325}
- AA 标记 `AA25_SINGLE` 系列 cy 直方图: {0.045: 354, 0.135: 380}
- BV0 相对同列 TEM(AA器件) 的 dy 直方图: dy=-0.045: 2169, dy=+0.045: 2221
  ⇒ BV0 在 AA 器件 cy=0.09 ±0.045 = 0.045 / 0.135（高 cell 第二对 0.27±0.045 = 0.225/0.315）

### 三次尝试
1. **UI#6 后 agent 第 1 版（IDX76-84）**: 新增 `XformAACenter`（就近吸附到 AA 的 4 Y 中心 [0.045,0.135,0.225,0.315]），把 BV0 和 devAA 都接到 XformAACenter。→ 用户 UI#7 否决："结果还是有问题，BV0 参考原对应关系映射修改"
2. **UI#7 后 agent 第 2 版（IDX86-108）**: 写 bv0_aa_offset.py 实测，发现 BV0 = TEM ±0.045。新增 `XformBV0`：BV0 跟随 AA 器件 TEM 映射后中心（0.09→0.10）并保留原 ±0.045 偏移 ⇒ 0.045→0.055, 0.135→0.145, 0.225→0.255, 0.315→0.345。verify_bv0.py 验证通过。→ 用户 UI#8 否决："参考的不是 AA 器件 TEM；BV0 应参考 AA 标记 devAA，XformAACenter 保持 0.045/0.135/0.225/0.315"
3. **UI#8 后 agent 第 3 版（IDX110-114）**: 把 bv0 规则改回 XformAACenter（与 devAA 同一函数），删除 XformBV0。**最终接受态**：
   - `XformAACenter`: 就近吸附 cy 到 [0.045, 0.135, 0.225, 0.315]
   - `bv0` 规则: 'exact ["BV0"] 'XformAACenter
   - `devAA` 规则: 'exact ["AA25_SINGLE","AA25_DUMMY_SINGLE","AMN25_SINGLE","GT_mark1_AA25"] 'XformAACenter
   - `TEM_AA25_SVT`: XformTrackRepitch（0.09→0.10，AA 器件，不变）
   - XformBV0（±0.045 偏移法）删除（被 UI#8 否决）
   - 其他结构层 V2/M3/MGC/SDB/VCC/VSS: XformId 保持原位

### gold（r7qrd 会话内接受态，UI#8 spec）
- BV0 与 devAA 共用 XformAACenter，cy 就近吸附到 4 中心 [0.045, 0.135, 0.225, 0.315]
- BV0 不参考 AA 器件 TEM（TEM 走 XformTrackRepitch 0.09→0.10，是另一条线）
- XformBV0（±0.045 偏移）被否决，不得出现
- BV0 与 devAA 的 cy 集合一致（"CY 一致"）

### XformTrackRepitch 公式（place_config.il）
```
n = (cy <= 0.146) ? round((cy-0.034)/0.028) : 5.0 + round((cy-0.214)/0.028)
target_cy = 0.016 + 0.042 * n
```
⇒ 0.09 → n=2 → 0.016+0.084=0.10；0.27 → n=7 → 0.016+0.294=0.31... 实际 0.016+0.042*7=0.31。会话内 agent 用 0.09→0.10, 0.27→0.30（verify_bv0.py 输出 tgtCtr=0.10/0.30，舍入差异，取 agent 实测 0.10/0.30）。

注：磁盘上的 place_config.il 在 r7qrd 之后的会话（261028 修订）又把 BV0/devAA 改成 XformBV0(0.045→0.07, 0.135→0.21) 并删了 XformAACenter——那是后续会话的演进，**不影响 r7qrd 会话内的接受态作为 gold**。

## case 设计（B档 mock-behavioral, L1-boundary）

**deliverable**: `bv0_coord_mapper.py <instances.json> <output.json>` — 给定 DBC180 源 instance 数据（category/name/cx/cy），按 UI#8 最终接受 spec 应用映射，输出结构化 JSON。

**spec（grounded in UI#8）**:
- TEM_AA25_SVT: XformTrackRepitch (0.09→0.10, 0.27→0.30)
- devAA (AA25_SINGLE/AA25_DUMMY_SINGLE/AMN25_SINGLE/GT_mark1_AA25): XformAACenter (snap to nearest of [0.045,0.135,0.225,0.315])
- BV0: XformAACenter (SAME as devAA)
- structural (V2/M3/MGC/SDB/VCC/VSS): XformId (identity)
- XformBV0 (±0.045) REJECTED

**asset A**: instance_data_a.json（含 BV0 cy=0.045/0.135/0.225/0.315, devAA 同, TEM 0.09/0.27, structural 各若干）
**隐藏 B**: instance_data_b.json（不同 cy 值，BV0 cy=0.05/0.14/0.22/0.32 等需 snap 到 4 中心，反硬编）
**隐藏 B2**: instance_data_b2.json（再换一组 cy，含偏离中心值需 snap）

**15 条 a-o 断言**：结构2 + spec 4 + 规则绑定 3 + 映射正确 4 + 一致性 1 + 反硬编 1 + 确定性 1（详见 check.py）
