from django.urls import path
from .views import (
    AdListView,
    AdCreateView,
    AdDetailView,
    AdToggleActiveView,
    AdByCategoryView,
    AdByUserView
)

urlpatterns = [
    path('', AdListView.as_view(), name='ad-list'),
    path('create/', AdCreateView.as_view(), name='ad-create'), 
    path('<int:pk>/', AdDetailView.as_view(), name='ad-detail'),
    path('<int:ad_id>/toggle-active/', AdToggleActiveView.as_view(), name='ad-toggle-active'),
    path('category/<int:category_id>/', AdByCategoryView.as_view(), name='ad-by-category'),
    path('user/<int:user_id>/', AdByUserView.as_view(), name='ad-by-user'),
]
