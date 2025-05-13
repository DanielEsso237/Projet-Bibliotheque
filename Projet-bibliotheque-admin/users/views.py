from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import LibrarianRegistrationForm, LibrarianLoginForm

def register_view(request):
    if request.method == 'POST':
        form = LibrarianRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Compte bibliothécaire créé avec succès ! Connectez-vous.')
            return redirect('login')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = LibrarianRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LibrarianLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_librarian:
                login(request, user)
                return redirect('librarian_dashboard')
            else:
                messages.error(request, 'Seuls les bibliothécaires peuvent se connecter ici.')
        else:
            messages.error(request, 'Identifiants invalides.')
    else:
        form = LibrarianLoginForm()
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Déconnexion réussie.')
    return redirect('login')