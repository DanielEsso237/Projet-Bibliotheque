from django.contrib.auth import authenticate, login, logout
from .forms import LibrarianRegistrationForm, LibrarianLoginForm, UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import CustomUser
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import update_session_auth_hash
from django.utils.text import slugify

def register_view(request):
    if request.method == 'POST':
        form = LibrarianRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Compte bibliothécaire créé avec succès ! Connectez-vous.')
            return redirect('users:login')
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
            login(request, user)
            
            # Redirection en fonction du type d'utilisateur
            if user.user_type == 'LIBRARIAN':
                return redirect('books:librarian_dashboard')
            else:  # Étudiant ou Professeur
                if user.first_login:
                    return render(request, 'users/login.html', {
                        'form': PasswordChangeForm(user),
                        'show_password_modal': True,
                        'user': user
                    })
                return redirect('books:standard_user_dashboard')
        else:
            messages.error(request, 'Identifiants invalides.')
    else:
        form = LibrarianLoginForm()
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Déconnexion réussie.')
    return redirect('users:login')

@login_required
def manage_users(request):
    if not request.user.user_type == 'LIBRARIAN':
        messages.error(request, "Seuls les bibliothécaires peuvent accéder à cette page.")
        return redirect('users:login')

    users_list = CustomUser.objects.all().order_by('username')

    # Recherche
    search_query = request.GET.get('search', '')
    if search_query:
        users_list = users_list.filter(
            Q(username__icontains=search_query) | Q(email__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(users_list, 10)  # 10 utilisateurs par page
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)

    return render(request, 'users/manage_users.html', {
        'users': users,
    })

@login_required
def create_user(request):
    if not request.user.user_type == 'LIBRARIAN':
        messages.error(request, "Seuls les bibliothécaires peuvent créer des utilisateurs.")
        return redirect('users:login')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            # Générer un username unique au format nom.prenomXXX
            base_username = f"{slugify(user.last_name)}.{slugify(user.first_name)}"
            counter = 1
            while True:
                username = f"{base_username}{counter:03d}"
                if not CustomUser.objects.filter(username=username).exists():
                    break
                counter += 1
            user.username = username
            
            # Définir un mot de passe par défaut
            default_password = "bibliotheque2025"
            user.password = make_password(default_password)
            user.first_login = True
            
            try:
                user.save()
                messages.success(request, f"Le compte {user.username} a été créé avec succès. Mot de passe par défaut: {default_password}")
                return redirect('users:manage_users')
            except Exception as e:
                messages.error(request, f"Erreur lors de la création de l'utilisateur: {str(e)}")
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = UserCreationForm()

    return render(request, 'users/create_user.html', {'form': form})

@login_required
def update_user(request, user_id):
    if not request.user.user_type == 'LIBRARIAN':
        messages.error(request, "Seuls les bibliothécaires peuvent effectuer cette action.")
        return redirect('users:login')

    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        user_type = request.POST.get('user_type')  

        user.username = username
        user.email = email
        user.user_type = user_type  
        user.save()
        messages.success(request, f"L'utilisateur {username} a été mis à jour.")
        return redirect('users:manage_users')

    return render(request, 'users/manage_users.html', {'user': user})

@login_required
def delete_user(request, user_id):
    if not request.user.user_type == 'LIBRARIAN':
        messages.error(request, "Seuls les bibliothécaires peuvent effectuer cette action.")
        return redirect('users:login')

    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        # Empêcher la suppression si c'est le dernier bibliothécaire
        if user.user_type == 'LIBRARIAN':
            librarian_count = CustomUser.objects.filter(user_type='LIBRARIAN').count()
            if librarian_count <= 1:
                messages.error(request, "Vous ne pouvez pas supprimer le dernier bibliothécaire.")
                return redirect('users:manage_users')

        username = user.username
        user.delete()
        messages.success(request, f"L'utilisateur {username} a été supprimé.")
        return redirect('users:manage_users')

    return render(request, 'users/manage_users.html', {'user': user})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            user.first_login = False
            user.save()
            messages.success(request, 'Votre mot de passe a été changé avec succès!')
            if request.user.user_type == 'LIBRARIAN':
                return redirect('books:librarian_dashboard')
            else:
                return redirect('books:standard_user_dashboard')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'users/change_password.html', {'form': form})