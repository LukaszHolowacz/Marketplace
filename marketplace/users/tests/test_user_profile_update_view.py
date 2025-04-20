import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.models import CustomUser, UserProfile

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user():
    def make_user(**kwargs):
        data = {
            "email": "test2@example.com",
            "username": "testuser2",
            "password": "StrongPass1",
        }
        data.update(kwargs)
        user = CustomUser.objects.create_user(**data)
        return user
    return make_user

@pytest.mark.django_db
class TestUserProfileUpdate:

    @pytest.fixture(autouse=True)
    def setup(self, create_user):
        self.user = create_user()
        self.profile = self.user.profile
        self.url = reverse('user-profile-update')

    def test_update_profile_successfully(self, api_client):
        api_client.force_authenticate(user=self.user)
        payload = {
            "username": "updateduser",
            "email": "updated@example.com",
            "phone": "+48123456789",
            "address": "Nowy adres",
            "bio": "Nowe bio użytkownika"
        }

        response = api_client.put(self.url, payload, format='json')

        assert response.status_code == status.HTTP_200_OK
        self.user.refresh_from_db()
        self.profile.refresh_from_db()
        assert self.user.username == "updateduser"
        assert self.user.email == "updated@example.com"
        assert self.profile.phone == "+48123456789"
        assert self.profile.address == "Nowy adres"
        assert self.profile.bio == "Nowe bio użytkownika"

    def test_partial_update_profile_bio_only(self, api_client):
        api_client.force_authenticate(user=self.user)
        payload = {
            "bio": "Zmienione tylko bio"
        }

        response = api_client.patch(self.url, payload, format='json')

        assert response.status_code == status.HTTP_200_OK
        self.profile.refresh_from_db()
        assert self.profile.bio == "Zmienione tylko bio"
        assert self.user.username == "testuser2"
        assert self.user.email == "test2@example.com"
        assert self.profile.phone == ""
        assert self.profile.address == ""

    def test_partial_update_username_only(self, api_client):
        api_client.force_authenticate(user=self.user)
        payload = {
            "username": "newusername"
        }

        response = api_client.patch(self.url, payload, format='json')

        assert response.status_code == status.HTTP_200_OK
        self.user.refresh_from_db()
        assert self.user.username == "newusername"
        assert self.user.email == "test2@example.com"
        assert self.profile.bio == ""
        assert self.profile.phone == ""
        assert self.profile.address == ""

    def test_update_profile_unauthenticated(self, api_client):
        payload = {
            "bio": "Nie powinno przejść"
        }

        response = api_client.patch(self.url, payload, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['detail'] == 'Authentication credentials were not provided.'

    def test_invalid_phone_format(self, api_client):
        api_client.force_authenticate(user=self.user)
        payload = {
            "phone": "123456"
        }

        response = api_client.patch(self.url, payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'phone' in response.data
        assert "Numer telefonu musi być w formacie: '+999999999'. Do 15 cyfr." in str(response.data['phone'][0])

    def test_partial_update_email_only(self, api_client):
        api_client.force_authenticate(user=self.user)
        payload = {
            "email": "new.email@example.com"
        }

        response = api_client.patch(self.url, payload, format='json')

        assert response.status_code == status.HTTP_200_OK
        self.user.refresh_from_db()
        assert self.user.email == "new.email@example.com"
        assert self.user.username == "testuser2"
        assert self.profile.bio == ""
        assert self.profile.phone == ""
        assert self.profile.address == ""

    def test_partial_update_address_only(self, api_client):
        api_client.force_authenticate(user=self.user)
        payload = {
            "address": "Inny adres"
        }

        response = api_client.patch(self.url, payload, format='json')

        assert response.status_code == status.HTTP_200_OK
        self.profile.refresh_from_db()
        assert self.profile.address == "Inny adres"
        assert self.user.username == "testuser2"
        assert self.user.email == "test2@example.com"
        assert self.profile.bio == ""
        assert self.profile.phone == ""

    def test_partial_update_phone_only(self, api_client):
        api_client.force_authenticate(user=self.user)
        payload = {
            "phone": "+48987654321"
        }

        response = api_client.patch(self.url, payload, format='json')

        assert response.status_code == status.HTTP_200_OK
        self.profile.refresh_from_db()
        assert self.profile.phone == "+48987654321"
        assert self.user.username == "testuser2"
        assert self.user.email == "test2@example.com"
        assert self.profile.bio == ""
        assert self.profile.address == ""

    def test_update_email_to_existing_email(self, api_client, create_user):
        other_user = create_user(email="duplicate@example.com", username="otheruser")
        api_client.force_authenticate(user=self.user)
        payload = {"email": "duplicate@example.com"}
        response = api_client.patch(self.url, payload, format='json')

        assert response.status_code == 400
        assert "Email jest już zajęty." in str(response.data['non_field_errors'][0])


    def test_clear_bio(self, api_client):
        self.profile.bio = "Jakiś tekst"
        self.profile.save()
        api_client.force_authenticate(user=self.user)
        payload = {"bio": ""}
        response = api_client.patch(self.url, payload, format='json')
        assert response.status_code == status.HTTP_200_OK
        self.profile.refresh_from_db()
        assert self.profile.bio == ""

    def test_invalid_email_format(self, api_client):
        api_client.force_authenticate(user=self.user)
        payload = {
            "email": "invalid-email-format"
        }
        response = api_client.patch(self.url, payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data
        assert "Enter a valid email address." in str(response.data['email'][0])

    def test_no_changes_in_address(self, api_client):
        api_client.force_authenticate(user=self.user)
        payload = {
            "address": self.profile.address
        }
        response = api_client.patch(self.url, payload, format='json')

        assert response.status_code == status.HTTP_200_OK
        self.profile.refresh_from_db()
        assert self.profile.address == self.profile.address
