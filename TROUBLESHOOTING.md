# Решение проблем

## Ошибка: cannot load library 'gobject-2.0-0'

Эта ошибка возникает при использовании WeasyPrint на Windows, так как WeasyPrint требует GTK+ библиотеки.

**Решение:** Проект уже использует `xhtml2pdf` вместо `weasyprint`, который работает на Windows без дополнительных системных зависимостей. Убедитесь, что установлены правильные зависимости:

```powershell
pip install -r requirements.txt
```

Если вы видите эту ошибку, проверьте, что в `requirements.txt` указан `xhtml2pdf`, а не `weasyprint`.

## Ошибка: ModuleNotFoundError: No module named 'xhtml2pdf'

Эта ошибка означает, что зависимости не установлены в Python, который использует Azure Functions Core Tools.

**ВАЖНО:** Azure Functions Core Tools использует системный Python, а не виртуальное окружение!

**Решение:**

1. **Деактивируйте виртуальное окружение** (если активировано):
   ```powershell
   deactivate
   ```

2. **Установите зависимости в системный Python:**
   ```powershell
   python -m pip install -r requirements.txt
   ```

3. **Проверьте установку:**
   ```powershell
   python -c "import xhtml2pdf; print('xhtml2pdf установлен!')"
   ```

4. **Проверьте, какой Python используется:**
   ```powershell
   python -c "import sys; print(sys.executable)"
   ```
   Должен быть системный Python, а не из `.venv`

5. **Запустите функции:**
   ```powershell
   func start
   ```

**Если используете виртуальное окружение:**
- Либо установите зависимости в системный Python (рекомендуется)
- Либо активируйте виртуальное окружение и запускайте `func start` из того же терминала

Подробнее см. [INSTALL.md](INSTALL.md)

## Ошибка: cannot import name 'cygrpc' from 'grpc._cython'

Эта ошибка возникает из-за конфликта версий grpc в Azure Functions Core Tools на Windows.

### Решения:

#### 1. Обновить Azure Functions Core Tools

```powershell
# Через Chocolatey
choco upgrade azure-functions-core-tools

# Или через npm
npm install -g azure-functions-core-tools@latest
```

#### 2. Указать правильный Python worker

Создайте файл `local.settings.json` (скопируйте из `local.settings.json.example`):

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsFeatureFlags": "EnableWorkerIndexing",
    "PYTHON_ENABLE_WORKER_EXTENSIONS": "1"
  }
}
```

#### 3. Использовать виртуальное окружение

Активируйте виртуальное окружение перед запуском:

```powershell
.venv\Scripts\Activate.ps1
func start
```

#### 4. Переустановить Azure Functions Core Tools

```powershell
# Удалить через Chocolatey
choco uninstall azure-functions-core-tools

# Переустановить
choco install azure-functions-core-tools
```

#### 5. Использовать Docker (альтернатива)

Если проблемы продолжаются, можно использовать Docker:

```bash
docker run -p 7071:80 -v ${PWD}:/home/site/wwwroot mcr.microsoft.com/azure-functions/python:4-python3.9
```

#### 6. Проверить версию Python

Убедитесь, что используется правильная версия Python (3.9 или 3.10):

```powershell
python --version
```

Если нужно, установите Python 3.10 и укажите его в настройках.

### Временное решение

Если ничего не помогает, можно попробовать запустить функции напрямую через Python (без Core Tools) для тестирования, но для развертывания в Azure все равно потребуется Core Tools.

## Linux Support

All functions are cross-platform and work on Ubuntu Linux. See `LINUX_SETUP.md` for detailed Linux installation instructions.

### Key differences on Linux:
- **Font paths**: Uses `/usr/share/fonts/truetype/` instead of `C:\Windows\Fonts\`
- **Playwright**: Requires system dependencies (see `LINUX_SETUP.md`)
- **Azure Functions Core Tools**: Works the same way on Linux

### Common Linux issues:

**Playwright dependencies missing:**
```bash
sudo apt-get update
sudo apt-get install -y libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2
```

**Fonts not found:**
```bash
sudo apt-get install -y fonts-dejavu-core fonts-dejavu-extra
```

