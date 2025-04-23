import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from users.models import CustomUser, UserProfile
from users.serializers import UserProfileSerializer
from django.db import IntegrityError, DataError

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user(db):
    def make_user(**kwargs):
        user_count = CustomUser.objects.count()
        data = {
            "email": f"test{user_count + 1}@example.com",
            "username": f"testuser{user_count + 1}",
            "password": "StrongPass1",
        }
        data.update(kwargs)
        user = CustomUser.objects.create_user(**data)
        return user
    return make_user

@pytest.mark.django_db
class TestPublicUserProfileView:
    def test_get_active_user_profile(self, api_client, create_user):
        user = create_user(username="active_user")
        url = reverse('public-user-profile', kwargs={'username': user.username})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        expected_data = UserProfileSerializer(user.profile).data
        assert response.data == expected_data

    def test_get_non_existent_user_profile(self, api_client):
        url = reverse('public-user-profile', kwargs={'username': "non_existent_user"})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] == "Użytkownik nie znaleziony"

    def test_get_inactive_user_profile_unauthenticated(self, api_client, create_user):
        inactive_user = create_user(username="inactive_user", is_active=False)
        url = reverse('public-user-profile', kwargs={'username': inactive_user.username})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] == "Użytkownik nie znaleziony"

    def test_get_inactive_user_profile_authenticated_other_user(self, api_client, create_user):
        inactive_user = create_user(username="inactive_other", is_active=False)
        other_user = create_user(username="other")
        api_client.force_authenticate(user=other_user)
        url = reverse('public-user-profile', kwargs={'username': inactive_user.username})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] == "Użytkownik nie znaleziony"

    def test_get_inactive_user_profile_authenticated_staff(self, api_client, create_user):
        inactive_user = create_user(username="inactive_staff", is_active=False)
        staff_user = create_user(username="staff", is_staff=True)
        api_client.force_authenticate(user=staff_user)
        url = reverse('public-user-profile', kwargs={'username': inactive_user.username})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        expected_data = UserProfileSerializer(inactive_user.profile).data
        assert response.data == expected_data

    def test_get_inactive_user_profile_authenticated_same_user(self, api_client, create_user):
        inactive_user = create_user(username="self_inactive", is_active=False)
        api_client.force_authenticate(user=inactive_user)
        url = reverse('public-user-profile', kwargs={'username': inactive_user.username})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        expected_data = UserProfileSerializer(inactive_user.profile).data
        assert response.data == expected_data

    def test_response_contains_expected_fields(self, api_client, create_user):
        user = create_user(username="fields_user")
        url = reverse('public-user-profile', kwargs={'username': user.username})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        serializer = UserProfileSerializer(user.profile)
        expected_fields = set(serializer.fields.keys())
        returned_fields = set(response.data.keys())
        assert expected_fields.issubset(returned_fields)

    def test_response_does_not_contain_sensitive_user_data(self, api_client, create_user):
        user = create_user(username="sensitive_user")
        url = reverse('public-user-profile', kwargs={'username': user.username})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'password' not in response.data
        assert 'is_staff' not in response.data
        assert 'is_active' not in response.data
        assert 'date_joined' not in response.data
        assert 'id' not in response.data

    def test_user_without_profile(self, api_client, create_user, settings):
        user_count = CustomUser.objects.count()
        user = CustomUser.objects.create_user(
            email=f"noprofile{user_count + 1}@example.com",
            username=f"noprofile_user{user_count + 1}",
            password="StrongPass1"
        )
        url = reverse('public-user-profile', kwargs={'username': user.username})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        serializer = UserProfileSerializer(UserProfile(user=user))
        expected_fields = set(serializer.fields.keys())
        returned_fields = set(response.data.keys())
        assert expected_fields.issubset(returned_fields)
        assert 'username' in response.data
        assert response.data['username'] == user.username
        assert 'email' in response.data
        assert response.data['email'] == user.email
        assert 'avatar' in response.data
        assert response.data['avatar'] == f'{settings.MEDIA_URL}images/default-avatar.png'
        assert 'phone' in response.data
        assert response.data['phone'] == ''
        assert response.data['address'] == ''
        assert response.data['bio'] == ''

    @pytest.mark.parametrize("http_method", ["post", "put", "patch", "delete"])
    def test_unsupported_methods(self, api_client, create_user, http_method):
        user = create_user(username="method_test")
        url = reverse('public-user-profile', kwargs={'username': user.username})
        method_func = getattr(api_client, http_method)
        response = method_func(url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert "detail" in response.data
        assert f'Method "{http_method.upper()}" not allowed.' in str(response.data['detail'])

    def test_user_with_custom_avatar(self, api_client, create_user, settings):
        user = create_user(username="avatar_user")
        avatar_file = SimpleUploadedFile("test-avatar.png", b"file_content", content_type="image/png")
        user.profile.avatar = avatar_file
        user.profile.save()
        url = reverse('public-user-profile', kwargs={'username': user.username})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert settings.MEDIA_URL + "users/avatars/" in response.data['avatar']
        assert response.data['avatar'].endswith(".png")

    def test_different_user_types(self, api_client, create_user):
        staff_user = create_user(username="staff_test_user", is_staff=True)
        superuser = create_user(username="superuser_test_user", is_superuser=True)
        inactive_staff = create_user(username="inactive_staff_test_user", is_staff=True, is_active=False)

        url_staff = reverse('public-user-profile', kwargs={'username': staff_user.username})
        response_staff = api_client.get(url_staff)
        assert response_staff.status_code == status.HTTP_200_OK

        url_superuser = reverse('public-user-profile', kwargs={'username': superuser.username})
        response_superuser = api_client.get(url_superuser)
        assert response_superuser.status_code == status.HTTP_200_OK

        url_inactive_staff = reverse('public-user-profile', kwargs={'username': inactive_staff.username})
        response_inactive_staff = api_client.get(url_inactive_staff)
        assert response_inactive_staff.status_code == status.HTTP_404_NOT_FOUND

    def test_default_field_values(self, api_client, create_user, settings):
        user = create_user(username="default_values_user")
        url = reverse('public-user-profile', kwargs={'username': user.username})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['avatar'] == f'{settings.MEDIA_URL}images/default-avatar.png'
        assert response.data['phone'] == ''
        assert response.data['address'] == ''
        assert response.data['bio'] == ''