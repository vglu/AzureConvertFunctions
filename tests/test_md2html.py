"""
Тест-кейсы для функции md2html
"""
import pytest
from md2html import __init__ as md2html_func


class MockRequest:
    def __init__(self, body: bytes):
        self._body = body
    
    def get_body(self) -> bytes:
        return self._body


def test_md2html_success():
    """Тест успешной конвертации Markdown в HTML"""
    md_data = "# Заголовок\n\nЭто **жирный** текст и *курсив*."
    req = MockRequest(md_data.encode('utf-8'))
    
    response = md2html_func.main(req)
    
    assert response.status_code == 200
    assert response.mimetype == "text/html"
    
    html_content = response.get_body().decode('utf-8')
    assert "<h1>Заголовок</h1>" in html_content
    assert "<strong>жирный</strong>" in html_content
    assert "<em>курсив</em>" in html_content
    assert "<!DOCTYPE html>" in html_content


def test_md2html_empty_body():
    """Тест обработки пустого тела запроса"""
    req = MockRequest(b"")
    
    response = md2html_func.main(req)
    
    assert response.status_code == 400
    assert "не предоставлен" in response.get_body().decode('utf-8')


def test_md2html_with_code_block():
    """Тест обработки блоков кода"""
    md_data = "```python\ndef hello():\n    print('Hello')\n```"
    req = MockRequest(md_data.encode('utf-8'))
    
    response = md2html_func.main(req)
    
    assert response.status_code == 200
    html_content = response.get_body().decode('utf-8')
    assert "<pre>" in html_content or "<code>" in html_content


def test_md2html_with_table():
    """Тест обработки таблиц"""
    md_data = """| Имя | Возраст |
|-----|---------|
| Иван | 25 |"""
    req = MockRequest(md_data.encode('utf-8'))
    
    response = md2html_func.main(req)
    
    assert response.status_code == 200
    html_content = response.get_body().decode('utf-8')
    assert "<table>" in html_content
    assert "Иван" in html_content


def test_md2html_with_links():
    """Тест обработки ссылок"""
    md_data = "[Google](https://google.com)"
    req = MockRequest(md_data.encode('utf-8'))
    
    response = md2html_func.main(req)
    
    assert response.status_code == 200
    html_content = response.get_body().decode('utf-8')
    assert "<a" in html_content
    assert "https://google.com" in html_content


def test_md2html_with_special_characters():
    """Тест обработки специальных символов"""
    md_data = "# Заголовок с символами: <>&\"'"
    req = MockRequest(md_data.encode('utf-8'))
    
    response = md2html_func.main(req)
    
    assert response.status_code == 200
    html_content = response.get_body().decode('utf-8')
    # Специальные символы должны быть экранированы
    assert "Заголовок" in html_content

