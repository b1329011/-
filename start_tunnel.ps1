
# 1. Setup Ports
$BACKEND_PORT = 8088
$FRONTEND_PORT = 5173

# 2. Cleanup old logs
$BE_LOG = "backend_tunnel.log"
$FE_LOG = "frontend_tunnel.log"
if (Test-Path $BE_LOG) { Remove-Item $BE_LOG }
if (Test-Path $FE_LOG) { Remove-Item $FE_LOG }

Write-Host "🚀 Starting Backend Django..." -ForegroundColor Cyan
Start-Process python -ArgumentList "backend/run_dev_server.py" -NoNewWindow
Start-Sleep -Seconds 3

Write-Host "🌐 Starting Cloudflare Tunnel (Backend)..." -ForegroundColor Cyan
# Using 127.0.0.1 instead of localhost to avoid IPv6 issues on Windows
$process = Start-Process cloudflared -ArgumentList "tunnel --url http://127.0.0.1:$BACKEND_PORT" -RedirectStandardError $BE_LOG -NoNewWindow -PassThru

# 3. Capture Backend URL
Write-Host "⏳ Waiting for backend URL generation..." -ForegroundColor Yellow
$backend_url = ""
$retry_count = 0
while (-not $backend_url -and $retry_count -lt 30) {
    Start-Sleep -Seconds 2
    if (Test-Path $BE_LOG) {
        $content = Get-Content $BE_LOG -Raw
        if ($content -match "(https://[a-zA-Z0-9-]+\.trycloudflare\.com)") {
            $backend_url = $matches[1]
        }
    }
    $retry_count++
}

if (-not $backend_url) {
    Write-Host "❌ Failed to capture Backend URL. Please check $BE_LOG" -ForegroundColor Red
    exit
}
Write-Host "✅ Backend URL: $backend_url" -ForegroundColor Green

# 4. Update Frontend Environment Variables
Write-Host "📝 Updating frontend configuration..." -ForegroundColor Cyan
$env_content = "VITE_API_BASE_URL=$backend_url/api/"
Set-Content -Path "frontend/.env.local" -Value $env_content

# 5. Start Frontend
Write-Host "🚀 Starting Frontend Vite..." -ForegroundColor Cyan
# Force Vite to bind to 127.0.0.1 for tunnel stability
Start-Process npm.cmd -WorkingDirectory "$PSScriptRoot/frontend" -ArgumentList "run dev -- --port $FRONTEND_PORT --host 127.0.0.1" -NoNewWindow
Start-Sleep -Seconds 5

Write-Host "🌐 Starting Cloudflare Tunnel (Frontend)..." -ForegroundColor Cyan
Start-Process cloudflared -ArgumentList "tunnel --url http://127.0.0.1:$FRONTEND_PORT" -RedirectStandardError $FE_LOG -NoNewWindow

# 6. Capture Frontend URL
Write-Host "⏳ Waiting for frontend URL generation..." -ForegroundColor Yellow
$frontend_url = ""
$retry_count = 0
while (-not $frontend_url -and $retry_count -lt 30) {
    Start-Sleep -Seconds 2
    if (Test-Path $FE_LOG) {
        $content = Get-Content $FE_LOG -Raw
        if ($content -match "(https://[a-zA-Z0-9-]+\.trycloudflare\.com)") {
            $frontend_url = $matches[1]
        }
    }
    $retry_count++
}

if (-not $frontend_url) {
    Write-Host "❌ Failed to capture Frontend URL. Please check $FE_LOG" -ForegroundColor Red
    exit
}

# 7. Show QR Code and Results in a separate popup window
Write-Host "==========================================" -ForegroundColor Magenta
Write-Host "🎉 Deployment Successful!" -ForegroundColor Green
Write-Host "Backend API: $backend_url/api/"
Write-Host "Frontend URL: $frontend_url/nojo/" -ForegroundColor White
Write-Host "==========================================" -ForegroundColor Magenta
Write-Host ""
Write-Host "✨ Opening a separate window for Frontend URL & QR Code..." -ForegroundColor Cyan

$popupScript = @"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Clear-Host
Write-Host "==========================================" -ForegroundColor Magenta
Write-Host "🎉 Deployment Successful!" -ForegroundColor Green
Write-Host "Backend API: $backend_url/api/"
Write-Host "Frontend URL: $frontend_url/nojo/" -ForegroundColor White
Write-Host "==========================================" -ForegroundColor Magenta
Write-Host ""
Write-Host "📱 Scan the QR Code below with your phone:" -ForegroundColor Yellow
try {
    `$response = Invoke-WebRequest -Uri "https://qrenco.de/$frontend_url/nojo/" -UserAgent "curl/7.54.0" -UseBasicParsing -TimeoutSec 10
    if (`$response.Content) {
        Write-Host `$response.Content
    } else {
        Write-Host "QR Code service returned empty content." -ForegroundColor Gray
    }
} catch {
    Write-Host "Could not fetch QR Code from qrenco.de." -ForegroundColor Gray
    Write-Host "Please visit the URL manually: $frontend_url/nojo/" -ForegroundColor Gray
}
Write-Host ""
Write-Host "Press Enter to close this window..." -ForegroundColor Gray
Read-Host
"@

$encodedScript = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($popupScript))
Start-Process powershell.exe -ArgumentList "-NoProfile", "-ExecutionPolicy Bypass", "-EncodedCommand", $encodedScript

Write-Host ""
Write-Host "Press Ctrl+C to stop this script. Keep this main window open to keep the servers and tunnels running." -ForegroundColor Gray

# Keep script running to show logs
Get-Content $FE_LOG -Wait
