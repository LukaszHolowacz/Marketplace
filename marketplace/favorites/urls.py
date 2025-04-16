from django.urls import path
from .views import (
    FavoriteListCreateView, 
    FavoriteRetrieveUpdateDestroyView, 
    FavoriteDeleteByAdView, 
    FavoriteCheckView
)

urlpatterns = [
    path('', FavoriteListCreateView.as_view(), name='favorite-list-create'),
    path('<int:pk>/', FavoriteRetrieveUpdateDestroyView.as_view(), name='favorite-detail'),
    path('by-ad/<int:ad_id>/', FavoriteDeleteByAdView.as_view(), name='favorite-delete-by-ad'),
    path('check/<int:ad_id>/', FavoriteCheckView.as_view(), name='favorite-check-by-ad'),
]
