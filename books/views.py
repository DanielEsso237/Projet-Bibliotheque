from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse, FileResponse
from .models import Book, Document
from .forms import BookForm, DocumentForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import logging
from users.models import UserFavorite, UserDownload
from django.http import Http404
from django.contrib.contenttypes.models import ContentType

logger = logging.getLogger(__name__)

@login_required
def librarian_dashboard(request):
    if not request.user.user_type == 'LIBRARIAN':
        messages.error(request, "Seuls les bibliothécaires peuvent accéder à cette page.")
        return redirect('books:standard_user_dashboard')
    books_list = Book.objects.all().order_by('title')
    search_query = request.GET.get('search', '')
    if search_query:
        books_list = books_list.filter(title__icontains=search_query)
    paginator = Paginator(books_list, 9)
    page_number = request.GET.get('book_page')
    books = paginator.get_page(page_number)
    document_types = Document.DOCUMENT_TYPES
    academic_levels = Document.ACADEMIC_LEVELS
    return render(request, 'books/librarian_dashboard.html', {'books': books, 'document_types': document_types, 'academic_levels': academic_levels})

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from users.models import UserDownload
from .models import Document
import logging

logger = logging.getLogger(__name__)

@login_required
def standard_user_dashboard(request):
    if request.user.user_type == 'LIBRARIAN':
        messages.error(request, "Les bibliothécaires doivent utiliser leur tableau de bord dédié.")
        return redirect('books:librarian_dashboard')
    
    # Calculer le nombre de téléchargements avec débogage
    user_id = request.user.id
    downloads = UserDownload.objects.filter(user_id=user_id)
    downloads_count = downloads.count()
    logger.info(f"Utilisateur: {request.user.username} (ID: {user_id}), Téléchargements: {downloads_count}, Enregistrements: {list(downloads.values())}")
    
    # Calculer le nombre de favoris
    favorites_count = request.user.favorites.count()
    
    # Notifications (à implémenter si nécessaire)
    notifications_count = 0
    
    academic_levels = Document.ACADEMIC_LEVELS
    return render(request, 'books/standard_user_dashboard.html', {
        'notifications_count': notifications_count,
        'favorites_count': favorites_count,
        'downloads_count': downloads_count,
        'academic_levels': academic_levels,
    })

def stats_api(request):
    total_books = Book.objects.count()
    return JsonResponse({'total_books': total_books, 'ebooks': total_books})

def doc_stats_api(request):
    total_docs = Document.objects.count()
    levels_count = Document.objects.values('academic_level').distinct().count()
    types_count = Document.objects.values('document_type').distinct().count()
    return JsonResponse({'total_docs': total_docs, 'levels_count': levels_count, 'types_count': types_count})

def search_books_api(request):
    books_list = Book.objects.all()
    search_query = request.GET.get('search', '')
    if search_query:
        books_list = books_list.filter(title__icontains=search_query)
    sort_field = request.GET.get('sort', 'title')
    sort_order = request.GET.get('order', 'asc')
    if sort_field in ['title', 'author']:
        if sort_order == 'desc':
            sort_field = f'-{sort_field}'
        books_list = books_list.order_by(sort_field)
    paginator = Paginator(books_list, 9)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    books = [{'id': book.id, 'title': book.title, 'author': book.author, 'cover_image': book.cover_image.url if book.cover_image else None, 'ebook_file': book.ebook_file.url if book.ebook_file else None} for book in page_obj]
    return JsonResponse({'books': books, 'has_previous': page_obj.has_previous(), 'has_next': page_obj.has_next(), 'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None, 'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None, 'page_range': list(page_obj.paginator.page_range), 'current_page': page_obj.number, 'paginator': {'num_pages': page_obj.paginator.num_pages}})

def search_docs_api(request):
    docs_list = Document.objects.all()
    search_query = request.GET.get('search', '')
    if search_query:
        docs_list = docs_list.filter(title__icontains=search_query)
    type_filter = request.GET.get('type', '')
    if type_filter:
        docs_list = docs_list.filter(document_type=type_filter)
    level_filter = request.GET.get('level', '')
    if level_filter:
        docs_list = docs_list.filter(academic_level=level_filter)
    sort_field = request.GET.get('sort', 'title')
    sort_order = request.GET.get('order', 'asc')
    if sort_field in ['title']:
        if sort_order == 'desc':
            sort_field = f'-{sort_field}'
        docs_list = docs_list.order_by(sort_field)
    paginator = Paginator(docs_list, 9)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    documents = [{'id': doc.id, 'title': doc.title, 'document_type': doc.document_type, 'document_type_display': doc.get_document_type_display(), 'academic_level': doc.academic_level, 'academic_level_display': doc.get_academic_level_display(), 'file_url': doc.file.url if doc.file else None} for doc in page_obj]
    return JsonResponse({'documents': documents, 'has_previous': page_obj.has_previous(), 'has_next': page_obj.has_next(), 'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None, 'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None, 'page_range': list(page_obj.paginator.page_range), 'current_page': page_obj.number, 'paginator': {'num_pages': page_obj.paginator.num_pages}})

def doc_api(request, doc_id):
    doc = get_object_or_404(Document, id=doc_id)
    data = {'title': doc.title, 'document_type': doc.document_type, 'document_type_display': doc.get_document_type_display(), 'academic_level': doc.academic_level, 'academic_level_display': doc.get_academic_level_display(), 'file_url': doc.file.url if doc.file else None}
    return JsonResponse(data)

def delete_doc(request, doc_id):
    doc = get_object_or_404(Document, id=doc_id)
    if request.method == 'POST':
        doc.delete()
        messages.success(request, 'Document supprimé avec succès !')
        return redirect('books:librarian_dashboard')
    return redirect('books:librarian_dashboard')

def edit_doc(request, doc_id):
    doc = get_object_or_404(Document, id=doc_id)
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=doc)
        if form.is_valid():
            form.save()
            messages.success(request, 'Document modifié avec succès !')
            return redirect('books:librarian_dashboard')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = DocumentForm(instance=doc)
    return render(request, 'books/edit_doc.html', {'form': form, 'doc': doc})

def choose_document_type(request):
    return render(request, 'books/choose_document_type.html')


def select_document_category(request):
    if request.method == "POST":
        document_type = request.POST.get('document_type')
        academic_level = request.POST.get('academic_level')
        department = request.POST.get('department')

        if not document_type or not academic_level:
            messages.error(request, "Veuillez sélectionner un type de document et un niveau académique.")
            return render(request, 'books/select_document_category.html', {
                'document_types': Document.DOCUMENT_TYPES,
                'academic_levels': Document.ACADEMIC_LEVELS,
                'departments': Document.DEPARTMENTS,
            })

        # Rediriger avec les paramètres dans l'URL au lieu de la session
        return redirect('books:add_document', document_type=document_type, academic_level=academic_level)

    return render(request, 'books/select_document_category.html', {
        'document_types': Document.DOCUMENT_TYPES,
        'academic_levels': Document.ACADEMIC_LEVELS,
        'departments': Document.DEPARTMENTS,
    })

def add_document(request, document_type, academic_level):
    department = None  # Vous pouvez ajouter la logique pour récupérer le département si nécessaire

    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.document_type = document_type
            document.academic_level = academic_level
            if department:
                document.department = department
            document.save()
            messages.success(request, "Document ajouté avec succès.")
            return redirect('books:librarian_dashboard')
        else:
            messages.error(request, "Erreur dans le formulaire.")
    else:
        form = DocumentForm()

    # Obtenir le libellé traduit du document_type
    document_type_display = dict(Document.DOCUMENT_TYPES).get(document_type, "document")
    return render(request, 'books/add_document.html', {
        'form': form,
        'document_type': document_type,
        'document_type_display': document_type_display,
        'academic_level': academic_level,
    })



def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'E-book ajouté avec succès !')
            return redirect('books:librarian_dashboard')
    else:
        form = BookForm()
    return render(request, 'books/add_book.html', {'form': form, 'redirect_url': reverse('books:librarian_dashboard')})

def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'E-book supprimé avec succès !')
        return redirect('books:librarian_dashboard')
    return redirect('books:librarian_dashboard')

def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'E-book modifié avec succès !')
            return redirect('books:librarian_dashboard')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = BookForm(instance=book)
    return render(request, 'books/edit_book.html', {'form': form, 'book': book})

def book_api(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    data = {'title': book.title, 'author': book.author, 'cover_image': book.cover_image.url if book.cover_image else None, 'ebook_file': book.ebook_file.url if book.ebook_file else None}
    return JsonResponse(data)

@login_required
def search_view(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    books = Book.objects.all()
    if query:
        books = books.filter(Q(title__icontains=query) | Q(author__icontains=query))
    if category:
        books = books.filter(category=category)
    paginator = Paginator(books, 9)
    page_number = request.GET.get('page')
    books_page = paginator.get_page(page_number)

    favorite_book_ids = UserFavorite.objects.filter(
        user=request.user,
        content_type=ContentType.objects.get_for_model(Book)
    ).values_list('object_id', flat=True)

    categories = Book.objects.values_list('category', flat=True)
    unique_categories = sorted(set(cat for cat in categories if cat))

    context = {
        'books': books_page,
        'query': query,
        'category': category,
        'categories': unique_categories,
        'favorite_ids': list(favorite_book_ids),
        'academic_levels': Document.ACADEMIC_LEVELS
    }
    return render(request, 'books/search_books_for_standard_users.html', context)

@login_required
def book_detail_view(request, pk):
    book = get_object_or_404(Book, pk=pk)
    favorite_book_ids = UserFavorite.objects.filter(
        user=request.user,
        content_type=ContentType.objects.get_for_model(Book)
    ).values_list('object_id', flat=True)
    academic_levels = Document.ACADEMIC_LEVELS
    context = {'book': book, 'favorite_ids': list(favorite_book_ids), 'academic_levels': academic_levels}
    return render(request, 'books/book_detail.html', context)

@login_required
def new_arrivals_view(request):
    recent_books = Book.objects.order_by('-created_at')
    paginator = Paginator(recent_books, 9)
    page_number = request.GET.get('page')
    recent_books_page = paginator.get_page(page_number)
    favorite_book_ids = UserFavorite.objects.filter(
        user=request.user,
        content_type=ContentType.objects.get_for_model(Book)
    ).values_list('object_id', flat=True)
    academic_levels = Document.ACADEMIC_LEVELS
    context = {'recent_books': recent_books_page, 'favorite_ids': list(favorite_book_ids), 'academic_levels': academic_levels}
    return render(request, 'books/new_arrivals_books_for_user.html', context)

@login_required
def epreuves_view(request):
    levels = [level for level in Document.ACADEMIC_LEVELS]
    selected_level = request.GET.get('level', '')
    epreuves = Document.objects.filter(document_type='exam')
    if selected_level:
        epreuves = epreuves.filter(academic_level=selected_level)
    paginator = Paginator(epreuves, 9)
    page_number = request.GET.get('page')
    epreuves_page = paginator.get_page(page_number)
    favorite_document_ids = UserFavorite.objects.filter(
        user=request.user,
        content_type=ContentType.objects.get_for_model(Document)
    ).values_list('object_id', flat=True)
    academic_levels = Document.ACADEMIC_LEVELS
    context = {'epreuves': epreuves_page, 'levels': levels, 'favorite_ids': list(favorite_document_ids), 'academic_levels': academic_levels}
    return render(request, 'books/epreuves_liste.html', context)

@login_required
def documents_view(request):
    document_types = Document.DOCUMENT_TYPES
    academic_levels = Document.ACADEMIC_LEVELS
    selected_type = request.GET.get('type', '')
    selected_level = request.GET.get('level', '')
    documents = Document.objects.all()
    if selected_type:
        documents = documents.filter(document_type=selected_type)
    if selected_level:
        documents = documents.filter(academic_level=selected_level)
    paginator = Paginator(documents, 9)
    page_number = request.GET.get('page')
    documents_page = paginator.get_page(page_number)
    favorite_document_ids = UserFavorite.objects.filter(
        user=request.user,
        content_type=ContentType.objects.get_for_model(Document)
    ).values_list('object_id', flat=True)
    context = {
        'documents': documents_page,
        'document_types': document_types,
        'academic_levels': academic_levels,
        'favorite_ids': list(favorite_document_ids)
    }
    return render(request, 'books/documents_list.html', context)

@login_required
def document_detail_view(request, pk):
    document = get_object_or_404(Document, pk=pk)
    favorite_document_ids = UserFavorite.objects.filter(
        user=request.user,
        content_type=ContentType.objects.get_for_model(Document)
    ).values_list('object_id', flat=True)
    academic_levels = Document.ACADEMIC_LEVELS
    context = {'document': document, 'favorite_ids': list(favorite_document_ids), 'academic_levels': academic_levels}
    return render(request, 'books/document_detail.html', context)

@login_required
def favorites_view(request):
    # Récupérer tous les favoris (Books et Documents)
    favorite_items = UserFavorite.objects.filter(user=request.user).select_related('content_type')
    book_content_type = ContentType.objects.get_for_model(Book)
    doc_content_type = ContentType.objects.get_for_model(Document)
    book_ids = UserFavorite.objects.filter(
        user=request.user,
        content_type=book_content_type
    ).values_list('object_id', flat=True)
    document_ids = UserFavorite.objects.filter(
        user=request.user,
        content_type=doc_content_type
    ).values_list('object_id', flat=True)

    favorite_books = Book.objects.filter(id__in=book_ids)
    favorite_documents = Document.objects.filter(id__in=document_ids)

    # Combiner les favoris dans une liste paginée
    all_favorites = list(favorite_books) + list(favorite_documents)
    paginator = Paginator(all_favorites, 9)
    page_number = request.GET.get('page')
    favorite_page = paginator.get_page(page_number)

    academic_levels = Document.ACADEMIC_LEVELS
    context = {
        'favorite_items': favorite_page,
        'message': 'Aucun élément en favoris.' if not all_favorites else '',
        'academic_levels': academic_levels
    }
    return render(request, 'books/favorites_books_for_users.html', context)

@login_required
@require_POST
def toggle_favorite(request):
    item_id = request.POST.get('book_id')  
    item_type = request.POST.get('item_type', 'book')  
    if not item_id or not item_type:
        return JsonResponse({'status': 'error', 'message': 'ID ou type manquant.'}, status=400)

    try:
        if item_type == 'book':
            content_type = ContentType.objects.get_for_model(Book)
            item = get_object_or_404(Book, id=item_id)
        elif item_type == 'document':
            content_type = ContentType.objects.get_for_model(Document)
            item = get_object_or_404(Document, id=item_id)
        else:
            return JsonResponse({'status': 'error', 'message': 'Type non pris en charge.'}, status=400)

        favorite, created = UserFavorite.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=item.id
        )

        if created:
            messages.success(request, f'{item.title} ajouté aux favoris.')
            return JsonResponse({'status': 'success', 'created': True, 'title': item.title})
        else:
            favorite.delete()
            messages.success(request, f'{item.title} retiré des favoris.')
            return JsonResponse({'status': 'success', 'created': False})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, FileResponse
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.contrib.contenttypes.models import ContentType
from .models import Book, Document
from users.models import UserDownload
import logging

logger = logging.getLogger(__name__)

@login_required
def download_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if not book.ebook_file or not book.ebook_file.name.endswith('.pdf'):
        raise Http404("Ce livre n'est pas disponible pour consultation ou téléchargement.")
    
    action = request.GET.get('action', 'download')
    
    # Enregistrer le téléchargement
    download, created = UserDownload.objects.get_or_create(
        user=request.user,
        content_type=ContentType.objects.get_for_model(Book),
        object_id=book.id
    )
    if created:
        logger.info(f"Téléchargement enregistré pour {request.user.username} (ID: {request.user.id}), Book ID: {book.id}")
    
    if action == 'view':
        response = FileResponse(open(book.ebook_file.path, 'rb'), as_attachment=False)
        response['Content-Type'] = 'application/pdf'
        response['Content-Disposition'] = 'inline; filename="{}"'.format(book.ebook_file.name)
        return response
    else:
        response = FileResponse(open(book.ebook_file.path, 'rb'), as_attachment=True, filename=book.ebook_file.name)
        return response

@login_required
def download_document(request, pk):
    document = get_object_or_404(Document, pk=pk)
    if not document.file or not document.file.name.endswith('.pdf'):
        raise Http404("Ce document n'est pas disponible pour consultation ou téléchargement.")
    
    action = request.GET.get('action', 'download')
    
    # Enregistrer le téléchargement
    download, created = UserDownload.objects.get_or_create(
        user=request.user,
        content_type=ContentType.objects.get_for_model(Document),
        object_id=document.id
    )
    if created:
        logger.info(f"Téléchargement enregistré pour {request.user.username} (ID: {request.user.id}), Document ID: {document.id}")
    
    if action == 'view':
        response = FileResponse(open(document.file.path, 'rb'), as_attachment=False)
        response['Content-Type'] = 'application/pdf'
        response['Content-Disposition'] = 'inline; filename="{}"'.format(document.file.name)
        return response
    else:
        response = FileResponse(open(document.file.path, 'rb'), as_attachment=True, filename=document.file.name)
        return response

@login_required
def home(request):
    if not request.user.is_authenticated or request.user.user_type not in ["STUDENT", "PROFESSOR"]:
        messages.error(request, "Accès réservé aux utilisateurs standard.")
        return redirect('users:login')
    academic_levels = Document.ACADEMIC_LEVELS
    return render(request, 'books/standard_user_dashboard.html', {'academic_levels': academic_levels})

@login_required
def recommendations_view(request):
    recommended_books = Book.objects.order_by('-created_at')
    paginator = Paginator(recommended_books, 9)
    page_number = request.GET.get('page')
    recommended_books_page = paginator.get_page(page_number)
    favorite_book_ids = UserFavorite.objects.filter(
        user=request.user,
        content_type=ContentType.objects.get_for_model(Book)
    ).values_list('object_id', flat=True)
    academic_levels = Document.ACADEMIC_LEVELS
    context = {'recommended_books': recommended_books_page, 'favorite_ids': list(favorite_book_ids), 'academic_levels': academic_levels}
    return render(request, 'books/recommendations_for_users.html', context)

@login_required
def check_favorite_status(request):
    book_ids = request.GET.getlist('book_ids')
    if not book_ids:
        return JsonResponse({'favorites': []})
    # Filtrer les favoris pour les Books uniquement
    book_content_type = ContentType.objects.get_for_model(Book)
    user_favorites = UserFavorite.objects.filter(
        user=request.user,
        content_type=book_content_type,
        object_id__in=book_ids
    ).values_list('object_id', flat=True)
    return JsonResponse({'favorites': list(user_favorites)})