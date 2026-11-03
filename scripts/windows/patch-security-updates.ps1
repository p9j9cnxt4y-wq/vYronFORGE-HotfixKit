[CmdletBinding()]
param(
  [ValidateSet('Audit','Apply')][string]$Mode='Audit',
  [switch]$OnlineScan
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
$searcher.Online=($Mode -eq 'Apply' -or $OnlineScan.IsPresent)
$result=$searcher.Search("IsInstalled=0 and Type='Software' and IsHidden=0")
if ($result.ResultCode -ne 2) {
  [pscustomobject]@{Status='UNKNOWN_SEARCH_INCOMPLETE'; ResultCode=[int]$result.ResultCode; Online=[bool]$searcher.Online} | ConvertTo-Json
  exit 2
}
$updates=New-Object -ComObject Microsoft.Update.UpdateColl
$summary=@()
for($i=0;$i -lt $result.Updates.Count;$i++){
  $u=$result.Updates.Item($i)
  # Classification GUID is language-independent; severity also includes low/moderate fixes.
  $securityCategory = @($u.Categories | Where-Object { $_.CategoryID -eq '0FA1201D-4330-4FA8-8AE9-B877473B6441' }).Count -gt 0
  $security = $securityCategory -or ($u.MsrcSeverity -in @('Critical','Important','Moderate','Low'))
  if($security){
    [void]$updates.Add($u)
    $summary += [pscustomobject]@{ Title=$u.Title; Severity=$u.MsrcSeverity; Reboot=$u.RebootRequired }
  }
}
[pscustomobject]@{
  Status=$(if($searcher.Online){'AUDIT_ONLINE'}else{'AUDIT_OFFLINE_CACHE'})
  Coverage=$(if($searcher.Online){'CONFIGURED_UPDATE_SERVICE'}else{'CACHED_METADATA_ONLY_NOT_CURRENT_COMPLIANCE'})
  Online=[bool]$searcher.Online
  SecurityUpdateCount=$updates.Count
  Updates=@($summary)
} | ConvertTo-Json -Depth 4
if($Mode -eq 'Audit'){ exit 0 }
if($updates.Count -eq 0){ Write-Host 'VYF_PASS_NO_PENDING_SECURITY_UPDATES'; exit 0 }
$downloader=$session.CreateUpdateDownloader(); $downloader.Updates=$updates
$d=$downloader.Download()
if($d.ResultCode -ne 2){ throw "VYF_DENY_DOWNLOAD_RESULT_$($d.ResultCode)" }
$installer=$session.CreateUpdateInstaller(); $installer.Updates=$updates
$r=$installer.Install()
Write-Host ("VYF_INSTALL_RESULT={0};REBOOT_REQUIRED={1}" -f $r.ResultCode,$r.RebootRequired)
if($r.ResultCode -ne 2){ exit 2 }
