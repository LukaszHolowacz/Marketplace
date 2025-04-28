import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.models import CustomUser
from messaging.models import Message
from messaging.serializers import MessageSerializer
from ads.models import Ad
from categories.models import Category
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestMessageByAdAndUserView:
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
        def make_message(sender, recipient, ad_id, **kwargs):
            return Message.objects.create(sender=sender, recipient=recipient, ad_id=ad_id, **kwargs)
        return make_message

    def test_message_by_ad_and_user_view_unauthenticated(self, api_client, create_user, create_ad, create_category):
        user1 = create_user(username='user1')
        ad_id = 5
        create_category(id=1)
        create_ad(id=ad_id, user=user1, category_id=1)
        url = reverse('message-by-ad-and-user', kwargs={'ad_id': ad_id, 'user_id': user1.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_message_by_ad_and_user_view_authenticated(self, api_client, create_user, create_message, create_ad, create_category):
        user1 = create_user(username='user1', is_active=True)
        user2 = create_user(username='user2', is_active=True)
        user3 = create_user(username='user3')
        api_client.force_authenticate(user=user1)
        ad_id_main = 12
        ad_id_other = 20
        create_category(id=2, name='Inna kategoria')
        create_ad(id=ad_id_main, user=user1, category_id=2)
        create_ad(id=ad_id_other, user=user1, category_id=2)

        message1_user1_to_user2 = create_message(sender=user1, recipient=user2, ad_id=ad_id_main, content='Wiadomość 1 do user2')
        message2_user2_to_user1 = create_message(sender=user2, recipient=user1, ad_id=ad_id_main, content='Wiadomość 2 od user2')
        create_message(sender=user1, recipient=user3, ad_id=ad_id_main, content='Wiadomość do innego użytkownika')
        create_message(sender=user1, recipient=user2, ad_id=ad_id_other, content='Wiadomość z innej oferty')

        url = reverse('message-by-ad-and-user', kwargs={'ad_id': ad_id_main, 'user_id': user2.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) == 2

        serializer1 = MessageSerializer(message1_user1_to_user2)
        serializer2 = MessageSerializer(message2_user2_to_user1)
        assert response.data[0] == serializer1.data or response.data[0] == serializer2.data
        assert response.data[1] == serializer1.data or response.data[1] == serializer2.data

        assert 'sender' in response.data[0]
        assert 'recipient' in response.data[0]
        assert 'sender' in response.data[1]
        assert 'recipient' in response.data[1]

    def test_message_by_ad_and_user_view_authenticated_user_blocked(self, api_client, create_user, create_ad, create_category):
        blocked_user = create_user(username='blocked', is_active=False)
        active_user = create_user(username='active', is_active=True)
        api_client.force_authenticate(user=blocked_user)
        ad_id = 25
        create_category(id=3)
        create_ad(id=ad_id, user=active_user, category_id=3)
        url = reverse('message-by-ad-and-user', kwargs={'ad_id': ad_id, 'user_id': active_user.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_message_by_ad_and_user_view_authenticated_other_user_blocked(self, api_client, create_user, create_ad, create_category):
        active_user = create_user(username='active', is_active=True)
        blocked_user = create_user(username='blocked', is_active=False)
        api_client.force_authenticate(user=active_user)
        ad_id = 30
        create_category(id=4)
        create_ad(id=ad_id, user=active_user, category_id=4)
        url = reverse('message-by-ad-and-user', kwargs={'ad_id': ad_id, 'user_id': blocked_user.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_message_by_ad_and_user_view_disallowed_methods(self, api_client, create_user, create_ad, create_category):
        user1 = create_user(username='user1', is_active=True)
        ad_id = 1
        create_category(id=1)
        create_ad(id=ad_id, user=user1, category_id=1)
        url = reverse('message-by-ad-and-user', kwargs={'ad_id': ad_id, 'user_id': user1.id})
        api_client.force_authenticate(user=user1)

        response_post = api_client.post(url)
        assert response_post.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        response_put = api_client.put(url)
        assert response_put.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        response_patch = api_client.patch(url)
        assert response_patch.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        response_delete = api_client.delete(url)
        assert response_delete.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_message_by_ad_and_user_view_no_messages(self, api_client, create_user, create_ad, create_category):
        user1 = create_user(username='user1', is_active=True)
        user2 = create_user(username='user2', is_active=True)
        api_client.force_authenticate(user=user1)
        ad_id = 40
        create_category(id=5)
        create_ad(id=ad_id, user=user1, category_id=5)
        url = reverse('message-by-ad-and-user', kwargs={'ad_id': ad_id, 'user_id': user2.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) == 0

    def test_message_by_ad_and_user_view_non_existent_ad(self, api_client, create_user):
        user1 = create_user(username='user1', is_active=True)
        api_client.force_authenticate(user=user1)
        non_existent_ad_id = 999
        user2 = create_user(username='user2', is_active=True)
        url = reverse('message-by-ad-and-user', kwargs={'ad_id': non_existent_ad_id, 'user_id': user2.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_message_by_ad_and_user_view_non_existent_user(self, api_client, create_user, create_ad, create_category):
        user1 = create_user(username='user1', is_active=True)
        api_client.force_authenticate(user=user1)
        ad_id = 50
        create_category(id=6)
        create_ad(id=ad_id, user=user1, category_id=6)
        non_existent_user_id = 999
        url = reverse('message-by-ad-and-user', kwargs={'ad_id': ad_id, 'user_id': non_existent_user_id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_message_by_ad_and_user_view_multiple_messages(self, api_client, create_user, create_message, create_ad, create_category):
        user1 = create_user(username='user1', is_active=True)
        user2 = create_user(username='user2', is_active=True)
        api_client.force_authenticate(user=user1)
        ad_id = 60
        create_category(id=7)
        create_ad(id=ad_id, user=user1, category_id=7)
        message1 = create_message(sender=user1, recipient=user2, ad_id=ad_id, content='Pierwsza wiadomość')
        message2 = create_message(sender=user2, recipient=user1, ad_id=ad_id, content='Druga wiadomość')
        message3 = create_message(sender=user1, recipient=user2, ad_id=ad_id, content='Trzecia wiadomość')

        url = reverse('message-by-ad-and-user', kwargs={'ad_id': ad_id, 'user_id': user2.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3
        messages_data = [MessageSerializer(msg).data for msg in [message1, message2, message3]]
        for item in response.data:
            assert item in messages_data