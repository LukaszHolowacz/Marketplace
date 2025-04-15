from rest_framework import serializers
from .models import Favorite

class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    ad = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'ad', 'created_at']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'user': {'required': True},
            'ad': {'required': True}
        }

    def validate(self, attrs):
        user = self.context['request'].user
        ad = self.initial_data.get('ad')

        if Favorite.objects.filter(user=user, ad=ad).exists():
            raise serializers.ValidationError("To ogłoszenie jest już dodane do ulubionych.")
        return attrs