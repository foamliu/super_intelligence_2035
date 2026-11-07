# 深读笔记 · 1793777251915_s3noo (e0045128 @ hfeg0pkn005, mc=54)

## trace 概要
- 304 msgs, 10 user turns, gen_lib_make 项目
- 双任务: ①gen_cfg_tcl.py(Makefile CFG变量检查+TCL生成 USER#0-7) ②gen_lef_list.py(LEF filelist生成 USER#8-9)
- kw: lef:358/rtl:27/synthesis:15/techfile:7 → pnr_signoff domain

## A-faithful 选轮: USER#8 (msg 250)
逐字: 「读一下CXDP_PROJ_CFG，帮我生成一个产生lef filelist的脚本，脚本后面跟的参数是$CXDP_LEF_FILES, $CXDP_LEF_DIRS以及输出的路径」
- rule2 未违反(干净需求,用户只描述目标,未给根因/修复)
- USER#9 补充: 重复LEF报Error

## gold (msg 281, 303)
gen_lef_list.py (CLI: -lef_list/-path/-out):
- 对-lef_list每个LEF, 依次在-path各目录找<dir>/<lef>, 命中第一个即停
- 找到的完整路径写入-out(每行一条)
- 找不到报Error exit1
- 目录不存在只Warning跳过(非致命)
- USER#9加: -lef_list重复LEF→Error exit1, 不生成输出

## 真实附件
- /home/e0045128/sandbox/gen_lib_make/CXDP_PROJ_CFG (LEF section lines 155-195)
- lef hack_path dirs: pad(GPIO_CUP_H.lef) / mem(5个CXN4HC...lef) / ana(ANA_PLLGP_1.lef) / dig(USB20_PHY_DIG.lef)
- 所有LEF文件0字节(占位)
- /proj/lacaa/.../LEF 远程不可达

## case 合成决策
- A档: 真实CXDP_PROJ_CFG子集 + 真实lef_dirs(9 LEF跨5目录: std/pad/mem/ana/dig)
- B档合成: 不同LEF名(INV_X1/NAND2_X1/FLOP_X1/PAD_IN/PAD_OUT/RAM_1K/ROM_256) + 不同dirs(std/io/mem/empty/nonexistent) + INV_X1双目录first-match测试 + GHOST缺失测试 + 重复检测测试
- 交付形态: gen_lef_list.py (通用LEF filelist生成器, CLI三参)
- check.py 16 conds(a-p): subprocess真跑候选于隐藏B, 覆盖 normal/missing/dup/all-dirs-missing 四场景 + A反硬编守卫 + 源码无LEF名字面量
