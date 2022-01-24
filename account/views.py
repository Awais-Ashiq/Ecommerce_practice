import imp
from django.forms import ValidationError
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

from account.models import Account
from .forms import RegistarionForm

#Email Verification Imports
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

def register(request):
    if request.method == 'POST':
        form = RegistarionForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email'].lower()
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save()

            # Send Email

            current_site = get_current_site(request)
            mail_subject = 'Please Activate your account'
            message = render_to_string('accounts/verification.html',{
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request,
             "An email with a verification has been sent to your email acccount please verify your account"
             )
            return redirect('/account/login/?command=verification&email='+email)
    else:
        form = RegistarionForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)
def login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)
        if user:
            auth.login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid Login Credentials")
            return redirect('login')

    return render(request, 'accounts/login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, "Logout Successfully")
    return redirect('login')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)

    except (TypeError, ValueError, Account.DoesNotExist):
        user=None
    
    if user and default_token_generator.check_token(user, token):
        user.is_active=True
        user.save()
        messages.success(request, "Congratulations! Your account is activated.")
        return redirect('login')
    else:
        messages.error(request, "Invalid Activation Link")
    return redirect('register')

@login_required(login_url='login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        user = Account.objects.filter(email=email)
        print("User: ", user[0])
        print("PK: ", user[0].id)
        if user.exists():
            current_site = get_current_site(request)
            mail_subject = 'Password Reset Field'
            message = render_to_string('accounts/verification.html',{
                'user': user[0].first_name,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                'token': default_token_generator.make_token(user[0]),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request,
                "An email with a verification has been sent to your email acccount please reset your account"
                )
            return redirect('login')
        else:
            messages.error(request, 'Email Does not exists.')
            return redirect('forgot_password')
    return render(request, 'accounts/forgot_password.html')

def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, Account.DoesNotExist):
        user = None
    print("user: ", urlsafe_base64_decode(uidb64).decode())
    if user and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, "Please Reset Your Password.")
        return redirect('resetpassword')
    else:
        messages.error(request, "Link has been Expired.")
        return redirect('login')

def resetpassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, "Congrats! Password has been reset.")
            return redirect('login')
        else:
            messages.error(request, "password Does not match")
            return redirect('resetpassword')
    return render(request, 'accounts/resetpassword.html')