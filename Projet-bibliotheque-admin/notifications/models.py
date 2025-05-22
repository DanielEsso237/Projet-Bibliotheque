from django.db import models
from django.utils import timezone
from users.models import CustomUser
import hashlib

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    type = models.CharField(max_length=20, choices=[
        ('warning', 'Warning'),
        ('danger', 'Danger'),
        ('info', 'Info')
    ])
    is_read = models.BooleanField(default=False)
    unique_identifier = models.CharField(max_length=64, default='', editable=False)
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.unique_identifier:
            self.unique_identifier = hashlib.sha256(self.message.encode('utf-8')).hexdigest()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.message} ({self.user.username})"

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'unique_identifier', 'type'],
                name='unique_notification'
            )
        ]

class DeletedNotification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='deleted_notifications')
    unique_identifier = models.CharField(max_length=64)
    type = models.CharField(max_length=20)
    deleted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'unique_identifier', 'type'],
                name='unique_deleted_notification'
            )
        ]