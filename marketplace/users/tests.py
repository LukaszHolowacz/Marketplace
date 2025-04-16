import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from .models import CustomUser


@pytest.mark.django_db
class TestUserRegistration:

    @pytest.fixture
    def api_client(self):
        return APIClient()

    def test_user_registration_success(self, api_client):
        url = reverse('user-create')
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'ValidPass123',
            'password2': 'ValidPass123'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert 'id' in response.data

    def test_user_registration_weak_password(self, api_client):
        url = reverse('user-create')
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'weak',
            'password2': 'weak'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Hasło musi mieć co najmniej 8 znaków.' in str(response.data)

    def test_user_registration_password_mismatch(self, api_client):
        url = reverse('user-create')
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'ValidPass123',
            'password2': 'DifferentPass123'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Hasła nie są identyczne.' in str(response.data)

    def test_user_registration_missing_data(self, api_client):
        url = reverse('user-create')
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'This field is required.' in str(response.data['password'])

    def test_user_registration_incomplete_data(self, api_client):
        url = reverse('user-create')
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'This field is required.' in str(response.data['password'])

    def test_user_registration_invalid_email(self, api_client):
        url = reverse('user-create')
        data = {
            'username': 'testuser',
            'email': 'invalidemail',
            'password': 'ValidPass123',
            'password2': 'ValidPass123'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Enter a valid email address.' in str(response.data)

    def test_user_registration_duplicate_email(self, api_client):
        CustomUser.objects.create_user(
            email='testuser@example.com',
            password='ValidPass123',
            username='existinguser'
        )
        url = reverse('user-create')
        data = {
            'username': 'newuser',
            'email': 'testuser@example.com',
            'password': 'ValidPass123',
            'password2': 'ValidPass123'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Email jest już zajęty.' in str(response.data)

    def test_user_registration_duplicate_username(self, api_client):
        CustomUser.objects.create_user(
            email='existinguser@example.com',
            password='ValidPass123',
            username='testuser'
        )
        url = reverse('user-create')
        data = {
            'username': 'testuser',
            'email': 'newuser@example.com',
            'password': 'ValidPass123',
            'password2': 'ValidPass123'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Nazwa użytkownika jest już zajęta.' in str(response.data)

    def test_user_registration_wrong_http_method(self, api_client):
        url = reverse('user-create')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_user_registration_email_too_long(self, api_client):
        url = reverse('user-create')
        data = {
            'username': 'testuser',
            'email': 'a' * 500 + '@example.com',
            'password': 'ValidPass123',
            'password2': 'ValidPass123'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Enter a valid email address.' in str(response.data['email'])
