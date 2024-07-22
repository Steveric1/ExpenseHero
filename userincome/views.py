from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Source, UserIncome
from userpreferences.models import UserPreference
from django.core.paginator import Paginator
from django.contrib import messages
import json
from django.http import JsonResponse
import datetime
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

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
@csrf_exempt
def income_delete(request, id):
    if request.method == "DELETE":
        income = get_object_or_404(UserIncome, pk=id)
        income.delete()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

# User income summary
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


def income_by_month(request):
    todays_date = datetime.date.today()
    start_of_year = datetime.date(todays_date.year, 1, 1)
    income = UserIncome.objects.filter(
        owner=request.user, date__gte=start_of_year, date__lte=todays_date)

    # Initialize a dictionary for the monthly totals
    monthly_income = {month: 0 for month in range(1, 13)}

    # Aggregate the income by month
    for income in income:
        month = income.date.month
        monthly_income[month] += income.amount

    # Format the result as a list of totals for each month
    monthly_totals = [monthly_income[month] for month in range(1, 13)]

    return JsonResponse({'monthly_totals': monthly_totals}, safe=False)


def income_by_week(request):
    todays_date = datetime.date.today()
    year, week, _ = todays_date.isocalendar()

    # Calculate the start and end of the current week
    start_of_week = datetime.date.fromisocalendar(year, week, 1)
    end_of_week = start_of_week + datetime.timedelta(days=6)

    income = UserIncome.objects.filter(
        owner=request.user, date__gte=start_of_week, date__lte=end_of_week)
    # Initialize a dictionary for the weekly totals
    weekly_income = {day: 0 for day in range(1, 8)}

    # Aggregate the income by day
    for income in income:
        day = income.date.isoweekday()
        weekly_income[day] += income.amount

    # Format the result as a list of totals for each day
    weekly_totals = [weekly_income[day] for day in range(1, 8)]

    return JsonResponse({'weekly_totals': weekly_totals}, safe=False)


def total_income_of_the_day(request):
    todays_date = datetime.date.today()
    income = UserIncome.objects.filter(owner=request.user, date=todays_date)

    total_income = 0
    for income in income:
        total_income += income.amount

    return JsonResponse({'today_total_income': total_income}, safe=False)


def total_income_of_the_week(request):
    todays_date = datetime.date.today()
    year, week, _ = todays_date.isocalendar()

    start_of_week = datetime.date.fromisocalendar(year, week, 1)
    end_of_week = start_of_week + datetime.timedelta(days=6)

    income = UserIncome.objects.filter(
        owner=request.user, date__gte=start_of_week, date__lte=end_of_week)

    total_week_income = 0

    for income in income:
        total_week_income += income.amount

    return JsonResponse({'total_week_income': total_week_income}, safe=False)


def total_income_of_the_month(request):
    todays_date = datetime.date.today()
    month = todays_date.month
    year = todays_date.year
    income = UserIncome.objects.filter(
        owner=request.user, date__year=year, date__month=month)

    total_month_income = 0

    for income in income:
        total_month_income += income.amount

    return JsonResponse({'total_month_income': total_month_income}, safe=False)


def total_income_of_the_year(request):
    todays_date = datetime.date.today()
    year = todays_date.year
    income = UserIncome.objects.filter(owner=request.user, date__year=year)
    
    total_year_income = 0
    
    for income in income:
        total_year_income += income.amount
    
    return JsonResponse({'total_year_income': total_year_income}, safe=False)


def income_stats_view(request):
    return render(request, "income/stats.html")