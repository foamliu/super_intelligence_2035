#!/usr/bin/env python3
"""从 /apps/imctf/runset/calibre 下查找 runset 版本文件夹。面向对象设计。"""
import os, sys


class FileUtils:
    @staticmethod
    def isDir(p):
        try:
            return os.path.isdir(p)
        except OSError:
            return False

    @staticmethod
    def hasRule(p):
        try:
            for e in os.listdir(p):
                if e.endswith('.rule') and (os.path.isfile(os.path.join(p,e)) or os.path.islink(os.path.join(p,e))):
                    return True
        except OSError: pass
        return False

    @staticmethod
    def listSubdirs(p, skip=None):
        if skip is None:
            skip = {"common","runset"}

        r=[]
        try:
            for e in sorted(os.listdir(p)):
                if e.startswith('.'):
                    continue
                if e.lower() in skip:
                    continue
                if FileUtils.isDir(os.path.join(p,e)):
                    r.append(e)
        except OSError: pass
        return r


class VersionScanner:
    def __init__(self, baseDir, maxDepth=7):
        self.baseDir = baseDir
        self.maxDepth = maxDepth
        self.releaseVersions = []
        self.betaVersions = []

    def appendVersionDir(self,versionList:list,versionDir:str):
        if "LDDB" in versionDir:

        versionList.append(versionDir)


    def scan(self):
        if not FileUtils.isDir(self.baseDir):
            print(f"[error]: {self.baseDir} not exists"); sys.exit(1)
        for project in sorted(os.listdir(self.baseDir)):
            if project.startswith('.'):
                continue

            pp = os.path.join(self.baseDir, project)
            if not FileUtils.isDir(pp):
                continue
            self._scanProject(project, pp)

        self._printSummary()

        return self.releaseVersions, self.betaVersions

    def _scanProject(self, projectName, projectPath):
        for item in FileUtils.listSubdirs(projectPath):
            ip = os.path.join(projectPath, item)
            il = item.lower()

            if il == "runset":
                self._collectFromRunset(ip, self.releaseVersions, f"{projectName}/runset")
            elif il == "frozen":
                self._collectFromFrozen(ip, self.betaVersions, f"{projectName}/frozen")
            elif il in ("current", "data", "git_repo"):
                self._collectFromGeneral(ip, self.releaseVersions, f"{projectName}/{item}")
            else:
                self._collectFromNested(ip, self.releaseVersions, f"{projectName}/{item}")

    def _collectFromRunset(self, path, versionList, prefix, depth=0):
        if depth >= self.maxDepth:
            return

        for sub in FileUtils.listSubdirs(path):
            sp = os.path.join(path, sub)
            if FileUtils.hasRule(sp):
                versionList.append(f"{prefix}/{sub}")
            else:
                self._collectFromRunset(sp, versionList, f"{prefix}/{sub}", depth + 1)

    def _collectFromFrozen(self, path, versionList, prefix, depth=0):
        if depth >= self.maxDepth: return
        for sub in FileUtils.listSubdirs(path):
            sp = os.path.join(path, sub)
            rs = [s for s in FileUtils.listSubdirs(sp) if s.lower() == "runset"]
            if rs:
                rp = os.path.join(sp, "runset")
                if FileUtils.isDir(rp):
                    self._collectFromRunset(rp, versionList, f"{prefix}/{sub}/runset")
            elif FileUtils.hasRule(sp):
                versionList.append(f"{prefix}/{sub}")
            else:
                self._collectFromFrozen(sp, versionList, f"{prefix}/{sub}", depth + 1)

    def _collectFromGeneral(self, path, versionList, prefix, depth=0):
        if depth >= self.maxDepth:
            return

        for sub in FileUtils.listSubdirs(path):
            sp = os.path.join(path, sub)
            if FileUtils.hasRule(sp):
                versionList.append(f"{prefix}/{sub}")
            else:
                self._collectFromGeneral(sp, versionList, f"{prefix}/{sub}", depth + 1)

    def _collectFromNested(self, path, versionList, prefix, depth=0):
        if depth >= self.maxDepth: return
        for sub in FileUtils.listSubdirs(path):
            sp = os.path.join(path, sub); sl = sub.lower()
            if sl in ("current", "data", "git_repo"):
                self._collectFromGeneral(sp, versionList, f"{prefix}/{sub}")
            elif sl == "frozen":
                self._collectFromFrozen(sp, versionList, f"{prefix}/{sub}")
            elif sl == "runset":
                self._collectFromRunset(sp, versionList, f"{prefix}/{sub}")
            elif FileUtils.hasRule(sp):
                versionList.append(f"{prefix}/{sub}")
            else:
                self._collectFromNested(sp, versionList, f"{prefix}/{sub}", depth + 1)

    def _printSummary(self):
        print("=" * 70); print("结果汇总"); print("=" * 70)
        print("\n【正式版版本 (release)】")
        if self.releaseVersions:
            for v in sorted(set(self.releaseVersions)): print(f"  {v}")
        else:
            print("  (无)")
        print("\n【测试版版本 (beta/frozen)】")
        if self.betaVersions:
            for v in sorted(set(self.betaVersions)): print(f"  {v}")
        else:
            print("  (无)")


class RunsetScanner(VersionScanner):
    def __init__(self):
        super().__init__(baseDir="/apps/imctf/runset/calibre", maxDepth=7)


class TechlibScanner(VersionScanner):
    def __init__(self, baseDir, maxDepth=7):
        super().__init__(baseDir=baseDir, maxDepth=maxDepth)


def main():
    RunsetScanner().scan()


if __name__ == "__main__":
    main()
