from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from .models import Message
from .serializers import MessageSerializer

class MessageCreateView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Message.objects.all()

class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer    
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(Q(receiver=user) | Q(sender=user)).select_related('sender', 'recipient')

class MessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(Q(receiver=user) | Q(sender=user)).select_related('sender', 'recipient')

    def perform_destroy(self, instance):
        if instance.sender == self.request.user or instance.receiver == self.request.user:
            instance.soft_delete() 
            return Response({"message": "Wiadomość została usunięta."}, status=204)
        return Response({"error": "Brak uprawnień."}, status=403)

    def perform_update(self, serializer):
        instance = serializer.save()
        return Response({"message": "Wiadomość została zaktualizowana."}, status=200)

class MessageReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, id):
        try:
            message = Message.objects.get(id=id, receiver=request.user)
        except Message.DoesNotExist:
            return Response({"error": "Nie znaleziono wiadomości."}, status=404)

        message.is_read = True
        message.save()
        return Response({"message": "Wiadomość oznaczona jako przeczytana."}, status=200)

class MessageByAdView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        ad_id = self.kwargs['ad_id']
        return Message.objects.filter(ad_id=ad_id).select_related('sender', 'recipient')
