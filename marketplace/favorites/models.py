from django.db import models

# Create your models here.
class Favorite(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='favorites')
    ad = models.ForeignKey('ads.Ad', on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)