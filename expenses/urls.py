from django.urls import path
from . import views
from django.views.decorators.csrf  import csrf_exempt

# Handle the urls
urlpatterns = [
    path('', views.index, name="expenses"),
    path('add_expense', views.add_expense, name="add_expense"),
    path('expense_edit/<int:id>', views.expense_edit, name="expense_edit"),
    path('expense_delete/<int:id>/', views.expense_delete, name='expense-delete'),
    path('search-expenses', csrf_exempt(views.search_expenses), name="search-expenses"),
    path('expense_category_summary', views.expense_category_summary, name="expense_category_summary"),
    path('expense_category_trend', views.expense_category_trend, name="expense_category_trend"),
    path('expense_by_month', views.expense_by_month, name='expense_by_month'),
    path('expense_of_week', views.expense_of_week, name='expense_of_week'),
    path('total_expense_of_the_day', views.total_expense_of_the_day, name='total_expense_of_the_day'),
    path('total_expense_of_the_week', views.total_expense_of_the_week, name='total_expense_of_the_week'),
    path('total_expense_of_the_month', views.total_expense_of_the_month, name='total_expense_of_the_month'),
    path('total_expense_of_the_year', views.total_expense_of_the_year, name='total_expense_of_the_year'),
    path('stats', views.stats_view, name="stats"),
    path('export_csv', views.export_csv, name='export_csv'),
    path('export_excel', views.export_excel, name='export_excel'),
    path('export_pdf', views.export_pdf, name='export_pdf')
]