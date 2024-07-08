from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Source, UserIncome
from userpreferences.models import UserPreference
from django.core.paginator import Paginator
from django.contrib import messages
import json
from django.http import JsonResponse

# Create your views here.

@login_required(login_url='login')
def search_income(request):
    if request.method == "POST":
        search_str = json.loads(request.body).get('searchText')
        income = UserIncome.objects.filter(
            amount__startswith=search_str, owner=request.user) | UserIncome.objects.filter(
            date__startswith=search_str, owner=request.user) | UserIncome.objects.filter(
                description__icontains=search_str, owner=request.user) | UserIncome.objects.filter(
                    source__icontains=search_str, owner=request.user
        )
        data = income.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='login')
def index(request):
    income = UserIncome.objects.filter(owner=request.user)
    paginator = Paginator(income, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    context = {
        'income': income,
        'page_obj': page_obj,
        'currency': currency
    }
    return render(request, 'income/index.html', context)


@login_required(login_url='login')
def add_income(request):
    sources = Source.objects.all()
    context = {
        'sources': sources,
        'values': request.POST
    }

    if request.method == "GET":
        return render(request, 'income/add_income.html', context)

    if request.method == "POST":
        amount = request.POST['amount']
        description = request.POST['description']
        if not amount:
            messages.error(request, 'amount is required')
            return render(request, 'income/add_income.html', context)
        elif not description:
            messages.error(request, 'description is required')
            return render(request, 'income/add_income.html', context)
    date = request.POST['income_date']
    source = request.POST['source']
    UserIncome.objects.create(owner=request.user, amount=amount, description=description,
                              date=date, source=source)
    messages.success(request, 'Record saved successfully!')
    return redirect('income')


@login_required(login_url='login')
def income_edit(request, id):
    income = UserIncome.objects.get(pk=id)
    sources = Source.objects.all()
    context = {
        'income': income,
        'values': income,
        'sources': sources 
    }
    if request.method == "GET":
        return render(request, 'income/edit_income.html', context)

    if request.method == "POST":
        amount = request.POST['amount']
        description = request.POST['description']
        if not amount:
            messages.error(request, 'amount is required')
            return render(request, 'income/edit_income.html', context)
        elif not description:
            messages.error(request, 'description is required')
            return render(request, 'income/edit_income.html', context)
    date = request.POST['income_date']
    source = request.POST['source']

    income.owner = request.user
    income.amount = amount  
    income.description = description
    income.date = date
    income.source = source

    income.save()
    messages.success(request, 'Record Edited successfully!')
    return redirect('income')


@login_required(login_url='login')
def income_delete(request, id):
    income = UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request, 'Record deleted successfully')
    return redirect('income')
