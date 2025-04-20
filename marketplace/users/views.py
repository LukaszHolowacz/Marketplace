from rest_framework import generics, permissions
from .models import CustomUser, UserProfile
from .serializers import UserSerializer, UserProfileSerializer, ChangePasswordSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from rest_framework import status
from django.contrib.auth import update_session_auth_hash
import logging

logger = logging.getLogger(__name__)

class UserCreateView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    queryset = CustomUser.objects.all()


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserProfileUpdateView(generics.UpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        try:
            profile = self.request.user.profile
            logger.info(f"Pobrano profil użytkownika: {profile.user.username}")
            return profile
        except UserProfile.DoesNotExist:
            raise NotFound("Profil użytkownika nie istnieje.")

    def update(self, request, *args, **kwargs):
        logger.info(f"Dane żądania PUT/PATCH: {request.data}")
        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        logger.info(f"Dane serializatora przed zapisem: {serializer.validated_data}")
        serializer.save()
        logger.info(f"Dane serializatora po zapisie: {serializer.instance.user.username}, {serializer.instance.user.email}")


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
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        update_session_auth_hash(request, request.user)
        return Response({"detail": "Hasło zostało zmienione."})

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