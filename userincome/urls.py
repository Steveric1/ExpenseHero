from django.urls import path
from . import views
from django.views.decorators.csrf  import csrf_exempt

# Handle the urls
urlpatterns = [
    path('', views.index, name="income"),
    path('add_income', views.add_income, name="add-income"),
    path('income_edit/<int:id>', views.income_edit, name="income_edit"),
    path('income_delete/<int:id>', views.income_delete, name='income-delete'),
    path('search-income', csrf_exempt(views.search_income), name="search-income"),
    path('income_source_summary', views.income_source_summary, name="income_source_summary"),
    path('income_source_trend', views.income_source_trend, name="income_source_trend"),
    path('income_stats', views.income_stats_view, name="income_stats"),
    path('income_by_month', views.income_by_month, name="income_by_month"),
    path('income_by_week', views.income_by_week, name="income_by_week"),
    path('total_income_of_the_day', views.total_income_of_the_day, name="total_income_of_the_day"),
    path('total_income_of_the_day', views.total_income_of_the_day, name="total_income_of_the_day"),
    path('total_income_of_the_week', views.total_income_of_the_week, name="total_income_of_the_week"),
    path('total_income_of_the_month', views.total_income_of_the_month, name="total_income_of_the_month"),
    path('total_income_of_the_year', views.total_income_of_the_year, name="total_income_of_the_year")
] 