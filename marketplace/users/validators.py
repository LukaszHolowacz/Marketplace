import re
from django.core.validators import validate_email 
from rest_framework import serializers
from .models import CustomUser


def validate_unique_email(value, exclude_user=None):
    try:
        validate_email(value)
    except:
        raise serializers.ValidationError("Podaj poprawny adres email.")

    qs = CustomUser.objects.filter(email=value)
    if exclude_user:
        qs = qs.exclude(pk=exclude_user.pk)
    if qs.exists():
        raise serializers.ValidationError("Email jest już zajęty.")
    return value


def validate_unique_username(value, exclude_user=None):
    if len(value) < 2:
        raise serializers.ValidationError("Nazwa użytkownika musi mieć co najmniej 2 znaki.")
    if len(value) > 50:
        raise serializers.ValidationError("Nazwa użytkownika nie może przekraczać 50 znaków.")
    if ' ' in value:
        raise serializers.ValidationError("Nazwa użytkownika nie może zawierać spacji.")

    qs = CustomUser.objects.filter(username=value)
    if exclude_user:
        qs = qs.exclude(pk=exclude_user.pk)
    if qs.exists():
        raise serializers.ValidationError("Nazwa użytkownika jest już zajęta.")
    return value


def validate_password_strength(password):
    if len(password) > 100:
        raise serializers.ValidationError("Hasło nie może być dłuższe niż 100 znaków.")
    if len(password) < 8:
        raise serializers.ValidationError("Hasło musi mieć co najmniej 8 znaków.")
    if not re.search(r'[A-Z]', password):
        raise serializers.ValidationError("Hasło musi zawierać co najmniej jedną dużą literę.")
    if not re.search(r'[a-z]', password):
        raise serializers.ValidationError("Hasło musi zawierać co najmniej jedną małą literę.")
    if not re.search(r'[0-9]', password):
        raise serializers.ValidationError("Hasło musi zawierać co najmniej jedną cyfrę.")
    return password
