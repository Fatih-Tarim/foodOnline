from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.defaultfilters import slugify

#Vendor App
from vendor.forms import VendorForm, OpeningHourForm
from vendor.models import OpeningHour

#Account App
from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from accounts.views import check_role_vendor

#Menu App
from menu.models import Category, FoodItem
from menu.forms import CategoryForm, FoodForm

#Vendor App
from vendor.utils import get_vendor

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def v_profile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_vendor(request)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)
        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, 'Settings updated.')
            return redirect('v_profile')
        else:
            print(profile_form.errors)
            print(vendor_form.errors)
    else:
        profile_form = UserProfileForm(instance = profile)
        vendor_form = VendorForm(instance=vendor)

    context = {
        'profile_form': profile_form,
        'vendor_form': vendor_form,
        'profile': profile,
        'vendor': vendor,
    }
    return render(request, 'vendor/v_profile.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def menu_builder(request):
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor=vendor).order_by('created_at')
    
    context = {
        'categories': categories,
    }
    return render(request, "vendor/menu_builder.html", context=context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def fooditems_by_category(request, pk=None):
    vendor = get_vendor(request)
    category = get_object_or_404(Category, pk=pk)
    fooditems = FoodItem.objects.filter(vendor=vendor, category=category)
    context = {
        'fooditems': fooditems,
        'category': category,
    }
    return render(request, "vendor/fooditems_by_category.html", context=context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.save() #here the category id generated
            category.slug = slugify(category_name) + '-' + str(category.id)
            category.save()
            messages.success(request, "Category added successfuly")
            return redirect("menu_builder")
        else:
            print(form.errors)
    else:
        form = CategoryForm()
    context = {
        'form': form,
    }
    return render(request, "vendor/add_category.html", context=context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
            form = CategoryForm(request.POST, instance=category)
            if form.is_valid():
                category_name = form.cleaned_data['category_name']
                category = form.save(commit=False)
                category.vendor = get_vendor(request)
                category.slug = slugify(category_name)
                form.save()
                messages.success(request, "Category updated successfuly")
                return redirect("menu_builder")
            else:
                print(form.errors)
    else:
        form = CategoryForm(instance=category)
    context = {
            'form': form,
            'category': category,
    }
    return render(request, "vendor/edit_category.html", context=context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, "Category has been deleted successfuly")
    return redirect("menu_builder")

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_food(request):
    if request.method == "POST":
        form = FoodForm(request.POST, request.FILES)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.slug= slugify(food_title)
            food.vendor = get_vendor(request)
            form.save()
            messages.success(request, "Food Added successfuly!")
            return redirect('fooditems_by_category', food.category.id)
        else:
            print(form.errors)
    else:
        form = FoodForm()
        #modify this form
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))
    context= {
        'form': form,
    }
    return render(request, "vendor/add_food.html", context=context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_food(request, pk=None):
    food = get_object_or_404(FoodItem, pk=pk)
    if request.method == 'POST':
        form = FoodForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.slug = slugify(food_title)
            food.vendor = get_vendor(request)
            form.save()
            messages.success(request,"Food Updated Successfuly")
            return redirect("fooditems_by_category", food.category.id)
        else:
            print(form.errors)
    else:   
        form = FoodForm(instance=food)
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))

    context = {
        'form': form,
        'food': food,
    }
    return render(request, "vendor/edit_food.html", context=context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_food(request, pk=None):
    food = get_object_or_404(FoodItem, pk=pk)
    food.delete()
    messages.success(request, "Food has been deleted !")
    return redirect("fooditems_by_category", food.category.id)

def opening_hours(request):
    opening_hours = OpeningHour.objects.filter(vendor=get_vendor(request))
    form = OpeningHourForm()
    context = {
        'form': form,
        'opening_hours': opening_hours,
    }
    return render(request, 'vendor/opening_hours.html', context)