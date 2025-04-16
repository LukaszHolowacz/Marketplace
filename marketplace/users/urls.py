from django.urls import path
from .views import (
    UserCreateView,
    UserListView,
    UserProfileUpdateView,
    PublicUserProfileView,
    ChangePasswordView,
    UserDeleteView
)

urlpatterns = [
    path('register/', UserCreateView.as_view(), name='user-create'), 
    path('me/', UserListView.as_view(), name='user-list'), 
    path('profile/', UserProfileUpdateView.as_view(), name='user-profile-update'), 
    path('<str:username>/', PublicUserProfileView.as_view(), name='public-user-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'), 
    path('<int:user_id>/delete/', UserDeleteView.as_view(), name='user-delete'),
]
