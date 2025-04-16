from django.db import models

class Ad(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='ads/images/', blank=True, null=True)
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='ads')
    category = models.ForeignKey('categories.Category', on_delete=models.CASCADE, related_name='ads')
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['price']),  
            models.Index(fields=['created_at']), 
        ]
    
    def __str__(self):
        return self.title
