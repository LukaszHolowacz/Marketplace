from django.urls import path
from .views import (
    UserCreateView,
    MeView,
    UserProfileUpdateView,
    PublicUserProfileView,
    ChangePasswordView,
    UserDeleteView,
)

urlpatterns = [
    path('register/', UserCreateView.as_view(), name='user-create'), 
    path('me/', MeView.as_view(), name='user-me'), 
    path('profile/', UserProfileUpdateView.as_view(), name='user-profile-update'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'), 
    path('<int:user_id>/delete/', UserDeleteView.as_view(), name='user-delete'),
    path('<str:username>/', PublicUserProfileView.as_view(), name='public-user-profile'),
]
