# trace deepread — whc3n (zanezang @ hfeg0plg57) — MOS DC GUI 仿真工具

## session
- sid: `1793942454477_whc3n`
- user: zanezang · host: hfeg0plg57 · mc=154 · 392 hspice · ratio=0.918 (纯 hspice)
- file: `/home/zanezang/.cline/data/sessions/1793942454477_whc3n/1793942454477_whc3n.messages.json` (1.21MB, 293 msgs, mtime Nov 9 20:02)
- Desktop 实文件已 GC，但 `.snapshot/hourly-new.2026-11-09_2000/Desktop/mos_dc_gui.py` 仍在 → 金标准完整取得(1210 行, 51KB)

## 13 个真实用户轮 (A-faithful 选轮)
- U#0(msg0): IC 前端工程师，Linux 仿真 nmos/pmos model 性能，写 py 可视化脚本，自动生成 bench，一键仿真出图，可提问 → **提需求 ✓**
- U#1(msg23): 给出 003_nmos_dc.sp/004_pmos_dc.sp + bsub 语句，param_modfiy 可配置，要 GUI 配 mode → **提需求 ✓**
- U#2(msg152): LX82 是电容值不是 vth，需要看 → 澄清 ✓
- U#3-9(msg196-210): 功能符合但需优化。pmos CV 范围 0~2*vcc(原 bug 只到 vcc)、器件名可填(ntn/ntn_lv)、单独器件区、双 model 对比(实线/虚线)、id/gm 单位 m/u → **提需求/细化 ✓**
- U#10-12(msg269-273): CV 纵坐标改 Cgg、GUI 高度贴合页面 → **提需求 ✓**
- 全 13 轮均「提需求/表达目标」，无给出根因或修复方案 → **A-合规 ✓**

## 金标准 = mos_dc_gui.py (snapshot 11-09_2000)
- 架构: tkinter GUI + `--cli` 无界面模式 + `--selftest` 自检(3s 退出打 SELFTEST OK)
- `NMOS_TEMPLATE`/`PMOS_TEMPLATE`: 逐字复制自 003/004 .sp，param_modfiy 块(temp/vcc/vg_l/vg_h/step/w/l/nf)
  - NMOS: `.dc vd 0 'vcc' 0.01 sweep vg 'vg_l' 'vg_h' 'step'` + `.print LX7(XMMN0)`/`1/LX8(XMMN0)`/`abs(i(vvdd))` + `.dc vref '-vcc' 'vcc' 0.01` + `.print LX82(XMMN1)`
  - PMOS: `.dc vds 0 'vcc' 0.01 sweep vgs 'vgs_l' 'vgs_h' 'step'` + 同 .print(XMMP0) + `.dc vref 0 '2*vcc' 0.01` + `.print LX82(XMMP1)` (U#4 CV 范围修复)
- `parse_print_file`: 解析 HSPICE ASCII .printswN，`***parameter vg=val` 分块，两行表头，数字行；`_ROW_RE`/`_PARAM_RE`
- `collect_results`: vref→cv_tab；`_classify` lx7→gm, lx8→rout, i(vvdd)/abs→id；PMOS cv_y 取 abs
- `save_csv`: `<pre>_iv.csv`(vg_V,vd_V,Id_A,gm_S,Rout_Ohm) + `<pre>_cv.csv`(vgs_V,c_lx82_F)
- `draw_device_figure` 2x2: Id-Vds(uA/mA 自动)/gm-Vds(uS/mS)/Rout(semilogy Ohm)/C-V(LX82 fF, m1实线 m2虚线)
  - 注: C-V y-label 在最终文件仍为 "LX82 (fF)"(U#11 求改 Cgg)；本 case 以 manifest y_labels 显式要求 Cgg 落实该需求
- `_si_scale`: 按 max|v| 自动选 SI 前缀(u/m/...)

## case 合成 (L1 · offline Python · 真跑候选)
- 本 case 聚焦离线可复刻核心: bench 生成 + .printsw 解析 + CSV/manifest 输出(跳过 bsub/GUI mainloop)
- 资产 A: example_nmos_dc.sp/example_pmos_dc.sp(逐字 bench) + simdir/(合成 .printsw0/.printsw1 + config.json, nmos+pmos, vcc=1.1)
- 隐藏 B1: vcc=1.2, dev ntn/ptn, 量级不同；B2: vcc=0.9, dev ntn_lv/ptn_lv, 反硬编码
- reference: mos_dc_tool_ref.py(gold --cli 派生, matplotlib 可选+stub PNG 兜底)
- check.py 13 断言(a..m): 真跑候选(gen-bench + parse subprocess on B1/B2)
- 自验: ref PASS 13/13 + 3neg(naive_empty/hardcoded_a/no_parse)全 FAIL + §4.9 三假(empty_shell/only_print/ref_core_deleted)全 FAIL + 断言门 k=13≥8 ✓
