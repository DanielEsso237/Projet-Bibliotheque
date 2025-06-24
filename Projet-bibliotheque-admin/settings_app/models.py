from django.db import models

class SystemSettings(models.Model):
    notifications_enabled = models.BooleanField(default=True, help_text="Activer/Désactiver les notifications globales")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paramètres du système"
        verbose_name_plural = "Paramètres du système"

    def __str__(self):
        return f"Paramètres: notifications={self.notifications_enabled}"