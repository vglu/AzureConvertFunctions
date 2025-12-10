"""
Тест-кейсы для функции html2pdf
"""
import pytest
from html2pdf import __init__ as html2pdf_func


class MockRequest:
    def __init__(self, body: bytes):
        self._body = body
    
    def get_body(self) -> bytes:
        return self._body


def test_html2pdf_success():
    """Тест успешной конвертации HTML в PDF"""
    html_data = "<html><body><h1>Тест</h1><p>Привет, мир!</p></body></html>"
    req = MockRequest(html_data.encode('utf-8'))
    
    response = html2pdf_func.main(req)
    
    assert response.status_code == 200
    assert response.mimetype == "application/pdf"
    
    # Проверяем, что ответ содержит валидный PDF (начинается с %PDF)
    pdf_bytes = response.get_body()
    assert pdf_bytes.startswith(b'%PDF')


def test_html2pdf_empty_body():
    """Тест обработки пустого тела запроса"""
    req = MockRequest(b"")
    
    response = html2pdf_func.main(req)
    
    assert response.status_code == 400
    assert "не предоставлен" in response.get_body().decode('utf-8')


def test_html2pdf_simple_html():
    """Тест конвертации простого HTML"""
    html_data = "<h1>Заголовок</h1><p>Параграф с <strong>жирным</strong> текстом.</p>"
    req = MockRequest(html_data.encode('utf-8'))
    
    response = html2pdf_func.main(req)
    
    assert response.status_code == 200
    pdf_bytes = response.get_body()
    assert pdf_bytes.startswith(b'%PDF')


def test_html2pdf_with_styles():
    """Тест конвертации HTML со стилями"""
    html_data = """
    <html>
    <head>
        <style>
            body { font-family: Arial; }
            h1 { color: blue; }
        </style>
    </head>
    <body>
        <h1>Заголовок</h1>
        <p>Текст</p>
    </body>
    </html>
    """
    req = MockRequest(html_data.encode('utf-8'))
    
    response = html2pdf_func.main(req)
    
    assert response.status_code == 200
    pdf_bytes = response.get_body()
    assert pdf_bytes.startswith(b'%PDF')


def test_html2pdf_with_unicode():
    """Тест конвертации HTML с Unicode символами"""
    html_data = "<html><body><p>Привет, мир! 🌍</p></body></html>"
    req = MockRequest(html_data.encode('utf-8'))
    
    response = html2pdf_func.main(req)
    
    assert response.status_code == 200
    pdf_bytes = response.get_body()
    assert pdf_bytes.startswith(b'%PDF')


def test_html2pdf_invalid_html():
    """Тест обработки некорректного HTML (xhtml2pdf может обработать)"""
    html_data = "<html><body><p>Незакрытый тег"
    req = MockRequest(html_data.encode('utf-8'))
    
    # xhtml2pdf может обработать некорректный HTML
    response = html2pdf_func.main(req)
    
    # Может быть успешным (xhtml2pdf исправляет) или ошибкой
    assert response.status_code in [200, 500]

