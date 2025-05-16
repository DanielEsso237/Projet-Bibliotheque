from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from books.models import Book
from loans.models import Loan
from users.models import CustomUser
from django.utils import timezone

@login_required
def statistics(request):
    if not request.user.is_librarian:
        return render(request, 'library_stats/permission_denied.html', {'message': "Seuls les bibliothécaires peuvent accéder à cette page."})

    # Statistiques sur les livres
    total_books = Book.objects.count()
    available_books = Book.objects.filter(is_available=True).count()
    unavailable_books = total_books - available_books
    top_borrowed_books = Book.objects.annotate(borrow_count=Count('loans')).order_by('-borrow_count')[:5]  # Changé 'loan' en 'loans'

    # Statistiques sur les emprunts
    active_loans = Loan.objects.filter(is_returned=False).count()
    overdue_loans = Loan.objects.filter(is_returned=False, due_date__lt=timezone.now()).count()
    total_loans = Loan.objects.count()

    # Statistiques sur les utilisateurs
    total_users = CustomUser.objects.count()
    librarians = CustomUser.objects.filter(is_librarian=True).count()
    standard_users = total_users - librarians
    top_borrowers = CustomUser.objects.annotate(borrow_count=Count('loans')).order_by('-borrow_count')[:5]  # Changé 'loan' en 'loans'

    context = {
        'total_books': total_books,
        'available_books': available_books,
        'unavailable_books': unavailable_books,
        'top_borrowed_books': top_borrowed_books,
        'active_loans': active_loans,
        'overdue_loans': overdue_loans,
        'total_loans': total_loans,
        'overdue_percentage': (overdue_loans / total_loans * 100) if total_loans > 0 else 0,
        'total_users': total_users,
        'librarians': librarians,
        'standard_users': standard_users,
        'top_borrowers': top_borrowers,
    }

    return render(request, 'library_stats/statistics.html', context)