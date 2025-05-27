from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime
from django.db.models import Q
from .models import Loan
from books.models import Book
from users.models import CustomUser
from django.http import JsonResponse
from settings_app.models import SystemSettings

@login_required
def loan_list(request):
    if not request.user.is_librarian:
        messages.error(request, "Seuls les bibliothécaires peuvent accéder à cette page.")
        return redirect('login')
    
    loans_list = Loan.objects.filter(is_returned=False).select_related('user', 'book').order_by('due_date')

    search_query = request.GET.get('search', '')
    if search_query:
        loans_list = loans_list.filter(
            Q(book__title__icontains=search_query) | Q(user__username__icontains=search_query)
        )

    status = request.GET.get('status', '')
    if status == 'overdue':
        loans_list = loans_list.filter(due_date__lt=timezone.now())
    elif status == 'in_progress':
        loans_list = loans_list.filter(due_date__gte=timezone.now())

    paginator = Paginator(loans_list, 10)
    page_number = request.GET.get('page')
    loans = paginator.get_page(page_number)

    return render(request, 'loans/loan_list.html', {'loans': loans, 'now': timezone.now()})

@login_required
def search_loans_api(request):
    if not request.user.is_librarian:
        return JsonResponse({'loans': []}, status=403)

    loans_list = Loan.objects.filter(is_returned=False).select_related('user', 'book').order_by('due_date')

    search_query = request.GET.get('search', '')
    if search_query:
        loans_list = loans_list.filter(
            Q(book__title__icontains=search_query) | Q(user__username__icontains=search_query)
        )

    status = request.GET.get('status', '')
    if status == 'overdue':
        loans_list = loans_list.filter(due_date__lt=timezone.now())
    elif status == 'in_progress':
        loans_list = loans_list.filter(due_date__gte=timezone.now())

    paginator = Paginator(loans_list, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    loans = [
        {
            'id': loan.id,
            'book_title': loan.book.title,
            'user_username': loan.user.username,
            'loan_date': loan.loan_date.strftime('%d/%m/%Y %H:%M'),
            'due_date': loan.due_date.strftime('%d/%m/%Y %H:%M'),
            'is_overdue': loan.due_date < timezone.now()
        } for loan in page_obj
    ]

    return JsonResponse({
        'loans': loans,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
        'page_range': list(page_obj.paginator.page_range),
        'current_page': page_obj.number,
        'paginator': {'num_pages': page_obj.paginator.num_pages}
    })

@login_required
def return_book(request, loan_id):
    if not request.user.is_librarian:
        messages.error(request, "Seuls les bibliothécaires peuvent effectuer cette action.")
        return redirect('login')
    
    loan = get_object_or_404(Loan, id=loan_id, is_returned=False)
    if request.method == 'POST':
        loan.return_date = timezone.now()
        loan.is_returned = True
        if loan.book.is_physical:
            loan.book.quantity += 1
            loan.book.is_available = loan.book.quantity > 0
            loan.book.save()
        loan.save()
        messages.success(request, f"Le livre '{loan.book.title}' a été rendu avec succès.")
        return redirect('loans:loan_list')
    else:
        return render(request, 'loans/return_book.html', {'loan': loan})

@login_required
def create_loan(request):
    if not request.user.is_librarian:
        messages.error(request, "Seuls les bibliothécaires peuvent effectuer cette action.")
        return redirect('login')
    
    if request.method == 'POST':
        user_id = request.POST.get('user')
        book_ids = request.POST.getlist('book_ids')
        quantities = request.POST.getlist('quantities')
        due_date_str = request.POST.get('due_date')

        # Validation des entrées
        if not user_id:
            messages.error(request, "Veuillez sélectionner un utilisateur.")
            return redirect('loans:create_loan')
        
        if not book_ids or not quantities or len(book_ids) != len(quantities):
            messages.error(request, "Veuillez sélectionner au moins un livre avec une quantité valide.")
            return redirect('loans:create_loan')
        
        try:
            user_id = int(user_id)
            book_ids = [int(book_id) for book_id in book_ids if book_id]
            quantities = [int(qty) for qty in quantities if qty]
        except (ValueError, TypeError):
            messages.error(request, "Identifiants ou quantités invalides.")
            return redirect('loans:create_loan')

        if len(book_ids) != len(quantities):
            messages.error(request, "Le nombre de livres et de quantités ne correspond pas.")
            return redirect('loans:create_loan')

        # Vérifier l'unicité des livres
        if len(set(book_ids)) != len(book_ids):
            messages.error(request, "Chaque livre ne peut être sélectionné qu'une seule fois.")
            return redirect('loans:create_loan')

        if not due_date_str:
            messages.error(request, "Veuillez entrer une date de retour.")
            return redirect('loans:create_loan')
        
        try:
            due_date_naive = datetime.strptime(due_date_str, '%Y-%m-%d')
            due_date = timezone.make_aware(due_date_naive)
            if due_date.date() < timezone.now().date():
                messages.error(request, "La date de retour ne peut pas être dans le passé.")
                return redirect('loans:create_loan')
        except ValueError:
            messages.error(request, "Format de date invalide. Utilisez AAAA-MM-JJ.")
            return redirect('loans:create_loan')

        user = get_object_or_404(CustomUser, id=user_id)
        if user.is_librarian:
            messages.error(request, "Les bibliothécaires ne peuvent pas emprunter de livres.")
            return redirect('loans:create_loan')

        # Vérifier max_loans_per_user
        settings = SystemSettings.objects.first()
        max_loans_per_user = settings.max_loans_per_user if settings else 3
        active_loans_count = Loan.objects.filter(user=user, is_returned=False).count()
        total_new_loans = sum(quantities)
        if active_loans_count + total_new_loans > max_loans_per_user:
            messages.error(request, f"L'utilisateur {user.username} a déjà {active_loans_count} prêt(s) actif(s). " +
                                  f"Avec {total_new_loans} nouveau(x) prêt(s), la limite de {max_loans_per_user} serait dépassée.")
            return redirect('loans:create_loan')

        # Vérifier les livres et leurs quantités
        books = Book.objects.filter(id__in=book_ids, is_physical=True, is_available=True)
        if len(books) != len(book_ids):
            messages.error(request, "Certains livres ne sont pas disponibles ou ne sont pas physiques.")
            return redirect('loans:create_loan')

        # Créer une liste de tuples (book, quantity)
        book_quantities = []
        for book_id, qty in zip(book_ids, quantities):
            book = books.get(id=book_id)
            if qty <= 0:
                messages.error(request, f"La quantité pour '{book.title}' doit être supérieure à 0.")
                return redirect('loans:create_loan')
            if qty > book.quantity:
                messages.error(request, f"Quantité demandée ({qty}) pour '{book.title}' dépasse le stock ({book.quantity}).")
                return redirect('loans:create_loan')
            book_quantities.append((book, qty))

        # Créer les prêts
        errors = []
        loans_created = []
        for book, qty in book_quantities:
            try:
                for _ in range(qty):
                    loan = Loan.objects.create(
                        user=user,
                        book=book,
                        due_date=due_date,
                        loan_date=timezone.now(),
                        is_physical=True
                    )
                    loans_created.append(loan)
                book.quantity -= qty
                book.is_available = book.quantity > 0
                book.save()
            except Exception as e:
                errors.append(f"Erreur lors de l'emprunt de '{book.title}' : {str(e)}")

        if errors:
            for error in errors:
                messages.error(request, error)
            if not loans_created:
                return redirect('loans:create_loan')

        if loans_created:
            messages.success(request, f"{len(loans_created)} emprunt(s) enregistré(s) avec succès pour {user.username}.")
        return redirect('loans:loan_list')

    return render(request, 'loans/create_loan.html')

@login_required
def late_books(request):
    if not request.user.is_librarian:
        messages.error(request, "Seuls les bibliothécaires peuvent accéder à cette page.")
        return redirect('login')

    late_loans = Loan.objects.filter(
        is_returned=False,
        due_date__lt=timezone.now()
    ).select_related('user', 'book').order_by('due_date')

    now = timezone.now()
    loans_with_days_late = []
    for loan in late_loans:
        days_late = (now - loan.due_date).days
        loans_with_days_late.append({
            'loan': loan,
            'days_late': days_late
        })

    paginator = Paginator(loans_with_days_late, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'loans/late_books.html', {
        'loans': page_obj,
        'now': now
    })

@login_required
def search_users_api(request):
    if not request.user.is_librarian:
        return JsonResponse({'users': []}, status=403)

    query = request.GET.get('query', '')
    users = CustomUser.objects.filter(
        is_standard_user=True,
        is_active=True
    )

    if query:
        users = users.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        )

    users_list = [
        {
            'id': user.id,
            'username': user.username,
            'email': user.email
        } for user in users[:10]
    ]

    return JsonResponse({'users': users_list})

@login_required
def search_books_api(request):
    if not request.user.is_librarian:
        return JsonResponse({'books': []}, status=403)

    query = request.GET.get('query', '')
    books = Book.objects.filter(
        is_physical=True,
        is_available=True
    )

    if query:
        books = books.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        )

    books_list = [
        {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'quantity': book.quantity
        } for book in books[:10]
    ]

    return JsonResponse({'books': books_list})