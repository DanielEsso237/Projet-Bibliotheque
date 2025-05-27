from django.shortcuts import render

def search_view(request):
    return render(request, 'books/search.html')

def loans_view(request):
    return render(request, 'books/loans.html')