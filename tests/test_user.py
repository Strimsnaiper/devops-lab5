from fastapi.testclient import TestClient

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.main import app

from src.main import app

client = TestClient(app)

# Существующие пользователи
users = [
    {
        'id': 1,
        'name': 'Ivan Ivanov',
        'email': 'i.i.ivanov@mail.com',
    },
    {
        'id': 2,
        'name': 'Petr Petrov',
        'email': 'p.p.petrov@mail.com',
    }
]


def test_get_existed_user():
    """Получение существующего пользователя"""
    response = client.get("/api/v1/user", params={"email": users[0]["email"]})
    assert response.status_code == 200
    assert response.json() == users[0]


def test_get_unexisted_user():
    """Получение несуществующего пользователя"""
    response = client.get("/api/v1/user", params={"email": "unknown_user@mail.com"})
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_create_user_with_valid_email():
    """Создание пользователя с уникальной почтой"""
    new_user = {
        "name": "New User",
        "email": "new.user@mail.com",
    }
    response = client.post("/api/v1/user", json=new_user)
    # Должен вернуться id (целое число) и статус 201
    assert response.status_code == 201
    user_id = response.json()
    assert isinstance(user_id, int)

    # Проверяем, что пользователь действительно создался и его можно получить
    response_get = client.get("/api/v1/user", params={"email": new_user["email"]})
    assert response_get.status_code == 200
    data = response_get.json()
    assert data["id"] == user_id
    assert data["name"] == new_user["name"]
    assert data["email"] == new_user["email"]


def test_create_user_with_invalid_email():
    """Создание пользователя с почтой, которую использует другой пользователь"""
    existing_email = users[0]["email"]
    new_user = {
        "name": "Duplicate Email User",
        "email": existing_email,
    }
    response = client.post("/api/v1/user", json=new_user)
    assert response.status_code == 409
    assert response.json() == {"detail": "User with this email already exists"}


def test_delete_user():
    """Удаление пользователя"""
    # Удаляем существующего пользователя
    email_to_delete = users[0]["email"]
    response_delete = client.delete("/api/v1/user", params={"email": email_to_delete})
    assert response_delete.status_code == 204

    # Проверяем, что теперь пользователь не находится
    response_get = client.get("/api/v1/user", params={"email": email_to_delete})
    assert response_get.status_code == 404
    assert response_get.json() == {"detail": "User not found"}
