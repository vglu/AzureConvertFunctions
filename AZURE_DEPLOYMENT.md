# Инструкция по развертыванию на Azure

Пошаговая инструкция по развертыванию Azure Convert Functions в Azure.

## Содержание

1. [Предварительные требования](#предварительные-требования)
2. [Подготовка к развертыванию](#подготовка-к-развертыванию)
3. [Создание ресурсов Azure](#создание-ресурсов-azure)
4. [Развертывание через Azure CLI](#развертывание-через-azure-cli)
5. [Развертывание через VS Code](#развертывание-через-vs-code)
6. [Развертывание через Azure Portal](#развертывание-через-azure-portal)
7. [Настройка после развертывания](#настройка-после-развертывания)
8. [Проверка работы](#проверка-работы)
9. [Решение проблем](#решение-проблем)

## ⚠️ Важные примечания

1. **Azure Functions на Windows не поддерживает Python runtime.** При создании Function App обязательно указывайте `--os-type Linux` или выберите Linux в Azure Portal. Python функции работают только на Linux.

2. **Python 3.9 достиг EOL (End of Life) 31 октября 2025** и больше не поддерживается. Рекомендуется использовать Python 3.11 или 3.10. Все команды в инструкции обновлены для использования Python 3.11.

## Предварительные требования

### Необходимое ПО

1. **Azure CLI** (рекомендуется)
   ```bash
   # Установка Azure CLI
   # Windows: https://aka.ms/installazurecliwindows
   # Linux: https://aka.ms/InstallAzureCLILinux
   # macOS: brew install azure-cli
   ```

2. **Azure Functions Core Tools**
   ```bash
   # Windows (Chocolatey)
   choco install azure-functions-core-tools-4
   
   # Windows (npm)
   npm install -g azure-functions-core-tools@4 --unsafe-perm true
   
   # Linux
   curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg
   sudo mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg
   sudo sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/microsoft-ubuntu-$(lsb_release -cs)-prod $(lsb_release -cs) main" > /etc/apt/sources.list.d/dotnetdev.list'
   sudo apt-get update
   sudo apt-get install azure-functions-core-tools-4
   ```

3. **Python 3.10+** (рекомендуется 3.11)
   - Убедитесь, что Python установлен и доступен в PATH
   ```bash
   python --version
   ```
   - **Примечание**: Python 3.9 достиг EOL (End of Life) 31 октября 2025 и больше не поддерживается

4. **Git** (опционально, для версионирования)

### Необходимые учетные данные Azure

- Активная подписка Azure
- Права на создание ресурсов (Owner или Contributor)
- Учетная запись Azure (для входа)

## Подготовка к развертыванию

### Шаг 1: Вход в Azure

```bash
# Войти в Azure
az login

# Выбрать подписку (если несколько)
az account list --output table
az account set --subscription "<subscription-id>"
```

### Шаг 2: Подготовка проекта

```bash
# Перейти в директорию проекта
cd D:\Projects\AzureConvertFunctions

# Убедиться, что все зависимости установлены
python -m pip install -r requirements.txt

# Установить браузеры Playwright
playwright install chromium

# Проверить, что функции работают локально
func start
```

### Шаг 3: Проверка конфигурации

Убедитесь, что файлы настроены правильно:

- `host.json` - конфигурация хоста
- `requirements.txt` - зависимости Python
- `local.settings.json` - локальные настройки (не развертывается)

## Создание ресурсов Azure

### Вариант 1: Через Azure CLI (рекомендуется)

#### Шаг 1: Создать группу ресурсов

```bash
# Создать группу ресурсов
az group create \
  --name rg-convert-functions \
  --location eastus

# Примечание: можно использовать другой регион:
# westeurope, westus2, japaneast и т.д.
```

#### Шаг 2: Создать учетную запись хранения

```bash
# Создать storage account
az storage account create \
  --name stconvertfuncs \
  --resource-group rg-convert-functions \
  --location eastus \
  --sku Standard_LRS

# Примечание: имя должно быть уникальным в Azure (только строчные буквы и цифры)
```

#### Шаг 3: Создать Function App

**Важно:** Azure Functions на Windows не поддерживает Python runtime. Необходимо использовать Linux.

```bash
# Создать Function App на Linux
az functionapp create \
  --resource-group rg-convert-functions \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name func-convert-app \
  --storage-account stconvertfuncs \
  --os-type Linux

# Примечание: Python 3.9 достиг EOL (End of Life) 31 октября 2025.
# Рекомендуется использовать Python 3.10 или 3.11.
# Доступные версии: 3.8, 3.9, 3.10, 3.11

# Примечание: имя должно быть уникальным в Azure (только строчные буквы, цифры и дефисы)
```

**Параметры:**
- `--resource-group`: группа ресурсов
- `--consumption-plan-location`: регион для Consumption плана
- `--runtime`: python
- `--runtime-version`: 3.11 (рекомендуется) или 3.10 (Python 3.9 достиг EOL)
- `--functions-version`: 4
- `--name`: уникальное имя Function App
- `--storage-account`: имя storage account
- `--os-type Linux`: **обязательно** указывать Linux для Python

**Альтернатива: Если нужно использовать Windows**, создайте Function App через Azure Portal (см. раздел "Через Azure Portal" ниже), но рекомендуется использовать Linux для лучшей поддержки Python.

#### Шаг 4: Настроить Python

```bash
# Установить версию Python и настройки (только для Linux)
az functionapp config set \
  --name func-convert-app \
  --resource-group rg-convert-functions \
  --linux-fx-version "Python|3.11"

# Примечание: Используйте Python 3.10 или 3.11 (Python 3.9 достиг EOL)
# Доступные версии: Python|3.8, Python|3.9, Python|3.10, Python|3.11

# Включить расширения worker
az functionapp config appsettings set \
  --name func-convert-app \
  --resource-group rg-convert-functions \
  --settings \
    PYTHON_ENABLE_WORKER_EXTENSIONS=1 \
    FUNCTIONS_WORKER_RUNTIME=python

# Примечание: Если вы создали Function App на Windows по ошибке, 
# его нужно пересоздать на Linux, так как Windows не поддерживает Python runtime
```

### Вариант 2: Через Azure Portal

1. Войдите в [Azure Portal](https://portal.azure.com)

2. Создайте группу ресурсов:
   - Нажмите "Create a resource"
   - Найдите "Resource group"
   - Имя: `rg-convert-functions`
   - Регион: `East US` (или другой)

3. Создайте Storage Account:
   - В группе ресурсов нажмите "Create"
   - Найдите "Storage account"
   - Имя: `stconvertfuncs` (уникальное)
   - Регион: тот же, что и группа ресурсов
   - Performance: Standard
   - Redundancy: LRS

4. Создайте Function App:
   - В группе ресурсов нажмите "Create"
   - Найдите "Function App"
   - Настройки:
     - **Subscription**: ваша подписка
     - **Resource Group**: `rg-convert-functions`
     - **Function App name**: `func-convert-app` (уникальное)
     - **Publish**: Code
     - **Runtime stack**: Python
     - **Version**: 3.11 (рекомендуется) или 3.10 (Python 3.9 достиг EOL 31.10.2025)
     - **Region**: тот же, что и группа ресурсов
     - **Operating System**: **Linux** (обязательно для Python, Windows не поддерживает Python runtime)
     - **Plan**: Consumption (Serverless)
   - Нажмите "Review + create", затем "Create"
   
   **Важно:** Python runtime поддерживается только на Linux. Если вы выберете Windows, функция не будет работать.

## Развертывание через Azure CLI

### Шаг 1: Подготовка к развертыванию

```bash
# Убедиться, что вы в правильной директории
cd D:\Projects\AzureConvertFunctions

# Проверить, что все файлы на месте
dir
```

### Шаг 2: Развертывание

```bash
# Развернуть Function App
func azure functionapp publish func-convert-app

# Примечание: если функция не найдена, используйте полное имя:
# func azure functionapp publish func-convert-app.azurewebsites.net
```

**Процесс развертывания:**
1. Создание zip-архива с кодом
2. Загрузка в Azure
3. Установка зависимостей из `requirements.txt`
4. Активация функций

**Важно:** Развертывание может занять 5-10 минут, особенно при первой установке зависимостей.

### Шаг 3: Установка Playwright браузеров (для Linux)

Если Function App работает на Linux, нужно установить системные зависимости и браузеры Playwright.

**Способ 1: Через SSH (если включен)**

```bash
# Включить SSH в Function App
az webapp ssh \
  --name func-convert-app \
  --resource-group rg-convert-functions

# В SSH сессии:
pip install playwright
playwright install chromium
```

**Способ 2: Через Kudu Console**

1. Откройте в браузере: `https://func-convert-app.scm.azurewebsites.net`
2. Войдите с учетными данными Azure
3. Перейдите в Debug Console → CMD или PowerShell
4. Выполните:
   ```bash
   cd site\wwwroot
   pip install playwright
   playwright install chromium
   ```

**Способ 3: Через deployment script**

Создайте файл `.deployment`:
```ini
[config]
SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

И добавьте в `requirements.txt` (если нужно):
```
playwright==1.57.0
```

Затем создайте скрипт развертывания (см. раздел "Автоматическая установка браузеров" ниже).

## Развертывание через VS Code

### Предварительная настройка

1. Установите расширения VS Code:
   - Azure Functions
   - Python
   - Azure Account

2. Войдите в Azure:
   - Нажмите на иконку Azure в боковой панели
   - Нажмите "Sign in to Azure"
   - Следуйте инструкциям

### Развертывание

1. Откройте проект в VS Code:
   ```bash
   code D:\Projects\AzureConvertFunctions
   ```

2. Развертывание:
   - Нажмите на иконку Azure в боковой панели
   - Найдите "Functions"
   - Нажмите на иконку "Deploy to Function App"
   - Выберите существующий Function App или создайте новый
   - Подтвердите развертывание

3. Следите за прогрессом в Output панели

## Развертывание через Azure Portal

### Через ZIP Deploy

1. Подготовьте ZIP-архив:
   ```bash
   # Создать ZIP (исключая ненужные файлы)
   # Windows PowerShell:
   Compress-Archive -Path * -DestinationPath deploy.zip -Exclude @('*.pyc','__pycache__','.venv','*.log')
   
   # Linux/Mac:
   zip -r deploy.zip . -x "*.pyc" "__pycache__/*" ".venv/*" "*.log"
   ```

2. Развертывание:
   - Откройте Function App в Azure Portal
   - Перейдите в "Deployment Center"
   - Выберите "Local Git" или "External Git"
   - Или используйте "Advanced Tools" → "Go" → "Zip Push Deploy"

### Через GitHub Actions

1. Создайте репозиторий на GitHub
2. Загрузите код в репозиторий
3. В Azure Portal:
   - Function App → Deployment Center
   - Выберите "GitHub"
   - Авторизуйтесь и выберите репозиторий
   - Настройте branch и путь
   - Сохраните

4. При каждом push в выбранную ветку будет автоматическое развертывание

## Настройка после развертывания

### Шаг 1: Настройка Application Settings

```bash
# Установить настройки приложения
az functionapp config appsettings set \
  --name func-convert-app \
  --resource-group rg-convert-functions \
  --settings \
    FUNCTIONS_WORKER_RUNTIME=python \
    PYTHON_ENABLE_WORKER_EXTENSIONS=1 \
    WEBSITE_TIME_ZONE=UTC \
    FUNCTIONS_EXTENSION_VERSION=~4
```

### Шаг 2: Настройка таймаутов

```bash
# Установить таймаут функции (максимум 10 минут для Consumption)
az functionapp config set \
  --name func-convert-app \
  --resource-group rg-convert-functions \
  --function-timeout 600
```

### Шаг 3: Установка системных зависимостей (Linux)

Если Function App на Linux, установите зависимости для Playwright:

```bash
# Создать startup script
az functionapp config set \
  --name func-convert-app \
  --resource-group rg-convert-functions \
  --generic-configurations '{"linuxFxVersion": "Python|3.11"}'

# Установить через SSH или Kudu (см. выше)
```

### Шаг 4: Настройка аутентификации (опционально)

```bash
# Включить аутентификацию на уровне функции
# Это делается в function.json каждого endpoint:
# "authLevel": "function"
```

### Шаг 5: Включение Application Insights (рекомендуется)

```bash
# Создать Application Insights
az monitor app-insights component create \
  --app ai-convert-functions \
  --location eastus \
  --resource-group rg-convert-functions

# Получить instrumentation key
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
  --app ai-convert-functions \
  --resource-group rg-convert-functions \
  --query instrumentationKey -o tsv)

# Установить в Function App
az functionapp config appsettings set \
  --name func-convert-app \
  --resource-group rg-convert-functions \
  --settings \
    APPINSIGHTS_INSTRUMENTATIONKEY=$INSTRUMENTATION_KEY
```

## Обновление функций в Azure

После внесения изменений в код функций, их нужно обновить в Azure. Процесс обновления аналогичен первоначальному развертыванию.

### Метод 1: Через Azure CLI (рекомендуется)

```bash
# Убедитесь, что вы в директории проекта
cd D:\Projects\AzureConvertFunctions

# Обновить все функции
func azure functionapp publish func-convert-app

# Примечание: Это обновит все функции в Function App
```

**Что происходит при обновлении:**
1. Создается ZIP-архив с кодом
2. Архив загружается в Azure
3. Зависимости переустанавливаются из `requirements.txt`
4. Функции перезапускаются с новым кодом

**Время обновления:** Обычно 2-5 минут

### Метод 2: Через VS Code

1. Откройте проект в VS Code
2. Нажмите на иконку Azure в боковой панели
3. Найдите ваш Function App
4. Нажмите правой кнопкой → "Deploy to Function App"
5. Подтвердите развертывание

### Метод 3: Через Azure Portal (ZIP Deploy)

1. Подготовьте ZIP-архив:
   ```powershell
   # Windows PowerShell
   Compress-Archive -Path * -DestinationPath deploy.zip -Exclude @('*.pyc','__pycache__','.venv','*.log','.git')
   ```

2. В Azure Portal:
   - Откройте Function App
   - Перейдите в "Deployment Center"
   - Выберите "Advanced Tools" → "Go"
   - В Kudu Console: "Tools" → "Zip Push Deploy"
   - Загрузите ZIP-файл

### Метод 4: Через GitHub Actions (автоматическое)

Если настроен CI/CD через GitHub:
1. Сделайте commit изменений
2. Push в ветку, для которой настроен deployment
3. GitHub Actions автоматически развернет обновления

### Проверка обновления

```bash
# Проверить статус развертывания
az functionapp deployment list-publishing-profiles \
  --name func-convert-app \
  --resource-group rg-convert-functions

# Проверить версию функции (через логи)
az webapp log tail \
  --name func-convert-app \
  --resource-group rg-convert-functions
```

### Обновление только одной функции

Если нужно обновить только одну функцию:

```bash
# Обновить конкретную функцию (все равно обновит весь Function App)
func azure functionapp publish func-convert-app

# Или через ZIP Deploy только нужной папки:
# 1. Создайте ZIP только с нужной функцией
# 2. Загрузите через Kudu Console
```

### Обновление зависимостей

Если изменился `requirements.txt`:

```bash
# 1. Обновите requirements.txt локально
# 2. Разверните заново
func azure functionapp publish func-convert-app

# Зависимости будут переустановлены автоматически
```

### Откат к предыдущей версии

Если нужно вернуться к предыдущей версии:

**Через Azure Portal:**
1. Function App → Deployment Center
2. Deployment History
3. Выберите предыдущую версию
4. Нажмите "Redeploy"

**Через Git:**
```bash
# Откатить код к предыдущему коммиту
git checkout <previous-commit-hash>
func azure functionapp publish func-convert-app
```

### Обновление конфигурации (без изменения кода)

Если нужно изменить только настройки:

```bash
# Обновить Application Settings
az functionapp config appsettings set \
  --name func-convert-app \
  --resource-group rg-convert-functions \
  --settings \
    NEW_SETTING=value

# Обновить таймаут
az functionapp config set \
  --name func-convert-app \
  --resource-group rg-convert-functions \
  --function-timeout 600
```

### Рекомендации по обновлению

1. **Тестируйте локально** перед развертыванием:
   ```bash
   func start
   # Протестируйте функции локально
   ```

2. **Используйте версионирование** (Git tags):
   ```bash
   git tag v1.0.1
   git push origin v1.0.1
   ```

3. **Проверяйте логи** после обновления:
   ```bash
   az webapp log tail --name func-convert-app --resource-group rg-convert-functions
   ```

4. **Мониторьте метрики** после обновления:
   - Application Insights
   - Function execution metrics
   - Error rates

### Решение проблем при обновлении

**Проблема: Обновление не применяется**

```bash
# Принудительно перезапустить Function App
az functionapp restart \
  --name func-convert-app \
  --resource-group rg-convert-functions

# Проверить статус
az functionapp show \
  --name func-convert-app \
  --resource-group rg-convert-functions \
  --query state
```

**Проблема: Зависимости не обновляются**

```bash
# Проверить requirements.txt
cat requirements.txt

# Принудительно переустановить зависимости через Kudu:
# 1. Откройте Kudu Console
# 2. Перейдите в site/wwwroot
# 3. Выполните: pip install -r requirements.txt --force-reinstall
```

**Проблема: Функции не работают после обновления**

1. Проверьте логи на ошибки
2. Убедитесь, что все зависимости установлены
3. Проверьте синтаксис кода
4. Откатитесь к предыдущей версии при необходимости

## Проверка работы

### Шаг 1: Получить URL функции

```bash
# Получить URL функции
az functionapp function show \
  --name func-convert-app \
  --resource-group rg-convert-functions \
  --function-name csv2json \
  --query invokeUrlTemplate -o tsv
```

Или в Azure Portal:
- Function App → Functions → csv2json → Get function URL

### Шаг 2: Тестирование endpoints

**CSV to JSON:**
```bash
curl -X POST "https://func-convert-app.azurewebsites.net/api/csv2json?code=your-code" \
  -H "Content-Type: text/csv" \
  -d "name,age\nJohn,25\nJane,30"
```

**JSON to CSV:**
```bash
curl -X POST "https://func-convert-app.azurewebsites.net/api/json2csv?code=your-code" \
  -H "Content-Type: application/json" \
  -d '[{"name":"John","age":25},{"name":"Jane","age":30}]'
```

**URL to PDF:**
```bash
curl -X POST "https://func-convert-app.azurewebsites.net/api/url2pdf?code=your-code" \
  -H "Content-Type: text/plain" \
  -d "https://example.com" \
  --output result.pdf
```

**Note:** The `code` parameter is optional. If your function uses `anonymous` authentication level, you can omit it. For `function` or `admin` levels, include the function key or master key as the `code` parameter.

**Swagger UI:**
Откройте в браузере:
```
https://func-convert-app.azurewebsites.net/api/swagger/ui
```

### Шаг 3: Проверка логов

```bash
# Просмотр логов в реальном времени
az webapp log tail \
  --name func-convert-app \
  --resource-group rg-convert-functions

# Или в Azure Portal:
# Function App → Log stream
```

## Автоматическая установка браузеров Playwright

### Для Linux Function App

Создайте файл `.deployment` в корне проекта:
```ini
[config]
SCM_DO_BUILD_DURING_DEPLOYMENT=true
POST_BUILD_COMMAND=playwright install chromium
```

Или создайте скрипт `deploy.sh`:
```bash
#!/bin/bash
pip install -r requirements.txt
playwright install chromium
```

Затем в Azure Portal:
- Function App → Configuration → General settings
- Добавьте в "Startup Command": `bash deploy.sh`

### Альтернатива: Custom Docker Image

Создайте `Dockerfile`:
```dockerfile
FROM mcr.microsoft.com/azure-functions/python:4-python3.11

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 \
    libxrandr2 libgbm1 libasound2 \
    fonts-dejavu-core fonts-dejavu-extra \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium

# Copy function code
COPY . /home/site/wwwroot
```

Затем разверните через Azure Container Registry (см. spec/deployment.md).

## Решение проблем

### Проблема: Ошибка "Runtime python not supported for os windows"

**Решение:**
Python runtime не поддерживается на Windows. Необходимо использовать Linux:

```bash
# Удалить Function App на Windows (если создан по ошибке)
az functionapp delete \
  --name func-convert-app \
  --resource-group rg-convert-functions

# Создать заново на Linux
az functionapp create \
  --resource-group rg-convert-functions \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name func-convert-app \
  --storage-account stconvertfuncs \
  --os-type Linux

# Примечание: Используйте Python 3.10 или 3.11 вместо 3.9 (EOL)
```

### Проблема: Функции не развертываются

**Решение:**
```bash
# Проверить логи развертывания
az functionapp deployment list-publishing-profiles \
  --name func-convert-app \
  --resource-group rg-convert-functions

# Проверить статус Function App
az functionapp show \
  --name func-convert-app \
  --resource-group rg-convert-functions \
  --query state

# Проверить OS тип
az functionapp show \
  --name func-convert-app \
  --resource-group rg-convert-functions \
  --query "kind"
# Должно быть: "functionapp,linux"
```

### Проблема: Зависимости не устанавливаются

**Решение:**
1. Проверьте `requirements.txt` - все зависимости должны быть указаны
2. Проверьте логи развертывания в Azure Portal
3. Убедитесь, что используется правильная версия Python

### Проблема: Playwright не работает

**Решение:**
1. Установите браузеры через SSH/Kudu (см. выше)
2. Проверьте системные зависимости (Linux)
3. Проверьте логи функции для ошибок

### Проблема: Функции возвращают 500 ошибку

**Решение:**
1. Проверьте логи в Application Insights или Log stream
2. Убедитесь, что все зависимости установлены
3. Проверьте конфигурацию в `function.json`

### Проблема: Таймауты при выполнении

**Решение:**
```bash
# Увеличить таймаут (максимум 10 минут для Consumption)
az functionapp config set \
  --name func-convert-app \
  --resource-group rg-convert-functions \
  --function-timeout 600
```

Или перейдите на Premium план для неограниченного времени выполнения.

### Проблема: Высокая стоимость

**Решение:**
1. Используйте Consumption план (платите только за использование)
2. Настройте Application Insights sampling
3. Оптимизируйте функции (кэширование, уменьшение времени выполнения)

## Мониторинг и оптимизация

### Настройка мониторинга

1. **Application Insights**:
   - Метрики выполнения
   - Логи и трассировка
   - Алерты

2. **Azure Monitor**:
   - Метрики Function App
   - Логи активности
   - Дашборды

### Оптимизация производительности

1. **Кэширование**:
   - Font registration (уже реализовано)
   - Image caching в link_callback

2. **Параллелизация**:
   - Используйте async/await где возможно
   - Оптимизируйте операции ввода-вывода

3. **Масштабирование**:
   - Consumption план автоматически масштабируется
   - Premium план для предсказуемой нагрузки

## Дополнительные ресурсы

- [Документация Azure Functions](https://docs.microsoft.com/azure/azure-functions/)
- [Python в Azure Functions](https://docs.microsoft.com/azure/azure-functions/functions-reference-python)
- [Troubleshooting Guide](../TROUBLESHOOTING.md)
- [Deployment Specification](./spec/deployment.md)

## Быстрая справка

```bash
# Полный процесс развертывания одной командой (после создания ресурсов)
func azure functionapp publish func-convert-app

# Проверка статуса
az functionapp show --name func-convert-app --resource-group rg-convert-functions

# Просмотр логов
az webapp log tail --name func-convert-app --resource-group rg-convert-functions

# Удаление всех ресурсов (осторожно!)
az group delete --name rg-convert-functions --yes --no-wait
```

