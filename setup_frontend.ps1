# Temporarily add Node.js to PATH for this session
$env:Path = "C:\Program Files\nodejs;$env:Path"

Write-Host "Node.js version:" -ForegroundColor Green
node --version

Write-Host "`nnpm version:" -ForegroundColor Green
npm --version

Write-Host "`nCreating Vite + React + TypeScript project..." -ForegroundColor Cyan
npm create vite@latest frontend -- --template react-ts

Write-Host "`nFrontend project created successfully!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. cd frontend"
Write-Host "2. npm install"
Write-Host "3. npm run dev"

# Made with Bob
