from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SystemSettings
from .forms import SystemSettingsForm
import os

@login_required
def settings_view(request):
    settings = SystemSettings.objects.first()
    log_content = ""
    log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'app.log')
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            log_content = f.read().splitlines()[-10:]  # Dernières 10 lignes
    except FileNotFoundError:
        log_content = ["Fichier de logs non trouvé."]

    if request.method == 'POST':
        form = SystemSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, "Paramètres mis à jour avec succès.")
            return redirect('settings')
    else:
        form = SystemSettingsForm(instance=settings)

    return render(request, 'settings_app/settings.html', {
        'form': form,
        'log_content': log_content,
    })