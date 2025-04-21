# views.py
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from rest_framework.response import Response

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except AuthenticationFailed as e:
            if e.detail.code == 'user_inactive':
                return Response({'detail': 'Konto użytkownika jest zablokowane.'}, status=status.HTTP_400_BAD_REQUEST)
            raise 

        return Response(serializer.validated_data, status=status.HTTP_200_OK)