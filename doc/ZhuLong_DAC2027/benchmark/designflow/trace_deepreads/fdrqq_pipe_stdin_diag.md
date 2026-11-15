# 深读笔记 · fdrqq · perl-python pipe STDIN 阻塞根因诊断

## trace 元数据
- session: 1792045004436_fdrqq (子目录 1792045004436_fdrqq/1792045004436_fdrqq.messages.json)
- user: zxtu · host: hfeg0pkn001 · mc: 70 · domain: spice_sim
- size: 159KB / 26 msgs / 14 user turns
- trace_source: real

## 用户原话（实质性 user turn）
1. 「怎么把perl脚本的STDOUT给到python输入」
2. 「python sys.stdin没有内容」
3. （贴出失败命令）`runsimFC_LP5_coverage_zxtu -Q -i 8 -q fqueue3 -p ddgoa -v V0 -s finesim -c control.finesim_promd_vcap_common -N Netlist_Vcap_20261012PM_Mod -n netlist -f ./cck_try.saved -C -Y Primesim_2023 | python /home/zxtu/zxtu_script/python/clprojinfo.py -label 0`
4. 「不能修改perl脚本，怎么吗拿到perl脚本的输出给到python脚本」
5. 「cat 显示文件前10行」

## 助手工具链
read_files(clprojinfo.py) → list_allowed_files → read_files(runsimFC_LP5_coverage_zxtu, base_func.py) → search_codebase → read_files(runsim lines 105-400, 400-780)

## 关键产物（真实脚本内容，已 scp 取证）
### clprojinfo.py（6 行，真实）
```python
from base_func import *
if __name__ == "__main__":
    col_type = int(get_argv_str("-label", default_value="0"))
    data = sys.stdin.read()
    print("len =", len(data))
```
→ 消费端用 `sys.stdin.read()`（读到 EOF 才返回）。

### runsimFC_LP5_coverage_zxtu（2456 行 perl，真实）关键根因片段（runOneSim, line 685-714）
```perl
sub runOneSim {
    my $cursimnum;
    if($opt_D){ print "Dry run done!\n"; sleep 6; }
    else {
        if($opt_q){
            if($use_smart && scalar @smart_queues > 1){
                my $chosen = pick_best_queue(\@smart_queues);
                $cmdpre = "bsub -I -q $chosen ";
            }
        } else {
            $cursimnum = `ps aux | grep $pslog `;
            chop($cursimnum);
            print "Waiting for license...";
            while($cursimnum>7){ ... sleep 30; print "."; }
        }
        defined(my $pid=fork) or die "Can not fork: $!\n";
        unless ($pid) {
            exec ("cd $matrixpath/$dir;./runscript");
        }
        print "Running in $matrixpath/$dir ...\n";
        sleep 10;
    }
}
```
→ 生产端：`fork()` 出子进程 `exec("./runscript")` 跑仿真，子进程**继承 STDOUT**（即接到 python 的管道写端）。父进程 `print "Running in ..." ; sleep 10` 后继续/退出，但后台仿真子进程长时间持有管道写端 → **管道永远不 EOF** → `sys.stdin.read()` 永久阻塞。

## 根因（助手结论，已证实）
**fork_inherit_stdout_no_eof**：perl `fork()` 的仿真子进程继承管道 STDOUT 写端，主进程退出后子进程仍存活（bsub 仿真跑数小时），管道无法 EOF，python `sys.stdin.read()` 永久阻塞，表现「sys.stdin 没有内容」。

## 约束 + 解决方案
- 约束：**不能修改 perl 脚本**
- 方案（助手给）：重定向到文件 + grep 过滤，再喂 python：
  `runsimFC_LP5_coverage_zxtu ... > /tmp/run.log 2>&1 ; grep "Running in" /tmp/run.log | python clprojinfo.py -label 0`
  → 绕开管道 EOF 阻塞，perl 主进程投递完退出后文件落盘，grep 只取 perl 自身打的 `Running in` 行（后台子进程的追加噪声被过滤）

## 造题设计
- archetype: debug-Q&A root-cause diagnosis（perl→python 管道 STDIN 阻塞/空）
- domain: spice_sim · layer: L1（离线 python 分析，无 EDA 工具运行）
- A 档不可行：真实 runsim 2456 行专有脚本 + bsub 仿真跑数小时 + SUT 沙盒无 /home/zxtu 与 /proj 权限 → B 档 synthesized
- A = 真实脚本的忠实节选（保留 fork/exec/STDOUT-inherit 根因模式 + 真实命令/参数/finesim/ddgoa/fqueue3/Primesim_2023）
- B = 合成类比场景，**不同根因**：`open(STDOUT,">",$logfile)` 自重定向 → 管道空（len=0，非阻塞），workaround = 直接读 redirect 目标文件
- check 独立解析 B 的 runsim.pl 求 ground truth（找 `open(STDOUT,">",...)` 提取 redirect 路径），断言 ≥8
- cross-input guard: B 根因 stdout_self_redirect ≠ A fork_inherit_stdout_no_eof；B 无 fork、有 STDOUT 重定向
- A-leak guard: 候选 JSON 不得含 A 专属 token（fork/runOneSim/fqueue3/ddgoa/Primesim_2023/finesim/runscript/zxtu/Running in/matrixpath）
