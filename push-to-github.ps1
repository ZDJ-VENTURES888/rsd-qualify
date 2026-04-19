# RSD Qualify - Push to GitHub
# Run from inside the qualify-node folder

Write-Host ""
Write-Host "RSD Qualify - Push to GitHub" -ForegroundColor Yellow
Write-Host "=============================" -ForegroundColor Yellow
Write-Host ""

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir
Write-Host "Working directory: $scriptDir" -ForegroundColor Cyan

# Check git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Git not found. Install from https://git-scm.com" -ForegroundColor Red
    exit 1
}

# Check gh CLI
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: GitHub CLI not found. Install from https://cli.github.com" -ForegroundColor Red
    exit 1
}

# Init git if needed
if (-not (Test-Path ".git")) {
    Write-Host "Initializing git repo..." -ForegroundColor Cyan
    git init
    git branch -M main
    git config user.email "communications@zdj-ventures.com"
    git config user.name "Zackary D. Jackson"
}

# Stage and commit
Write-Host "Staging files..." -ForegroundColor Cyan
git add -A

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
git commit -m "init: RSD qualify subdomain - qualify.rsddirect.com $timestamp" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Nothing new to commit - pushing existing." -ForegroundColor DarkGray
}

# Check remote
$remoteExists = git remote get-url origin 2>$null
if (-not $remoteExists) {
    Write-Host ""
    Write-Host "Creating GitHub repo: ZDJ-VENTURES888/rsd-qualify..." -ForegroundColor Cyan
    gh repo create ZDJ-VENTURES888/rsd-qualify --public --source=. --push
    Write-Host ""
    Write-Host "Repo created and pushed!" -ForegroundColor Green
} else {
    Write-Host "Remote: $remoteExists" -ForegroundColor Cyan
    Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
    git push -u origin main
}

Write-Host ""
Write-Host "PUSHED TO GITHUB SUCCESSFULLY" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT - Deploy on Vercel:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. Go to: https://vercel.com/new" -ForegroundColor White
Write-Host "  2. Click: Import Git Repository" -ForegroundColor White
Write-Host "  3. Select: ZDJ-VENTURES888/rsd-qualify" -ForegroundColor White
Write-Host "  4. Framework Preset: Other" -ForegroundColor White
Write-Host "  5. Click Deploy" -ForegroundColor White
Write-Host ""
Write-Host "  After deploy - add Environment Variables in Vercel:" -ForegroundColor Yellow
Write-Host "  Settings > Environment Variables > Add each one:" -ForegroundColor White
Write-Host "    GHL_WEBHOOK_URL" -ForegroundColor DarkGray
Write-Host "    GOOGLE_CLIENT_EMAIL" -ForegroundColor DarkGray
Write-Host "    GOOGLE_PRIVATE_KEY" -ForegroundColor DarkGray
Write-Host "    GOOGLE_DRIVE_PARENT_FOLDER_ID" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  After deploy - add subdomain in Vercel:" -ForegroundColor Yellow
Write-Host "  Settings > Domains > Add: qualify.rsddirect.com" -ForegroundColor White
Write-Host ""
Write-Host "  In your DNS (Hostinger or wherever rsddirect.com is hosted):" -ForegroundColor Yellow
Write-Host "  Type: CNAME" -ForegroundColor White
Write-Host "  Name: qualify" -ForegroundColor White
Write-Host "  Value: cname.vercel-dns.com" -ForegroundColor White
Write-Host ""
