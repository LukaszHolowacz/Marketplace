from rest_framework import generics, permissions
from .models import CustomUser, UserProfile
from .serializers import UserSerializer, UserProfileSerializer, ChangePasswordSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from django.contrib.auth import get_user_model
from rest_framework import status
from django.contrib.auth import update_session_auth_hash
import logging
from utils.helpers import ActiveUserVerifier  

logger = logging.getLogger(__name__)
active_user_verifier = ActiveUserVerifier() 

class UserCreateView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    queryset = CustomUser.objects.all()


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user = self.request.user
        active_user_verifier.verify(user) 
        return user


class UserProfileUpdateView(generics.UpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user = self.request.user
        active_user_verifier.verify(user) 
        try:
            profile = user.profile
            logger.info(f"Pobrano profil użytkownika: {profile.user.username}")
            return profile
        except UserProfile.DoesNotExist:
            raise NotFound("Profil użytkownika nie istnieje.")

    def update(self, request, *args, **kwargs):
        user = request.user
        active_user_verifier.verify(user)  
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
            if not user.is_active and request.user != user and not request.user.is_staff:
                raise NotFound(detail="Użytkownik nie znaleziony") 
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
        active_user_verifier.verify(user)  
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        update_session_auth_hash(request, request.user)
        return Response({"detail": "Hasło zostało zmienione."})

class UserDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, user_id):
        requesting_user = request.user
        active_user_verifier.verify(requesting_user)  

        try:
            user_to_delete = get_user_model().objects.get(id=user_id)
        except get_user_model().DoesNotExist:
            raise NotFound(detail="Użytkownik nie został znaleziony")

        if requesting_user.is_staff or requesting_user == user_to_delete:
            user_to_delete.delete()
            return Response({"message": "Użytkownik został usunięty."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Brak uprawnień do usunięcia tego użytkownika."}, status=status.HTTP_403_FORBIDDEN)