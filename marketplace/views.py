from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch

#Vendor App
from vendor.models import Vendor
from vendor.utils import get_vendor

#Menu App
from menu.models import Category, FoodItem

#Cart App
from marketplace.models import Cart


def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    context = {
        'vendors': vendors,
        'vendor_count': vendor_count,
    }
    return render(request, "marketplace/listings.html", context=context)

def vendor_detail(request, vendor_slug=None):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset=FoodItem.objects.filter(is_available=True)
        )
    )
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    context= {
        'vendor': vendor,
        'categories': categories,
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/vendor_detail.html', context)

def add_to_cart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            #Check if the fooditem exists
            try:
                food_item = FoodItem.objects.get(id=food_id)
                #Check if the user has already added that food to the cart
                try:
                    check_cart = Cart.objects.get(user=request.user, fooditem=food_item)
                    #Increase the cart quantity
                    check_cart.quantity += 1
                    check_cart.save()
                    return JsonResponse({'status':'Success', 'message':'Increased the cart quantity'})
                except:
                    check_cart = Cart.objects.create(user=request.user, fooditem=food_item, quantity=1)
                    return JsonResponse({'status':'Success', 'message':'Added the food to the cart'})
            except:
                return JsonResponse({'status':'Failed', 'message':'This food does not exist.'})
        else:
            return JsonResponse({'status':'Failed', 'message':'Invalid request'})

    else:
        return JsonResponse({
            'status': 'Failed',
            'message': 'Please login to continue'
        })

