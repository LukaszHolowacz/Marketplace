from django.db import models

# Create your models here.
class Message(models.Model):
    sender = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='received_messages')
    ad = models.ForeignKey('ads.Ad', on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"From {self.sender} to {self.recipient} about {self.ad.title}"
    
    class Meta:
        ordering = ['-timestamp']

