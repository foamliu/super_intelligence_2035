#!/usr/bin/env python3
"""Build the jsonl entry for EDA-Eval-DesignFlow-PexRunlpePathFormatDiag-001
and append to EDA-Eval-DesignFlow_C.jsonl."""
import hashlib
import json
import os

REF = "reference/EDA-Eval-DesignFlow-PexRunlpePathFormatDiag-001"
CASE = "EDA-Eval-DesignFlow-PexRunlpePathFormatDiag-001"

check_py = open(REF + "/check.py").read()
sha16 = hashlib.sha256(check_py.encode("utf-8")).hexdigest()[:16]

prompt = (
    "run /rundata/lacaa/TV1_FS/simdir/finesim/workdir/e0024852/SRAM_bitcell_DTCO/hd_CH252_bitcell/lpe/hd_CH252_bitcell/runlpe.sh "
    "if sucess where is the dspf\n\n"
    "附件说明（已从真实 PEX LPE 运行目录摘取，原值保留）：\n"
    "- runlpe.sh：用户 invoke 的 LPE 提参驱动脚本（内含 cd、module load、bsub 调用 runlpe_gxrc、spf 软链创建）\n"
    "- lpe.config：runlpe.sh 通过 -config 指向的 CalibreLVS + StarRC 配置文件（含 cdl/gds 路径、mode、CORNER、Temperature 等）\n"
    "- user_invoked_dir.txt：用户实际 invoke runlpe.sh 时所在的目录绝对路径（即 runlpe.sh 在文件系统中的位置）\n"
    "- workspace_listing.txt：user_invoked_dir 目录下已存在的文件与子目录清单（含历史的 .dspf、.cc_rep、CCI_DB/、svdb/ 等）\n"
    "- user_asked_format.txt：用户口头要求得到的寄生网表格式（\"dspf\"）\n\n"
    "请生成一份结构化 JSON 诊断报告，回答用户两个问题：\n"
    "1. 如果 runlpe.sh 跑成功，寄生网表文件实际叫什么名字、落在哪个绝对路径？（注意：runlpe.sh 内部 cd 到的工程目录可能与 user_invoked_dir 不同——需要明确指出）\n"
    "2. 用户问的是 \"dspf\"，但本次配置实际产出的格式叫什么？如果两者不一致，需要说明用户当前目录里那些已存在的 .dspf 是从哪里来的（不是本次流程的产物）。\n\n"
    "报告还需要给出 recommended_fix（结构化修复建议列表）和 severity。"
)

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": prompt,
    "attachments": [
        "assets/" + CASE + "/prompt.txt",
        "assets/" + CASE + "/task_brief.md",
        "assets/" + CASE + "/runlpe_A.sh",
        "assets/" + CASE + "/lpe_A.config",
        "assets/" + CASE + "/user_invoked_dir_A.txt",
        "assets/" + CASE + "/workspace_listing_A.txt",
        "assets/" + CASE + "/user_asked_format_A.txt",
    ],
    "test": check_py,
    "metadata": {
        "trace_source": {
            "user": "e0024852",
            "host": "hfeg0pkn004 (10.129.2.13)",
            "session_file": "1793685645025_x0ib4.messages.json",
            "match_count": 116,
            "real_task_summary": (
                "e0024852 在 hfeg0pkn004 上的 PEX LPE 提参流程 Q&A 串（73 msgs/42 user turns/13 真实 user_input 轮）。"
                "用户先问某 finesim 仿真目录的「difference」，再连续追问 PEX 提参需要哪些输入、版图 GDS 在哪、"
                "是否有版图→gds 的命令、lpe.config 里有哪些输入、CAPTAB/tran.map/pin_file/hcell 能否省略。"
                "末轮 U#65（★core produce-task seed）「run /rundata/lacaa/TV1_FS/.../e0024852/.../runlpe.sh if sucess where is the dspf」。"
                "助手尝试 run_approved_command 被策略引擎拒绝（filePath outside dynamicFileRoots），改读 runlpe.sh + lpe.config "
                "给出确定性诊断：(1) runlpe.sh 内部 cd 写死 /proj/lacaa/V0/ver/pex_gxrc/e0012583/hd_CH252_bitcell/lpe/hd_CH252_bitcell/，"
                "lpe.config 里 cdl/gds 也指向 e0012583 工程目录，与用户 invoke 的 TV1_FS/e0024852 目录不同 → 输出不会落入用户当前目录；"
                "(2) lpe.config mode=RCC → 实际产出 hd_CH252_bitcell.spf_RCC，不是 .dspf；用户目录里已存在的 "
                "hd_CH252_bitcell_rev03.dspf 是之前另一次 rev03 DSPF 流程的产物，本次 RCC 流程不会生成它；"
                "(3) 输出位置=.../e0012583/.../hd_CH252_bitcell.spf_RCC + 脚本末尾向上两级建软链 .../e0012583/hd_CH252_bitcell/hd_CH252_bitcell.spf_RCC；"
                "(4) 修复=要么把 runlpe.sh/lpe.config 的硬编码路径改成用户本地 TV1_FS/e0024852 路径，要么在能访问 /proj/lacaa/V0 的登录节点上跑。"
                "本案 reframe 聚焦在 (1)+(2)+(3) 三条确定性可验证事实。"
            ),
        },
        "domain": "physical_verify",
        "track": "B",
        "tier": "L1",
        "test_rationale": (
            "20 条断言：①zip 合法+候选 .py >=300B UTF-8 无 NUL+py_compile+stdlib-only(禁 numpy/pandas/calibre/virtuoso/aether 等) "
            "②候选跑隐藏 B exit0+合法 JSON+24 顶层键齐全 ③runlpe_cd_path==/proj/lacaa/V1/.../e0024852/ampMacro_v9/lpe/ampMacro_v9/（反 A 的 V0/e0012583/hd_CH252_bitcell，从 cd 行解析） "
            "④path_mismatch==True（B user_invoked_dir != B runlpe_cd_path） ⑤config_mode==RC（反 A 的 RCC，从 mode= 行解析） "
            "⑥expected_output_format==spf_RC（反 A 的 spf_RCC，由 mode 派生） ⑦expected_output_filename==ampMacro_v9.spf_RC（反 A 的 hd_CH252_bitcell.spf_RCC，由 cdl_top+format 派生） "
            "⑧expected_output_path==B runlpe_cd_path+ampMacro_v9.spf_RC（反 A 的 e0012583 路径） ⑨symlink_levels_up==1（B 单 cd ..，反 A 的 2 cd ../..，从 bsub 后第一个 cd-up+ln 块解析） "
            "⑩expected_symlink_path==.../ampMacro_v9/lpe/ampMacro_v9.spf_RC（B 1-up，反 A 的 2-up .../hd_CH252_bitcell/hd_CH252_bitcell.spf_RCC） "
            "⑪config_version==v1（反 A 的 v0） ⑫module_loads==[glory/2025.12_P001, ds/calibre/2024.1_12]（反 A 的 glory/2026.03_P002+ds/calibre/2023.3_14） "
            "⑬user_asked_format==dspf ⑭format_mismatch==True（dspf != spf_RC） "
            "⑮preexisting_dspf_in_user_dir==[ampMacro_v9_rev07.dspf]（反 A 的 hd_CH252_bitcell_rev03.dspf，从 workspace_listing 解析） "
            "⑯recommended_fix 非空 list(>=2)+含 edit/change/verify/replace/fix 动作关键词 ⑰severity==high "
            "⑱反硬编码 A：A 跑 config_mode==RCC & expected_output_format==spf_RCC & symlink_levels_up==2 & preexisting_dspf==[hd_CH252_bitcell_rev03.dspf]（与 B 四轴全异） "
            "⑲缺路径 exit!=0 ⑳3-seed sha256 稳定"
        ),
        "reframe_note": (
            "档 B reframe：A 档 gold=assistant 对真实 PEX 运行目录的 free-text 诊断 prose（live runlpe.sh 被 agent-policy "
            "拒绝执行，依赖 /proj/lacaa 不可达且无 >=8 独立硬断言牙）→ reframe 为离线纯 stdlib(re/json/os/sys/argparse) "
            "pex_runlpe_diag.py，CLI <runlpe_sh> <lpe_config> <user_invoked_dir> <workspace_listing> <user_asked_format> [-o out.json]，"
            "解析 runlpe.sh(首条 cd 绝对路径→runlpe_cd_path、-config 路径、module load 行→module_loads、bsub 后第一个 cd-up 块→symlink_levels_up+symlink_target_rel)，"
            "解析 lpe.config(mode/cdl/gds/cdl_top/gds_top/version/CORNER/Temperature/lpe_star/hcell/skip_cell)，"
            "解析 workspace_listing(.dspf 文件清单→preexisting_dspf_in_user_dir)，"
            "派生 expected_output_format(由 mode 映射 R/C/RC/CC/RCC/FSCOMPARE→spf_X)、expected_output_filename(cdl_top+format)、"
            "expected_output_path(runlpe_cd_path+filename)、symlink_levels_up→expected_symlink_path(parent(cd_path,levels)+filename)、"
            "path_mismatch(runlpe_cd_path != user_invoked_dir)、format_mismatch(user_asked_format != expected_output_format)，"
            "输出 24 顶层键结构化 JSON+recommended_fix+severity。"
            "visible A 忠实 trace(V0/e0012583/hd_CH252_bitcell/mode=RCC/cdl_top=hd_CH252_bitcell/v0/2-up 软链/"
            "glory/2026.03_P002+ds/calibre/2023.3_14/preexisting hd_CH252_bitcell_rev03.dspf)；"
            "hidden B 全反相(V1/e0024852/ampMacro_v9/mode=RC/cdl_top=ampMacro_v9/v1/1-up 软链/"
            "glory/2025.12_P001+ds/calibre/2024.1_12/preexisting ampMacro_v9_rev07.dspf)，"
            "10+轴全异(runlpe_cd_path workspace/top name/mode/expected_output_format/expected_output_filename/expected_output_path/"
            "symlink_levels_up/expected_symlink_path/config_version/module_loads/CORNER/Temperature/preexisting_dspf)防硬编码 A。"
        ),
        "asset_fidelity": (
            "visible A 的 runlpe.sh/lpe.config 忠实摘自 trace x0ib4 (e0024852 @ hfeg0pkn004, 2026-11-03) 中真实文件内容："
            "runlpe.sh line 3 cd /proj/lacaa/V0/ver/pex_gxrc/e0012583/hd_CH252_bitcell/lpe/hd_CH252_bitcell/、line 15 bsub -config 路径、"
            "module load glory/2026.03_P002 + ds/calibre/2023.3_14、line 17-22 cd ../.. + ln -sf lpe/hd_CH252_bitcell/hd_CH252_bitcell.spf_RCC，"
            "lpe.config version=v0/mode=RCC/cdl=.../e0012583/hd_CH252_bitcell/hd_CH252_bitcell.cdl/cdl_top=hd_CH252_bitcell/"
            "CORNER=TYP/Temperature=85，均与原 trace 一致（无需 mask key/token，路径无敏感信息）；"
            "user_invoked_dir=TV1_FS/e0024852/SRAM_bitcell_DTCO（用户真实 invoke 位置）；"
            "workspace_listing 含真实 hd_CH252_bitcell_rev03.dspf + hd_CH252_bitcell.spf_RCC 软链 + CCI_DB/svdb/gexRpt 等；"
            "user_asked_format=dspf（用户原话「where is the dspf」）。"
            "hidden B 同结构但 workspace/top/mode/version/CORNER/Temperature/module 版本/软链级数/preexisting dspf 全反相。"
        ),
    },
}

out = "EDA-Eval-DesignFlow_C.jsonl"
with open(out, "a", encoding="utf-8") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("appended to", out)
print("task_id:", entry["task_id"])
print("prompt len:", len(entry["prompt"]))
print("test bytes:", len(entry["test"]))
print("check.py sha16:", sha16)
print("attachments:", entry["attachments"])
