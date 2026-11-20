# migrate_resume_paths.ps1
# 用途：把旧「日期子目录」结构的简历迁成「扁平存放 + 文件名前缀日期」结构
#   旧:  简历\<社招|实习生>\<YYYY-MM-DD>\<原名>.pdf
#   新:  简历\<社招|实习生>\<YYYY_MM_DD>_<原名>.pdf
# 依据：刘杨 2026-09-27 指示（日期子目录不方便，日期改由文件名体现）
# 状态：已于 2026-09-27 执行一次（社招 14 份 + 实习生 3 份 = 17 份，字节数均未变）；脚本保留以便复现
# 用法：powershell -File migrate_resume_paths.ps1            # 真跑
#       powershell -File migrate_resume_paths.ps1 -WhatIfOnly  # 只看映射不落盘
param(
  [string]$Root = 'C:\Users\liuyu\recruit\简历',
  [switch]$WhatIfOnly
)

$report = @()
foreach ($cat in @('社招', '实习生')) {
  $catPath = Join-Path $Root $cat
  if (-not (Test-Path $catPath)) { continue }
  Get-ChildItem $catPath -Directory | ForEach-Object {
    $prefix = ($_.Name -replace '-', '_')      # 2026-09-19 -> 2026_09_19
    $dir = $_.FullName
    Get-ChildItem $dir -File | ForEach-Object {
      $newName = $prefix + '_' + $_.Name
      $dest = Join-Path $catPath $newName
      if ($WhatIfOnly) {
        $report += "$($_.FullName)  ->  $dest"
      } else {
        Move-Item -LiteralPath $_.FullName -Destination $dest -Force
        $report += "$cat\$newName"
      }
    }
    if (-not $WhatIfOnly) { Remove-Item -LiteralPath $dir -Force }
  }
}

if ($report.Count -eq 0) { 'nothing to do (already flat)' } else { $report }
