from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from users.models import CustomUser

@login_required
def home(request):
    if not request.user.is_authenticated or not request.user.is_standard_user:
        messages.error(request, "Accès réservé aux utilisateurs standard.")
        return redirect('readers:login')
    return redirect('books:dashboard')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_standard_user = True
            user.is_librarian = False
            user.save()
            messages.success(request, "Inscription réussie ! Vous pouvez maintenant vous connecter.")
            return redirect('readers:login')
        else:
            messages.error(request, "Erreur dans le formulaire.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'readers/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_standard_user:
                login(request, user)
                messages.success(request, "Connexion réussie !")
                return redirect('readers:home')
            else:
                messages.error(request, "Vous n'êtes pas un utilisateur standard.")
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    return render(request, 'readers/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, "Déconnexion réussie.")
    return redirect('readers:login')

@login_required
def notifications_view(request):
    if not request.user.is_standard_user:
        messages.error(request, "Accès réservé aux utilisateurs standard.")
        return redirect('readers:login')
    return render(request, 'readers/notifications.html', {'message': 'Page en cours de développement'})

@login_required
def profile_view(request):
    if not request.user.is_standard_user:
        messages.error(request, "Accès réservé aux utilisateurs standard.")
        return redirect('readers:login')
    return render(request, 'readers/profile.html', {'message': 'Page en cours de développement'})