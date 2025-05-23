from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SystemSettings
from .forms import SystemSettingsForm

@login_required
def settings_view(request):
    settings = SystemSettings.objects.first()
    
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
    })