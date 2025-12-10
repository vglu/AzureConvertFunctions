"""
Тест-кейсы для функции json2csv
"""
import pytest
import json
import csv
import io
from json2csv import __init__ as json2csv_func


class MockRequest:
    def __init__(self, body: bytes):
        self._body = body
    
    def get_body(self) -> bytes:
        return self._body


def test_json2csv_array_success():
    """Тест успешной конвертации массива JSON в CSV"""
    json_data = [
        {"name": "Иван", "age": 25, "city": "Москва"},
        {"name": "Мария", "age": 30, "city": "СПб"}
    ]
    req = MockRequest(json.dumps(json_data).encode('utf-8'))
    
    response = json2csv_func.main(req)
    
    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    
    csv_content = response.get_body().decode('utf-8')
    reader = csv.DictReader(io.StringIO(csv_content))
    rows = list(reader)
    
    assert len(rows) == 2
    assert rows[0]["name"] == "Иван"
    assert rows[1]["city"] == "СПб"


def test_json2csv_object_success():
    """Тест успешной конвертации одного объекта JSON в CSV"""
    json_data = {"name": "Иван", "age": 25, "city": "Москва"}
    req = MockRequest(json.dumps(json_data).encode('utf-8'))
    
    response = json2csv_func.main(req)
    
    assert response.status_code == 200
    csv_content = response.get_body().decode('utf-8')
    reader = csv.DictReader(io.StringIO(csv_content))
    rows = list(reader)
    
    assert len(rows) == 1
    assert rows[0]["name"] == "Иван"


def test_json2csv_empty_body():
    """Тест обработки пустого тела запроса"""
    req = MockRequest(b"")
    
    response = json2csv_func.main(req)
    
    assert response.status_code == 400
    assert "не предоставлен" in response.get_body().decode('utf-8')


def test_json2csv_invalid_json():
    """Тест обработки некорректного JSON"""
    req = MockRequest(b"{invalid json}")
    
    response = json2csv_func.main(req)
    
    assert response.status_code == 400
    assert "Ошибка парсинга JSON" in response.get_body().decode('utf-8')


def test_json2csv_invalid_type():
    """Тест обработки JSON неподдерживаемого типа"""
    req = MockRequest(b'"просто строка"')
    
    response = json2csv_func.main(req)
    
    assert response.status_code == 400
    assert "Неверный формат JSON" in response.get_body().decode('utf-8')


def test_json2csv_with_nested_objects():
    """Тест обработки вложенных объектов (должны быть сериализованы)"""
    json_data = [
        {"name": "Иван", "address": {"city": "Москва", "street": "Ленина"}}
    ]
    req = MockRequest(json.dumps(json_data).encode('utf-8'))
    
    response = json2csv_func.main(req)
    
    assert response.status_code == 200
    csv_content = response.get_body().decode('utf-8')
    # Вложенные объекты будут сериализованы как строки
    assert "address" in csv_content

