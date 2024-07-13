from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name='preferences'), 
    path('delete_account/<int:id>', views.user_delete_account, name='delete_account')
]