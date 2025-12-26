# Установка на Linux (Ubuntu/Debian)

## Системные зависимости

### Для Playwright (url2pdf, url2jpg)

```bash
sudo apt-get update
sudo apt-get install -y \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2
```

### Для работы с PDF (шрифты)

Обычно шрифты уже установлены в Ubuntu. Если нет:

```bash
# Установить DejaVu шрифты (рекомендуется)
sudo apt-get install -y fonts-dejavu-core fonts-dejavu-extra

# Или Liberation шрифты
sudo apt-get install -y fonts-liberation

# Или Noto шрифты (лучшая поддержка Unicode)
sudo apt-get install -y fonts-noto-core
```

## Установка Python зависимостей

```bash
# Установить зависимости
pip install -r requirements.txt

# Установить браузеры для Playwright
playwright install chromium
```

## Проверка установки

```bash
# Проверить Python модули
python -c "import pandas, markdown, xhtml2pdf, requests; print('All modules installed!')"

# Проверить Playwright
python -c "from playwright.sync_api import sync_playwright; print('Playwright available!')"

# Проверить шрифты
python -c "import os; print('DejaVu:', os.path.exists('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))"
```

## Запуск функций

```bash
func start
```

## Особенности Linux

1. **Шрифты**: Функции автоматически ищут шрифты в стандартных Linux путях:
   - `/usr/share/fonts/truetype/dejavu/`
   - `/usr/share/fonts/truetype/liberation/`
   - `/usr/share/fonts/truetype/noto/`

2. **Playwright**: Требует установки системных зависимостей (см. выше)

3. **Пути**: Все пути в коде кроссплатформенные и автоматически определяют операционную систему

## Развертывание в Azure

Azure Functions на Linux работают так же, как на Windows. Убедитесь, что:
- Все зависимости установлены в `requirements.txt`
- Системные зависимости для Playwright установлены в Docker образе (если используете custom image)





