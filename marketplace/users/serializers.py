from rest_framework import serializers
from django.core.validators import RegexValidator
from .models import CustomUser, UserProfile
from .validators import (
    validate_unique_email,
    validate_unique_username,
    validate_password_strength
)


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
        return validate_unique_email(value)

    def validate_username(self, value):
        return validate_unique_username(value)

    def validate_password(self, value):
        return validate_password_strength(value)

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
    username = serializers.CharField(source='user.username', required=False)
    email = serializers.EmailField(source='user.email', required=False)
    avatar = serializers.ImageField(required=False)

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Numer telefonu musi być w formacie: '+999999999'. Do 15 cyfr."
    )
    phone = serializers.CharField(validators=[phone_regex], required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    bio = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'avatar', 'phone', 'address', 'bio']

    def validate(self, data):
        user_data = data.get('user', {})
        request_user = self.instance.user if self.instance else None

        email = user_data.get('email')
        if email:
            validate_unique_email(email, exclude_user=request_user)

        username = user_data.get('username')
        if username:
            validate_unique_username(username, exclude_user=request_user)

        return data

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})

        for attr in ['phone', 'address', 'bio', 'avatar']:
            if attr in validated_data:
                setattr(instance, attr, validated_data[attr])
        instance.save()

        user = instance.user
        for attr in ['username', 'email']:
            if attr in user_data:
                setattr(user, attr, user_data[attr])
        user.save()

        return instance


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
        return validate_password_strength(value)

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
