from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_decode
from django.template.defaultfilters import slugify

#Account App
from .forms import UserForm
from .models import User, UserProfile
from accounts.utils import detectUser, send_verification_email

#Vendor App
from vendor.forms import VendorForm
from vendor.models import Vendor

#Order App
from orders.models import Order

#Restrict the vendor from accessing the customer page 
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied

#Restrict the customer from accessing the vendor page 
def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied

def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, "You have already loged in!")
        return redirect('myAccount')
    
    elif request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            #CREATE USER using  form
            # password = form.cleaned_data['password'] 
            # user = form.save(commit=False)
            # user.role = User.CUSTOMER
            # user.set_password(password)
            # form.save()

            #Create the user using create_user() method
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.role = User.CUSTOMER
            user.save()

            #Send verification email
            mail_subject = 'Please activate your account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, 'Your account has been registered successfully')
            return redirect('registerUser')
        else:
            print('invalid form')
            print(form.errors)
        
    else:
        form = UserForm()
    
    context = {
        'form':form,
    }
    return render(request, template_name='accounts/registerUser.html', context=context)

def activate(request, uidb64, token):
    #activate the user by setting the is_active status to True
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulation! Your account is activated.")
        return redirect("myAccount")
    else:
        messages.error(request, "Invalid activation link")
        return redirect('myAccount')


def registerVendor(request):
    if request.user.is_authenticated:
        messages.warning(request, "You have already loged in!")
        return redirect('myAccount')
    
    elif request.method == "POST":
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(
                first_name=first_name, 
                last_name=last_name, 
                username=username, 
                email=email, 
                password=password, 
            )
            user.role = User.VENDOR
            user.save()
            vendor = v_form.save(commit=False)
            vendor.user = user
            vendor_name = v_form.cleaned_data['vendor_name']
            vendor.vendor_slug = slugify(vendor_name)+ '-' + str(user.id)
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
            #Send verification email
            mail_subject = 'Please activate your account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, 'Your account has been registered successfuly! Please wait for the approval')
            return redirect('registerVendor')
            
        else:
            print('invalid form')
            print(form.errors, v_form.errors)

    else:
        form = UserForm()
        v_form = VendorForm()
    context = {
        'form': form,
        'v_form': v_form
    }
    return render(request, template_name='accounts/registerVendor.html', context=context)


def login(request):
    if request.user.is_authenticated:
        messages.warning(request, "You have already loged in!")
        return redirect('myAccount')

    elif request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, "You are now logged in")
            return redirect('myAccount')
        else:
            messages.error(request, "Invalid login credentials")
            return redirect('login')

    return render(request, template_name="accounts/login.html")

def logout(request):
    auth.logout(request)
    messages.warning(request,"You are logged out.")
    return redirect("login")

@login_required(login_url="login")
def myAccount(request):
    user = request.user
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)

@login_required(login_url="login")
@user_passes_test(check_role_customer)
def customerDashboard(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True)
    recent_orders = orders[:5]
    context = {
        'orders': orders,
        'orders_count': orders.count(),
        'recent_orders': recent_orders,
    }
    return render(request, "accounts/customerDashboard.html", context=context)

@login_required(login_url="login")
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    vendor = Vendor.objects.get(user=request.user)
    orders = Order.objects.filter(vendors__in=[vendor.id], is_ordered=True).order_by('-created_at')
    recent_orders = orders[:5]
    context = {
        'orders': orders,
        'orders_count': orders.count(),
        'recent_orders': recent_orders,
    }
    return render(request, "accounts/vendorDashboard.html", context=context)

def forgot_password(request):
    if request.method == "POST":
        email = request.POST['email']
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            #Send reset password email.
            mail_subject = 'FoodOnline - Reset password'
            email_template = 'accounts/emails/reset_password_email.html'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, 'Password reset link has been send your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist')
            return redirect('forgot_password')

    return render(request, 'accounts/forgot_password.html')

def reset_password_validate(request, uidb64, token):
    #validate the user by decoding the token and user pk
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, "Please reset your password")
        return redirect('reset_password')
    else:
        messages.error(request, "This link has been expired.")
        return redirect('myAccount')
     

def reset_password(request):
    if request.method == 'POST':
        #field name -> password
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            #This give me primary key of the user
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, "Password reset successful")
            return redirect("login")
        else:
            messages.error(request, "Password do not match!")
            return redirect('reset_password')

    return render(request, 'accounts/reset_password.html')





