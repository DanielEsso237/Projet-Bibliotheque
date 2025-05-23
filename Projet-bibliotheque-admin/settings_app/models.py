from django.db import models

class SystemSettings(models.Model):
    notification_cleanup_days = models.PositiveIntegerField(
        default=30,
        help_text="Nombre de jours avant suppression des notifications supprimées"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paramètres du système"
        verbose_name_plural = "Paramètres du système"

    def __str__(self):
        return f"Seuil de nettoyage: {self.notification_cleanup_days} jours"
    

