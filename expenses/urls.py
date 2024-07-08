from django.urls import path
from . import views
from django.views.decorators.csrf  import csrf_exempt

# Handle the urls
urlpatterns = [
    path('', views.index, name="expenses"),
    path('add_expense', views.add_expense, name="add_expense"),
    path('expense_edit/<int:id>', views.expense_edit, name="expense_edit"),
    path('expense_delete/<int:id>', views.expense_delete, name='expense-delete'),
    path('search-expenses', csrf_exempt(views.search_expenses), name="search-expenses")
]