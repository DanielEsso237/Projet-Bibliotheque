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
        loan.book.is_available = True
        if loan.book.is_physical:
            loan.book.quantity += 1
        loan.book.save()
        loan.save()
        messages.success(request, f"Le livre '{loan.book.title}' a été rendu avec succès.")
        return redirect('loan_list')
    
    return render(request, 'loans/return_book.html', {'loan': loan})

@login_required
def create_loan(request):
    if not request.user.is_librarian:
        messages.error(request, "Seuls les bibliothécaires peuvent effectuer cette action.")
        return redirect('login')
    
    if request.method == 'POST':
        user_id = request.POST.get('user')
        book_id = request.POST.get('book')
        due_date_str = request.POST.get('due_date')

        user = get_object_or_404(CustomUser, id=user_id)
        book = get_object_or_404(Book, id=book_id)

        # Convertir due_date en datetime conscient
        try:
            due_date_naive = datetime.strptime(due_date_str, '%Y-%m-%d')
            due_date = timezone.make_aware(due_date_naive)
        except ValueError:
            messages.error(request, "Format de date invalide. Utilisez AAAA-MM-JJ.")
            return redirect('create_loan')

        if not book.is_physical:
            messages.error(request, "Seuls les livres physiques peuvent être empruntés.")
            return redirect('create_loan')
        
        if not book.is_available:
            messages.error(request, "Ce livre n'est pas disponible pour l'emprunt.")
            return redirect('create_loan')
        
        if book.is_physical and book.quantity <= 0:
            messages.error(request, "Aucun exemplaire physique disponible pour cet emprunt.")
            return redirect('create_loan')

        loan = Loan.objects.create(
            user=user,
            book=book,
            due_date=due_date,
            loan_date=timezone.now()
        )
        book.quantity -= 1
        if book.quantity == 0:
            book.is_available = False
        book.save()
        messages.success(request, f"L'emprunt du livre '{book.title}' pour {user.username} a été enregistré.")
        return redirect('loan_list')

    users = CustomUser.objects.filter(is_standard_user=True)
    books = Book.objects.filter(is_physical=True, is_available=True)
    return render(request, 'loans/create_loan.html', {'users': users, 'books': books})

@login_required
def late_books(request):
    if not request.user.is_librarian:
        messages.error(request, "Seuls les bibliothécaires peuvent accéder à cette page.")
        return redirect('login')

    # Liste des emprunts en retard (due_date < maintenant et non rendus)
    late_loans = Loan.objects.filter(
        is_returned=False,
        due_date__lt=timezone.now()
    ).select_related('user', 'book').order_by('due_date')

    # Calculer les jours de retard pour chaque prêt
    now = timezone.now()
    loans_with_days_late = []
    for loan in late_loans:
        days_late = (now - loan.due_date).days
        loans_with_days_late.append({
            'loan': loan,
            'days_late': days_late
        })

    # Pagination
    paginator = Paginator(loans_with_days_late, 10)  # 10 emprunts par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'loans/late_books.html', {
        'loans': page_obj,
        'now': now
    })