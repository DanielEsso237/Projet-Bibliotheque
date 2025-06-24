from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .models import SystemSettings
from .forms import SystemSettingsForm, UserProfileForm

@login_required
def settings_view(request):
    if not request.user.user_type == 'LIBRARIAN':
        messages.error(request, "Seuls les bibliothécaires peuvent accéder à cette page.")
        return redirect('users:login')

    # Récupérer les instances
    settings = SystemSettings.objects.first()
    if settings is None:
        settings = SystemSettings.objects.create()  # Crée une instance par défaut si elle n'existe pas
    user = request.user

    if request.method == 'POST':
        # Gestion du formulaire de profil
        profile_form = UserProfileForm(request.POST, instance=user)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('settings')

        # Gestion du formulaire de paramètres globaux
        settings_form = SystemSettingsForm(request.POST, instance=settings)
        if settings_form.is_valid():
            settings_form.save()
            messages.success(request, "Paramètres mis à jour avec succès.")
            return redirect('settings')

        # Gestion du changement de mot de passe
        password_form = PasswordChangeForm(user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Maintient la session active
            messages.success(request, "Mot de passe mis à jour avec succès.")
            return redirect('settings')
    else:
        profile_form = UserProfileForm(instance=user)
        settings_form = SystemSettingsForm(instance=settings)
        password_form = PasswordChangeForm(user)

    return render(request, 'settings_app/settings_admin.html', {
        'profile_form': profile_form,
        'settings_form': settings_form,
        'password_form': password_form,
    })