import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model

@pytest.mark.django_db
class TestMeView:

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
    def inactive_user(self):
        user = get_user_model().objects.create_user(
            email='inactive@example.com',
            username='inactiveuser',
            password='ValidPass123'
        )
        user.is_active = False
        user.save()
        return user

    @pytest.fixture
    def token(self, api_client, user):
        response = api_client.post(reverse('token_obtain_pair'), {
            'login': user.email,
            'password': 'ValidPass123'
        }, format='json')
        assert response.status_code == 200
        return response.data['access']

    @pytest.fixture
    def inactive_user_token(self, api_client, inactive_user):
        response = api_client.post(reverse('token_obtain_pair'), {
            'login': inactive_user.email,
            'password': 'ValidPass123'
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        return None

    def test_inactive_user_cannot_access(self, api_client, inactive_user):
        login_response = api_client.post(reverse('token_obtain_pair'), {
            'login': inactive_user.email,
            'password': 'ValidPass123'
        }, format='json')
        assert login_response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Konto użytkownika jest zablokowane.' in str(login_response.data)

        url = reverse('user-me')
        response = api_client.get(url, HTTP_AUTHORIZATION='Bearer invalid_token')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        response_no_token = api_client.get(url)
        assert response_no_token.status_code == status.HTTP_401_UNAUTHORIZED

    def test_me_view_authenticated(self, api_client, token, user):
        url = reverse('user-me')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email
        assert response.data['username'] == user.username
        assert 'password' not in response.data

        allowed_fields = ['email', 'username', 'first_name', 'last_name', 'is_active', 'is_staff']
        assert all(field in response.data for field in allowed_fields)

    def test_me_view_unauthenticated(self, api_client):
        url = reverse('user-me')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_me_view_method_not_allowed(self, api_client, token):
        url = reverse('user-me')
        data = {'username': 'newuser', 'email': 'newuser@example.com'}
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        for method in [api_client.post, api_client.put, api_client.delete]:
            response = method(url, data, format='json')
            assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED