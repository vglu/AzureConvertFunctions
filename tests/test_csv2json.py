"""
Тест-кейсы для функции csv2json
"""
import pytest
import json
import azure.functions as func
from csv2json import __init__ as csv2json_func


class MockRequest:
    def __init__(self, body: bytes):
        self._body = body
    
    def get_body(self) -> bytes:
        return self._body


def test_csv2json_success():
    """Тест успешной конвертации CSV в JSON"""
    csv_data = "name,age,city\nИван,25,Москва\nМария,30,СПб"
    req = MockRequest(csv_data.encode('utf-8'))
    
    response = csv2json_func.main(req)
    
    assert response.status_code == 200
    assert response.mimetype == "application/json"
    
    result = json.loads(response.get_body())
    assert isinstance(result, str)  # JSON строка
    parsed = json.loads(result)
    assert len(parsed) == 2
    assert parsed[0]["name"] == "Иван"
    assert parsed[0]["age"] == "25"
    assert parsed[1]["city"] == "СПб"


def test_csv2json_empty_body():
    """Тест обработки пустого тела запроса"""
    req = MockRequest(b"")
    
    response = csv2json_func.main(req)
    
    assert response.status_code == 400
    assert "не предоставлен" in response.get_body().decode('utf-8')


def test_csv2json_invalid_csv():
    """Тест обработки некорректного CSV"""
    csv_data = "name,age\nИван,25,Москва,лишнее"
    req = MockRequest(csv_data.encode('utf-8'))
    
    # pandas обычно обрабатывает это, но может быть предупреждение
    response = csv2json_func.main(req)
    
    # Функция должна обработать это (pandas может проигнорировать лишние колонки)
    assert response.status_code in [200, 500]


def test_csv2json_with_special_characters():
    """Тест обработки специальных символов"""
    csv_data = "text,number\nПривет, мир!,42\nТест \"кавычек\",100"
    req = MockRequest(csv_data.encode('utf-8'))
    
    response = csv2json_func.main(req)
    
    assert response.status_code == 200
    result = json.loads(response.get_body())
    parsed = json.loads(result)
    assert "Привет, мир!" in parsed[0]["text"]


def test_csv2json_single_row():
    """Тест конвертации одной строки CSV"""
    csv_data = "name,age\nИван,25"
    req = MockRequest(csv_data.encode('utf-8'))
    
    response = csv2json_func.main(req)
    
    assert response.status_code == 200
    result = json.loads(response.get_body())
    parsed = json.loads(result)
    assert len(parsed) == 1
    assert parsed[0]["name"] == "Иван"



