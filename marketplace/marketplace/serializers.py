from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from axes.helpers import get_client_ip_address
from axes.handlers.proxy import AxesProxyHandler
import re

User = get_user_model()

class CustomTokenObtainPairSerializer(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        request = self.context.get('request') 
        login = attrs.get('login')
        password = attrs.get('password')

        if not request:
            raise AuthenticationFailed("Brak requestu w kontekście serializera.")

        credentials = {'username': login}

        if not AxesProxyHandler.is_allowed(request, credentials=credentials):
            raise AuthenticationFailed("Za dużo nieudanych prób logowania. Spróbuj później.")

        try:
            if re.match(r"[^@]+@[^@]+\.[^@]+", login): 
                user = User.objects.get(email=login)
            else:
                user = User.objects.get(username=login)
        except User.DoesNotExist:
            AxesProxyHandler.user_login_failed(request, credentials=credentials)
            raise AuthenticationFailed("Nie znaleziono użytkownika.")

        if not user.check_password(password):
            AxesProxyHandler.user_login_failed(request, credentials=credentials)
            raise AuthenticationFailed("Niepoprawne hasło.")

        AxesProxyHandler.user_logged_in(sender=User, request=request, credentials=credentials, user=user)

        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
