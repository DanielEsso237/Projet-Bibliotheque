from django.shortcuts import render
from .models import Loan
from datetime import date

def loans_view(request):
    if not request.user.is_authenticated:
        return render(request, 'loans/loans.html', {'loans': []})
    
    loans = Loan.objects.filter(user=request.user).select_related('book')
    context = {
        'loans': loans,
        'today': date.today(),
    }
    return render(request, 'loans/loans.html', context)