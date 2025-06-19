from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count,Q
from books.models import Book, Document
from users.models import CustomUser
import json

@login_required
def statistics(request):
    if not request.user.is_librarian:
        return render(request, 'library_stats/permission_denied.html', {'message': "Seuls les bibliothécaires peuvent accéder à cette page."})

    # Statistiques sur les e-books
    ebook_stats = Book.objects.aggregate(total_ebooks=Count('id'))
    total_ebooks = ebook_stats['total_ebooks']

    # Statistiques sur les documents par type
    document_stats = Document.objects.values('document_type').annotate(count=Count('id')).order_by('document_type')
    document_type_data = {
        'labels': [item['document_type'] for item in document_stats],
        'data': [item['count'] for item in document_stats],
        'backgroundColor': ['#28a745', '#dc3545', '#17a2b8', '#ffc107', '#007bff'][:len(document_stats)]
    }

    # Statistiques sur les documents par niveau académique
    academic_level_stats = Document.objects.values('academic_level').annotate(count=Count('id')).order_by('academic_level')
    academic_level_data = {
        'labels': [item['academic_level'] for item in academic_level_stats],
        'data': [item['count'] for item in academic_level_stats],
        'backgroundColor': ['#007bff', '#6c757d', '#28a745', '#dc3545', '#17a2b8'][:len(academic_level_stats)]
    }

    # Statistiques sur les utilisateurs
    user_stats = CustomUser.objects.aggregate(
        total=Count('id'),
        librarians=Count('id', filter=Q(is_librarian=True))
    )
    total_users = user_stats['total']
    librarians = user_stats['librarians']
    standard_users = total_users - librarians

    user_type_data = {
        'labels': ['Bibliothécaires', 'Utilisateurs standards'],
        'data': [librarians, standard_users],
        'backgroundColor': ['#007bff', '#6c757d']
    }

    context = {
        'total_ebooks': total_ebooks,
        'total_users': total_users,
        'librarians': librarians,
        'standard_users': standard_users,
        'document_type_data': json.dumps(document_type_data),
        'academic_level_data': json.dumps(academic_level_data),
        'user_type_data': json.dumps(user_type_data),
    }

    return render(request, 'library_stats/statistics.html', context)