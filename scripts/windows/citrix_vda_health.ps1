[CmdletBinding()]
param([int]$LookbackHours = 6)
$ErrorActionPreference='Stop'
$since=(Get-Date).AddHours(-1 * [Math]::Abs($LookbackHours))
$term=Get-Service -Name TermService -ErrorAction SilentlyContinue
if(-not $term){
  [pscustomobject]@{ Status='NOT_APPLICABLE'; Reason='TermService not found' } | ConvertTo-Json
  exit 0
}
$bad20498 = @(Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-TerminalServices-RemoteConnectionManager/Operational'; Id=20498; StartTime=$since} -ErrorAction SilentlyContinue).Count
$bad6005 = @(Get-WinEvent -FilterHashtable @{LogName='Application'; Id=6005; StartTime=$since} -ErrorAction SilentlyContinue | Where-Object { $_.ProviderName -match 'Winlogon' -or $_.Message -match 'SessionEnv' }).Count
$unhealthy = ($term.Status -ne 'Running') -or ($bad20498 -gt 0) -or ($bad6005 -gt 0)
[pscustomobject]@{
  Status = $(if($unhealthy){'UNHEALTHY'}else{'PASS'})
  TermService = [string]$term.Status
  Event20498 = $bad20498
  Event6005 = $bad6005
  WindowHours = $LookbackHours
} | ConvertTo-Json
if($unhealthy){ exit 2 }
