from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Loan
from books.models import Book
from users.models import CustomUser  # Ajout de l'importation
from django.utils import timezone

@login_required
def loan_list(request):
    if not request.user.is_librarian:
        messages.error(request, "Seuls les bibliothécaires peuvent accéder à cette page.")
        return redirect('login')
    
    loans = Loan.objects.filter(is_returned=False).select_related('user', 'book')
    return render(request, 'loans/loan_list.html', {'loans': loans})

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
        due_date = request.POST.get('due_date')

        user = get_object_or_404(CustomUser, id=user_id)
        book = get_object_or_404(Book, id=book_id)

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
        book.is_available = False
        if book.is_physical:
            book.quantity -= 1
        book.save()
        messages.success(request, f"L'emprunt du livre '{book.title}' pour {user.username} a été enregistré.")
        return redirect('loan_list')

    users = CustomUser.objects.all()
    books = Book.objects.filter(is_available=True)
    return render(request, 'loans/create_loan.html', {'users': users, 'books': books})