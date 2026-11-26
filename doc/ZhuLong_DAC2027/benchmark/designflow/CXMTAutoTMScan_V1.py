#;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
#;  Description
#;  
#;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
#;  Revision History
#;    -v1.0  Zixu  2026-09-22
#;      - Initial version
#;    -v1.1  Zixu & Jincanw 2026-10-03
#;      - Improve flow
#;      - Support independent TM SCAN check
#;      - CXMTseTestModePinNetMismatchChk support multiCell, support hierPath
#:      - CXMTseGetCmModuleAndPort support mos target, improve script
#;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

import pyAether as ae
import difflib
import os
import re
import csv
from collections import deque, defaultdict, OrderedDict
from csv import DictReader

def CXMTseAutoTMCheck_GUI():
    global myForm_autoTMScan
    global CMLatchListDef

    projName = leGlobalVariables.project
    lib1 = ae.strcat(projName,"_digital")
    lib2 = ae.strcat(projName,"_cmos_digital")
    lib = lib1 if ae.dbLibExist(lib1) else lib2
    if projName == "ddgoa":
        #CMLatchList = ["CMCenterL","CMCenterR","CMAryA"]
        CMLatchList = ["CMAryA","CMCenterR","CMCenterL","CMDqL","CMDqR","CMRight","CMLeft"]
    else:
        CMLatchList = [str(cell.name) for cell in ae.dmGetObj(lib).cells if re.search("^CM[a-zA-Z]*$", str(cell.name))]

    CMLatchList.sort()
    CMLatchDef = ' '.join(CMLatchList)

    lib_list = [str(lib) for lib in ae.dbGetAllLibs()]
    myLib = ae.aeCreateComboField(
        widgetName = "myLib", 
        choice = lib_list, 
        prompt = "CMBlock Library", 
        currentValue = lib,
        isEnabled=False,
    )
    searchCellsComFld = ae.geCreateStringField(
        name='searchCellsComFld',
        prompt='CM Cells',
        defValue=CMLatchDef,
        value=CMLatchDef,
    )
    hierConfigFld = ae.aeCrtFileSelectorField(   
        fieldName="hierConfigFld",
        prompt='HierPath File',
        mode='existingFile',
        defValue=f"{ae.etGetWorkingDir()}/HierPathFile",
    )
    netPincheckFld = ae.geCreateRadioField(
        name='netPincheckFld',
        prompt='PinNet Mismatch',
        choices=['Check', 'NotCheck'],
        defValue='Check',
        value='Check',
    )
    modeFld = ae.aeCreateRadioField(
        name = "modeFld",
        choices = ['PreChk+DDVChk', 'PreChk', 'DDVChk'],
        prompt = "Mode",
        defValue = 'PreChk+DDVChk',
    )
    fields = [netPincheckFld, myLib, searchCellsComFld, hierConfigFld,  modeFld]
    myForm_autoTMScan = ae.aeCreateAppForm(name="myForm", 
        widgetEntrys=fields,title = "CXMTAutoTMCheck", 
        buttonLayout="ApplyCancelDef",
        callBack= CXMTseAutoTMScanFunc, 
        initialSize = [500,220])
    ae.aeDisplayForm(myForm_autoTMScan)


class CXMTseAutoTMScanFuncClass(ae.aeBaseAppFormCallBack):
    def funcCb(self):
        global myForm_autoTMScan
        ae.etPrintf("\n")
        ae.etPrintf("Begin:Start to check testmode")
        ae.etPrintf("-" * 180 + "\n")
        CXMTseAutoTMScan_main(myForm_autoTMScan)

CXMTseAutoTMScanFunc = CXMTseAutoTMScanFuncClass()

def CXMTseAutoTMScan_main(mainForm):
        lib = str(mainForm.myLib.value)
        cellList = str(mainForm.searchCellsComFld.value)
        mode = str(mainForm.modeFld.value)
        netPinChk = str(mainForm.netPincheckFld.value)
        configFile = str(mainForm.hierConfigFld.value).strip()
        if not configFile or not os.path.isfile(configFile):
            ae.etPrintf("[ERROR]HierPath file missing or invalid.\n")

        workDir = ae.etGetWorkingDir()

        step1_File = strcat(str(workDir), "/Step1_allCMAdr_MAandOP.csv")
        step1_errFile = strcat(str(workDir), "/Step1_allCMAdr_MAandOP_ErrorInfo.csv")
        step2_File = strcat(str(workDir), "/Step2_allCM_HierPath.csv")
        step3_File = strcat(str(workDir), "/Step3_TMScanTable.rpt")
        step4_File = strcat(str(workDir), "/Step4_TMScanTable.csv")
        tmScan_File = strcat(str(workDir), "/out_files")

        if mode in ['PreChk+DDVChk','PreChk']:
            ############ STEP 0 pin vs net name mismatch check  ###########################
            step0_File = strcat(str(workDir), "/Step0_Pin_net_mismatch.log")
            TestModeMisMatchNets = set()
            if netPinChk == 'Check':
                TestModeMisMatchNets = CXMTseTestModePinNetMismatchChk(configFile,step0_File)
                ae.etPrintf(">>> Step0 : Check pin net finished.\n")
                ae.etPrintf("-" * 180 + "\n")
            ############ STEP 1 generate allCMAdr_MAandOP.csv ###########################
            ae.etPrintf(f">>> Step 1 : Generate {step1_File} begin\n")
            CXMTseGetAllLatchInfo(lib,cellList,mode,step1_File,step1_errFile,TestModeMisMatchNets)
            ae.etPrintf(f"Done! The file {step1_File} generated successfully.\n")   
            ae.etPrintf("-" * 180 + "\n")
            ############ STEP 2 generate Step2_allCM_HierPath.csv #######################
            #short_step1_file = step1_File.replace('.csv', '_short.csv') #short for test
            #os.system(f"sed -n '1,50p' {step1_File} > {short_step1_file}") #short for test
            #os.system(f"sed -n '1,1p' {step1_File} > {short_step1_file}")
            #os.system(f"grep cm1_io_WrR1dly {step1_File} >> {short_step1_file}")
            #if os.path.isfile(short_step1_file): #short for test
            ae.etPrintf(">>> Step 2 : Generate {step2_File} begin\n")
            CXMTseCMBlockAddHierPath(step1_File, configFile, step2_File) #long for nomal
                #CXMTseCMBlockAddHierPath(short_step1_file, configFile, step2_File) #short for test
            ae.etPrintf(f"Done! The file {step2_File} generated successfully.\n")
            ae.etPrintf("-" * 180 + "\n")  
            ############ STEP 3 generate Step3_TMScanTable.rpt ##########################
            ae.etPrintf(">>> Step 3 : Generate TMScanTable.rpt\n")
            CXMTseGetCmModuleAndPort(step2_File,step3_File)
            ae.etPrintf(f"Done! The file {step3_File} generated successfully.\n")
            ae.etPrintf("-" * 180 + "\n")  
        if mode in ['PreChk+DDVChk','DDVChk']:
            ############ STEP 4 generate Step4_TMScanTable.csv ##########################
            ae.etPrintf(">>> Step 4 : Generate tmscan.csv\n")
            CXMTseConvertTMScanRptToCsv(step3_File, step4_File)
            ae.etPrintf(f"Done! The file {step4_File} generated successfully.\n")
            ae.etPrintf("-" * 180 + "\n")
            ############ STEP 5 ddv check ##########################
            ae.etPrintf(">>> Step 5 : tm scan begin\n")
            run_cmd = (f"bash -c 'unset PYTHONHOME PYTHONPATH; "
                       f"PYTHONPATH=/proj/shdc/cad/tools/python3.7/lib/python3.7/site-packages:/proj/shdc/cad/cck_utility/python_packages "
                       #f"/home/zixuguo/testmode/lp/ctm_inputcsv_1.py -tm-csv {step4_File} -csv {step1_File}'")
                       #f"/home/zixuguo/AutoTMScan/output/ctm_inputcsv_2.py -xls {step4_File} -csv {step1_File}'")
                       f"/home/zixuguo/AutoTMScan/output/ctm_inputcsv_2.py -xls {step4_File} -csv {step1_File} -sv /rundata/ddgoa/V0/simdir/verilog/thomaswu/verilog.lpddr5.ddgoa.new/libs -netlist /rundata/ddgoa/V0/simdir/verilog/thomaswu/verilog.lpddr5.ddgoa.new/netlist/V0_WOWTOP_2026Oct15.193816/netlist -top WOWTOP'")
            if os.system(run_cmd):
                info = "[ERROR] python may run have issue!!\n"
                ae.aeError(info)
                return
            ae.etPrintf(f"Done! tm scan finished, pls check {tmScan_File}\n")
            ae.etPrintf("-" * 180 + "\n")

def CXMTseGetAllLatchInfo(lib,cellList,mode,logFile,errFile,excluded_nets):
        libName = lib
        process = leGlobalVariables.process
        projName = leGlobalVariables.project
        cmStautsTable = {
            'ag': 'Analog',
            'cl': 'Column',
            'fc': 'Function',
            'id': 'IDD',
            'io': 'IO',
            'ro': 'Row',
            'ts': 'Test',
            'sp': 'Spare',
        }
        if projName == 'ddcpb' or projName == 'ddjoc' or projName == 'ddgoa':
            cmStautsTable["gc"] = "GlobalFunction"
            cmStautsTable["rf"] = "Refresh"
            cmStautsTable["sc"] = "Scrc"
            cmStautsTable["ta"] = "TimingAdjust"

        with open(f"{logFile}", 'w') as OUTP, open(f"{errFile}", 'w') as OUTP1:
            OUTP.write("MA(O),MA(H),OP,Category,Module Name,CM Name,CM Block\n")
            extractSel = 'Yes' #zixu
            CMLatchListSel = [x for x in cellList.split() if x]

            if projName == "iejoal":
                LatchList = [str(x) for x in ae.dbGetAllCells(libName) if re.search(r'^T_Cm.*Latch', str(x)) or re.search(r'^Cm.*Latch.*22ull', str(x))]
            else:
                LatchList = [str(x) for x in ae.dbGetAllCells(libName) if re.search(r'^T_Cm.*Latch', str(x)) or re.search(r'^Cm.*Latch', str(x))]

            LatchTable     = {}
            Cm2Table       = {}
            testmodeInfoTable = {}
            MAInfoTable       = {}
            for Latch in LatchList:
                LatchInfo = CXMTseGetLatchInfo_getTerms(libName, Latch)
                if LatchInfo:
                    LatchTable[Latch] = LatchInfo
                    testmodeLen = len(cadr(LatchInfo))
            for CMLatch in CMLatchListSel:
                if not ae.dbCVExist(libName, CMLatch, "schematic"):
                    ae.aeMessage(f'[WARN]: Not found {libName}/{CMLatch}/schematic!!!')
                    continue
                cv = ae.dbOpenCV(libName, CMLatch, "schematic", mode="r")
                if cv:
                    #print(cv.cellName)
                    CXMTseGetAllLatchInfo_ByCell(cv,LatchTable,testmodeInfoTable,MAInfoTable,OUTP1,excluded_nets)
                    #print(cv.cellName)

                    AllCm2InfoList = CXMTseGetAllCm2Info_ByCell(cv,excluded_nets)
                    if len(AllCm2InfoList) > 0:
                        Cm2Table[str(cv.cellName)] = AllCm2InfoList[::]
                    ae.dbCloseCV(cv)
            # global cxmtTestModeBefore, cxmtTestModeAfter
            # cxmtTestModeBefore = testmodeInfoTable.copy()

            CXMTseMergeMoudleName(testmodeInfoTable)
            ########################################################################
            # Rename duplicate third-part net names to avoid sorting failure in external script.
            rename_map = {}
            occurrence = {}
            for ma_key in testmodeInfoTable:
                for item in testmodeInfoTable[ma_key]:
                    if 'ERROR' not in item[2] and (parts := item[2].split('_')) and len(parts) >= 3 and (third_part := parts[2]):
                        count = occurrence.get(third_part, 0) + 1; occurrence[third_part] = count
                        if count >= 2:
                            new_name = f"{item[2]}_WANNING<{count-1}>"
                            rename_map[item[2]] = new_name
                            #ae.aeMessage(f"[WARNING] Third part '{third_part}' duplicated: {item[2]} -> {new_name}")
            for cell in Cm2Table:
                for net_index, net in enumerate(Cm2Table[cell]):
                    if (parts := net.split('_')) and len(parts) >= 3 and (third_part := parts[2]):
                        count = occurrence.get(third_part, 0) + 1; occurrence[third_part] = count
                        if count >= 2:
                            new_name = f"{net}_WANNING<{count-1}>"
                            Cm2Table[cell][net_index] = new_name
                            ae.aeMessage(f"[WARNING] Third part '{third_part}' duplicated: {net} -> {new_name}")
            for ma_key in testmodeInfoTable:
                for item in testmodeInfoTable[ma_key]:
                    if item[2] in rename_map:
                        item[2] = rename_map[item[2]]
            ########################################################################
            # cxmtTestModeAfter = testmodeInfoTable.copy()
            MALen     = len(list(testmodeInfoTable.keys())[0]) if len(testmodeInfoTable) >= 1 else 3
            MAFullLen = 511
            if MALen > 3:
                MAFullLen = 1023

            # ae.aeMessage(f'len: -----------> {MALen}, {MAFullLen}, {testmodeLen}')
            if extractSel == 'No':
                for k in sorted(list(testmodeInfoTable.keys())):
                    MAadrOct = k
                    MAadrHex = CXMTseConvertStrOutp("%x" % ae.etEvalString(f'0{k}'), 3)
                    for j in range(1, testmodeLen+1):
                        testmodeList = testmodeInfoTable[MAadrOct][j-1]
                        tmFullName   = testmodeList[2]
                        tmFullNameList = [x for x in tmFullName.split('_') if x]
                        category = ''
                        module   = testmodeList[3]
                        # if not re.search(r'ERROR', tmFullNameList[0]):
                        if cadr(tmFullNameList) == 'sp':
                            spPat = re.findall(r'cm([0-9])', car(tmFullNameList))
                            spNum = spPat[0]
                            category = f'{cmStautsTable["sp"]}{spNum}'
                        elif cadr(tmFullNameList) in cmStautsTable:
                            category = cmStautsTable[cadr(tmFullNameList)]
                        #cellNameStr = ae.buildString(ciUtilsMakeUnique(ae.car(testmodeList)),";")
                        cellNameStr = ae.buildString([str(x) for x in ciUtilsMakeUnique(ae.car(testmodeList))], ";")
                        OUTP.write(f'{MAadrOct:<3},{MAadrHex:<3},{j - 1},{category},{module},{tmFullName},{cellNameStr}\n')
                        #table_test[{tmFullName}]= ({MAadrOct:<3},{MAadrHex:<3},{j - 1},{category},{module},{tmFullName},{cellNameStr})
            else:
                for i in range(0, MAFullLen + 1):
                    MAadrOct = CXMTseConvertStrOutp("%o" % i, MALen)
                    MAadrHex = CXMTseConvertStrOutp("%x" % i, 3)
                    for j in range(1,testmodeLen+1):
                        if MAadrOct in testmodeInfoTable:
                            testmodeList = testmodeInfoTable[MAadrOct][j-1]
                            tmFullName   = testmodeList[2]
                            tmFullNameList = [x for x in tmFullName.split('_') if x]
                            category = ''
                            module   = testmodeList[3]
                            # if not re.search(r'ERROR', tmFullNameList[0]):
                            # if tmFullNameList[1] == 'sp':
                            if cadr(tmFullNameList) == 'sp':
                                spPat = re.findall(r'cm([0-9])', car(tmFullNameList))
                                spNum = spPat[0]
                                category = f'{cmStautsTable["sp"]}{spNum}'
                            elif cadr(tmFullNameList) in cmStautsTable:
                                category = cmStautsTable[cadr(tmFullNameList)]
                            cellNameStr  = ae.buildString(ciUtilsMakeUnique(ae.car(testmodeList)),";")
                            OUTP.write(f'{MAadrOct:<3},{MAadrHex:<3},{j - 1},{category},{module},{tmFullName},{cellNameStr}\n')
                        else:
                            OUTP.write(f'{MAadrOct:<3},{MAadrHex:<3},{j - 1},NA,NA,NA,NA\n')

            if len(Cm2Table) > 0:
                cm2ModuleList = []
                cm2ModulePat  = re.compile(r'(.*)<[0-9]*>')
                for cell in Cm2Table:
                    for cm2 in Cm2Table[cell]:
                        cm2Type = [x for x in cm2.split('_') if x][1]
                        cm2Category = 'Spare2' if cm2Type == 'sp' else cmStautsTable[cm2Type]
                        findPattern = re.findall(cm2ModulePat, cm2)
                        tm2 = findPattern[0] if findPattern else cm2
                        if tm2 not in cm2ModuleList:
                            cm2Module = tm2
                            cm2ModuleList.append(cm2Module)
                        else:
                            cm2Module = ''
                        OUTP.write(f"NA,NA,NA,{cm2Category},{cm2Module},{cm2},{cell}\n")


def CXMTseGetAllLatchInfo_ByCell(cv,LatchTable,testmodeInfoTable,MAInfoTable,OUTP1=None,excluded_nets=None):
    projName = leGlobalVariables.project
   # workDir  = ae.etGetWorkingDir()
   # OUTP1 = ae.strcat(workDir,"/allCMAdr_MAandOP_ErrorInfo.log")
   # with open(OUTP1,"w") as OUTP1:
    if OUTP1:
        for Latch in LatchTable:
            LatchInstList = [inst for inst in cv.instances if re.search(strcat('^',Latch,'$'), str(inst.cellName))]
            inputTerm   = ae.car(LatchTable[Latch])
            outputTerm  = ae.cadr(LatchTable[Latch])
            MAcodeArray = [False for idx in range(len(inputTerm))]
            outputArray = [False for idx in range(len(outputTerm))]
            CmOp = f'CmOp<{len(outputTerm) - 1}:0>'
            MACodeList = []
            for LatchInst in LatchInstList:
                if excluded_nets:
                    skip_inst = False
                    for conn in LatchInst.instTerms:
                        if conn.net and str(conn.net.name) in excluded_nets:
                            skip_inst = True
                            break
                    if skip_inst:
                        continue
                # declare(MAcodeArray[length(inputTerm)])
                # declare(outputArray[length(outputTerm)])
                # MAcodeArray = {}
                # outputArray = {}
                MACode = ""
                outputList = []
                for conn in LatchInst.instTerms:
                    if str(conn.direction) == "input":
                        if str(conn.name) in inputTerm:
                            netSite = inputTerm.index(str(conn.name))
                            netName = str(conn.net.name)
                            netNum = CXMTseGetLatchInfo_getNetNum(netName)
                            MAcodeArray[netSite]=netNum
                        elif str(conn.name) == CmOp:
                            if str(conn.net.name) != CmOp:
                                OUTP1.write(f'[ERROR4] {cv.cellName}/{LatchInst.name} {CmOp} connection is incorrect\n')
                    if str(conn.direction) == "output" and str(conn.name) in outputTerm:
                        testmodeSite = outputTerm.index(str(conn.name))
                        testmode = str(conn.net.name)
                        if not (projName == "drgpa" or projName == "drjpa"):
                            comPat = re.compile("(.*)_[I|i]nt([^a-z]*$)")
                            if re.search(comPat, testmode):
                                testmode = re.sub(comPat,"\\1\\2",testmode)
                        outputArray[testmodeSite]= [[str(cv.cellName)], str(conn.name), testmode]

                for i in range(0,len(inputTerm)):
                    MACode = ae.strcat(MACode,MAcodeArray[i])

                #print(MACode)
                #print(LatchInst.name)
                #print(MACodeList)
                if not re.search(" ", MACode) and (projName in ["ddjoc","ddgoa","decqa","ddcpc"]):
                    #OUTP1.write(f'{cv.cellName}/{LatchInst.name}  net name MACode {MACode} and label name labelAddress {labelAddress}\n')
                    #print(MACode)                            
                    if len(MACode) == 3:
                        if atoi(ae.substring(MACode, 1, 1)) >= 8:
                            MACode = f"{atoi(ae.substring(MACode, 1, 1)):o}{ae.substring(MACode, 2, 3)}"
                        else:
                            MACode = f"0{atoi(ae.substring(MACode, 1, 1)):o}{ae.substring(MACode, 2, 3)}"
                    else:
                        MACode = f"{atoi(ae.substring(MACode, 1, 2)):o}{atoi(ae.substring(MACode, 3, 1))}{atoi(ae.substring(MACode, 4, 1))}"
                    #print(MACode)    
                if not re.search(" ", MACode) and MACode not in MACodeList:
                    MACodeList.append(MACode)
                    # mismatch between net name and label name
                    instBbox  = ae.emyBox()
                    instBboxF = ae.emyBoxF()
                    ae.EmyInstGetSelectBox(LatchInst, instBbox)
                    ae.emyDbu2UU(cv, instBbox, instBboxF)
                    labelNameList_pre = ae.dbGetTrueOverlapsEx(cv, bbox=instBboxF, stopLevel=1, layerName='text')
                    labelNameList     = [x.object for x in labelNameList_pre if x.object.objType == 'Text']
                    #for x in  labelNameList:             
                    #    print(x.text)
                    if len(labelNameList) >= 1:
                        #labelName1    = [str(x.text) for x in labelNameList if re.search(r'MA[0-9]*<', str(x.text))][0]
                        #labelName2    = [str(x.text) for x in labelNameList if re.search(r'CmAdr', str(x.text))][0]
                        labelName    = [str(x.text) for x in labelNameList if re.search(r'CmAdr', str(x.text)) or re.search(r'MA[0-9]*<', str(x.text))][0]
                        #if labelName1:
                        #    comPatLabelP = re.findall(r'>=([0-9]*)', labelName1)
                        #if labelName2:
                        #    comPatLabelP = re.findall(r'=9\'o([0-9]*)', labelName2)
                        if labelName:
                            if re.findall(r'>=([0-9]*)', labelName):
                                comPatLabelP = re.findall(r'>=([0-9]*)', labelName)
                            if re.findall(r'=9\'o([0-9]*)', labelName) :
                                comPatLabelP = re.findall(r'=9\'o([0-9]*)', labelName)
                            if re.findall(r'=6\'o([0-9]*)', labelName):
                                comPatLabelP = re.findall(r'=6\'o([0-9]*)', labelName)
                        if comPatLabelP:
                            labelAddress = comPatLabelP[0]
                          #  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
                          #  ;;for ddjoc, MAcode 962  <-->  Label 1162
                          #  ;;           MAcode 1062 <-->  Label 1262
                          #  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

                            #OUTP1.write(f'{cv.cellName}/{LatchInst.name}  net name MACode {MACode} and label name labelAddress {labelAddress}\n')        
                            if labelAddress != MACode:
                                OUTP1.write(f'[ERROR3] {cv.cellName}/{LatchInst.name} mismatch between net name {MACode} and label name {labelAddress}\n')
                        else:
                            OUTP1.write(f'[ERROR3] {cv.cellName}/{LatchInst.name}: {labelName} the label is incorrect\n')
                    else:
                        OUTP1.write(f'[ERROR3] {cv.cellName}/{LatchInst.name} the label does not exist\n')
                     
                    #print(MACode)
                    for i in range(0,len(outputTerm)):
                        if MACode in testmodeInfoTable:
                            singleTestmodeList = testmodeInfoTable[MACode][i][::]
                            if ae.cadr(outputArray[i]) == ae.cadr(singleTestmodeList) and (ae.caddr(outputArray[i]) == ae.caddr(singleTestmodeList) or ae.caddr(singleTestmodeList) == 'ERROR5'):
                                testmodeInfoList = ae.rplaca(testmodeInfoTable[MACode][i], ae.append1(ae.car(singleTestmodeList), str(cv.cellName)))
                            else:
                                testmodeInfoList = [ae.append1(ae.car(singleTestmodeList), str(cv.cellName)),ae.cadr(outputArray[i]),"ERROR1"]
                                OUTP1.write(f"[ERROR1] same Latch with different testmode: cell : {cv.libName} {ae.append1(ae.car(singleTestmodeList), str(cv.cellName))} testmode: {ae.caddr(outputArray[i])} <--> {ae.caddr(singleTestmodeList)} MACode: {MACode}\n" )
                                # ;; if same MA address with different testmode
                            outputList.append(testmodeInfoList[::])
                        else:
                            if ae.caddr(outputArray[i]).upper() in [x.upper() for x in MAInfoTable.keys()]:
                            # if ae.caddr(outputArray[i]) in MAInfoTable:
                                MAInfo = ae.car(MAInfoTable[ae.caddr(outputArray[i]).upper()])
                                if MAInfo != MACode:
                                    error2Address = ae.car(MAInfoTable[ae.caddr(outputArray[i]).upper()])
                                    error2Lib     = ciUtilsMakeUnique(append1(ae.car(ae.car(testmodeInfoTable[error2Address])), str(cv.cellName)))
                                    testmodeInfoList = [error2Lib[::], ae.cadr(outputArray[i]),"ERROR2"]

                                    for jj in range(0,length(testmodeInfoTable[MAInfo])):
                                        if testmodeInfoTable[MAInfo][jj][1] == ae.cadr(MAInfoTable[ae.caddr(outputArray[i]).upper()]):
                                          ii = jj
                                    testmodeInfoTable[MAInfo][ii][0] = error2Lib[::]
                                    testmodeInfoTable[MAInfo][ii][2] = "ERROR2"
                                    # OUTP1.write(f"[ERROR2] same testmode with different MA address: cell : {ae.car(singleTestmodeList)} testmode: {ae.caddr(outputArray[i])} MA address: {MAInfo} <--> {MACode}\n")
                                    OUTP1.write(f'[ERROR2] same testmode with different MA address: cell : {error2Lib} '
                                             f'testmode: {ae.caddr(outputArray[i])} MA address: {MAInfo} <--> {MACode}\n')
                                    outputList = ae.append1(outputList,testmodeInfoList)
                            else:
                                MAInfoTable[ae.caddr(outputArray[i]).upper()]= [MACode, ae.cadr(outputArray[i])]
                                outputList = ae.append1(outputList,outputArray[i])
                                # ;; if same testmode with different MA address
                            # ;; if same instance in differnent CM block
                        # ;;if same instance in differnent CM block
                    testmodeInfoTable[MACode] = outputList[::]
                elif MACode in MACodeList:
                    testmodeInfoList_new = []
                    #print(MACode)
                    #print(cv.cellName)
                    #df = pd.DataFrame(testmodeInfoTable)
                    #print(df)
                    #print(testmodeInfoTable.keys)
                    #print(testmodeInfoTable.items)
                    #for key,value in testmodeInfoTable:
                    #  print(key,value)
                    #print(testmodeInfoTable)
                    for outputList2 in testmodeInfoTable[MACode]:
                        outputList2[2] = 'ERROR5'
                    OUTP1.write(f'[ERROR5] same MA in a block {cv.cellName}/{LatchInst.name}, MA Address: {MACode}\n')
                # ;; foreach LatchInstList
            # ;;foreach LatchTable

    return testmodeInfoTable

def CXMTseGetAllCm2Info_ByCell(cv, excluded_nets=None):
    Cm2InstInfoList = []
    for inst in cv.instances:
        if inst:
            Cm2InstInfoList_tmp = []
            count = 0
            skip_inst = False
            for term in inst.instTerms:
                if term.net:
                    if excluded_nets and str(term.net.name) in excluded_nets:
                        skip_inst = True
                        break
                    Cm2InstInfoList_tmp.append(str(term.net.name))
                    if re.search("cm2",str(term.net.name)):
                        count = 1
            if skip_inst:
                continue
            if count == 1:
                Cm2InstInfoList.append(Cm2InstInfoList_tmp)
    Cm2InfoList     = []
    Cm2InfoList_pre = []
    cm2ComPat = re.compile("(.*)_[I|i]nt([^a-z]*$)")
    if len(Cm2InstInfoList) >= 1:
        for cm2List in Cm2InstInfoList:
            tmpPat = [x for x in cm2List if re.search(r'cm2', x)]
            if tmpPat:
                Cm2InfoList_pre.append(tmpPat[0])
            Cm2InfoList_pre.sort()

    if len(Cm2InfoList_pre) >= 1:
        for net in Cm2InfoList_pre:
            if re.search("cm2", net):
                cm2Name = net
                if re.search(cm2ComPat,cm2Name):
                    cm2Name = re.sub(cm2ComPat,"\\1\\2",cm2Name)
                cm2Name_exp = ae.etExpandName(cm2Name,True,"net")
                Cm2InfoList.extend(cm2Name_exp)
    Cm2InfoList = sorted(ciUtilsMakeUnique(Cm2InfoList))
    return Cm2InfoList


def CXMTseConvertStrOutp(MAadrNum, MAadrLen):
    MAadrNum = upperCase(MAadrNum)
    emptyStr = ""
    if len(MAadrNum) < MAadrLen:
        for i in range(1, (MAadrLen + 1) - len(MAadrNum)):
            emptyStr = ae.strcat("0",emptyStr)
    return ae.strcat(emptyStr, MAadrNum)

def CXMTseMergeMoudleName(testmodeInfoTable):
    for MA in testmodeInfoTable.keys():
        tmList = []
        for tmInfo in testmodeInfoTable[MA]:
            if not re.search(r'ERROR', tmInfo[2]):
                tmList.append(tmInfo[2])
        tmInfoList = []
        tmInfoTmp  = []
        for tmInfo in testmodeInfoTable[MA]:
            tmpInfoList   = tmInfo[::]
            findModulePat = re.findall(r'(.*)<[0-9]*>', tmInfo[2])
            if not re.search(r'_sp_', tmInfo[2]) and findModulePat:   # info: the order of judgment can't be changed
                tm = findModulePat[0]
            else:
                tm = tmInfo[2]
            if tm not in tmInfoList and not re.search(r'ERROR', tm):
                tmpMatchList = [x for x in tmList if re.search(rf'{tm}', x)]
                if len(tmpMatchList) == 1:
                    tmpInfoList.extend(tmpMatchList)
                else:
                    tmInfoList.append(tm)
                    tmpInfoList.extend([tm])
            else:
                tmpInfoList.extend([''])
            tmInfoTmp.append(tmpInfoList[::])
        testmodeInfoTable[MA] = tmInfoTmp[::]

def CXMTseCMBlockAddHierPath(csv_path, config_path, step2_File):
    block_to_paths = defaultdict(list)
    if config_path and os.path.isfile(config_path):
        with open(config_path) as config_file:
            for line in (line.strip() for line in config_file if line.strip() and not line.startswith('CM Block')):
                if ' ' in line and (parts := line.split(None, 1)):
                    block_name, hierarchy_path = parts  # block_name = parts[0],hierarchy_path = parts[1]
                    block_to_paths[block_name].append(hierarchy_path.strip())
    block_cm_name_mapping = {}
    with open(csv_path) as csv_file:
        for row in DictReader(csv_file):
            if 'Spare' in (category := row.get('Category', '').strip()):
                continue
            if (cm_name := row.get('CM Name', '').strip()) and cm_name !='NA' and 'ERROR' not in cm_name:
                for current_block in (block.strip() for block in row.get('CM Block', '').split(';') if block.strip()):
                    name_list = block_cm_name_mapping.setdefault(current_block, [])
                    if cm_name not in name_list:
                        name_list.append(cm_name)
    with open(step2_File, 'w') as output_file:
        if config_path:
            output_file.write("CM Block Full Path\n")
        for current_block, cm_names in block_cm_name_mapping.items():
            for path in block_to_paths.get(current_block, ['']):
                prefix = f"{path}." if path else ""
                for cm_name in cm_names:
                    output_file.write(f"{current_block} {prefix}{cm_name}\n")

def CXMTseGetCmModuleAndPort(step2_File,step3_File):
    result_table = {}
    netNameList = []
    with open(step2_File, 'r') as IN:
        for line in IN:
            #zixu
            if not (line := line.strip()) or ' ' not in line or re.match(r'^CM\s+Block', line, re.I): continue
            if (full_path := line.split(None, 1)[1].strip()) and (elements := full_path.split('.')) and (prefix := elements[:-1]):
                # Build the instance prefix: replace '.X' with '/' and remove a leading 'X'
                inst_prefix = re.sub(r'\.X', '/', re.sub(r'^X', '', '.'.join(prefix)))
                # Final path = instance hierarchy (slash separated) + '/' + net name
                path = f"{inst_prefix}/{elements[-1]}"
            else:
                # Fallback for rare lines without a dot (e.g. top-level net names)
                # Treat full_path as the complete net path (add leading '/' if needed)
                if full_path:
                    path = f"/{full_path}" if not full_path.startswith('/') else full_path
                else:
                    continue          # Skip lines that do not contain a valid path

            # Add the path to the list only once
            if path not in netNameList:
                netNameList.append(path)  
            #zixu

    projectName = os.getenv('PROJ_NAME', '')
    versionName = os.getenv('Ver', '')
    lvsShortCellList = []
    lvsShortCellList_default = [
                    ['TECHLIB', 'parasiticRC1'], ['TECHLIB', 'parasiticRC2'], ['TECHLIB', 'parasiticRCC1'],
                    ['TECHLIB', 'parasiticRCC2'],
                ]
    if os.path.isfile(f'/proj/{projectName}/{versionName}/setup/aether.rc.cdl'):
        hnlUserShortCVLine = None
        with open(f'/proj/{projectName}/{versionName}/setup/aether.rc.cdl', 'r') as fp:
            for line in fp:
                if re.search(r'emp-short-cell-list', line.strip()):
                    hnlUserShortCVLine = line.strip()
                    break
        if hnlUserShortCVLine:
            hnlUserShortCVLine = re.sub(r'emp-short-cell-list', '', hnlUserShortCVLine)
            hnlUserShortCVList = [x for x in re.split(r'[ \t=,]', hnlUserShortCVLine.replace('"', '')) if x]
            if hnlUserShortCVList:
                lvsShortCellList = [[x for x in libCell.split('/') if x] for libCell in hnlUserShortCVList]
            else:
                lvsShortCellList = lvsShortCellList_default
        else:
            lvsShortCellList = lvsShortCellList_default
    else:
        lvsShortCellList = lvsShortCellList_default
    lvsShortCellSet = {(lib, cell) for lib, cell in lvsShortCellList}


    topCvId = ae.dbOpenCV("ddgoa_cmos_top", "LP5TOP", "schematic", 'r')
    if not topCvId:
        ae.etPrintf("[ERROR] Step 3: Please open the top cell before running TM Scan Table generation!\n")
        return

    num = 0
    found_int_cnt = 0
    for hierNetPath in netNameList:
        new_path = ""
        new_netName = ""
        instHierPath = ""
        #ae.aeMessage(f"[hierNetPath]: {hierNetPath}\n")  zixu
        new_path = ae.dbGetTopNetNameByHierNameEx(topCvId.libName, topCvId.cellName, topCvId.viewName, hierNetPath)
        #ae.etPrintf("[DEBUG1] Direct lookup path '%s' result length = %d\n" % (hierNetPath, len(new_path)))
        if len(new_path) == 0:
            if '/' in hierNetPath:                  
                prefix, netname = hierNetPath.rsplit('/', 1)
            else:                                       
                prefix = ''                             
                netname = hierNetPath
            found = False
            for suffix in ['_Int']:
                try_path = f"{prefix}/{netname}{suffix}" if prefix else f"{netname}{suffix}"
                res = ae.dbGetTopNetNameByHierNameEx(topCvId.libName, topCvId.cellName, topCvId.viewName, try_path)
                #ae.etPrintf("[DEBUG2] Try with suffix path '%s' result length = %d\n" % (try_path, len(res)))
                if len(res) > 0:                            
                    new_path = res                             
                    hierNetPath = try_path                      
                    found = True
                    found_int_cnt += 1
                    #ae.etPrintf("[INFO] _Int suffix matched (#%d): %s\n" % (found_int_cnt, try_path))
                    ae.etPrintf("[INFO] Find net: %s\n" %try_path)
                    break
            if not found:                               
                ae.etPrintf(f"[ERROR] Step 3: Net incorrect: {hierNetPath}\n")
                continue                                       
        else:
            new_path = ae.aeGetAdjustedPath(ae.aeGetActiveDa(), hierNetPath)
            #ae.aeMessage(f"[Info trace path]:{hierNetPath} {new_path}\n")  zixu
            new_netName = car(reverse(ae.etParseString(new_path, "/")))
            needUpdateHierInstPath = reverse(cdr(reverse(ae.etParseString(new_path, "/"))))
            if needUpdateHierInstPath:
                #instHierPath = ae.buildString(needUpdateHierInstPath, "/")
                instHierPath = ae.buildString([str(x) for x in needUpdateHierInstPath], "/")
            else:
                instHierPath = ""
            cvId_sub = topCvId

            CM_HierPath = 'TOP.Chip.I_C_Top'
            while needUpdateHierInstPath:
                inst = car(needUpdateHierInstPath)
                #print(f"[INFO-1]needUpdateHierInstPath is {needUpdateHierInstPath}")
                CM_HierPath = f"{CM_HierPath}.{inst}"
                needUpdateHierInstPath.remove(inst)
                #print(f"[INFO-1]needUpdateHierInstPath is {needUpdateHierInstPath}")
                instId = ae.dbFindInst(cvId_sub, inst)
                if instId:
                    #print(f"[INFO-1]instId is {instId.cellName}")
                    cvId_sub = ae.dbGetAnyInstSwitchMaster(instId, "schematic")
                    #print(f"[INFO-1]cvId_sub is {cvId_sub.cellName}")
                    #if cvId_sub:
                        #needUpdateHierInstPath.remove(inst)
                    #    needUpdateHierInstPath = cdr(needUpdateHierInstPath)

            up_instName = ""
            checkNetTraceUpFalg = 1
            #currentPortNetList = deque([])
            new_portNameList = set()
            for portName in [x.name for x in cvId_sub.terminals]:
                for port in ae.dbGetMemName(portName):
                    if port not in new_portNameList:
                        new_portNameList.add(port)
            if num not in result_table:
                result_table[num] = {}
            traceNetRecord_table = {}
            traceCellTerminalRecord_table = {}
            CXMTseGetCmModuleAndPort_loop(topCvId, hierNetPath, cvId_sub, new_netName, up_instName, result_table, instHierPath, checkNetTraceUpFalg, num, traceNetRecord_table,lvsShortCellList, traceCellTerminalRecord_table,CM_HierPath)
            if hierNetPath not in result_table[num] or not result_table[num][hierNetPath]:
                result_table[num][hierNetPath] = ["notFound"]
            num += 1
    if result_table:
        #print(f"result_table is {result_table}")
        with open(step3_File, "w") as OUT:
            OUT.write(f"##Net Module Module_Port\n")
            for num in sorted(result_table.keys()):
                for net in result_table[num]:
                    moduleList = deque([])
                    portList = deque([])
                    pathList = deque([])
                    netPathList = deque([])
                    resultInfoList = result_table[num][net]
                    if resultInfoList == ["notFound"]:
                        OUT.write(f"{net} {ae.buildString(resultInfoList, ' ')}\n")
                    else:
                        newresultInfoList = deque([])
                        for resultInfo in resultInfoList:
                            if resultInfo not in newresultInfoList:
                                newresultInfoList.appendleft(resultInfo)
                        for resultInfo in newresultInfoList:
                            moduleList.appendleft(f"{car(resultInfo.split())}")
                            portList.appendleft(f"{cadr(resultInfo.split())}")
                            pathList.appendleft(f"{resultInfo.split()[-1]}")
                            if len(portList) > len(pathList):
                              portList.remove(portList[0])
                            netPathList = [f"{x}.{y}" for x,y in zip(pathList,portList)]
                        #OUT.write(f"{net} {ae.buildString(moduleList, '/')} {ae.buildString(portList, '/')} {ae.buildString(pathList, '/')}\n")
                        OUT.write(f"{net} {ae.buildString(moduleList, '/')} {ae.buildString(portList, '/')} {ae.buildString(netPathList, '/')}\n")
    else:
        ae.etPrintf("[ERROR] Step 3: No information was retrieved. Please contact CAD.\n")
        return

        
#cxmt_GenerateTMScanTable_CB = cxmt_GenerateTMScanTable_CB_Func()  invild


def CXMTseConvertTMScanRptToCsv(report_path, output_path=None):
    """
    Process the generated TMScanTable.rpt file to produce a cleaned CSV.
    Steps:
      1. Remove lines where Module is 'notFound'.
      2. For nets with <digit>, keep only the line with the largest digit group.
      3. Strip the hierarchical prefix from the Net column.
      4. Replace all <n> with <n:0> in Net and Module_Port columns.
      5. Write a comma-separated CSV with header; default name: tmscan_MMDD.csv.
    """
    # ---- read all lines, skip empty ----
    with open(report_path) as f:
        raw_lines = [line.strip() for line in f if line.strip()]

    # ---- extract header line (first one starting with ##) ----
    #header_line = next((l for l in raw_lines if l.startswith('##')), None)
    #header = header_line.lstrip('#').split() if header_line else [f"CM\tmodule name\tcm name in module top\tdefault value\tcm path\tenable cm"]
    header = ["CM", "module name", "cm name in module top", "default value", "cm path", "enable cm"]
    # ---- build ordered list of (index, net, module, module_port) for valid lines ----
    # use walrus operator to keep it compact
    ordered = []                #  [idx, net, mod, port]
    notfound_lines = []     
    for idx, line in enumerate(raw_lines):  
        if line.startswith('#'):               
            continue
        #parts = line.split(None, 2)
        parts = line.split(None, 3)
        if len(parts) >= 3 and parts[1] != "notFound":
            net = parts[0]           
            mod = parts[1]           
            port = re.sub(r'[\[\]\'",]', '', parts[2])
            #path = parts[3] if len(parts) > 3 else '' 
            path = re.sub(r'[\[\]\'",]', '', parts[3]) if len(parts) > 3 else ''
            ordered.append((idx, net, mod, port, path))
        elif "notFound" in line:
            notfound_lines.append(line)
    # NOTE: recovered portion (lines 1-775 of 1158); tail of CXMTseConvertTMScanRptToCsv
    # and any subsequent helpers were not read by the agent in the source trace.
