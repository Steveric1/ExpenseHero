from django.shortcuts import render, redirect,  get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import os
import json
from django.conf import settings
from .models import UserPreference
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout


# Create your views here.
@login_required(login_url='login')
def index(request):
    """Function to handle user preferences"""
    exist = UserPreference.objects.filter(user=request.user).exists()
    user_preferences = None

    if exist:
        user_preferences = UserPreference.objects.get(user=request.user)

    if request.method == 'GET':
        currency_data = []
        file_path = os.path.join(settings.BASE_DIR, 'currencies.json')

        with open(file_path, 'r') as file_json:
            data = json.load(file_json)
            for key, value in data.items():
                currency_data.append({'name': key, 'value': value})
        return render(request, 'preferences/index.html', {
            'currencies': currency_data,
            'user_preferences': user_preferences,
            'user_id': request.user.id
        })
    else:
        currency = request.POST['currency']
        if exist:
            user_preferences.currency = currency
            user_preferences.save()
        else:
            UserPreference.objects.create(user=request.user, currency=currency)
        messages.success(request, 'Changes saved!')
        return redirect('preferences')


@login_required(login_url='login')
@csrf_exempt
def user_delete_account(request, id):
    """Function to delete user account"""
    if request.user.id != id and not request.user.is_staff:
        messages.error(
            request, "You do not have permission to delete this account.")
        return redirect('preferences')
    
    if request.method == "DELETE":
        current_user = get_object_or_404(User, pk=id)
        current_user.delete()
        logout(request)
        return JsonResponse({'success': True}, status=204)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)
