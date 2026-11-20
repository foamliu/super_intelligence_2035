# deepread — sid 1785478098817_yxin0 (e0014566 @ hfeg0pkn001, mc=237, 230 msgs / 566KB)

trace: `/home/e0014566/.cline/data/sessions/1785478098817_yxin0/1785478098817_yxin0.messages.json`
ip 10.129.2.10. tool fingerprint: 163 virtuoso + 26 cellview + 19 calibre + 5 skill + 2 dbGet → **layout_virtuoso** (RsCalc flow).

## 会话主线

USER#1 (msg 0) `read the prompt.md and do the job in it.` — agent 执行 `/home/e0014566/test_RScalc/test_skills/prompt.md` 描述的 RsCalc runner 流：
1. `gen_rscalc_agent.py` 把 `rscalc.config` 内联进 `run_rscalc_nogui.il` → `run_rscalc_agent.il`/`.cmd`
2. `virtuoso -nograph -replay run_rscalc_agent.cmd` 跑 RsCalc（power-net 电阻）
3. 等 ~180s，grep `DONE!`，cat `*.rvn` 结果
首次跑成功（cell `testa` @ `/proj/train/AI_Virtuoso/ver/rscalc/e0030265/testa`），产出 `RSDB_vdd/vdd.rvn` 等。

USER#2-4 (msg 46/68/78) 是**理解性问题**（不是需求）：
- 「只算几个点位的电阻能代表整体版图吗？」
- 「RTEXT 和 RNODE 两种标签作用分别是什么？」
- 「算出的电阻是 RNODE 之间的？怎么配对的？」
agent 通过读 `run_rscalc_nogui.il` + `addNets.txt`/`addPoints.txt` + `RSDB_vdd/dbBase` 给出解释：
- **RTEXT** = 网络定义标签（`addNets.txt`，告诉引擎这位置属于哪个 net）
- **RNODE** = 测量点标签（`addPoints.txt`，告诉引擎在这位置输出电阻）
- 配对不是两两配对，而是**星型汇聚到 PAD**（RTEXT 标记的 PAD 为供电入口，所有 RNODE 到 PAD 算电阻）。

## USER#5 (msg 94) — 唯一需求轮（本轮 A-档不可用：用户给了修复方案）

> 配置文件中有个要填写的 Nets， 是要填写的 RTEXT , 而我可能预先并不知道RTEXT有哪些。能不能增加一个选项，就是如果我不填，所有的RTEXT都生效，需要计算。

用户**直接给出了修复方案**（不填→所有 RTEXT 生效），故按 A-档规则不可用作 A 档任务说明 → 本 case 用 **B-档 synthesized**。

## agent 实现的 gold（= 本 case 参考解来源）

修改三处：

### 1. `run_rscalc_nogui.il` 新增 `CXMTAutoDetectNets(runDir)` 过程
```skill
procedure( CXMTAutoDetectNets(runDir)
  let((netFile inPort nextline lab_nm autoNets netStr)
    netFile = strcat(runDir "/addNets.txt")
    autoNets = nil
    inPort = infile(netFile)
    if(inPort then
      while(gets(nextline inPort)
        lab_nm = nth(1 parseString(nextline "\""))   ;; 按双引号切，取第 2 段 = net name
        if(lab_nm && lab_nm != "" then
          unless(member(lab_nm autoNets)             ;; member 去重
            autoNets = cons(lab_nm autoNets)
          )
        )
      )
      close(inPort)
    else
      error("Cannot open %s for auto-detection of nets\n" netFile)
    )
    if(autoNets then
      netStr = ""
      foreach(net reverse(autoNets)                  ;; reverse(cons...) 恢复首见序
        if(netStr == "" then netStr = net
        else netStr = strcat(netStr " " net))
      )
      netStr
    else ""
    )
  )
)
```

### 2. `CXMTutRscalc_run` 集成（提取 RTEXT/RNODE 标签之后，跑引擎之前）
```skill
unless(pwrNets && pwrNets != ""
  printf("[INFO] pwrNets not specified, auto-detecting from RTEXT labels...\n")
  pwrNets = CXMTAutoDetectNets(runDir)
  printf("[INFO] Auto-detected pwrNets: %L\n" pwrNets)
  unless(pwrNets && pwrNets != ""
    error("No RTEXT labels found in layout for auto-detection of pwrNets!\n")
  )
)
```

### 3. `RunRsCalcNoGui` 放宽必填校验
原 `unless(pwrNets && pwrNets != "" error("'pwrNets' not defined in config!\n"))` → 改为 info 提示（auto-detect 在 CXMTutRscalc_run 内做）。

### 4. `rscalc.config` + `SKILL.md` 文档
`pwrNets = ""` + 注释 `Leave empty ("") to auto-detect all nets from RTEXT labels in layout`；SKILL.md `pwrNets` 标 `No**` + 自动检测说明 + Troubleshooting 条目。

## addNets.txt 真实格式（= 本 case 的输入格式）

`/proj/train/AI_Virtuoso/ver/rscalc/e0030265/testa/addNets.txt`（3 行）：
```
TX_ADD\t"M1"\t1.15\t\t-4.3925\t"TX_M1"
TX_ADD\t"vdd"\t10.525\t\t-2.075\t"TX_M1"
TX_ADD\t"vbb"\t22.725\t\t4.225\t"TX_M1"
```
tab 分隔，x/y 之间**两个 tab**（中间空字段）。net name = 第一个双引号串（SKILL `nth(1 parseString(line "\""))`）。→ A 资产 `addNets_A.txt` 用此真实样本。

## 合成方案（B-档 synthesized, L1-boundary）

SUT 写 `rscalc_autonet.py`（纯 Python3 标准库）把自动检测逻辑落地成离线可验：
- 默认 `<addNets_file>` → JSON `{nets, count, unique, duplicates, malformed}`（首见序、member 去重、malformed=无引号网络名的行）
- `--emit-skill` → 打印等价 `CXMTAutoDetectNets` SKILL 过程体
- `--help`/`-h` exit0；无参/文件不存在 exit1+stderr
- 解析语义严格对齐 `nth(1 parseString(line "\""))`

check.py 14 条断言(a-n)：zip+py_compile / CLI 契约 / B1 多 net+重复+malformed 解析 / B2 跨输入守卫(无 A token M1/vdd/vbb 泄漏) / B3 空文件+全 malformed 边界 / 空引号网络名边界 / 首位重复序 / --emit-skill 内容 / 确定性 / 退化 stub 拦截。gold=solution.py。自验：ref PASS 14/14 + 4 negatives 全 FAIL + §4.9 三假全 FAIL。check_md5=dcf2374f411826567373f8b9ac134243. k_rationale=k_check=14≥8 GATE PASS. layout_virtuoso 域 +1.

## 候选筛选记录（本轮）
本轮选料先评 4 条非 xinqiaoz 高 mc 候选：
- `1793147699495_as67p`(easont mc786) / `1791963281932_4a852`(e0039602 mc661) / `1793078405436_t0aom`(easont mc650) / `1791526272387_1i0em`(rongtaoy mc574) — 全是 netlist/schematic 主体（hspice/netlist/schematic），非 physical_layout，弃。
- `1792042618272_wl9i4`(xingx mc290, innovus+calibre) — 实为 xcelium Verilog netlist 编译时长优化（make compile_net，二分注释 netlist 找慢段），数字仿真域，弃。
- `1792827081154_d810y`(jackjia mc274, virtuoso+cellview+calibre) — 实为 Aether 原理图/WaveView/dsim GUI 问答（飞线取消、波形信号显示、bmatrix），非 physical_layout，弃。
- `1792375022144_ekpd7`(xinqiaoz mc308, 288 calibre) — 是 DummyConfigCheck 同一会话延续（已有 DummyCfgCheck-001），重复，弃。
- `1785478098817_yxin0`(e0014566 mc237, 163 virtuoso+26 cellview+19 calibre) — 真 RsCalc SKILL feature，layout_virtuoso，**选定**。
