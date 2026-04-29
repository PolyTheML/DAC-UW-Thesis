# Poll Render backend until new routes are live
$uri = "https://dac-healthprice-api.onrender.com/api/v1/rl/algorithms"
while ($true) {
    try {
        $r = Invoke-RestMethod -Uri $uri -Method GET -TimeoutSec 15
        Write-Host "BACKEND IS LIVE!" -ForegroundColor Green
        Write-Host ($r | ConvertTo-Json -Depth 3)
        break
    } catch {
        Write-Host "$(Get-Date -Format HH:mm:ss) — Backend not ready yet (404 expected while deploying)..." -ForegroundColor DarkGray
        Start-Sleep -Seconds 30
    }
}
