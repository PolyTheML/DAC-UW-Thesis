#!/usr/bin/env pwsh
$ErrorActionPreference = "Stop"

Write-Host "DAC Thesis Bandit Demo - Deployment Script" -ForegroundColor Cyan

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Node.js is required." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Building production bundle..." -ForegroundColor Cyan
npm run build

Write-Host ""
Write-Host "Deploying to Vercel..." -ForegroundColor Cyan
$env:VITE_API_URL = "https://dac-healthprice-api.onrender.com"
vercel --prod --yes

Write-Host ""
Write-Host "Deployment complete!" -ForegroundColor Green
