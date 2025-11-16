# Quick Setup Script for HW5 - Map Servers Project
# This script helps you get started quickly

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "HW5 Map Servers - Quick Setup" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found! Please install Python 3.9 or higher." -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "`nInstalling required packages..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ All packages installed successfully!" -ForegroundColor Green
} else {
    Write-Host "✗ Package installation failed. Please check errors above." -ForegroundColor Red
    exit 1
}

# Check for OpenAI API key
Write-Host "`nChecking for OpenAI API key..." -ForegroundColor Yellow
if ($env:OPENAI_API_KEY) {
    Write-Host "✓ OpenAI API key found in environment" -ForegroundColor Green
    $hasApiKey = $true
} elseif (Test-Path .env) {
    Write-Host "✓ .env file found (API key may be there)" -ForegroundColor Green
    $hasApiKey = $true
} else {
    Write-Host "⚠ No OpenAI API key detected" -ForegroundColor Yellow
    Write-Host "  You'll need an API key to run agent_demo.py" -ForegroundColor Yellow
    $hasApiKey = $false
}

# Run tests
Write-Host "`nRunning tests..." -ForegroundColor Yellow
Write-Host "(Note: Some tests may fail if external APIs are temporarily unavailable)`n" -ForegroundColor Gray

python -m pytest tests/ -v --tb=short

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✓ All tests passed!" -ForegroundColor Green
} else {
    Write-Host "`n⚠ Some tests failed (this may be normal if APIs are down)" -ForegroundColor Yellow
}

# Show next steps
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Setup Complete! Next Steps:" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Option 1: Test servers without OpenAI (no API key needed)" -ForegroundColor White
Write-Host "  python examples\interactive_demo.py`n" -ForegroundColor Gray

if ($hasApiKey) {
    Write-Host "Option 2: Run full agent demo with OpenAI" -ForegroundColor White
    Write-Host "  python agent_demo.py`n" -ForegroundColor Gray
} else {
    Write-Host "Option 2: Run full agent demo with OpenAI" -ForegroundColor White
    Write-Host "  First, set your API key:" -ForegroundColor Yellow
    Write-Host "    `$env:OPENAI_API_KEY='your-key-here'" -ForegroundColor Gray
    Write-Host "  Then run:" -ForegroundColor Yellow
    Write-Host "    python agent_demo.py`n" -ForegroundColor Gray
}

Write-Host "Option 3: Read the documentation" -ForegroundColor White
Write-Host "  README.md - Project overview and usage" -ForegroundColor Gray
Write-Host "  VIDEO_GUIDE.md - How to record your demo video" -ForegroundColor Gray
Write-Host "  SUBMISSION_CHECKLIST.md - Ensure everything is ready`n" -ForegroundColor Gray

Write-Host "========================================`n" -ForegroundColor Cyan
