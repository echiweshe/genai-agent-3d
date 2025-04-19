# PowerShell script to run the WebSocket test

# Start the server process in test mode in the background
Write-Host "Starting server in test mode..." -ForegroundColor Green
$serverProcess = Start-Process -FilePath "python" -ArgumentList "run_server.py --test-mode" -PassThru -NoNewWindow

# Wait a bit for the server to start
Write-Host "Waiting for server to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

try {
    # Run the WebSocket test
    Write-Host "Running WebSocket test..." -ForegroundColor Green
    & python tests\manual_websocket_test.py
    
    $testResult = $LASTEXITCODE
    
    if ($testResult -eq 0) {
        Write-Host "WebSocket test completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "WebSocket test failed with exit code $testResult" -ForegroundColor Red
    }
} finally {
    # Always stop the server process
    Write-Host "Stopping server..." -ForegroundColor Yellow
    Stop-Process -Id $serverProcess.Id -Force
    Write-Host "Server stopped" -ForegroundColor Green
}
