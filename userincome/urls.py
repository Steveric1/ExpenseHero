from django.urls import path
from . import views
from django.views.decorators.csrf  import csrf_exempt

# Handle the urls
urlpatterns = [
    path('', views.index, name="income"),
    path('add_income', views.add_income, name="add-income"),
    path('income_edit/<int:id>', views.income_edit, name="income_edit"),
    path('income_delete/<int:id>', views.income_delete, name='income-delete'),
    path('search-income', csrf_exempt(views.search_income), name="search-income")
] 