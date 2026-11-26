# cfreq_ctrl — Design Compiler 综合流程

本目录为 VCO 自动校准模块 `cfreq_ctrl` 的 Synopsys Design Compiler (DC)
综合流程，目标 RTL 为 `assets/rtl_synth/cfreq_ctrl.v`。

## 目录结构

```
syn/
├── Makefile                      # 顶层 Makefile (make syn / make clean)
├── SourceMe                      # 环境设置脚本 (source 后进入流程)
├── README.md                     # 本文件
├── setup/
│   └── common_setup.tcl          # 公共库 / 通用变量设置
├── scripts/
│   ├── dc.tcl                    # 综合主脚本 (read/elaborate/compile/write)
│   ├── dc_setup.tcl              # 顶层设置脚本 (source 其余两个)
│   └── dc_setup_filenames.tcl    # 目录 / 文件名变量
├── sdc/
│   └── cfreq_ctrl.sdc            # 时序约束 (时钟 / 分组 / IO / false path)
└── data/
    └── syn_filelist.f            # RTL 源文件列表
```

## 快速开始

```bash
source ./SourceMe
make syn      # 运行综合, 输出网表到 ./netlist
make clean    # 清理综合产物
```

## 设计信息

| 项目 | 值 |
|------|----|
| 顶层模块 | `cfreq_ctrl` |
| 参考时钟 REFCLK | 25 MHz (period 40 ns) |
| 反馈时钟 FBCLK | ~25 MHz, 与 REFCLK 异步 |
| 复位 | `RST_N` 低有效异步复位 (各时钟域同步释放) |
| 时钟域 | REFCLK 域 / FBCLK 域 (CDC) |

## 约束说明 (sdc/cfreq_ctrl.sdc)

- `create_clock` 定义 REFCLK / FBCLK 两个时钟 (period 40ns)。
- `set_clock_groups -asynchronous` 声明两个时钟域异步。
- `set_false_path` 屏蔽异步复位 `RST_N` 路径。
- 对 `LOOP_BREAK` / `WINDOW_LEN` / `THRESHOLD` 施加输入延迟,
  对 `RDY` / `CAP_CTRL_OUT` 施加输出延迟 (均相对 REFCLK 域)。