from rest_framework import serializers
from django.core.validators import validate_email
from .models import CustomUser, UserProfile
import re

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        max_length=100,
        error_messages={'max_length': 'Hasło nie może być dłuższe niż 100 znaków.'}
    )
    password2 = serializers.CharField(write_only=True)
    email = serializers.EmailField(
        error_messages={'invalid': 'Podaj poprawny adres email.', 'required': 'To pole jest wymagane.'}
    )
    username = serializers.CharField(
        error_messages={'required': 'To pole jest wymagane.'}
    )
    first_name = serializers.CharField(
        required=False,
        max_length=50,
        error_messages={'max_length': 'Imię nie może mieć więcej niż 50 znaków.'}
    )
    last_name = serializers.CharField(
        required=False,
        max_length=50,
        error_messages={'max_length': 'Nazwisko nie może mieć więcej niż 50 znaków.'}
    )

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'first_name', 'last_name',
                  'is_active', 'is_staff', 'date_joined', 'password', 'password2']
        read_only_fields = ['id', 'date_joined']
        extra_kwargs = {
            'password': {'write_only': True},
            'password2': {'write_only': True},
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
        if len(value) < 2:
            raise serializers.ValidationError("Nazwa użytkownika musi mieć co najmniej 2 znaki.")
        if len(value) > 50:
            raise serializers.ValidationError("Nazwa użytkownika nie może przekraczać 50 znaków.")

        if ' ' in value:
            raise serializers.ValidationError("Nazwa użytkownika nie może zawierać spacji.")

        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Nazwa użytkownika jest już zajęta.")

        return value

    def validate_password(self, value):
        if len(value) > 100:
            raise serializers.ValidationError("Hasło nie może być dłuższe niż 100 znaków.")
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


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(
        write_only=True,
        max_length=100,
        error_messages={'max_length': 'Nowe hasło nie może być dłuższe niż 100 znaków.'}
    )

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Stare hasło jest niepoprawne.")
        return value

    def validate_new_password(self, value):
        if len(value) > 100:
            raise serializers.ValidationError("Nowe hasło nie może być dłuższe niż 100 znaków.")
        if len(value) < 8:
            raise serializers.ValidationError("Hasło musi mieć co najmniej 8 znaków.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Hasło musi zawierać dużą literę.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Hasło musi zawierać małą literę.")
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Hasło musi zawierać cyfrę.")
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user