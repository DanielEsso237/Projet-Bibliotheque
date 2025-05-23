from django.db import models

class SystemSettings(models.Model):
    notification_cleanup_days = models.PositiveIntegerField(
        default=30,
        help_text="Nombre de jours avant suppression des notifications supprimées"
    )
    low_stock_threshold = models.PositiveIntegerField(
        default=5,
        help_text="Seuil de stock minimum pour alerte de réapprovisionnement"
    )
    loan_warning_days = models.PositiveIntegerField(
        default=2,
        help_text="Jours avant la date de retour pour alerte de retour proche"
    )
    loan_overdue_days = models.PositiveIntegerField(
        default=0,
        help_text="Jours après la date de retour pour alerte de retard"
    )
    max_loans_per_user = models.PositiveIntegerField(
        default=3,
        help_text="Nombre maximum de prêts simultanés par utilisateur"
    )
    loan_duration = models.PositiveIntegerField(
        default=14,
        help_text="Durée standard d’un prêt en jours"
    )
    critical_stock_threshold = models.PositiveIntegerField(
        default=1,
        help_text="Seuil critique pour alerte de stock urgent"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paramètres du système"
        verbose_name_plural = "Paramètres du système"

    def __str__(self):
        return f"Paramètres: nettoyage={self.notification_cleanup_days}j, stock={self.low_stock_threshold}, retour proche={self.loan_warning_days}j, retard={self.loan_overdue_days}j"