from rest_framework import generics, permissions
from .models import CustomUser, UserProfile
from .serializers import UserSerializer, UserProfileSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from rest_framework import status
from django.contrib.auth import update_session_auth_hash
import re


class UserCreateView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    queryset = CustomUser.objects.all()


class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CustomUser.objects.all()
    

class UserProfileUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = UserProfile.objects.all()


class PublicUserProfileView(generics.GenericAPIView):
    permission_classes = []  

    def get(self, request, username):
        try:
            user = CustomUser.objects.get(username=username)
            profile = UserProfile.objects.get(user=user)
        except CustomUser.DoesNotExist:
            raise NotFound(detail="Użytkownik nie znaleziony")
        except UserProfile.DoesNotExist:
            profile = None 

        serialized_data = UserProfileSerializer(profile or user.profile).data

        return Response(serialized_data)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not user.check_password(old_password):
            return Response({"detail": "Stare hasło jest niepoprawne."}, status=400)

        if len(new_password) < 8:
            return Response({"detail": "Nowe hasło musi mieć co najmniej 8 znaków."}, status=400)
        if not re.search(r'[A-Z]', new_password):
            return Response({"detail": "Nowe hasło musi zawierać co najmniej jedną wielką literę."}, status=400)
        if not re.search(r'[a-z]', new_password):
            return Response({"detail": "Nowe hasło musi zawierać co najmniej jedną małą literę."}, status=400)
        if not re.search(r'[0-9]', new_password):
            return Response({"detail": "Nowe hasło musi zawierać co najmniej jedną cyfrę."}, status=400)

        user.set_password(new_password)
        user.save()

        update_session_auth_hash(request, user)

        return Response({"detail": "Hasło zostało pomyślnie zmienione."}, status=200)

class UserDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, user_id):
        try:
            user = get_user_model().objects.get(id=user_id)
        except get_user_model().DoesNotExist:
            raise NotFound(detail="Użytkownik nie został znaleziony")

        if request.user.is_staff or request.user == user:
            user.delete()
            return Response({"message": "Użytkownik został usunięty."}, status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Brak uprawnień do usunięcia tego użytkownika."}, status=status.HTTP_403_FORBIDDEN)