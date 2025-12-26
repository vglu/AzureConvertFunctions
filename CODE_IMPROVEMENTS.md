# Анализ кода и предложения по улучшению

## 🔍 Общий анализ

Проект представляет собой набор Azure Functions для конвертации различных форматов данных. Код в целом структурирован, но есть несколько областей для улучшения.

---

## 1. 🔴 Критические проблемы

### 1.1 Дублирование кода

**Проблема**: Функция `register_fonts()` полностью дублируется в `html2pdf/__init__.py` и `url2pdf/__init__.py`.

**Решение**: Создать общий модуль `utils/fonts.py`:

```python
# utils/fonts.py
import logging
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

_fonts_registered = False

def register_fonts():
    """Registers fonts for Unicode and Cyrillic support"""
    global _fonts_registered
    
    if _fonts_registered:
        return 'Arial'
    
    # ... existing code ...
```

**Преимущества**:
- Устранение дублирования
- Единая точка изменений
- Легче тестировать

### 1.2 Отсутствие валидации размера входных данных

**Проблема**: Нет ограничений на размер входных данных, что может привести к:
- Исчерпанию памяти
- Таймаутам
- DoS-атакам

**Решение**: Добавить валидацию размера:

```python
MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10 MB

def validate_request_size(req: func.HttpRequest) -> bool:
    content_length = req.headers.get('Content-Length')
    if content_length and int(content_length) > MAX_REQUEST_SIZE:
        return False
    return True
```

### 1.3 Небезопасная обработка URL

**Проблема**: В `url2pdf` и `url2jpg` нет проверки на:
- SSRF (Server-Side Request Forgery)
- Доступ к внутренним ресурсам
- Валидацию схемы URL

**Решение**:

```python
ALLOWED_URL_SCHEMES = ['http', 'https']
BLOCKED_IP_RANGES = [
    '127.0.0.1',
    'localhost',
    '169.254.169.254',  # Azure metadata service
    '10.0.0.0/8',
    '172.16.0.0/12',
    '192.168.0.0/16'
]

def validate_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_URL_SCHEMES:
        return False
    # Check for blocked IPs
    # ...
    return True
```

---

## 2. ⚠️ Важные улучшения

### 2.1 Улучшение обработки ошибок

**Проблема**: Использование слишком общего `except Exception` скрывает специфичные ошибки.

**Решение**: Создать иерархию исключений:

```python
# utils/exceptions.py
class ConversionError(Exception):
    """Base exception for conversion errors"""
    pass

class ValidationError(ConversionError):
    """Input validation error"""
    pass

class ProcessingError(ConversionError):
    """Processing/conversion error"""
    pass

class ExternalServiceError(ConversionError):
    """External service (Playwright, requests) error"""
    pass
```

**Использование**:

```python
try:
    # ...
except ValidationError as e:
    return func.HttpResponse(
        json.dumps({"error": str(e)}),
        mimetype="application/json",
        status_code=400
    )
except ProcessingError as e:
    return func.HttpResponse(
        json.dumps({"error": str(e)}),
        mimetype="application/json",
        status_code=500
    )
except Exception as e:
    logging.exception("Unexpected error")
    return func.HttpResponse(
        json.dumps({"error": "Internal server error"}),
        mimetype="application/json",
        status_code=500
    )
```

### 2.2 Добавление type hints

**Проблема**: Отсутствие type hints усложняет поддержку и использование IDE.

**Решение**: Добавить type hints везде:

```python
from typing import Optional, Dict, List, Any
import azure.functions as func

def register_fonts() -> Optional[str]:
    """Registers fonts for Unicode and Cyrillic support"""
    # ...

def download_image_to_base64(
    image_url: str, 
    base_url: Optional[str] = None
) -> Optional[bytes]:
    """Downloads an image and returns its bytes"""
    # ...

def main(req: func.HttpRequest) -> func.HttpResponse:
    # ...
```

### 2.3 Конфигурация через переменные окружения

**Проблема**: Хардкод значений (таймауты, размеры, пути к шрифтам).

**Решение**: Использовать переменные окружения:

```python
# utils/config.py
import os
from typing import Optional

class Config:
    # Request limits
    MAX_REQUEST_SIZE = int(os.getenv('MAX_REQUEST_SIZE', '10485760'))  # 10 MB
    MAX_URL_FETCH_TIMEOUT = int(os.getenv('MAX_URL_FETCH_TIMEOUT', '30'))
    
    # Playwright settings
    PLAYWRIGHT_TIMEOUT = int(os.getenv('PLAYWRIGHT_TIMEOUT', '30000'))
    PLAYWRIGHT_NETWORK_IDLE_TIMEOUT = int(os.getenv('PLAYWRIGHT_NETWORK_IDLE_TIMEOUT', '10000'))
    
    # Screenshot settings
    DEFAULT_SCREENSHOT_WIDTH = int(os.getenv('DEFAULT_SCREENSHOT_WIDTH', '1920'))
    DEFAULT_SCREENSHOT_HEIGHT = int(os.getenv('DEFAULT_SCREENSHOT_HEIGHT', '1080'))
    DEFAULT_SCREENSHOT_QUALITY = int(os.getenv('DEFAULT_SCREENSHOT_QUALITY', '90'))
    
    # Font paths (can be overridden)
    FONT_PATHS_WINDOWS = os.getenv(
        'FONT_PATHS_WINDOWS',
        'C:\\Windows\\Fonts\\arial.ttf;C:\\Windows\\Fonts\\arialuni.ttf'
    ).split(';')
    
    FONT_PATHS_LINUX = os.getenv(
        'FONT_PATHS_LINUX',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    ).split(':')
```

### 2.4 Улучшение логирования

**Проблема**: Логи не содержат достаточно контекста для отладки.

**Решение**: Добавить структурированное логирование:

```python
import logging
import uuid
from typing import Dict, Any

def create_logger_context(req: func.HttpRequest) -> Dict[str, Any]:
    """Create logging context from request"""
    return {
        'request_id': str(uuid.uuid4()),
        'function_name': req.route_params.get('function_name', 'unknown'),
        'method': req.method,
        'url': req.url,
    }

def main(req: func.HttpRequest) -> func.HttpResponse:
    context = create_logger_context(req)
    logging.info('Function started', extra=context)
    
    try:
        # ...
        logging.info('Function completed successfully', extra=context)
    except Exception as e:
        logging.error('Function failed', extra={**context, 'error': str(e)})
        # ...
```

---

## 3. 📈 Улучшения производительности

### 3.1 Кэширование для URL

**Проблема**: Повторные запросы к одному URL обрабатываются заново.

**Решение**: Добавить кэширование (для Production можно использовать Redis):

```python
# utils/cache.py
from functools import lru_cache
from typing import Optional
import hashlib
import time

class SimpleCache:
    def __init__(self, ttl: int = 3600):  # 1 hour
        self._cache: Dict[str, tuple] = {}
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            del self._cache[key]
        return None
    
    def set(self, key: str, value: Any):
        self._cache[key] = (value, time.time())

url_cache = SimpleCache(ttl=3600)

def get_cached_url_content(url: str) -> Optional[str]:
    cache_key = hashlib.md5(url.encode()).hexdigest()
    return url_cache.get(cache_key)

def set_cached_url_content(url: str, content: str):
    cache_key = hashlib.md5(url.encode()).hexdigest()
    url_cache.set(cache_key, content)
```

### 3.2 Оптимизация CSS очистки

**Проблема**: Множественные regex-операции над HTML замедляют обработку.

**Решение**: Использовать BeautifulSoup для парсинга HTML:

```python
from bs4 import BeautifulSoup

def clean_html_css(html_content: str) -> str:
    """Clean HTML from problematic CSS using BeautifulSoup"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove all style tags
    for style in soup.find_all('style'):
        style.decompose()
    
    # Remove all link tags
    for link in soup.find_all('link', rel='stylesheet'):
        link.decompose()
    
    # Remove inline styles
    for tag in soup.find_all(True):
        if tag.get('style'):
            del tag['style']
    
    return str(soup)
```

**Примечание**: Это может быть медленнее для очень больших HTML, но более надежно.

### 3.3 Параллельная загрузка изображений

**Проблема**: Изображения загружаются последовательно в `link_callback`.

**Решение**: Использовать `concurrent.futures`:

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple

def download_images_parallel(image_urls: List[str], max_workers: int = 5) -> Dict[str, bytes]:
    """Download multiple images in parallel"""
    results = {}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {
            executor.submit(download_image_to_base64, url): url 
            for url in image_urls
        }
        
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                results[url] = future.result()
            except Exception as e:
                logging.warning(f'Failed to download {url}: {e}')
    
    return results
```

---

## 4. 🛡️ Улучшения безопасности

### 4.1 Валидация входных данных

**Решение**: Создать модуль валидации:

```python
# utils/validation.py
import re
from urllib.parse import urlparse
from typing import Optional

def validate_csv_content(content: str) -> bool:
    """Validate CSV content"""
    if not content or len(content) > MAX_REQUEST_SIZE:
        return False
    # Additional CSV validation
    return True

def validate_json_content(content: str) -> bool:
    """Validate JSON content"""
    try:
        import json
        data = json.loads(content)
        # Check for circular references, depth, etc.
        return True
    except:
        return False

def validate_url(url: str) -> tuple[bool, Optional[str]]:
    """Validate URL and return (is_valid, error_message)"""
    try:
        parsed = urlparse(url)
        
        if not parsed.scheme or parsed.scheme not in ['http', 'https']:
            return False, "Invalid URL scheme"
        
        if not parsed.netloc:
            return False, "Missing URL host"
        
        # Check for SSRF
        if parsed.hostname in ['localhost', '127.0.0.1', '0.0.0.0']:
            return False, "Localhost URLs are not allowed"
        
        # Check for private IP ranges
        # ...
        
        return True, None
    except Exception as e:
        return False, f"URL validation error: {str(e)}"
```

### 4.2 Ограничение размера файлов

**Решение**: Добавить проверки везде:

```python
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

def validate_file_size(data: bytes) -> bool:
    if len(data) > MAX_FILE_SIZE:
        return False
    return True
```

### 4.3 Санитизация HTML

**Проблема**: В `md2html` закомментирован `bleach.clean()`.

**Решение**: Использовать санитизацию с настраиваемыми тегами:

```python
ALLOWED_HTML_TAGS = [
    'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'strong', 'em', 'ul', 'ol', 'li', 'a',
    'code', 'pre', 'table', 'thead', 'tbody',
    'tr', 'td', 'th', 'blockquote', 'img'
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    'img': ['src', 'alt', 'title']
}

def sanitize_html(html: str) -> str:
    """Sanitize HTML content"""
    return bleach.clean(
        html,
        tags=ALLOWED_HTML_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )
```

---

## 5. 📝 Улучшения кода

### 5.1 Документация функций

**Проблема**: Недостаточно docstrings.

**Решение**: Добавить подробные docstrings:

```python
def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Convert CSV data to JSON format.
    
    Args:
        req: Azure Function HTTP request containing CSV data in body
        
    Returns:
        HTTP response with JSON data (200) or error message (400/500)
        
    Example:
        Request body: "name,age\\nJohn,25"
        Response: [{"name": "John", "age": "25"}]
    """
    # ...
```

### 5.2 Разделение логики

**Проблема**: Функции `main()` содержат слишком много логики.

**Решение**: Вынести бизнес-логику в отдельные функции:

```python
# csv2json/converter.py
def convert_csv_to_json(csv_content: str) -> str:
    """Convert CSV string to JSON string"""
    from io import StringIO
    import pandas as pd
    
    csv_buffer = StringIO(csv_content)
    df = pd.read_csv(csv_buffer)
    return df.to_json(orient='records', force_ascii=False, indent=2)

# csv2json/__init__.py
from .converter import convert_csv_to_json

def main(req: func.HttpRequest) -> func.HttpResponse:
    # Validation
    # Call converter
    # Return response
```

### 5.3 Улучшение обработки кодировок

**Проблема**: Жестко задана кодировка UTF-8.

**Решение**: Определять кодировку автоматически:

```python
import chardet

def detect_encoding(data: bytes) -> str:
    """Detect encoding of byte data"""
    result = chardet.detect(data)
    return result.get('encoding', 'utf-8') or 'utf-8'

def decode_request_body(req: func.HttpRequest) -> str:
    """Decode request body with automatic encoding detection"""
    body = req.get_body()
    
    # Try UTF-8 first (most common)
    try:
        return body.decode('utf-8')
    except UnicodeDecodeError:
        pass
    
    # Try to detect encoding
    encoding = detect_encoding(body)
    try:
        return body.decode(encoding)
    except UnicodeDecodeError:
        # Fallback to UTF-8 with error handling
        return body.decode('utf-8', errors='replace')
```

---

## 6. 🧪 Улучшения тестирования

### 6.1 Перевод тестов на английский

**Проблема**: Тесты содержат русские комментарии и данные.

**Решение**: Перевести все на английский:

```python
def test_csv2json_success():
    """Test successful CSV to JSON conversion"""
    csv_data = "name,age,city\nJohn,25,New York\nJane,30,London"
    # ...
```

### 6.2 Добавление интеграционных тестов

**Решение**: Создать интеграционные тесты для Playwright:

```python
# tests/integration/test_url2pdf.py
@pytest.mark.integration
def test_url2pdf_with_playwright():
    """Integration test for url2pdf with Playwright"""
    # Requires Playwright to be installed
    # ...
```

### 6.3 Покрытие тестами

**Решение**: Добавить тесты для edge cases:

- Пустые входные данные
- Очень большие файлы
- Некорректные форматы
- Специальные символы
- Unicode
- Таймауты

---

## 7. 🔧 Технические улучшения

### 7.1 Использование контекстных менеджеров

**Проблема**: В `dbf2json` используется `try-finally` для очистки.

**Решение**: Создать контекстный менеджер:

```python
from contextlib import contextmanager
import tempfile
import os

@contextmanager
def temporary_file(suffix: str = '', prefix: str = 'tmp', delete: bool = True):
    """Context manager for temporary files"""
    temp_file = tempfile.NamedTemporaryFile(
        delete=False, 
        suffix=suffix, 
        prefix=prefix
    )
    temp_file.close()
    try:
        yield temp_file.name
    finally:
        if delete and os.path.exists(temp_file.name):
            os.unlink(temp_file.name)

# Usage
with temporary_file(suffix='.dbf') as temp_path:
    # Use temp_path
    pass
# File automatically deleted
```

### 7.2 Улучшение обработки таймаутов

**Решение**: Добавить таймауты везде:

```python
import signal
from contextlib import contextmanager

@contextmanager
def timeout(seconds: int):
    """Context manager for function timeout"""
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds")
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

# Usage
try:
    with timeout(30):
        result = fetch_url_content(url)
except TimeoutError:
    return func.HttpResponse("Request timeout", status_code=504)
```

### 7.3 Мониторинг и метрики

**Решение**: Добавить метрики для Application Insights:

```python
from opencensus.ext.azure.log_exporter import AzureLogHandler

logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(
    connection_string=os.getenv('APPLICATIONINSIGHTS_CONNECTION_STRING')
))

def track_metric(name: str, value: float):
    """Track custom metric"""
    logger.info(f"Metric: {name}={value}", extra={
        'custom_dimensions': {name: value}
    })
```

---

## 8. 📋 Приоритеты внедрения

### Высокий приоритет (сделать сразу):
1. ✅ Вынести `register_fonts()` в общий модуль
2. ✅ Добавить валидацию размера входных данных
3. ✅ Улучшить обработку ошибок (специфичные исключения)
4. ✅ Добавить валидацию URL (защита от SSRF)
5. ✅ Добавить type hints

### Средний приоритет (в ближайшее время):
6. ✅ Конфигурация через переменные окружения
7. ✅ Улучшить логирование (структурированное)
8. ✅ Добавить docstrings
9. ✅ Разделить логику (вынести конвертеры)
10. ✅ Улучшить тесты (перевести на английский)

### Низкий приоритет (когда будет время):
11. ✅ Кэширование URL
12. ✅ Оптимизация CSS очистки (BeautifulSoup)
13. ✅ Параллельная загрузка изображений
14. ✅ Мониторинг и метрики
15. ✅ Интеграционные тесты

---

## 9. 📊 Метрики качества кода

### Текущее состояние:
- **Дублирование кода**: ~150 строк дублируется
- **Покрытие тестами**: ~60% (оценка)
- **Type hints**: 0%
- **Документация**: ~40%

### Целевое состояние:
- **Дублирование кода**: 0%
- **Покрытие тестами**: >80%
- **Type hints**: 100%
- **Документация**: 100%

---

## 10. 🔄 Рекомендуемый порядок рефакторинга

1. **Фаза 1**: Безопасность и стабильность
   - Валидация входных данных
   - Обработка ошибок
   - Защита от SSRF

2. **Фаза 2**: Структура кода
   - Вынести общий код
   - Разделить логику
   - Добавить type hints

3. **Фаза 3**: Производительность
   - Кэширование
   - Оптимизация
   - Параллелизм

4. **Фаза 4**: Качество
   - Тесты
   - Документация
   - Мониторинг

---

## Заключение

Код проекта в целом хорошо структурирован, но есть значительный потенциал для улучшения в области безопасности, производительности и поддерживаемости. Рекомендуется начать с критических проблем (безопасность, дублирование кода), затем перейти к улучшению структуры и качества кода.

