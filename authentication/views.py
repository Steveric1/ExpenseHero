from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import User
import json
from django.http import JsonResponse
from validate_email import validate_email
from django.contrib import messages
from .utilities import email_sender, token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import auth


class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')

    def post(self, request):
        # Get user data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        context = {
            'fieldValues': request.POST
        }

        # Check if user or email exist
        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                # Check the length of the password
                if password and len(password) < 6:
                    messages.error(request, 'Password too short')
                    return render(request, 'authentication/register.html', context)
                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = False
                user.save()

                # step to sending activation link to user
                # - getting  domain we are on
                # - relative url to verification
                # - encode uid
                # - token

                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                domain = get_current_site(request).domain
                link = reverse('activate',
                               kwargs={'uidb64': uidb64,
                                       'token': token_generator.make_token(user)}
                               )

                activate_url = 'http://{}{}'.format(domain, link)
                email_subject = 'Acitvate your account'
                message = 'Hi ' + user.username + \
                    ' please use the below link to verify your account\n' + activate_url

                recipient_list = [email]
                email_sender(email_subject, message, recipient_list)

                messages.success(request, 'Account created successfully')
                return render(request, 'authentication/register.html')

        return render(request, 'authentication/register.html')


# Username validation
class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data.get('username')
        if not str(username).isalnum():
            return JsonResponse({'username_error': 'Username should only contain alphanumeric characters'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'sorry username is taken!'}, status=409)
        return JsonResponse({'username_valid': True})


# Email Validation
class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email')
        if not validate_email(email):
            return JsonResponse({'email_error': 'Invalid email, please input the correct email address'}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'sorry email is taken!'}, status=409)
        return JsonResponse({'email_valid': True})


class VerificationView(View):
    """verification view """

    def get(self, request, uidb64, token):
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)
            
            # check if user has already used the activation link
            if not token_generator.check_token(user, token):
                return redirect('login'+'?message='+'User already activated')
            
            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()
            
            messages.success(request, 'Account activated successfully')
            return redirect('login')
        
        except Exception as e:
            pass
        
        return redirect('login')


class LoginView(View):
    """Login view"""

    def get(self, request):
        return render(request, 'authentication/login.html') 
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = auth.authenticate(username=username, password=password)
            
            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, 'Welcome, '+ 
                                     user.username + ' you are now logged in')
                    return redirect('expenses')
                else:
                    messages.error(request, 'Account is not activated, please check your email')
                    return render(request, 'authentication/login.html')
            
            
            messages.error(request, 'Invalid creditials, try again')
            return render(request, 'authentication/login.html')
        
        messages.error(request, 'Please fill all fields')
        return render(request, 'authentication/login.html')


class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, 'You have been logged out')
        return redirect('login')