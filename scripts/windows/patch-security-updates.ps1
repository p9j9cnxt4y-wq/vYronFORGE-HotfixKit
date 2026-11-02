[CmdletBinding()]
param(
  [ValidateSet('Audit','Apply')][string]$Mode='Audit'
)
$ErrorActionPreference='Stop'

function Is-Admin {
  $id=[Security.Principal.WindowsIdentity]::GetCurrent()
  $p=New-Object Security.Principal.WindowsPrincipal($id)
  return $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if ($Mode -eq 'Apply' -and -not (Is-Admin)) { throw 'VYF_DENY_ADMIN_REQUIRED' }

$session=New-Object -ComObject Microsoft.Update.Session
$searcher=$session.CreateUpdateSearcher()
$result=$searcher.Search("IsInstalled=0 and Type='Software' and IsHidden=0")
$updates=New-Object -ComObject Microsoft.Update.UpdateColl
$summary=@()
for($i=0;$i -lt $result.Updates.Count;$i++){
  $u=$result.Updates.Item($i)
  $security = ($u.MsrcSeverity -in @('Critical','Important')) -or ($u.Title -match 'Security Update|Sicherheitsupdate')
  if($security){
    [void]$updates.Add($u)
    $summary += [pscustomobject]@{ Title=$u.Title; Severity=$u.MsrcSeverity; Reboot=$u.RebootRequired }
  }
}
$summary | ConvertTo-Json -Depth 4
if($Mode -eq 'Audit'){ exit 0 }
if($updates.Count -eq 0){ Write-Host 'VYF_PASS_NO_PENDING_SECURITY_UPDATES'; exit 0 }
$downloader=$session.CreateUpdateDownloader(); $downloader.Updates=$updates
$d=$downloader.Download()
if($d.ResultCode -notin 2,3){ throw "VYF_DENY_DOWNLOAD_RESULT_$($d.ResultCode)" }
$installer=$session.CreateUpdateInstaller(); $installer.Updates=$updates
$r=$installer.Install()
Write-Host ("VYF_INSTALL_RESULT={0};REBOOT_REQUIRED={1}" -f $r.ResultCode,$r.RebootRequired)
if($r.ResultCode -notin 2,3){ exit 2 }
