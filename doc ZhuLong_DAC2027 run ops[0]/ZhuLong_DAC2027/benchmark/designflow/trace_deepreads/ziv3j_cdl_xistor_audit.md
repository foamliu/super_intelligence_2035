# ziv3j — CDL/GDS 对照与晶体管统计 (schematic_netlist)

- **session**: 1793157233266_ziv3j · user e0047434 · host 10.129.32.190 · mc=54 · N=134 msgs
- **trace_source**: 真实 cline 会话，FS204 标准单元库审计
- **A-faithful produce-task**: U#0 逐字（唯一干净 produce 轮；U#1/U#3 是补充需求，U#2/U#4 是 continue）

## U#0 逐字（A-faithful prompt 原文）
> 请到这个目录中：/home/e0047434/work/std_cell/data/FS204_for_Justin
> 里面有两个子目录，分别放着cdl网表和gds版图
> 在本会话中，你不能修改CDL和GDS目录中的任何内容；
> 你如果需要输出，请写在zl_output 目录中
> 所有输出尽量用中文，专业名词除外。
> 请帮我做两件事：1. 检查cdl和gds是否是一一对应的，看文件名；2. 对每个cdl，统计它们分别有几根管子组成，既要写文字的report，也要给出适合人类直观查看的可视化输出

## trace agent 演化
- U#0 → analyze_cdl.py 解析 CDL/GDS 目录，按基名集合比对，统计 .SUBCKT 内 M 器件（按模型名 psvt_fs→PMOS / nsvt_fs→NMOS），产 summary.txt + 晶体管数量明细表.md + FS204_CDL_GDS对照与晶体管统计报告.md + PNG 图表
- U#1 → 补充管子数统计指标（agent 自定：总管子数/PMOS/NMOS/P-N比/奇偶性/等效fin/引脚数/功能类别/功能族/驱动档/线性扩展），画图
- U#3 → 补充 GDS 金属层统计（每版图几个金属层 + 通孔层统计 + 可视化）

## 真实金标准事实（zl_output 报告）
- 464 CDL / 464 GDS，基名全匹配（0 cdl_only / 0 gds_only）
- 模型仅两种：psvt_fs (PMOS) / nsvt_fs (NMOS)，单一 SVT 阈值
- 总 10812 管子 = 5406 PMOS + 5406 NMOS，P/N=1.000
- 全库管子参数一致：l=6n, wgaa=0.035u, nfin=1, nf=1, mr=1（靠并联更多单元管实现驱动强度）
- 平均 23.30 / 中位 24 / 最小 0（BOUNDARYLEFT 等 30 物理单元）/ 最大 80（CKNR2D8）/ 非零最小 2（INVD1）
- 28 功能类别，464 单元，平均引脚 7.80（2~11）
- 驱动档靠并联：总管数 = k × 档数（线性扩展）

## 合成决策
- 真实 /proj std-cell lib 不可附加 → B-grade synthesized
- 参数化生成器 cdl_lib_core.py：19 功能族 × drive 缩放，SVT/HVT/LVT 三阈值模型
- A=SVT 30 CDL 全匹配 344 管子；B=HVT 42 CDL 含 1 cdl_only+1 gds_only 662 管子；B2=LVT 23 CDL 全匹配 158 管子
- 反硬编码三轴：模型名 + 单元数/mismatch + 族分布全不同；check(o) 禁源码任何模型字面量
