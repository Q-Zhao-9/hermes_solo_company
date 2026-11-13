# AI Solo Company Class 2 - Windows installer
# Run from Windows PowerShell. It installs WSL + Ubuntu 24.04, then installs Hermes inside Ubuntu.
[CmdletBinding()]
param(
    [switch]$SkipSetup
)

$ErrorActionPreference = "Stop"
$Distro = "Ubuntu-24.04"
$BootstrapUrl = "https://raw.githubusercontent.com/Easiio-Inc/hermes_solo_company/main/scripts/class2/install-hermes.sh"

function Step([string]$Message) {
    Write-Host "`n[Class 2] $Message" -ForegroundColor Cyan
}

function Is-Administrator {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Is-Administrator)) {
    Step "Requesting Administrator permission..."
    $arguments = @(
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-File", ('"{0}"' -f $PSCommandPath)
    )
    if ($SkipSetup) { $arguments += "-SkipSetup" }
    Start-Process powershell.exe -Verb RunAs -ArgumentList ($arguments -join " ")
    exit
}

Step "Checking Windows Subsystem for Linux"
$installedDistros = @(& wsl.exe --list --quiet 2>$null) | ForEach-Object { ($_ -replace "`0", "").Trim() } | Where-Object { $_ }

if ($installedDistros -notcontains $Distro) {
    Step "Installing WSL and Ubuntu 24.04"
    Write-Host "Windows may ask you to restart. If it does, restart and run this file again." -ForegroundColor Yellow
    & wsl.exe --install --distribution $Distro --no-launch
    if ($LASTEXITCODE -ne 0) {
        throw "WSL installation did not finish. Restart Windows, then run Install-Hermes-Windows.cmd again."
    }

    $installedDistros = @(& wsl.exe --list --quiet 2>$null) | ForEach-Object { ($_ -replace "`0", "").Trim() } | Where-Object { $_ }
    if ($installedDistros -notcontains $Distro) {
        Write-Host "Ubuntu will be ready after a Windows restart. Restart, then run this installer again." -ForegroundColor Yellow
        Read-Host "Press Enter to close"
        exit 0
    }
}

Step "Starting Ubuntu 24.04"
Write-Host "On the first launch, Ubuntu may ask you to create a Linux username and password." -ForegroundColor Yellow
Write-Host "When typing the password, the screen stays blank; this is normal." -ForegroundColor Yellow
& wsl.exe --distribution $Distro -- bash -lc "printf 'Ubuntu is ready.\n'"
if ($LASTEXITCODE -ne 0) {
    throw "Ubuntu did not start. Restart Windows and run this installer again."
}

Step "Downloading and installing the AI Solo Company edition of Hermes"
$bashArgs = if ($SkipSetup) { "--skip-setup" } else { "" }
$linuxCommand = "set -o pipefail; curl -fsSL '$BootstrapUrl' | bash -s -- $bashArgs"
& wsl.exe --distribution $Distro -- bash -lc $linuxCommand
if ($LASTEXITCODE -ne 0) {
    throw "Hermes installation failed. Review the error above, then run this installer again."
}

Step "Installation complete"
Write-Host "Open Ubuntu 24.04 from the Start menu and enter: hermes" -ForegroundColor Green
Write-Host "Then ask Hermes: Create a simple one-page website for my solo company."
Read-Host "Press Enter to close"
