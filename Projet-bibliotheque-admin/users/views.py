from django.contrib.auth import authenticate, login, logout
from .forms import LibrarianRegistrationForm, LibrarianLoginForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import CustomUser
from django.http import JsonResponse

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
                return redirect('books:librarian_dashboard')  # Ajout de l'espace de noms
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

@login_required
def manage_users(request):
    if not request.user.is_librarian:
        messages.error(request, "Seuls les bibliothécaires peuvent accéder à cette page.")
        return redirect('login')

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
def update_user(request, user_id):
    if not request.user.is_librarian:
        messages.error(request, "Seuls les bibliothécaires peuvent effectuer cette action.")
        return redirect('login')

    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        is_librarian = request.POST.get('is_librarian') == 'yes'

        user.username = username
        user.email = email
        user.is_librarian = is_librarian
        user.save()
        messages.success(request, f"L'utilisateur {username} a été mis à jour.")
        return redirect('manage_users')

    return render(request, 'users/manage_users.html', {'user': user})

@login_required
def delete_user(request, user_id):
    if not request.user.is_librarian:
        messages.error(request, "Seuls les bibliothécaires peuvent effectuer cette action.")
        return redirect('login')

    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        # Empêcher la suppression si c'est le dernier bibliothécaire
        if user.is_librarian:
            librarian_count = CustomUser.objects.filter(is_librarian=True).count()
            if librarian_count <= 1:
                messages.error(request, "Vous ne pouvez pas supprimer le dernier bibliothécaire.")
                return redirect('manage_users')

        username = user.username
        user.delete()
        messages.success(request, f"L'utilisateur {username} a été supprimé.")
        return redirect('manage_users')

    return render(request, 'users/manage_users.html', {'user': user})