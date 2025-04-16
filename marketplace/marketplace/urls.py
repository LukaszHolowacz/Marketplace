from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # JWT Auth
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # API Endpoints
    path('api/users/', include('users.urls')),
    path('api/categories/', include('categories.urls')),
    path('api/ads/', include('ads.urls')),
    path('api/favorites/', include('favorites.urls')),
    path('api/messages/', include('messaging.urls')),
]
