import os,sys,tempfile,zipfile,shutil,importlib.util,json
sys.path.insert(0,"/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow")
import lite_verify_judge_B as lv
cid=sys.argv[1]
with tempfile.TemporaryDirectory() as judge:
    g2,err=lv.setup_judge(judge,cid)
    if not g2:
        print(json.dumps({"case_id":cid,"L2":"NO_REF","detail":err})); sys.exit(0)
    chk=os.path.join(g2,"check.py")
    spec=importlib.util.spec_from_file_location("chk_"+cid.replace("-","_"),chk)
    mod=importlib.util.module_from_spec(spec)
    os.chdir(g2)
    try:
        spec.loader.exec_module(mod)
        res=mod.check(os.path.join(g2,"submit.zip"),".")
        ok=(res is True) or (isinstance(res,dict) and (res.get("pass") is True or res.get("ok") is True))
        out={"case_id":cid,"L2":"PASS" if ok else "FAIL:"+repr(res)[:200],"detail":""}
    except AssertionError as e:
        out={"case_id":cid,"L2":"FAIL:"+str(e)[:200],"detail":""}
    except Exception as e:
        out={"case_id":cid,"L2":"ERR:"+repr(e)[:200],"detail":""}
    print(json.dumps(out))
