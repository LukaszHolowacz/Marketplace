from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from .models import Message
from ads.models import Ad
from .serializers import MessageSerializer
from rest_framework.permissions import BasePermission
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from utils.helpers import ActiveUserVerifier
from django.core.exceptions import PermissionDenied

User = get_user_model()
active_user_verifier = ActiveUserVerifier()

class IsActiveUser(BasePermission):
    def has_permission(self, request, view):
        try:
            active_user_verifier.verify(request.user)
            return True
        except PermissionDenied:
            return False

class AreBothUsersActive(BasePermission):
    def has_permission(self, request, view):
        try:
            active_user_verifier.verify(request.user)
        except PermissionDenied:
            return False
        else:
            try:
                other_user_id = view.kwargs.get('user_id')
                if other_user_id:
                    other_user = get_object_or_404(User, id=other_user_id)
                    return other_user.is_active
                return True
            except Exception:
                return False

    def has_object_permission(self, request, view, obj):
        return True

class MessageCreateByAdView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsActiveUser]
    queryset = Message.objects.all()

    def perform_create(self, serializer):
        ad_id = self.kwargs['ad_id']
        serializer.save(sender=self.request.user, ad_id=ad_id)

class MessageListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsActiveUser]

    def get_queryset(self):
        user = self.request.user
        queryset = Message.objects.filter(Q(receiver=user) | Q(sender=user)).select_related('sender', 'receiver', 'ad')
        return queryset.filter(sender__is_active=True, receiver__is_active=True)

class MessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsActiveUser]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(Q(receiver=user) | Q(sender=user)).select_related('sender', 'receiver').filter(sender__is_active=True, receiver__is_active=True)

    def perform_destroy(self, instance):
        if instance.sender == self.request.user or instance.receiver == self.request.user:
            instance.soft_delete()
            return Response({"message": "Wiadomość została usunięta."}, status=204)
        return Response({"error": "Brak uprawnień."}, status=403)

    def perform_update(self, serializer):
        instance = serializer.save()
        return Response({"message": "Wiadomość została zaktualizowana."}, status=200)

class MessageReadView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsActiveUser]

    def patch(self, request, id):
        try:
            message = Message.objects.get(id=id, recipient=request.user, sender__is_active=True, recipient__is_active=True)
        except Message.DoesNotExist:
            return Response({"error": "Nie znaleziono wiadomości."}, status=404)

        message.is_read = True
        message.save()
        return Response({"message": "Wiadomość oznaczona jako przeczytana."}, status=200)

class MessageByAdAndUserView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, AreBothUsersActive]

    def dispatch(self, request, *args, **kwargs):
        try:
            get_object_or_404(Ad, id=kwargs['ad_id'])
            get_object_or_404(User, id=kwargs['user_id'])
        except Http404:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        ad_id = self.kwargs['ad_id']
        other_user_id = self.kwargs['user_id']
        user_id = self.request.user.id

        queryset1 = Message.objects.filter(
            ad_id=ad_id,
            sender_id=user_id,
            recipient_id=other_user_id
        ).select_related('sender', 'recipient')

        queryset2 = Message.objects.filter(
            ad_id=ad_id,
            recipient_id=user_id,
            sender_id=other_user_id
        ).select_related('sender', 'recipient')

        return queryset1.union(queryset2)