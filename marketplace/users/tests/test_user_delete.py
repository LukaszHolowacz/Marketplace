import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from django.conf import settings
from users.models import CustomUser
from django.contrib.auth import get_user_model


@pytest.mark.django_db
class TestUserDeleteView:

    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def user(self):
        return CustomUser.objects.create_user(
            email="user@example.com",
            username="testuser",
            password="StrongPass123"
        )

    @pytest.fixture
    def another_user(self):
        return CustomUser.objects.create_user(
            email="other@example.com",
            username="otheruser",
            password="OtherPass123"
        )

    @pytest.fixture
    def admin_user(self):
        return CustomUser.objects.create_superuser(
            email="admin@example.com",
            username="admin",
            password="AdminPass123"
        )

    def test_unauthenticated_user_cannot_delete_user(self, api_client, user):
        url = reverse('user-delete', kwargs={'user_id': user.id})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticated_user_cannot_delete_other_user(self, api_client, user, another_user):
        api_client.force_authenticate(user=user)
        url = reverse('user-delete', kwargs={'user_id': another_user.id})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'Brak uprawnień do usunięcia tego użytkownika.' in str(response.data)

    def test_authenticated_user_can_delete_self(self, api_client, user):
        api_client.force_authenticate(user=user)
        url = reverse('user-delete', kwargs={'user_id': user.id})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not CustomUser.objects.filter(id=user.id).exists()

    def test_authenticated_admin_can_delete_any_user(self, api_client, admin_user, user):
        api_client.force_authenticate(user=admin_user)
        url = reverse('user-delete', kwargs={'user_id': user.id})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not CustomUser.objects.filter(id=user.id).exists()

    def test_authenticated_admin_can_delete_self(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        url = reverse('user-delete', kwargs={'user_id': admin_user.id})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not CustomUser.objects.filter(id=admin_user.id).exists()

    def test_authenticated_admin_cannot_delete_nonexistent_user(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        url = reverse('user-delete', kwargs={'user_id': 99999})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'Użytkownik nie został znaleziony' in str(response.data)

    @pytest.mark.parametrize(
        "http_method",
        ["get", "post", "put"]
    )
    def test_wrong_http_method_on_delete_endpoint_returns_405(self, api_client, user, http_method):
        api_client.force_authenticate(user=user)
        url = reverse('user-delete', kwargs={'user_id': user.id})
        method_to_call = getattr(api_client, http_method)
        response = method_to_call(url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_authenticated_admin_cannot_delete_with_invalid_id_format(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        url = "/users/invalid/delete/"
        response = api_client.delete(url)
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST]

    def test_inactive_user_cannot_authenticate_to_get_token(self, api_client, user):
        user.is_active = False
        user.set_password("testpassword")
        user.save()

        url = reverse('token_obtain_pair')
        response = api_client.post(url, {'login': user.username, 'password': 'testpassword'}) 
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Konto użytkownika jest zablokowane.' in str(response.data)

    def test_authenticated_admin_can_delete_inactive_user(self, api_client, admin_user, user):
        user.is_active = False
        user.save()
        api_client.force_authenticate(user=admin_user)
        url = reverse('user-delete', kwargs={'user_id': user.id})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not CustomUser.objects.filter(id=user.id).exists()

    def test_authenticated_user_cannot_delete_admin(self, api_client, user, admin_user):
        api_client.force_authenticate(user=user)
        url = reverse('user-delete', kwargs={'user_id': admin_user.id})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'Brak uprawnień do usunięcia tego użytkownika.' in str(response.data)

    # def test_authenticated_user_rate_limit(self, api_client, user):
    #     api_client.force_authenticate(user=user)
    #     url = reverse('user-delete', kwargs={'user_id': user.id})
    #     rate_limit = settings.REST_FRAMEWORK.get('DEFAULT_THROTTLE_RATES', {}).get('user', '0/minute')
    #     allowed_requests = int(rate_limit.split('/')[0]) if rate_limit else 0

    #     for _ in range(allowed_requests):
    #         response = api_client.delete(url)
    #         assert response.status_code != status.HTTP_429_TOO_MANY_REQUESTS

    #     response = api_client.delete(url)
    #     assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    # def test_authenticated_admin_rate_limit(self, api_client, admin_user, user):
    #     api_client.force_authenticate(user=admin_user)
    #     url = reverse('user-delete', kwargs={'user_id': user.id})
    #     rate_limit = settings.REST_FRAMEWORK.get('DEFAULT_THROTTLE_RATES', {}).get('user', '0/minute') 
    #     allowed_requests = int(rate_limit.split('/')[0]) if rate_limit else 0

    #     for _ in range(allowed_requests):
    #         response = api_client.delete(url)
    #         assert response.status_code != status.HTTP_429_TOO_MANY_REQUESTS

    #     response = api_client.delete(url)
    #     assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS