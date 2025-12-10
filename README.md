# Azure Convert Functions

Набор Azure Functions для конвертации различных форматов данных, реализованный на Python.

## Быстрый старт

- [Установка и настройка](INSTALL.md)
- [Развертывание на Azure](AZURE_DEPLOYMENT.md)
- [Решение проблем](TROUBLESHOOTING.md)
- [Спецификация проекта](spec/README.md)

## Функции

### 1. CSV2JSON
Конвертирует CSV данные в JSON формат.

**Endpoint:** `POST /api/csv2json`

**Query Parameters:**
- `code` (optional) - код авторизации Azure Function

**Request Body:** CSV данные в виде строки

**Response:** JSON массив объектов

**Пример:**
```bash
curl -X POST "http://localhost:7071/api/csv2json?code=your-code" \
  -H "Content-Type: text/csv" \
  -d "name,age,city
Иван,25,Москва
Мария,30,СПб"
```

### 2. HTML2PDF
Конвертирует HTML в PDF документ.

**Endpoint:** `POST /api/html2pdf`

**Query Parameters:**
- `code` (optional) - код авторизации Azure Function

**Request Body:** HTML данные в виде строки

**Response:** PDF файл в бинарном формате

**Пример:**
```bash
curl -X POST "http://localhost:7071/api/html2pdf?code=your-code" \
  -H "Content-Type: text/html" \
  -d "<html><body><h1>Привет</h1></body></html>"
```

### 3. DBF2JSON
Конвертирует DBF (dBase) файл в JSON формат.

**Endpoint:** `POST /api/dbf2json`

**Query Parameters:**
- `code` (optional) - код авторизации Azure Function

**Request Body:** DBF файл в бинарном формате

**Content-Type:** `application/x-dbf` или `application/octet-stream`

**Response:** JSON массив объектов

**Пример:**
```bash
# Загрузить DBF файл
curl -X POST "http://localhost:7071/api/dbf2json?code=your-code" \
  -H "Content-Type: application/x-dbf" \
  --data-binary "@data.dbf"
```

**Примечание:** Функция принимает DBF файл в бинарном формате. Поддерживаются форматы dBASE III, dBASE IV, FoxPro.

### 4. JSON2CSV
Конвертирует JSON данные в CSV формат.

**Endpoint:** `POST /api/json2csv`

**Query Parameters:**
- `code` (optional) - код авторизации Azure Function

**Request Body:** JSON объект или массив объектов

**Response:** CSV данные

**Пример:**
```bash
curl -X POST "http://localhost:7071/api/json2csv?code=your-code" \
  -H "Content-Type: application/json" \
  -d '[{"name":"Иван","age":25},{"name":"Мария","age":30}]'
```

### 5. MD2HTML
Конвертирует Markdown в HTML.

**Endpoint:** `POST /api/md2html`

**Query Parameters:**
- `code` (optional) - код авторизации Azure Function

**Request Body:** Markdown данные в виде строки

**Response:** Полный HTML документ со стилями

**Пример:**
```bash
curl -X POST "http://localhost:7071/api/md2html?code=your-code" \
  -H "Content-Type: text/markdown" \
  -d "# Heading\n\nThis is **bold** text."
```

### 6. URL2PDF
Конвертирует веб-страницу по URL в PDF документ. Поддерживает JavaScript рендеринг через Playwright.

**Endpoint:** `POST /api/url2pdf`

**Query Parameters:**
- `code` (optional) - код авторизации Azure Function

**Request Body:** URL в виде строки

**Response:** PDF файл в бинарном формате

**Пример:**
```bash
curl -X POST "http://localhost:7071/api/url2pdf?code=your-code" \
  -H "Content-Type: text/plain" \
  -d "https://example.com"
```

**Примечание:** Для страниц с динамическим контентом (JavaScript) требуется установка Playwright и браузеров:
```powershell
playwright install chromium
```

### 7. URL2JPG
Создает скриншот веб-страницы по URL и возвращает JPG изображение. Использует Playwright для рендеринга JavaScript.

**Endpoint:** `POST /api/url2jpg`

**Request Body:** URL в виде строки

**Query Parameters:**
- `code` (optional) - код авторизации Azure Function
- `width` (optional) - ширина скриншота в пикселях (по умолчанию: 1920)
- `height` (optional) - высота скриншота в пикселях (по умолчанию: 1080)

**Response:** JPG изображение в бинарном формате

**Пример:**
```bash
curl -X POST "http://localhost:7071/api/url2jpg?code=your-code&width=1920&height=1080" \
  -H "Content-Type: text/plain" \
  -d "https://example.com"
```

**Примечание:** Требуется установка Playwright и браузеров:
```powershell
playwright install chromium
```

## Swagger/OpenAPI Документация

API документация доступна через Swagger UI:

**Endpoint:** `GET /api/swagger`

Откройте в браузере: `http://localhost:7071/api/swagger` для просмотра интерактивной документации API.

Swagger JSON спецификация доступна по адресу: `GET /api/swagger/swagger.json`

## Установка и запуск

### Требования
- Python 3.10+ (рекомендуется 3.11, Python 3.9 достиг EOL)
- Azure Functions Core Tools

**Поддерживаемые платформы:**
- Windows
- Linux (Ubuntu/Debian)
- macOS

### Установка зависимостей

**ВАЖНО:** Azure Functions Core Tools использует системный Python, а не виртуальное окружение!

**Если виртуальное окружение активировано, сначала деактивируйте его:**

```powershell
deactivate
```

**Затем установите зависимости в системный Python:**

```powershell
# Установить все зависимости
python -m pip install -r requirements.txt

# Установить браузеры для Playwright (для url2pdf и url2jpg с поддержкой JavaScript)
playwright install chromium

# На Linux также требуется установить системные зависимости:
# Ubuntu/Debian:
# sudo apt-get update
# sudo apt-get install -y libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2
```

**Проверка установки:**

```powershell
# Проверить, что используется системный Python
python -c "import sys; print(sys.executable)"

# Проверить установку модулей
python -c "import pandas, markdown, xhtml2pdf, requests; print('All modules installed!')"

# Проверить Playwright (опционально)
python -c "from playwright.sync_api import sync_playwright; print('Playwright available!')"
```

**Альтернатива - виртуальное окружение:**

Если хотите использовать виртуальное окружение, активируйте его и запускайте `func start` из того же терминала:

```powershell
.venv\Scripts\Activate.ps1
func start
```

### Локальный запуск

**Перед запуском создайте `local.settings.json`:**

```powershell
# Скопировать пример
Copy-Item local.settings.json.example local.settings.json
```

Затем запустите функции:

```bash
func start
```

**Если возникает ошибка с grpc**, см. раздел [Решение проблем](#решение-проблем) ниже или запустите:

```powershell
.\fix-grpc-issue.ps1
```

### Запуск тестов

```bash
pip install pytest
pytest
```

## Зависимости

- `azure-functions` - SDK для Azure Functions
- `pandas` - для работы с CSV и данными
- `markdown` - для конвертации Markdown в HTML
- `xhtml2pdf` - для конвертации HTML в PDF (кроссплатформенная)
- `bleach` - для очистки HTML (опционально)
- `requests` - для загрузки HTML с URL
- `playwright` - для рендеринга JavaScript на веб-страницах (для url2pdf и url2jpg)
- `dbfread` - для чтения DBF (dBase) файлов

**Примечание для Linux:**
- Для работы с PDF нужны системные шрифты (обычно уже установлены: DejaVu Sans, Liberation Sans)
- Для Playwright требуются системные зависимости (см. инструкции выше)

## Структура проекта

```
.
├── csv2json/
│   ├── __init__.py
│   └── function.json
├── html2pdf/
│   ├── __init__.py
│   └── function.json
├── json2csv/
│   ├── __init__.py
│   └── function.json
├── md2html/
│   ├── __init__.py
│   └── function.json
├── swagger/
│   ├── __init__.py
│   └── function.json
├── tests/
│   ├── test_csv2json.py
│   ├── test_html2pdf.py
│   ├── test_json2csv.py
│   ├── test_md2html.py
│   └── test_swagger.py
├── host.json
├── swagger.json
├── requirements.txt
└── README.md
```

## Тестирование

Все функции покрыты тест-кейсами:

- **test_csv2json.py** - тесты для CSV2JSON конвертации
- **test_json2csv.py** - тесты для JSON2CSV конвертации
- **test_md2html.py** - тесты для MD2HTML конвертации
- **test_html2pdf.py** - тесты для HTML2PDF конвертации
- **test_swagger.py** - тесты для Swagger UI функции
- **test_url2pdf.py** - тесты для URL2PDF конвертации (если созданы)
- **test_url2jpg.py** - тесты для URL2JPG конвертации (если созданы)

Каждый тест-файл содержит:
- Тесты успешной конвертации
- Тесты обработки ошибок
- Тесты граничных случаев
- Тесты со специальными символами

## Решение проблем

### Ошибка: cannot import name 'cygrpc' from 'grpc._cython'

Это известная проблема Azure Functions Core Tools на Windows. Решения:

1. **Обновить Azure Functions Core Tools:**
   ```powershell
   choco upgrade azure-functions-core-tools
   # или
   npm install -g azure-functions-core-tools@latest
   ```

2. **Использовать виртуальное окружение:**
   ```powershell
   .venv\Scripts\Activate.ps1
   func start
   ```

3. **Запустить скрипт диагностики:**
   ```powershell
   .\fix-grpc-issue.ps1
   ```

Подробные инструкции см. в [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## Развертывание в Azure

1. Создайте Azure Function App
2. Установите зависимости через Kudu или SSH
3. Разверните функции через Azure CLI или Visual Studio Code

```bash
func azure functionapp publish <your-function-app-name>
```

