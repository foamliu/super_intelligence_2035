# deepread: iludo (cuij) — DRC runset 自动配置机制分析

- session: 1795001912028_iludo · user cuij · host hfeg0plg86 · mc=79
- 关键词: drc:948 lvs:836 calibre:229 aether:44 .gds:28 → physical_verify
- trace: 32 msgs, 2 真实 user 轮

## 用户真实意图（逐字）
- U#1 (idx0): `/proj/dscqa/V0_20261105_LVSClean/ver/drc/cuij/drcRunset 这个文件是如何自动配置的`
- U#16 (idx24): `bootstrap是什么脚本`

## assistant gold 链
1. list_allowed_files ver/drc/cuij → read_files drcRunset
2. list_allowed_files ver/drc (depth2) → 拿到全部 per-user 目录清单(aaron3xu/allanx/andyz/cuij/cuij_20261106/daley/deniss/dscqa_analog/dscqa_array/dscqa_top/dscqa_top_R/dustinwu/e0026699/fanglei/felxz/jingpei/jingsheng/jinyuli/jjfeng/kentw/kevin3d/kiaray/...)
3. read_files 多个用户 drcRunset (cuij/aaron3xu/allanx/daley) 对比 → 逐字节一致
4. read_files dscqa_top/Channel/rundrc.log + gdsOut.log + utRunset + _cluster.master_ → 看调用方式
5. list_allowed_files simdir → finesim/workdir
6. 结论(idx23): drcRunset=Calibre DRC runset 控制文件,行以*开头,cmn*=通用,drc*=DRC专用; per-user 由 bootstrap/环境初始化脚本模板复制(逐字节一致); *drcRulesFile 指向 /apps/imctf/cad/runset/dscqa/v0_20261105_lvsclean/current/calibreDRC.rule,current/是软链→最新PDK发布; .cgidrcdb 是符号链接
7. U#16 追问 bootstrap → idx31 澄清: "bootstrap"是描述性通称,非具体脚本; 真正生成脚本在 /apps/imctf(不可读); ver/drc 与 ver/lvs 同结构同用户清单,印证批量模板生成

## 关键事实（判分锚点）
- per-user drcRunset 逐字节一致 = 模板复制证据
- rule file 经 current/ 软链 = 自动指向最新
- cmn* / drc* 行分类
- dscqa_* = 功能库目录; .cgidrcdb = 符号链接
- drc 与 lvs 用户目录清单一致

## reframe（档 B, L1, fixture-driven）
真实 gold=分析聊天(无可执行交付物)→reframe 为离线分析器 analyze_drcrunset.py:
扫 ver/drc/<user>/drcRunset + ver/lvs/<user>/lvsRunset → JSON 报告(drc/lvs 用户清单、是否逐字节一致、md5多数派、规则文件路径+current软链、cmn/drc行数、功能库目录、符号链接)。
判分=check.py 内嵌隐藏 fixture B(不同用户集/规则路径/行数+evelyns植入差异使identical=False),11 teeth,独立算ground truth。自验 ref PASS 11/11,3 negative FAIL distinct(c/e/i)。
