from django.urls import path
from .views import (
    MessageCreateByAdView,
    MessageListView,
    MessageDetailView,
    MessageReadView,
    MessageByAdAndUserView,
)

urlpatterns = [
    path('', MessageListView.as_view(), name='message-list'),
    path('by-ad/<int:ad_id>/create/', MessageCreateByAdView.as_view(), name='message-create-by-ad'),
    path('<int:id>/', MessageDetailView.as_view(), name='message-detail'),
    path('<int:id>/read/', MessageReadView.as_view(), name='message-mark-read'),
    path('by-ad/<int:ad_id>/user/<int:user_id>/', MessageByAdAndUserView.as_view(), name='message-by-ad-and-user'),
]