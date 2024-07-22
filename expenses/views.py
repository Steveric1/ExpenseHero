from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Category, Expense
from django.contrib import messages
import json
from django.http import JsonResponse, HttpResponse
from userpreferences.models import UserPreference
import datetime
import csv
import xlwt
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
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
    expenses = Expense.objects.filter(owner=request.user).order_by('-date')
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
@csrf_exempt
def expense_delete(request, id):
    if request.method == "DELETE":
        expense = get_object_or_404(Expense, pk=id)
        expense.delete()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


# User expense summary
def expense_category_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30*3)
    expenses = Expense.objects.filter(owner=request.user,
                                      date__gte=six_months_ago, date__lte=todays_date)

    final_resp = {}

    def get_category(expense):
        return expense.category

    category_list = list(set(map(get_category, expenses)))

    def get_expense_category_amount(category):
        amount = 0
        filtered_category = expenses.filter(category=category)

        for item in filtered_category:
            amount += item.amount

        return amount

    for x in expenses:
        for y in category_list:
            final_resp[y] = get_expense_category_amount(y)

    return JsonResponse({'expense_category_data': final_resp}, safe=False)


def expense_category_trend(request):
    todays_date = datetime.date.today()
    three_months_ago = todays_date - datetime.timedelta(days=90)
    expenses = Expense.objects.filter(
        owner=request.user, date__gte=three_months_ago, date__lte=todays_date)

    category_trend = {}

    unique_categories = list(set(expense.category for expense in expenses))

    # Initialize the category_trend dictionary with dates and categories
    for expense in expenses:
        month = expense.date.strftime("%Y-%m-%d")
        if month not in category_trend:
            category_trend[month] = {
                category: 0 for category in unique_categories}

    # Fill the dictionary with cumulative expenses
    for expense in expenses:
        month = expense.date.strftime("%Y-%m-%d")
        category_trend[month][expense.category] += expense.amount

    return JsonResponse({'category_trend': category_trend}, safe=False)


def expense_by_month(request):
    todays_date = datetime.date.today()
    start_of_year = datetime.date(todays_date.year, 1, 1)
    expenses = Expense.objects.filter(
        owner=request.user, date__gte=start_of_year, date__lte=todays_date)

    # Initialize a dictionary for the monthly totals
    monthly_expenses = {month: 0 for month in range(1, 13)}

    # Aggregate the expenses by month
    for expense in expenses:
        month = expense.date.month
        monthly_expenses[month] += expense.amount

    # Format the result as a list of totals for each month
    monthly_totals = [monthly_expenses[month] for month in range(1, 13)]

    return JsonResponse({'monthly_totals': monthly_totals}, safe=False)


def expense_of_week(request):
    todays_date = datetime.date.today()
    year, week, _ = todays_date.isocalendar()

    # Calculate the start and end of the current week
    start_of_week = datetime.date.fromisocalendar(year, week, 1)
    end_of_week = start_of_week + datetime.timedelta(days=6)

    expenses = Expense.objects.filter(
        owner=request.user, date__gte=start_of_week, date__lte=end_of_week)
    # Initialize a dictionary for the weekly totals
    weekly_expense = {day: 0 for day in range(1, 8)}

    # Aggregate the expenses by day
    for expense in expenses:
        day = expense.date.isoweekday()
        weekly_expense[day] += expense.amount

    # Format the result as a list of totals for each day
    weekly_totals = [weekly_expense[day] for day in range(1, 8)]

    return JsonResponse({'weekly_totals': weekly_totals}, safe=False)


def total_expense_of_the_day(request):
    todays_date = datetime.date.today()
    expenses = Expense.objects.filter(owner=request.user, date=todays_date)

    total_expenses = 0
    for expense in expenses:
        total_expenses += expense.amount

    return JsonResponse({'today_total_expenses': total_expenses}, safe=False)


def total_expense_of_the_week(request):
    todays_date = datetime.date.today()
    year, week, _ = todays_date.isocalendar()

    start_of_week = datetime.date.fromisocalendar(year, week, 1)
    end_of_week = start_of_week + datetime.timedelta(days=6)

    expenses = Expense.objects.filter(
        owner=request.user, date__gte=start_of_week, date__lte=end_of_week)

    total_week_expense = 0

    for expense in expenses:
        total_week_expense += expense.amount

    return JsonResponse({'total_week_expense': total_week_expense}, safe=False)


def total_expense_of_the_month(request):
    todays_date = datetime.date.today()
    month = todays_date.month
    year = todays_date.year
    expenses = Expense.objects.filter(
        owner=request.user, date__year=year, date__month=month)

    total_month_expense = 0

    for expense in expenses:
        total_month_expense += expense.amount

    return JsonResponse({'total_month_expense': total_month_expense}, safe=False)


def total_expense_of_the_year(request):
    todays_date = datetime.date.today()
    year = todays_date.year
    expenses = Expense.objects.filter(owner=request.user, date__year=year)
    
    total_year_expense = 0
    
    for expense in expenses:
        total_year_expense += expense.amount
    
    return JsonResponse({'total_year_expense': total_year_expense}, safe=False)


def stats_view(request):
    return render(request, "expenses/stats.html")


# View that implement how to download expsenses in csv
@login_required(login_url='login')
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Expenses' + \
        str(datetime.datetime.now()) + '.csv'

    writer = csv.writer(response)
    writer.writerow(['Amount', 'Description', 'Category', 'Date'])

    expenses = Expense.objects.filter(owner=request.user)

    for expense in expenses:
        writer.writerow([expense.amount, expense.description,
                        expense.category, expense.date])

    return response


# View that implement how to download expsenses in excel
@login_required(login_url='login')
def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachement; filename=Expenses' + \
        str(datetime.datetime.now()) + '.xls'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Expenses')

    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Amount', 'Description', 'Category', 'Date']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()

    rows = Expense.objects.filter(owner=request.user).values_list(
        'amount', 'description', 'category', 'date')

    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)

    wb.save(response)
    return response


@login_required(login_url='login')
def export_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename=Expenses_' + \
        str(datetime.datetime.now()) + '.pdf'
    response['Content-Transfer-Encoding'] = 'binary'

    expenses = Expense.objects.filter(owner=request.user)
    total_amount = expenses.aggregate(Sum('amount'))

    html_string = render_to_string(
        'expenses/output-pdf.html', {'expenses': expenses, 'total': total_amount['amount__sum']})
    html = HTML(string=html_string)

    result = html.write_pdf()

    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        output = open(output.name, 'rb')
        response.write(output.read())

    return response
