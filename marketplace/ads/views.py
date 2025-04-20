from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Ad
from .serializers import AdSerializer

class AdListView(generics.ListAPIView):
    serializer_class = AdSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Ad.objects.filter(is_active=True)

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'city', 'street', 'postal_code', 'price']
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at', 'updated_at']
    ordering = ['-created_at']


class AdCreateView(generics.CreateAPIView):
    serializer_class = AdSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AdDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AdSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Ad.objects.all()

    def perform_update(self, serializer):
        if self.request.user != self.get_object().user:
            raise PermissionDenied("Nie masz uprawnień do edycji tego ogłoszenia.")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user != instance.user:
            raise PermissionDenied("Nie masz uprawnień do usunięcia tego ogłoszenia.")
        instance.delete()


class AdToggleActiveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, ad_id):
        try:
            ad = Ad.objects.get(id=ad_id, user=request.user)
        except Ad.DoesNotExist:
            return Response({"error": "Ogłoszenie nie zostało znalezione."}, status=404)

        ad.is_active = not ad.is_active
        ad.save()
        return Response({"message": "Status ogłoszenia został zmieniony."}, status=200)


class AdByCategoryView(generics.ListAPIView):
    serializer_class = AdSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        category_id = self.kwargs.get("category_id")
        return Ad.objects.filter(category_id=category_id, is_active=True)


class AdByUserView(generics.ListAPIView):
    serializer_class = AdSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        return Ad.objects.filter(user_id=user_id, is_active=True)

