# deepread: 1795087698313_mxv3d (jinsongl @ hfeg0pfn101 / 10.129.33.227)

- shard: B | domain: spice_sim | mc=4 | msgs=111 | user_msgs=5
- r915-rescan 41 fresh B sid, ranked #4 (rescan_1120_B_ranked.tsv)
- picked over 5v4tq (near-dup parked joeyl DelvtoNetlistMod cluster) and 71kny/sik16/ovji6/tom4v (junk/too-short/out-of-domain)

## user intent (5 msgs, verbatim)
- msg0: "/home/jinsongl/package/packageSimCase.pl通读这个文件 并且告诉我对于spf文件的处理是怎么样的"
- msg4: "请帮我重新进行修改，要求当遇到meaure文件时候，按照spf文件来进行减时处理，对measure文件的识别按照文件的每一行开头都需要是.meas"
- msg38: "还是用head的方式 都是.meas就可以 把新增的自程序删除"
- msg64: "measure 文件在 packageNetlist（不递归）和 transDir（不改写路径）阶段也按 SPF 处理"
- msg90: "比较现在路径下的两个结果文件有没有区别 packsim_1119193008/ packsim_1119173809/"

## real artifact
- /home/jinsongl/package/packageSimCase.pl (v2.4, 536 lines post-fix / 534 pre-fix)
- 4 measure-regex locations: copyFile unique-name branch (L210), copyFile dup-name branch (L230), packageNetlist early-return (L263), transDir early-next (L457)
- measure regex: /^(?:[ \t]*\.meas\b[^\n]*\n?)+[ \t]*\z/i  (OR-ed onto existing SPF condition)
- pre-fix: SPF-only (`$head =~ /\*\*FORMAT SPF/ and $head !~ /\r/` for copyFile; `$line10 =~ /\*\*FORMAT SPF/` for packageNetlist/transDir)
- post-fix: SPF OR measure

## reframe
- faithful port (trace IS a real code-mod task, not Q&A). A = pre-fix .pl (user's starting state). hidden B = structurally different netlist tree.
- primary observable: copyFile \r-preservation on pure-measure file (pre-fix sed-strips=0, post-fix preserves=4)
- packageNetlist/transDir measure-handling is defensive (pure measure files have no .include keywords → no observable diff), verified by structural condition (c) checking all 4 regex locations

## case
- id: EDA-Eval-DesignFlow-MeasFileSpfStyleGen-001
- k_check=12, ref PASS 12/12, NEG 5/5 FAIL (empty_shell/print_expected/core_removed=§4.9三假 + hardcode_a + firstline_only)
