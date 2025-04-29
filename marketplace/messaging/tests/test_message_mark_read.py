import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.models import CustomUser
from messaging.models import Message
from ads.models import Ad
from categories.models import Category
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestMessageReadView:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def create_user(self):
        def make_user(**kwargs):
            kwargs.setdefault('email', f"{kwargs.get('username', 'testuser')}@example.com")
            kwargs.setdefault('password', 'testpassword')
            return User.objects.create_user(**kwargs)
        return make_user

    @pytest.fixture
    def create_category(self):
        def make_category(id, name='Testowa kategoria', **kwargs):
            return Category.objects.create(id=id, name=name, **kwargs)
        return make_category

    @pytest.fixture
    def create_ad(self, create_user):
        def make_ad(id, user=None, title='Testowa oferta', price=10.0, category_id=1, **kwargs):
            if user is None:
                user = create_user()
            return Ad.objects.create(id=id, user=user, title=title, price=price, category_id=category_id, **kwargs)
        return make_ad

    @pytest.fixture
    def create_message(self, create_user):
        def make_message(sender, recipient, ad_id, is_read=False, **kwargs):
            return Message.objects.create(sender=sender, recipient=recipient, ad_id=ad_id, is_read=is_read, **kwargs)
        return make_message

    def test_message_read_view_unauthenticated(self, api_client, create_user, create_message, create_ad, create_category):
        user1 = create_user(username='user1', is_active=True)
        user2 = create_user(username='user2', is_active=True)
        ad_id = 1
        create_category(id=1)
        create_ad(id=ad_id, user=user1, category_id=1)
        message = create_message(sender=user1, recipient=user2, ad_id=ad_id)
        url = reverse('message-mark-read', kwargs={'id': message.id})
        response = api_client.patch(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_message_read_view_authenticated_success(self, api_client, create_user, create_message, create_ad, create_category):
        user1 = create_user(username='user1', is_active=True)
        user2 = create_user(username='user2', is_active=True)
        api_client.force_authenticate(user=user2)
        ad_id = 2
        create_category(id=2)
        create_ad(id=ad_id, user=user1, category_id=2)
        message = create_message(sender=user1, recipient=user2, ad_id=ad_id, is_read=False)
        url = reverse('message-mark-read', kwargs={'id': message.id})
        response = api_client.patch(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"message": "Wiadomość oznaczona jako przeczytana."}
        message.refresh_from_db()
        assert message.is_read

    def test_message_read_view_message_not_found(self, api_client, create_user):
        user1 = create_user(username='user1', is_active=True)
        api_client.force_authenticate(user=user1)
        non_existent_message_id = 999
        url = reverse('message-mark-read', kwargs={'id': non_existent_message_id})
        response = api_client.patch(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data == {"error": "Nie znaleziono wiadomości."}

    def test_message_read_view_wrong_receiver(self, api_client, create_user, create_message, create_ad, create_category):
        user1 = create_user(username='user1', is_active=True)
        user2 = create_user(username='user2', is_active=True)
        user3 = create_user(username='user3', is_active=True)
        api_client.force_authenticate(user=user3) 
        ad_id = 3
        create_category(id=3)
        create_ad(id=ad_id, user=user1, category_id=3)
        message = create_message(sender=user1, recipient=user2, ad_id=ad_id, is_read=False)
        url = reverse('message-mark-read', kwargs={'id': message.id})
        response = api_client.patch(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data == {"error": "Nie znaleziono wiadomości."}
        message.refresh_from_db()
        assert not message.is_read

    def test_message_read_view_sender_inactive(self, api_client, create_user, create_message, create_ad, create_category):
        user1 = create_user(username='user1', is_active=False)  
        user2 = create_user(username='user2', is_active=True)
        api_client.force_authenticate(user=user2)
        ad_id = 4
        create_category(id=4)
        create_ad(id=ad_id, user=user1, category_id=4)
        message = create_message(sender=user1, recipient=user2, ad_id=ad_id, is_read=False)
        url = reverse('message-mark-read', kwargs={'id': message.id})
        response = api_client.patch(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data == {"error": "Nie znaleziono wiadomości."}
        message.refresh_from_db()
        assert not message.is_read

    def test_message_read_view_receiver_inactive(self, api_client, create_user, create_message, create_ad, create_category):
        user1 = create_user(username='user1', is_active=True)
        user2 = create_user(username='user2', is_active=False)
        api_client.force_authenticate(user=user2)
        ad_id = 5
        create_category(id=5)
        create_ad(id=ad_id, user=user1, category_id=5)
        message = create_message(sender=user1, recipient=user2, ad_id=ad_id, is_read=False)
        url = reverse('message-mark-read', kwargs={'id': message.id})
        response = api_client.patch(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['detail'] == 'Twoje konto jest zablokowane.'
        message.refresh_from_db()
        assert not message.is_read


    def test_message_read_view_authenticated_user_inactive(self, api_client, create_user, create_message, create_ad, create_category):
        user1 = create_user(username='user1', is_active=True)
        user2 = create_user(username='user2', is_active=True)
        inactive_user = create_user(username='inactive', is_active=False)
        api_client.force_authenticate(user=inactive_user)
        ad_id = 6
        create_category(id=6)
        create_ad(id=ad_id, user=user1, category_id=6)
        message = create_message(sender=user1, recipient=user2, ad_id=ad_id, is_read=False)
        url = reverse('message-mark-read', kwargs={'id': message.id})
        response = api_client.patch(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_message_read_view_disallowed_methods(self, api_client, create_user, create_message, create_ad, create_category):
        user1 = create_user(username='user1', is_active=True)
        user2 = create_user(username='user2', is_active=True)
        api_client.force_authenticate(user=user2)
        ad_id = 7
        create_category(id=7)
        create_ad(id=ad_id, user=user1, category_id=7)
        message = create_message(sender=user1, recipient=user2, ad_id=ad_id, is_read=False)
        url = reverse('message-mark-read', kwargs={'id': message.id})

        response_get = api_client.get(url)
        assert response_get.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        response_post = api_client.post(url)
        assert response_post.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        response_put = api_client.put(url)
        assert response_put.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        response_delete = api_client.delete(url)
        assert response_delete.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
