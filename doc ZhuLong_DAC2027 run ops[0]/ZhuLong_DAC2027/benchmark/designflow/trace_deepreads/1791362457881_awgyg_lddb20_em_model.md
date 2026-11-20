# trace_deepread: 1791362457881_awgyg (hbpeng / hfeg0pkn005, mc=445) — LDDB2.0 EM xls 模板→静态类

- **session**: `1791362457881_awgyg`，user `hbpeng`，host `hfeg0pkn005`，733 msgs / 3.0MB，agent=lead，模型 deepseek-v4-flash。
- **真实任务（A 档任务说明取 #277 用户原话逐字）**：解析 `/apps/imctf/develop/PDK_QA/EMIR/test/emtfVsEmrule/LDDB2.0_EM_File.xls` 模板——每个 sheet 名→驼峰类名（如 EmTemp），第一行表头→属性，行数据→Row 类（sheet 类名 + `Row` 后缀，如 EmTempRow）；直接生成最终静态类（非动态），封装读取文件的类；类名/变量名驼峰命名。用户分 6 轮（#0/#188/#198/#199/#277/#333）逐次细化规格，最终接受 #277 的 Row 后缀版本。
- **A 档合规性**：#277 是「提出需求」轮（不是给出根因/修复方案），符合运维令 21:3x §①2 选轮规则。
- **金标准（trace 末尾用户实际接受的产物）**：`/home/hbpeng/Lddb20EmModels.py`（705 行，scp 取回本地 reference/，sha e2a0a0d5...）。结构：
  - 5 个 Row 类：`EmTempRow`/`EmIpeakRow`/`EmIrmsRow`/`EmIdcMetalRow`/`EmIdcViaRow`，各带 `SHEET_NAME` + `HEADER_MAP`(OrderedDict，驼峰键) + `fromRow`/`fromRowDict` classmethod。
  - 5 个容器类：`EmTemp`/`EmIpeak`/`EmIrms`/`EmIdcMetal`/`EmIdcVia`，各带 `SHEET_NAME`/`ROW_CLASS`/`rows`/`addRow`/`__len__`/`__getitem__`。
  - `SHEET_CLASS_MAP`（5 个原始 sheet 名→容器类）、`EmXlsReader`（`parse` 用 xlrd 读 xls，`temps/ipeaks/irms/idcMetals/idcVias` 便捷属性 + `getContainer/getData`）、`parseXls` 便捷函数。
  - sheets：EM_TEMP(11 col) / EM_Ipeak(8) / EM_Irms(8) / EM_Idc_metal(19) / EM_Idc_via(21)。
- **附件处理**：原始 `LDDB2.0_EM_File.xls` 在 .75 与 hbpeng 机器上均 permission denied（属 imctf 用户）。trace 中 assistant 的 `run_approved_command` 被 policy 拒绝、`read_files` 读二进制 xls 返回空——assistant 实际是从已有相关 .py（Emtf.py/Itf.py/EmXls.py 旧版）推断 HEADER_MAP 结构。**故附件 xlsx 由 gold 的 HEADER_MAP（真实表头）+ 模板样例行重建**（pure-stdlib .xlsx writer，xlrd 1.2.0 已验证可读）。A=3 行/sheet，隐藏 B=5/4/4/5/4 行（不同 seed/取值，跨输入守卫用）。
- **判分依赖处理**：gold 的 `EmXlsReader.parse` 内 `import xlrd`，判分机（36.15）无 xlrd。**check.py 内嵌 stdlib-only xlrd shim**（读 .xlsx via zipfile+xml.etree，注入 sys.modules['xlrd']），判分全程零第三方依赖。.75（有 xlrd 1.2.0）与本地（无 xlrd）均自验通过。
- **自验**（本地，无 xlrd）：ref reference_submit.zip → check() PASS（15/15）；5 negative（fake_empty→c / fake_print_expected→c / fake_core_deleted→h / naive_hardcode_a→m / naive_stub_constants→n）全 FAIL，NEG_RC=0；§4.9 (a)(b)(c) 三假提交覆盖。
- **case**：`EDA-Eval-DesignFlow-EmXlsModel-001`，domain=eda_other，track=faithful，level=L1，k 条断言=k_check=15≥8 GATE PASS。已追加 EDA-Eval-DesignFlow_A.jsonl（第 28 行），台账 mark case。
