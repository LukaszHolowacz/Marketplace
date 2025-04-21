import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model


@pytest.mark.django_db
class TestChangePassword:

    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def user(self):
        return get_user_model().objects.create_user(
            email='testuser@example.com',
            username='testuser',
            password='ValidPass123'
        )

    @pytest.fixture
    def token(self, api_client, user):
        response = api_client.post(reverse('token_obtain_pair'), {
            'login': user.email,
            'password': 'ValidPass123'
        }, format='json')
        assert response.status_code == 200, f"Login failed: {response.data}"
        return response.data['access']
    
    @pytest.fixture
    def inactive_user(self):
        user = get_user_model().objects.create_user(
            email='inactive@example.com',
            username='inactiveuser',
            password='ValidPass123'
        )
        user.is_active = False
        user.save()
        return user

    def test_change_password_success(self, api_client, token):
        url = reverse('change-password')
        data = {
            'old_password': 'ValidPass123',
            'new_password': 'NewValidPass123'
        }
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = api_client.put(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK

    def test_change_password_invalid_old_password(self, api_client, token):
        url = reverse('change-password')
        data = {
            'old_password': 'WrongOldPass',
            'new_password': 'NewValidPass123'
        }
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = api_client.put(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_inactive_user_cannot_access(self, api_client, inactive_user):
        login_response = api_client.post(reverse('token_obtain_pair'), {
            'login': inactive_user.email,
            'password': 'ValidPass123'
        }, format='json')
        assert login_response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Konto użytkownika jest zablokowane.' in str(login_response.data)

        url = reverse('change-password')
        response = api_client.get(url, HTTP_AUTHORIZATION='Bearer invalid_token')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_change_password_too_short_new_password(self, api_client, token):
        url = reverse('change-password')
        data = {
            'old_password': 'ValidPass123',
            'new_password': 'short'
        }
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = api_client.put(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password_missing_uppercase(self, api_client, token):
        url = reverse('change-password')
        data = {
            'old_password': 'ValidPass123',
            'new_password': 'newpassword123'
        }
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = api_client.put(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password_missing_lowercase(self, api_client, token):
        url = reverse('change-password')
        data = {
            'old_password': 'ValidPass123',
            'new_password': 'NEWPASSWORD123'
        }
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = api_client.put(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password_missing_number(self, api_client, token):
        url = reverse('change-password')
        data = {
            'old_password': 'ValidPass123',
            'new_password': 'NewPassword'
        }
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = api_client.put(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password_no_old_password(self, api_client, token):
        url = reverse('change-password')
        data = {
            'new_password': 'NewValidPass123'
        }
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = api_client.put(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password_no_new_password(self, api_client, token):
        url = reverse('change-password')
        data = {
            'old_password': 'ValidPass123'
        }
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = api_client.put(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password_new_password_too_long(self, api_client, token):
        url = reverse('change-password')
        data = {
            'old_password': 'ValidPass123',
            'new_password': 'a' * 201 
        }
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = api_client.put(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password_new_password_same_as_old(self, api_client, token):
        url = reverse('change-password')
        data = {
            'old_password': 'ValidPass123',
            'new_password': 'ValidPass123'
        }
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = api_client.put(url, data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]

    def test_change_password_new_password_only_spaces(self, api_client, token):
        url = reverse('change-password')
        data = {
            'old_password': 'ValidPass123',
            'new_password': '   '
        }
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = api_client.put(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password_invalid_method(self, api_client, token):
        url = reverse('change-password')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response_post = api_client.post(url, {}, format='json')
        assert response_post.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        response_get = api_client.get(url)
        assert response_get.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        response_delete = api_client.delete(url)
        assert response_delete.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_change_password_unauthorized(self, api_client):
        url = reverse('change-password')
        data = {
            'old_password': 'ValidPass123',
            'new_password': 'NewValidPass123'
        }
        response = api_client.put(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_change_password_with_special_characters(self, api_client, token):
        url = reverse('change-password')
        data = {
            'old_password': 'ValidPass123',
            'new_password': 'NewPass123!@#$'
        }
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = api_client.put(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK


    def test_change_password_login_with_username(self, api_client, user):
        token_response = api_client.post(reverse('token_obtain_pair'), {
            'login': user.username,
            'password': 'ValidPass123'
        }, format='json')
        assert token_response.status_code == 200
        access_token = token_response.data['access']

        url = reverse('change-password')
        data = {
            'old_password': 'ValidPass123',
            'new_password': 'AnotherValidPass123'
        }
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = api_client.put(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK

    def test_change_password_old_password_no_longer_valid(self, api_client, user, token):
        url = reverse('change-password')
        new_password = 'CompletelyNewPass123'
        data = {
            'old_password': 'ValidPass123',
            'new_password': new_password
        }
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = api_client.put(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK

        login_attempt = api_client.post(reverse('token_obtain_pair'), {
            'login': user.email,
            'password': 'ValidPass123'
        }, format='json')
        assert login_attempt.status_code == status.HTTP_401_UNAUTHORIZED

        login_success = api_client.post(reverse('token_obtain_pair'), {
            'login': user.email,
            'password': new_password
        }, format='json')
        assert login_success.status_code == status.HTTP_200_OK

    def test_change_password_with_spaces_in_new_password(self, api_client, token):
        url = reverse('change-password')
        data = {
            'old_password': 'ValidPass123',
            'new_password': 'New Pass With Spaces'
        }
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = api_client.put(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    
    def test_change_password_with_unicode_characters(self, api_client, token):
        url = reverse('change-password')
        data = {
            'old_password': 'ValidPass123',
            'new_password': 'NewPassword123😊'
        }
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = api_client.put(url, data, format='json')
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
