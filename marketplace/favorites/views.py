from rest_framework import generics, permissions, status
from django.shortcuts import get_object_or_404
from .models import Favorite
from .serializers import FavoriteSerializer
from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.
class FavoriteListCreateView(generics.ListCreateAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FavoriteRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)
    

class FavoriteDeleteByAdView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, ad_id):
        favorite = get_object_or_404(Favorite, user=request.user, ad_id=ad_id)
        favorite.delete()
        return Response({"message": "Ulubione ogłoszenie zostało usunięte pomyślnie."}, status=status.HTTP_204_NO_CONTENT)
    

class FavoriteCheckView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, ad_id):
        favorite = Favorite.objects.filter(user=request.user, ad_id=ad_id).exists()
        return Response({"is_favorite": favorite}, status=status.HTTP_200_OK)
