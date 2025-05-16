from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from .models import Book
from .forms import BookForm

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

def search_books_api(request):
    books_list = Book.objects.all().order_by('title')

    search_query = request.GET.get('search', '')
    if search_query:
        books_list = books_list.filter(title__icontains=search_query)

    availability = request.GET.get('availability', '')
    if availability:
        books_list = books_list.filter(is_available=(availability.lower() == 'true'))

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



def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ajouté avec succès !')
            return render(request, 'books/add_book.html', {
                'form': BookForm(),
                'redirect_url': reverse('librarian_dashboard')
            })
    else:
        form = BookForm()
    return render(request, 'books/add_book.html', {
        'form': form,
        'redirect_url': reverse('librarian_dashboard')
    })

def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Livre supprimé avec succès !')
        return redirect('librarian_dashboard')
    return redirect('librarian_dashboard')

def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Livre modifié avec succès !')
            return redirect('librarian_dashboard')
    else:
        form = BookForm(instance=book)
    return render(request, 'books/librarian_dashboard.html', {'form': form})  # À ajuster avec une modale

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
