from rest_framework import serializers
from django.core.validators import validate_email
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined']
        read_only_fields = ['id', 'date_joined']
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'is_active': {'required': False},
            'is_staff': {'required': False},
        }

    def validate_email(self, value):
        try:
            validate_email(value)
        except:
            raise serializers.ValidationError("Podaj poprawny adres email.")
        
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email jest już zajęty.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Nazwa użytkownika jest już zajęta.")
        return value
