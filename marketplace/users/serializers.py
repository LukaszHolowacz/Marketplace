from rest_framework import serializers
from django.core.validators import validate_email
from .models import CustomUser, UserProfile
import re 

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    email = serializers.EmailField()  
    username = serializers.CharField()

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'first_name', 'last_name',
                  'is_active', 'is_staff', 'date_joined', 'password', 'password2']
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
        
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email jest już zajęty.")
        return value

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Nazwa użytkownika jest już zajęta.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Hasło musi mieć co najmniej 8 znaków.")
        
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Hasło musi zawierać co najmniej jedną cyfrę.")
        
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Hasło musi zawierać co najmniej jedną dużą literę.")
        
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Hasło musi zawierać co najmniej jedną małą literę.")
        
        return value

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Hasła nie są identyczne.")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    avatar = serializers.ImageField(required=False)
    phone = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    bio = serializers.CharField(required=False)

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'avatar', 'phone', 'address', 'bio']

