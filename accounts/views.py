from django.shortcuts import render,redirect
from django.http import HttpResponse
from .forms import UserForm
from .models import User

def registerUser(request):
    if request.method == 'POST':
        print(request.POST)
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.CUSTOMER
            form.save()
            return redirect('registerUser')
        
    else:
        form = UserForm()
    
    context = {
        'form':form,
    }
    return render(request, template_name='accounts/registerUser.html', context=context)

def registerRestaurant(request):
    return HttpResponse("registerRestaurant")