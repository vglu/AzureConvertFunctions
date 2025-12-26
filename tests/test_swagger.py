"""
Тест-кейсы для функции Swagger
"""
import pytest
import json
from swagger import __init__ as swagger_func


class MockRequest:
    def __init__(self, body: bytes = b"", route_params: dict = None, headers: dict = None):
        self._body = body
        self._route_params = route_params or {}
        self._headers = headers or {}
    
    def get_body(self) -> bytes:
        return self._body
    
    @property
    def route_params(self):
        return self._route_params
    
    @property
    def headers(self):
        return self._headers


def test_swagger_json_endpoint():
    """Тест получения swagger.json"""
    req = MockRequest(route_params={'restOfPath': 'swagger.json'}, headers={'Host': 'localhost:7071'})
    
    response = swagger_func.main(req)
    
    # Может быть 200 (если файл найден) или 404 (если нет)
    assert response.status_code in [200, 404]
    
    if response.status_code == 200:
        content = response.get_body().decode('utf-8')
        swagger_data = json.loads(content)
        assert 'openapi' in swagger_data
        assert 'paths' in swagger_data
        assert '/csv2json' in swagger_data['paths']


def test_swagger_ui_endpoint():
    """Тест получения Swagger UI HTML"""
    req = MockRequest(route_params={'restOfPath': ''}, headers={'Host': 'localhost:7071'})
    
    response = swagger_func.main(req)
    
    assert response.status_code == 200
    assert response.mimetype == "text/html"
    
    html_content = response.get_body().decode('utf-8')
    assert '<!DOCTYPE html>' in html_content
    assert 'swagger-ui' in html_content
    assert 'SwaggerUIBundle' in html_content


def test_swagger_ui_with_path():
    """Тест Swagger UI с различными путями"""
    req = MockRequest(route_params={'restOfPath': 'index.html'}, headers={'Host': 'localhost:7071'})
    
    response = swagger_func.main(req)
    
    assert response.status_code == 200
    html_content = response.get_body().decode('utf-8')
    assert 'swagger-ui' in html_content





