import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from users.models import CustomUser
from django.contrib.auth import get_user_model


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
        assert 'Podaj poprawny adres email.' in str(response.data['email'])

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

    def test_user_registration_username_too_short(self, api_client):
        url = reverse('user-create')
        data = {
            'username': 'a',
            'email': 'testuser@example.com',
            'password': 'ValidPass123',
            'password2': 'ValidPass123'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Nazwa użytkownika musi mieć co najmniej 2 znaki.' in str(response.data)

    def test_user_registration_username_too_long(self, api_client):
        url = reverse('user-create')
        data = {
            'username': 'a' * 51,
            'email': 'testuser@example.com',
            'password': 'ValidPass123',
            'password2': 'ValidPass123'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Nazwa użytkownika nie może przekraczać 50 znaków.' in str(response.data)

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
        assert 'Podaj poprawny adres email.' in str(response.data['email'])

    def test_user_registration_password_missing_uppercase(self, api_client):
        url = reverse('user-create')
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'validpass123',
            'password2': 'validpass123'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Hasło musi zawierać co najmniej jedną dużą literę.' in str(response.data)

    def test_user_registration_missing_username(self, api_client):
        url = reverse('user-create')
        data = {
            'email': 'testuser@example.com',
            'password': 'ValidPass123',
            'password2': 'ValidPass123'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'To pole jest wymagane.' in str(response.data['username'])

    def test_user_registration_missing_email(self, api_client):
        url = reverse('user-create')
        data = {
            'username': 'testuser',
            'password': 'ValidPass123',
            'password2': 'ValidPass123'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'To pole jest wymagane.' in str(response.data['email'])

    def test_user_registration_empty_email(self, api_client):
        url = reverse('user-create')
        data = {
            'username': 'testuser',
            'email': '',
            'password': 'ValidPass123',
            'password2': 'ValidPass123'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'This field may not be blank.' in str(response.data['email'])

    def test_user_registration_invalid_method(self, api_client):
        url = reverse('user-create')
        response = api_client.put(url, {}, format='json')
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_user_registration_password_missing_lowercase(self, api_client):
        url = reverse('user-create')
        data = {
            'username': 'TESTUSER',
            'email': 'test@example.com',
            'password': 'VALIDPASS123',
            'password2': 'VALIDPASS123'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Hasło musi zawierać co najmniej jedną małą literę.' in str(response.data)

    def test_user_registration_password_missing_digit(self, api_client):
        url = reverse('user-create')
        data = {
            'username': 'Testuser',
            'email': 'test@example.com',
            'password': 'ValidPassABC',
            'password2': 'ValidPassABC'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Hasło musi zawierać co najmniej jedną cyfrę.' in str(response.data)

    def test_user_registration_first_name_too_long(self, api_client):
        url = reverse('user-create')
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'ValidPass123',
            'password2': 'ValidPass123',
            'first_name': 'a' * 51
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Imię nie może mieć więcej niż 50 znaków.' in str(response.data['first_name'])

    def test_user_registration_last_name_too_long(self, api_client):
        url = reverse('user-create')
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'ValidPass123',
            'password2': 'ValidPass123',
            'last_name': 'a' * 51
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Nazwisko nie może mieć więcej niż 50 znaków.' in str(response.data['last_name'])

    def test_user_registration_email_with_spaces(self, api_client):
        url = reverse('user-create')
        data = {
            'username': 'testuser',
            'email': 'test user@example.com',
            'password': 'ValidPass123',
            'password2': 'ValidPass123'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Podaj poprawny adres email.' in str(response.data['email'])

    def test_user_registration_username_with_spaces(self, api_client):
        url = reverse('user-create')
        data = {
            'username': 'test user',
            'email': 'test@example.com',
            'password': 'ValidPass123',
            'password2': 'ValidPass123'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Nazwa użytkownika nie może zawierać spacji.' in str(response.data['username'])

    def test_register_user_with_special_characters_in_password(self, api_client):
        url = reverse('user-create')  
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'ValidPass123!@#$%',
            'password2': 'ValidPass123!@#$%'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert get_user_model().objects.filter(username='testuser').exists()

    def test_user_registration_sql_injection_attempt(self, api_client):
        url = reverse('user-create')
        injection_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT NULL --",
            "'; INSERT INTO users (id, username) VALUES (9999, 'hacker'); --",
            "' OR ''='",
            "'; --",
            "' OR 1=1 --"
        ]

        for payload in injection_payloads:
            data = {
                'username': payload,
                'email': f"{payload}@example.com",
                'password': 'ValidPass123',
                'password2': 'ValidPass123'
            }
            response = api_client.post(url, data, format='json')

            assert response.status_code == status.HTTP_400_BAD_REQUEST