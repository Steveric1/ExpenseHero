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
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import threading


# Handle sending of mail fast


def send_email_async(email_subject, message, recipient_list):
    email_thread = threading.Thread(target=email_sender, args=(
        email_subject, message, recipient_list))
    return email_thread


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
                # domain = get_current_site(request).domain
                domain = settings.SITE_DOMAIN
                link = reverse('activate',
                               kwargs={'uidb64': uidb64,
                                       'token': token_generator.make_token(user)}
                               )

                activate_url = 'http://{}{}'.format(domain, link)
                email_subject = 'Acitvate your account'
                message = 'Hi ' + user.username + \
                    ' please use the below link to verify your account\n' + activate_url

                recipient_list = [email]
                send_email_async(email_subject, message,
                                 recipient_list).start()

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


# Password Validation
class PasswordValidation(View):
    def post(self, request):
        data = json.loads(request.body)
        password = data.get('password')
        if len(password) < 6:
            return JsonResponse({'password_error': 'Password too short'}, status=400)
        return JsonResponse({'password_valid': True})

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
        context = {
            'fieldValues': request.POST
        }
        
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username and password:
            user = auth.authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, 'Welcome, ' +
                                     user.username + ' you are now logged in')
                    return redirect('expenses')
                else:
                    messages.error(
                        request, 'Account is not activated, please check your email')
                    return render(request, 'authentication/login.html', context)

            messages.error(request, 'Invalid creditials, try again')
            return render(request, 'authentication/login.html', context)

        messages.error(request, 'Please fill all fields')
        return render(request, 'authentication/login.html', context)


class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, 'You have been logged out')
        return redirect('login')


class RequestPasswordResetEmail(View):
    def get(self, request):
        return render(request, 'authentication/reset-password.html')

    def post(self, request):
        email = request.POST.get('email')

        context = {
            'values': request.POST
        }

        if not validate_email(email):
            messages.error(request, 'Please supply a valid email')
            return render(request, 'authentication/reset-password.html', context)

        user = User.objects.filter(email=email)
        if user.exists():
            uidb64 = urlsafe_base64_encode(force_bytes(user[0].pk))
            domain = settings.SITE_DOMAIN
            password_token = PasswordResetTokenGenerator()
            link = reverse('reset-user-password',
                           kwargs={'uidb64': uidb64,
                                   'token': password_token.make_token(user[0])}
                           )

            reset_url = 'http://{}{}'.format(domain, link)
            email_subject = 'Password Reset Instructions'
            message = 'Hi there, please click the link below to reset your password\n' + reset_url

            recipient_list = [email]
            send_email_async(email_subject, message, recipient_list).start()
        messages.success(
            request, "We have sent a password reset link to your email")
        return render(request, 'authentication/reset-password.html', context)


class UserPasswordReset(View):
    def get(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token
        }

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.error(
                    request, 'The reset link is invalid, probably becauase it has already been used.')
                return redirect('reset-password')
        except Exception as e:
            pass

        return render(request, 'authentication/set-new-password.html', context)

    def post(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token
        }

        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if len(password) < 6:
            messages.error(request, 'Password too short')
            return render(request, 'authentication/set-new-password.html', context)

        if password != password2:
            messages.error(request, 'Password does not match!')
            return render(request, 'authentication/set-new-password.html', context)

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)

            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successfully')
            return redirect('login')
        except Exception as e:
            messages.error(request, 'Something went wrong, please try again.')
            return render(request, 'authentication/set-new-password.html', context)
