# 00_setup_redis_windows.ps1
# Production-grade Redis setup on Windows using Memurai

$ErrorActionPreference = "Stop"

$installerUrl = "https://downloads.memurai.com/latest/memurai.msi"
$installerPath = "$env:TEMP\memurai.msi"
$serviceName = "Memurai"

Write-Host "`n📥 Downloading Memurai installer..."
Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath

Write-Host "📦 Attempting silent install..."
Start-Process "msiexec.exe" -ArgumentList "/i `"$installerPath`" /quiet /norestart" -Wait

Start-Sleep -Seconds 3
$service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue

if (-not $service) {
    Write-Host "⚠️ Silent install might have failed. Trying interactive install..."
    Start-Process "msiexec.exe" -ArgumentList "/i `"$installerPath`"" -Wait
    Start-Sleep -Seconds 3
    $service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
}

if ($service) {
    Write-Host "✅ Memurai service found. Starting and enabling on boot..."
    Start-Service $serviceName
    Set-Service -Name $serviceName -StartupType Automatic
    Write-Host "🟢 Status: $((Get-Service $serviceName).Status)"
    Write-Host "📄 Logs: C:\Program Files\Memurai\memurai.log"
    Write-Host "⚙️ Config: C:\Program Files\Memurai\memurai.conf"
    Write-Host "🔧 CLI: Run `C:\Program Files\Memurai\redis-cli.exe ping`"
} else {
    Write-Host "❌ Memurai installation failed. Please try running the MSI manually: $installerPath"
}
