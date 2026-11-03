[CmdletBinding()]
param([ValidateRange(1,168)][int]$LookbackHours = 6)
$ErrorActionPreference='Stop'
$since=(Get-Date).AddHours(-1 * [Math]::Abs($LookbackHours))
function Read-OptionalService($name) {
  try { Get-Service -Name $name -ErrorAction Stop }
  catch {
    if($_.FullyQualifiedErrorId -like 'NoServiceFoundForGivenName*'){ return }
    throw
  }
}
try { $broker=Read-OptionalService 'BrokerAgent'; $term=Read-OptionalService 'TermService' }
catch {
  [pscustomobject]@{Status='UNKNOWN';Reason='Required service evidence unavailable'} | ConvertTo-Json
  exit 3
}
if(-not $broker){
  [pscustomobject]@{ Status='NOT_APPLICABLE'; Reason='Citrix BrokerAgent service not found; no VDA health claim' } | ConvertTo-Json
  exit 0
}
if(-not $term){
  [pscustomobject]@{ Status='UNKNOWN'; Reason='Citrix detected but TermService not found' } | ConvertTo-Json
  exit 3
}
function Read-HealthEvents($filter) {
  try { Get-WinEvent -FilterHashtable $filter -ErrorAction Stop }
  catch {
    if($_.FullyQualifiedErrorId -like 'NoMatchingEventsFound*'){ return }
    throw
  }
}
try {
  $bad20498 = @(Read-HealthEvents @{LogName='Microsoft-Windows-TerminalServices-RemoteConnectionManager/Operational'; Id=20498; StartTime=$since}).Count
  $bad6005 = @(Read-HealthEvents @{LogName='Application'; Id=6005; StartTime=$since} | Where-Object { $_.ProviderName -match 'Winlogon' -or $_.Message -match 'SessionEnv' }).Count
} catch {
  [pscustomobject]@{Status='UNKNOWN';Reason='Required event evidence unavailable; not a healthy result'} | ConvertTo-Json
  exit 3
}
$unhealthy = ($broker.Status -ne 'Running') -or ($term.Status -ne 'Running') -or ($bad20498 -gt 0) -or ($bad6005 -gt 0)
[pscustomobject]@{
  Status = $(if($unhealthy){'UNHEALTHY'}else{'PASS'})
  TermService = [string]$term.Status
  BrokerService = [string]$broker.Status
  Event20498 = $bad20498
  Event6005 = $bad6005
  WindowHours = $LookbackHours
} | ConvertTo-Json
if($unhealthy){ exit 2 }
