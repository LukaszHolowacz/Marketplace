from rest_framework import serializers
from .models import Ad

class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = [
            'id', 'title', 'description', 'price', 'created_at', 'updated_at',
            'is_active', 'image', 'user', 'category', 'location'
        ]
        read_only_fields = ['created_at', 'updated_at', 'user']
        extra_kwargs = {
            'price': {'required': True, 'min_value': 5.00},  
            'image': {'required': False}
        }
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Cena musi być większa niż 0.")
        return value
