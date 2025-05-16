from django.db import models
from django.utils import timezone
from users.models import CustomUser

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    type = models.CharField(max_length=20, choices=[
        ('warning', 'Warning'),
        ('danger', 'Danger'),
        ('info', 'Info')
    ])
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'message', 'type')  # Ajoute cette contrainte d'unicité

    def __str__(self):
        return f"{self.message} ({self.user.username})"

    class Meta:
        ordering = ['-created_at']