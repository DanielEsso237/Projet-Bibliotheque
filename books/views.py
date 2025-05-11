from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from .models import Book
from .forms import BookForm

def librarian_dashboard(request):
    books = Book.objects.all()
    return render(request, 'books/librarian_dashboard.html', {'books': books})

def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('librarian_dashboard')
    else:
        form = BookForm()
    return render(request, 'books/add_book.html', {'form': form})