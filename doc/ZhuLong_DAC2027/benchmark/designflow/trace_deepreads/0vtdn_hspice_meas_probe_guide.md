# trace_deepread: 1793341791924_0vtdn (weizhuo@hfeg0plg52)

- session: 1793341791924_0vtdn/1793341791924_0vtdn.messages.json (31 msgs, mc=15, keywords hspice:62/waveview:3/synopsys:2/pdk:2/drc:2/netlist:1)
- host: hfeg0plg52 = 10.129.35.68, user: weizhuo (also on hfeg0plg96/103/07)
- domain: spice_sim (HSPICE .measure/.probe Q&A teaching session)

## 用户意图（逐字原文）
- U#0: 「你怎么读取文件夹中的文件？」(meta: 询问 agent 读取文件能力)
- U#4: 「你可以帮我写hspice语句吗」
- U#6: 「帮我测试bla<25>和blb<25>这两个线的最大最小值的平均值」
- U#8: 「解释一下什么时候用param，什么时候不用」
- U#10: 「那么probe什么时候可以用呢」
- U#12: 「.probe似乎可以做仿真波形的处理，比如叠加啥的，你大致给我举几个例子，并说明其中注意事项」
- U#14: 「我怎么感觉probe」(不完整)
- U#16: 「你这个可以读取csv文件生成html文件吗」
- U#18: 「你就先用你这个例子先生成一个html文件就行」
- U#29: 「话说我怎么使用命令打开html文件呀」

核心 spice_sim 意图 = U#4-U#12: HSPICE .measure/.probe 语法教学 Q&A (how-to/explain)
非核心 = U#0(工具能力), U#16-U#29(CSV→HTML 代码生成, 非 spice_sim 域)

## 助手实际做了什么
1. 解释 list_allowed_files / read_files 工具用法
2. 给 .MEASURE 语句: MAX/MIN/AVG V(bla<25>), PARAM='(max+min)/2' 算术表达式
3. 解释何时用 PARAM: 直接函数(MAX/MIN/AVG/PP/RMS)不需 PARAM, 算术运算/引用其他 measure 结果需 PARAM='expr'
4. 解释 .PROBE: 控制哪些信号存入波形文件(.tr0), .MEASURE 依赖 .PROBE 保存的信号
5. 解释 .PROBE 表达式: V(diff)=V(a)-V(b), V(cm)=(V(a)+V(b))/2, DB(x)/LOG10 等
6. CSV→HTML: 写 Python 脚本 generate_html.py 生成 measurement_results.html (3.9KB)
7. 解释 Linux 打开 HTML 命令: firefox/xdg-open/cat/less

## 合成 case
- case_id: EDA-Eval-DesignFlow-HspiceMeasProbeGuide-001
- 形态: A 档 trace-faithful, spice_sim how-to Q&A → 产出生成式 HSPICE .measure/.probe 语句 + 结构化讲解报告
- A (doc/requirements.json): signals bla<25>/blb<25>, measurements MAX/MIN/AVG/PARAM/DIFF/COMMON_MODE
- hidden B: signals sa<3>/san<3>, measurements MAX/MIN/PP/PARAM/DIFF/GAIN_DB (cross-input guard)
- check.py: 25 conditions, cross-input guard (B signals/types), A-leak guard (A tokens not in B output)
- 自验: ref 25/25 PASS + 4 negs all FAIL
