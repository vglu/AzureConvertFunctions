# Инструкция по установке

## Установка зависимостей для Azure Functions

Azure Functions Core Tools использует системный Python или виртуальное окружение. Важно установить зависимости в правильное место.

### Вариант 1: Установка в системный Python (рекомендуется для быстрого старта)

```powershell
# Установить все зависимости
python -m pip install -r requirements.txt
```

### Вариант 2: Использование виртуального окружения

```powershell
# Создать виртуальное окружение
python -m venv .venv

# Активировать (PowerShell)
.venv\Scripts\Activate.ps1

# Установить зависимости
pip install -r requirements.txt
```

**Важно:** После активации виртуального окружения запускайте `func start` из того же терминала.

### Вариант 3: Установка для конкретного пользователя

Если возникают проблемы с правами доступа:

```powershell
python -m pip install --user -r requirements.txt
```

## Проверка установки

Проверьте, что все модули установлены:

```powershell
python -c "import pandas; import markdown; import xhtml2pdf; print('Все модули установлены!')"
```

## Запуск функций

После установки зависимостей:

```powershell
# Убедитесь, что local.settings.json существует
if (-not (Test-Path "local.settings.json")) {
    Copy-Item "local.settings.json.example" "local.settings.json"
}

# Запустить функции
func start
```

## Решение проблем

Если видите ошибку `ModuleNotFoundError`:

1. Убедитесь, что используете правильный Python:
   ```powershell
   python --version
   where python
   ```

2. Проверьте, что зависимости установлены:
   ```powershell
   pip list | Select-String "pandas|xhtml2pdf|markdown"
   ```

3. Переустановите зависимости:
   ```powershell
   pip install --upgrade -r requirements.txt
   ```

4. Если используете виртуальное окружение, убедитесь, что оно активировано перед запуском `func start`.



