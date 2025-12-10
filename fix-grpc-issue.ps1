# Скрипт для решения проблемы с grpc в Azure Functions Core Tools

Write-Host "Проверка версии Azure Functions Core Tools..." -ForegroundColor Cyan
$funcVersion = func --version
Write-Host "Текущая версия: $funcVersion" -ForegroundColor Green

Write-Host "`nРекомендуемые действия:" -ForegroundColor Yellow
Write-Host "1. Обновить Azure Functions Core Tools:" -ForegroundColor White
Write-Host "   choco upgrade azure-functions-core-tools" -ForegroundColor Gray
Write-Host "`n2. Или через npm:" -ForegroundColor White
Write-Host "   npm install -g azure-functions-core-tools@latest" -ForegroundColor Gray

Write-Host "`n3. Создать local.settings.json (если еще не создан):" -ForegroundColor White
if (-not (Test-Path "local.settings.json")) {
    Copy-Item "local.settings.json.example" "local.settings.json"
    Write-Host "   Файл local.settings.json создан!" -ForegroundColor Green
} else {
    Write-Host "   Файл local.settings.json уже существует" -ForegroundColor Gray
}

Write-Host "`n4. Установить зависимости:" -ForegroundColor White
Write-Host "   Azure Functions использует системный Python, поэтому:" -ForegroundColor Yellow
Write-Host "   python -m pip install -r requirements.txt" -ForegroundColor Gray
Write-Host "`n   Или если используете виртуальное окружение:" -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "   .venv\Scripts\python.exe -m pip install -r requirements.txt" -ForegroundColor Gray
    Write-Host "   (Не забудьте активировать: .venv\Scripts\Activate.ps1)" -ForegroundColor Gray
} else {
    Write-Host "   python -m venv .venv" -ForegroundColor Gray
    Write-Host "   .venv\Scripts\python.exe -m pip install -r requirements.txt" -ForegroundColor Gray
}

Write-Host "`n5. Попробовать запустить функции:" -ForegroundColor White
Write-Host "   func start" -ForegroundColor Gray

Write-Host "`nЕсли проблема сохраняется, см. TROUBLESHOOTING.md" -ForegroundColor Yellow

