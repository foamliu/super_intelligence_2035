# Deepread: cpv3d — FineSim connectFile 网表连接性校验 Perl 脚本

- **session**: 1793067588685_cpv3d.messages.json
- **user/host**: taodu @ hfeg0plg87 (mc=356, netlist:2257/hspice:46/schematic:25)
- **agent**: cline (lead)
- **domain**: schematic_netlist → case `EDA-Eval-DesignFlow-ConnFileNetChk-001` (L1, track B)

## 用户意图（7 轮真实需求演进）
1. U[0]（原话）:「读取下面到 si.inp 文件，查找是否存在文件名以 connectFile 开头到，如果存在，则抓取网表到 hierarchy, 判断 connectFile 中的 net 是否都存在，排除 ignore 的 instance hierarchy, 形成一个 perl 脚本」(附 FineSim 仿真目录路径)
2. U[81]: connectFile 文件可以包含路径，也可以是 .inc/.include hierarchy 调用到的
3. U[377]: 脚本要支持 .module 的网表
4. U[417]: 对 check_connectFile_nets.pl 添加注释，变量进行有意义命名，程序进行规范化优化
5. U[466]: 脚本使用没有提供对应到输入，进行提示
6. U[510]: 不采用默认的 si.inp 文件，由用户进行输入，每次产生的 report 文件按时间命名，避免覆盖之前的结果
7. U[531]: 目前的脚本跑起来速度很慢，需要进行速度优化，毕竟 connection 文件有百万千万行，网表的 instance hierarchy 也数量庞大

## 助手工具链
read_files（读 si.inp / netlist / connectFile 片段）+ list_allowed_files + search_codebase + editor（132 次，构建/迭代 check_connectFile_nets.pl 及大量 gen_*.sh/gen_*.py 辅助脚本绕开 editor 长度限制）+ run_approved_command（跑 perl -c / test_run.sh 验证）。原始 /rundata 仿真目录已被清理（si.inp/connectFile 均已不存在），但最终脚本 `/home/taodu/check_connectFile_nets.pl`（240 行）仍在主机上，已 scp 取回作为金标准。

## 金标准（check_connectFile_nets.pl 核心逻辑）
- 参数：`-i <si.inp>`(必需) / `-n <netlist>`(可选,自动检测) / `-o <outdir>` / `-h` / 位置参 sim_dir
- Step0：解析 si.inp 的 `.inc/.include` 建 search_dirs；从 `[!netlist]` 或 `.inc netlist*` 自动定位网表
- Step1：`File::Find` 在 sim_dir + search_dirs 找 `connectFile*`（排除自己的 `connectFile_check_*` 报告）；并解析 si.inp 里 `.inc connectFile*` 引用（含嵌套 .inc）
- Step2：读 connectFile，支持两格式——`R<name> <path1> <path2> <val>` 电阻行（取 path1/path2，按最后 `.` 拆 leaf net + inst path）与 `<net> <hier.path>` 普通行；跳过 gnd/vss/vcc/vdd 电源
- Step3：从 si.inp `.option finesim_ignore="..."` 与 `si.ignore_block` 文件收集 ignore hierarchy，建合并正则
- Step4：递归 `.inc` 解析网表，支持 `.subckt/.ends` 与 `.module/.endmodule`，记端口表（O(1) 哈希）与 `X<inst>`→子电路映射；算顶层子电路
- Step5/6：每个 connectFile net 沿 inst path 从顶层子电路走到实例，查该 net 是否为所达子电路端口 → PASS/FAIL；ignore 命中跳过；带 path_cache
- 输出：`connectFile_check_YYYYMMDD_HHMMSS.txt`，末尾 `PASS: n | FAIL: m`，有 FAIL 则 exit 1

## case 合成（B 档，L1 离线）
- 真实脚本=金标准，原 /rundata 输入已清理 → 自建保真缩比 A/B sim_dir
- A（公开，.subckt）：TOP/invx4/arrblk/nand2/ignstub/pch/nch 7 子电路，connectFile 9 net（含 R-line），ignore TOP.Xarr.Xn1 → PASS=6/FAIL=3
- B（hidden，.module + .inc connectFile 发现 + File::Find）：mTop/decblk/drvbuf/nandg2/invx2/biasgen/rfareg/pmod/nmod 9 子电路，connectFile 14 net（2 个 connectFile 文件，含 R-line），ignore mTop.Xdec.Xbuf → PASS=8/FAIL=6
- 跨输入守卫：B 计数(8/6)与 A(6/3)全异，杀硬编码；B 用 .module 测网表格式分支；B 用 .inc+File::Find 双路径测 connectFile 发现；R-line 测电阻行解析
- check.py 15 条件 a–o：zip 含脚本/shebang/perl -c/-h USAGE/缺 -i 报错/B exit 1/报告文件名/汇总 8|6/Subckts:9/Files:2/Top-level:mTop/TotalCF:2/Ignored:1/跨输入 A 6|3/时间戳格式
- 自验：ref 15/15 · §4.9 三假(空壳/print_expected/core_deleted)全 FAIL · 5 negatives NEG_RC=0(distinct d–o) · test==disk roundtrip OK · 端到端 PASS · k=15 闸门 PASS
