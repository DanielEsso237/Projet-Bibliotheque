# library_stats/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from books.models import Book
from loans.models import Loan
from users.models import CustomUser
from django.utils import timezone
import json
from django.db.models.functions import TruncMonth  # Pour regrouper par mois
from datetime import datetime, timedelta

@login_required
def statistics(request):
    if not request.user.is_librarian:
        return render(request, 'library_stats/permission_denied.html', {'message': "Seuls les bibliothécaires peuvent accéder à cette page."})

    # Statistiques sur les livres
    book_stats = Book.objects.aggregate(
        total=Count('id'),
        available=Count('id', filter=Q(is_available=True))
    )
    total_books = book_stats['total']
    available_books = book_stats['available']
    unavailable_books = total_books - available_books
    top_borrowed_books = Book.objects.annotate(borrow_count=Count('loans')).order_by('-borrow_count')[:5]

    # Statistiques sur les emprunts
    loan_stats = Loan.objects.aggregate(
        total=Count('id'),
        active=Count('id', filter=Q(is_returned=False)),
        overdue=Count('id', filter=Q(is_returned=False, due_date__lt=timezone.now()))
    )
    total_loans = loan_stats['total']
    active_loans = loan_stats['active']
    overdue_loans = loan_stats['overdue']

    # Statistiques sur les utilisateurs
    user_stats = CustomUser.objects.aggregate(
        total=Count('id'),
        librarians=Count('id', filter=Q(is_librarian=True))
    )
    total_users = user_stats['total']
    librarians = user_stats['librarians']
    standard_users = total_users - librarians
    top_borrowers = CustomUser.objects.annotate(borrow_count=Count('loans')).order_by('-borrow_count')[:5]

    # Données pour les graphiques existants
    book_status_data = {
        'labels': ['Disponibles', 'Indisponibles'],
        'data': [available_books, unavailable_books],
        'backgroundColor': ['#28a745', '#dc3545']
    }

    loan_status_data = {
        'labels': ['Actifs', 'En retard'],
        'data': [active_loans, overdue_loans],
        'backgroundColor': ['#17a2b8', '#ffc107']
    }

    user_type_data = {
        'labels': ['Bibliothécaires', 'Utilisateurs standards'],
        'data': [librarians, standard_users],
        'backgroundColor': ['#007bff', '#6c757d']
    }

    top_borrowed_data = {
        'labels': [book.title for book in top_borrowed_books],
        'data': [book.borrow_count for book in top_borrowed_books],
        'backgroundColor': ['#28a745', '#dc3545', '#17a2b8', '#ffc107', '#007bff']
    }

    # Données pour la courbe des emprunts et retours par mois
    # On va regarder les 12 derniers mois
    end_date = timezone.now()
    start_date = end_date - timedelta(days=365)  # 1 an en arrière

    # Emprunts par mois
    loans_by_month = Loan.objects.filter(
        loan_date__gte=start_date,
        loan_date__lte=end_date
    ).annotate(
        month=TruncMonth('loan_date')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')

    # Retours par mois
    returns_by_month = Loan.objects.filter(
        return_date__gte=start_date,
        return_date__lte=end_date,
        is_returned=True
    ).annotate(
        month=TruncMonth('return_date')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')

    # Générer les labels (mois) et les données
    labels = []
    loans_data = []
    returns_data = []
    current_date = start_date
    while current_date <= end_date:
        month_str = current_date.strftime('%b %Y')  # Format : "Jan 2025"
        labels.append(month_str)

        # Emprunts pour ce mois
        loan_count = next((item['count'] for item in loans_by_month if item['month'].strftime('%Y-%m') == current_date.strftime('%Y-%m')), 0)
        loans_data.append(loan_count)

        # Retours pour ce mois
        return_count = next((item['count'] for item in returns_by_month if item['month'].strftime('%Y-%m') == current_date.strftime('%Y-%m')), 0)
        returns_data.append(return_count)

        # Passer au mois suivant
        current_date = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1)

    # Données pour le graphique de la courbe
    loan_trend_data = {
        'labels': labels,
        'datasets': [
            {
                'label': 'Emprunts',
                'data': loans_data,
                'borderColor': '#17a2b8',
                'fill': False
            },
            {
                'label': 'Retours',
                'data': returns_data,
                'borderColor': '#28a745',
                'fill': False
            }
        ]
    }

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
        'book_status_data': json.dumps(book_status_data),
        'loan_status_data': json.dumps(loan_status_data),
        'user_type_data': json.dumps(user_type_data),
        'top_borrowed_data': json.dumps(top_borrowed_data),
        'loan_trend_data': json.dumps(loan_trend_data),  # Nouvelle donnée pour la courbe
    }

    return render(request, 'library_stats/statistics.html', context)