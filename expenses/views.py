from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Category, Expense
from django.contrib import messages
import json
from django.http import JsonResponse
from userpreferences.models import UserPreference

# Create your views here.


@login_required(login_url='login')
def search_expenses(request):
    if request.method == "POST":
        search_str = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(
            amount__startswith=search_str, owner=request.user) | Expense.objects.filter(
            date__startswith=search_str, owner=request.user) | Expense.objects.filter(
                description__icontains=search_str, owner=request.user) | Expense.objects.filter(
                    category__icontains=search_str, owner=request.user
        )
        data = expenses.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='login')
def index(request):
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    try:
        currency = UserPreference.objects.get(user=request.user).currency
    except UserPreference.DoesNotExist:
        currency = None
    context = {
        'expenses': expenses,
        'page_obj': page_obj,
        'currency': currency
    } 
    return render(request, 'expenses/index.html', context)


@login_required(login_url='login')
def add_expense(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'values': request.POST
    }

    if request.method == "GET":
        return render(request, 'expenses/add_expense.html', context)

    if request.method == "POST":
        amount = request.POST['amount']
        description = request.POST['description']
        if not amount:
            messages.error(request, 'amount is required')
            return render(request, 'expenses/add_expense.html', context)
        elif not description:
            messages.error(request, 'description is required')
            return render(request, 'expenses/add_expense.html', context)
    date = request.POST['expense_date']
    category = request.POST['category']
    Expense.objects.create(owner=request.user, amount=amount, description=description,
                           date=date, category=category)
    messages.success(request, 'Expense saved successfully!')
    return redirect('expenses')


@login_required(login_url='login')
def expense_edit(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    context = {
        'expense': expense,
        'values': expense,
        'categories': categories
    }
    if request.method == "GET":
        return render(request, 'expenses/edit_expense.html', context)

    if request.method == "POST":
        amount = request.POST['amount']
        description = request.POST['description']
        if not amount:
            messages.error(request, 'amount is required')
            return render(request, 'expenses/edit_expense.html', context)
        elif not description:
            messages.error(request, 'description is required')
            return render(request, 'expenses/edit_expense.html', context)
    date = request.POST['expense_date']
    category = request.POST['category']

    expense.owner = request.user
    expense.amount = amount
    expense.description = description
    expense.date = date
    expense.category = category

    expense.save()
    messages.success(request, 'Expense Edited successfully!')
    return redirect('expenses')


@login_required(login_url='login')
def expense_delete(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Expense deleted successfully')
    return redirect('expenses')
