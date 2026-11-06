交付：outputs/submit.zip，内含 fm/ 与 cov/ 两套独立流程目录（各自 Makefile + scripts + setup + data + SourceMe + README）。
入口：outputs/submit.zip
判分：check(submit.zip, workdir) —— 静态结构断言 + tclsh stub / make -n 跨输入守护。