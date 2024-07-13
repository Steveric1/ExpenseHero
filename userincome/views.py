from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Source, UserIncome
from userpreferences.models import UserPreference
from django.core.paginator import Paginator
from django.contrib import messages
import json
from django.http import JsonResponse
import datetime

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
    try:
        currency = UserPreference.objects.get(user=request.user).currency
    except UserPreference.DoesNotExist:
        currency = None
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


# User expense summary
def income_source_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30*3)
    income = UserIncome.objects.filter(owner=request.user,
                                      date__gte=six_months_ago, date__lte=todays_date)

    final_resp = {}

    def get_source(income):
        return income.source

    source_list = list(set(map(get_source, income)))

    def get_income_source_amount(source):
        amount = 0
        filtered_source = income.filter(source=source)

        for item in filtered_source:
            amount += item.amount

        return amount

    for x in income:
        for y in source_list:
            final_resp[y] = get_income_source_amount(y)

    return JsonResponse({'income_source_data': final_resp}, safe=False)


def income_source_trend(request):
    todays_date = datetime.date.today()
    three_months_ago = todays_date - datetime.timedelta(days=90)
    incomes = UserIncome.objects.filter(
        owner=request.user, date__gte=three_months_ago, date__lte=todays_date)
    
    source_trend = {}
    
    unique_sources = list(set(income.source for income in incomes))
    
    # Initialize the source_trend dictionary with dates and sources
    for income in incomes:
        month = income.date.strftime("%Y-%m-%d")
        if month not in source_trend:
            source_trend[month] = {source: 0 for source in unique_sources}
    
    # Fill the dictionary with cumulativecome
    for income in incomes:
        month = income.date.strftime("%Y-%m-%d")
        source_trend[month][income.source] += income.amount
    
    return JsonResponse({'source_trend': source_trend}, safe=False)


def income_stats_view(request):
    return render(request, "income/stats.html")