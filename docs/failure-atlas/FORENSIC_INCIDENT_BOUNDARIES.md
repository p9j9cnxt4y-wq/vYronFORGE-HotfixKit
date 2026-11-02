# Incident history versus root-cause evidence

## Historical local disk and server incidents

The user reported an April 2026 local drive data-loss event and a May 2026
server failure/rebuild with missing directories. The current public package
does not include raw command transcripts, device sector evidence, backup
images or independent forensic attribution. File loss / recovery and the
existence of execution-boundary weaknesses must not be turned into an
unqualified vendor-causality statement.

## Blue screens and disk pressure

Prior review reported three Windows bugchecks `0x1000007F` / arg1 `0x8`
(double fault), alongside a separate severe shortage of free space on the
system volume. The dumps themselves are not distributed. Memory pressure,
filled system storage and kernel double faults require separate diagnostics;
none is evidence that another directly caused it.

## Vault archive metadata

An inventory of 1,749,996 archive members contained 3,123 Vault-related name
hits and no direct Vault `.csproj`/`.sln` bind. Path-name classification is
not source-content inspection and not proof of source authority. Separate
partial archive families must never be mixed or substituted.

## AngelWings OwnerBridge and VM discovery

30 C# source files in three OwnerBridge projects were bounded; a full
AngelWings C# product was NOT proven. Two local no-restore builds exited
1 with MSB5021; the initial cancellation source is unknown. VM110 service
enumeration later reportedly stopped at `SYSTEMD_UNIT_LIST ->
SECRET_BOUNDARY_STOP`. The fixture here does not read production units or
resolve that security classification.
