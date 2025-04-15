from rest_framework import serializers
from .models import Message

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField(read_only=True)
    recipient = serializers.StringRelatedField(read_only=True)
    ad = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'recipient', 'ad', 'content', 'timestamp', 'is_read']
        read_only_fields = ['id', 'sender', 'timestamp', 'is_read']
        extra_kwargs = {
            'content': {'required': True},
            'recipient': {'required': True},
            'ad': {'required': True}
        }

    def validate(self, attrs):
        sender = self.context['request'].user
        recipient = attrs.get('recipient')
        ad = attrs.get('ad')
        content = attrs.get('content')
        if not recipient:
            raise serializers.ValidationError("Odbiorca wiadomości jest wymagany.")
        if not ad:
            raise serializers.ValidationError("Ogłoszenie jest wymagane.")
        if ad and not ad.is_active:
            raise serializers.ValidationError("Ogłoszenie jest nieaktywne.")
        if not content:
            raise serializers.ValidationError("Treść wiadomości jest wymagana.")
        if sender == recipient:
            raise serializers.ValidationError("Nie możesz wysłać wiadomości do siebie.")
        return attrs

    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)
