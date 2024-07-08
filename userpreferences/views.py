from django.shortcuts import render, redirect
import os
import json
from django.conf import settings
from .models import UserPreference
from django.contrib import messages


# Create your views here.
def index(request):
    exist =  UserPreference.objects.filter(user=request.user).exists()
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
            'user_preferences': user_preferences
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