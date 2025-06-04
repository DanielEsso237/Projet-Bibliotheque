from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from .models import Book, Document
from .forms import BookForm, DocumentForm
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger(__name__)

def librarian_dashboard(request):
    books_list = Book.objects.all().order_by('title')
    search_query = request.GET.get('search', '')
    if search_query:
        books_list = books_list.filter(title__icontains=search_query)
    availability = request.GET.get('availability', '')
    if availability:
        books_list = books_list.filter(is_available=(availability.lower() == 'true'))
    paginator = Paginator(books_list, 9)
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)
    return render(request, 'books/librarian_dashboard.html', {'books': books})

def stats_api(request):
    total_books = Book.objects.count()
    available_books = Book.objects.filter(is_available=True).count()
    ebooks = Book.objects.filter(is_physical=False).count()
    physical_books = Book.objects.filter(is_physical=True).count()
    return JsonResponse({
        'total_books': total_books,
        'available_books': available_books,
        'ebooks': ebooks,
        'physical_books': physical_books
    })

def search_books_api(request):
    books_list = Book.objects.all()
    search_query = request.GET.get('search', '')
    if search_query:
        books_list = books_list.filter(title__icontains=search_query)
    availability = request.GET.get('availability', '')
    if availability:
        books_list = books_list.filter(is_available=(availability.lower() == 'true'))
    type_filter = request.GET.get('type', '')
    if type_filter == 'physical':
        books_list = books_list.filter(is_physical=True)
    elif type_filter == 'ebook':
        books_list = books_list.filter(is_physical=False)
    
    # Tri
    sort_field = request.GET.get('sort', 'title')
    sort_order = request.GET.get('order', 'asc')
    if sort_field in ['title', 'author']:
        if sort_order == 'desc':
            sort_field = f'-{sort_field}'
        books_list = books_list.order_by(sort_field)

    paginator = Paginator(books_list, 9)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    books = [
        {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'is_physical': book.is_physical,
            'quantity': book.quantity if book.is_physical else None,
            'is_available': book.is_available,
            'cover_image': book.cover_image.url if book.cover_image else None,
        } for book in page_obj
    ]
    return JsonResponse({
        'books': books,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
        'page_range': list(page_obj.paginator.page_range),
        'current_page': page_obj.number,
        'paginator': {'num_pages': page_obj.paginator.num_pages}
    })

def choose_document_type(request):
    return render(request, 'books/choose_document_type.html')

@login_required
def select_document_category(request):
    document_types = [dt for dt in Document.DOCUMENT_TYPES if dt[0] != 'ebook']
    academic_levels = [al for al in Document.ACADEMIC_LEVELS if al[0] != 'N/A']
    if request.method == 'POST':
        document_type = request.POST.get('document_type')
        academic_level = request.POST.get('academic_level')
        logger.debug(f"POST data: document_type={document_type}, academic_level={academic_level}")
        if not document_type:
            logger.error("No document_type selected")
            messages.error(request, 'Veuillez sélectionner un type de document.')
        elif not academic_level:
            logger.error("No academic_level selected")
            messages.error(request, 'Veuillez sélectionner un niveau académique.')
        elif document_type == 'ebook':
            logger.error("E-book selection not allowed")
            messages.error(request, 'Les e-books ne peuvent pas être ajoutés ici.')
        elif academic_level == 'N/A':
            logger.error("N/A level not allowed")
            messages.error(request, 'Veuillez sélectionner un niveau académique valide.')
        else:
            return redirect('books:add_document', document_type=document_type, academic_level=academic_level)
        return render(request, 'books/select_document_category.html', {
            'document_types': document_types,
            'academic_levels': academic_levels,
        })
    return render(request, 'books/select_document_category.html', {
        'document_types': document_types,
        'academic_levels': academic_levels,
    })

@login_required
def add_document(request, document_type, academic_level):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        logger.debug(f"POST data: {request.POST}, FILES: {request.FILES}")
        if form.is_valid():
            document = form.save(commit=False)
            document.document_type = document_type
            document.academic_level = academic_level
            document.save()
            messages.success(request, 'Document ajouté avec succès !')
            return redirect('books:librarian_dashboard')
        else:
            logger.error(f"Form errors: {form.errors.as_json()}")
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = DocumentForm()
    return render(request, 'books/add_document.html', {
        'form': form,
        'document_type': document_type,
        'academic_level': academic_level,
    })

def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Livre ajouté avec succès !')
            return redirect('books:librarian_dashboard')
    else:
        form = BookForm()
    return render(request, 'books/add_book.html', {
        'form': form,
        'redirect_url': reverse('books:librarian_dashboard')
    })

def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Livre supprimé avec succès !')
        return redirect('books:librarian_dashboard')
    return redirect('books:librarian_dashboard')

def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Livre modifié avec succès !')
            return redirect('books:librarian_dashboard')
    else:
        form = BookForm(instance=book)
    return render(request, 'books/edit_book.html', {'form': form, 'book': book})

def book_api(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    data = {
        'title': book.title,
        'author': book.author,
        'is_physical': book.is_physical,
        'quantity': book.quantity if book.is_physical else None,
        'is_available': book.is_available,
        'cover_image': book.cover_image.url if book.cover_image else None,
        'ebook_file': book.ebook_file.url if book.ebook_file and not book.is_physical else None
    }
    return JsonResponse(data)