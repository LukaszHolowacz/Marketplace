from django.urls import path
from .views import (
    MessageCreateView,
    MessageListView,
    MessageDetailView,
    MessageReadView,
    MessageByAdView
)

urlpatterns = [
    path('', MessageListView.as_view(), name='message-list'), 
    path('create/', MessageCreateView.as_view(), name='message-create'), 
    path('<int:id>/', MessageDetailView.as_view(), name='message-detail'), 
    path('<int:id>/read/', MessageReadView.as_view(), name='message-mark-read'), 
    path('by-ad/<int:ad_id>/', MessageByAdView.as_view(), name='message-by-ad'),  
]
