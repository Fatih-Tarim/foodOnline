from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required
from django.db.models import Q

#Datetime
from datetime import date,datetime

#Gis
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance

#Vendor App
from vendor.models import Vendor, OpeningHour
from vendor.utils import get_vendor

#Menu App
from menu.models import Category, FoodItem

#Cart App
from marketplace.models import Cart

#Marketplace App
from marketplace.context_processors import get_card_counter, get_cart_amount

#Order App
from orders.forms import OrderForm


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
    opening_hours = OpeningHour.objects.filter(vendor=vendor).order_by('day', '-from_hour')
    #Check current day's opening hours
    today_date = date.today()
    today = today_date.isoweekday()
    current_opening_hours = OpeningHour.objects.filter(vendor=vendor, day=today)
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    context= {
        'vendor': vendor,
        'categories': categories,
        'cart_items': cart_items,
        'opening_hours': opening_hours,
        'current_opening_hours': current_opening_hours,
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
                    return JsonResponse({'status':'Success', 'message':'Increased the cart quantity', 'cart_counter': get_card_counter(request), 'qty':check_cart.quantity, 'cart_amount':get_cart_amount(request)})
                except:
                    check_cart = Cart.objects.create(user=request.user, fooditem=food_item, quantity=1)
                    return JsonResponse({'status':'Success', 'message':'Added the food to the cart', 'cart_counter': get_card_counter(request), 'qty':check_cart.quantity, 'cart_amount':get_cart_amount(request)})
            except:
                return JsonResponse({'status':'Failed', 'message':'This food does not exist.'})
        else:
            return JsonResponse({'status':'Failed', 'message':'Invalid request'})

    else:
        return JsonResponse({
            'status': 'login_required',
            'message': 'Please login to continue'
        })
    
def decrease_cart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            #Check if the fooditem exists
            try:
                food_item = FoodItem.objects.get(id=food_id)
                #Check if the user has already added that food to the cart
                try:
                    check_cart = Cart.objects.get(user=request.user, fooditem=food_item)
                    if check_cart.quantity >= 1:
                        #Decrease the cart quantity
                        check_cart.quantity -= 1
                        check_cart.save()
                    else:
                        check_cart.delete()
                        check_cart.quantity = 0
                    return JsonResponse({'status':'Success', 'message':'Increased the cart quantity', 'cart_counter': get_card_counter(request), 'qty':check_cart.quantity, 'cart_amount':get_cart_amount(request)})
                except:
                    return JsonResponse({'status':'Failed', 'message':'You do not have this item in your cart!'})
            except:
                return JsonResponse({'status':'Failed', 'message':'This food does not exist.'})
        else:
            return JsonResponse({'status':'Failed', 'message':'Invalid request'})

    else:
        return JsonResponse({
            'status': 'login_required',
            'message': 'Please login to continue'
        })

@login_required(login_url="login")
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    context= {
        'cart_items': cart_items,
    }
    return render(request, "marketplace/cart.html", context)

def delete_cart(request, cart_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                #check if the cart item exist
                cart_item = Cart.objects.get(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status':'Success', 'message':'Cart item has been deleted!', 'cart_counter': get_card_counter(request), 'cart_amount':get_cart_amount(request)})
            except:
                #cart item doesn't exist
                return JsonResponse({'status':'Failed', 'message':'Cart item does not exist!'})
        else:
            return JsonResponse({'status':'Failed', 'message':'Invalid request'})


def search(request):
    if not 'address' in request.GET:
        return redirect("marketplace")
    else:
        address = request.GET['address']
        latitude = request.GET['lat']
        longitude = request.GET['lng']
        radius = request.GET['radius']
        keyword = request.GET['keyword']

        #get vendor ids that has the food item the user is looking for
        fetch_vendors_by_fooditems = FoodItem.objects.filter(food_title__icontains=keyword, is_available=True).values_list('vendor', flat=True)
        vendors = Vendor.objects.filter(Q(id__in=fetch_vendors_by_fooditems) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True))
        if latitude and longitude and radius:
            point = GEOSGeometry('POINT(%s %s)' %(longitude, latitude))
            vendors = Vendor.objects.filter(Q(id__in=fetch_vendors_by_fooditems) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True),
                                            user_profile__location__distance_lte=(point, D(km=radius))).annotate(distance=Distance("user_profile__location", point)).order_by("distance")

            for vendor in vendors:
                vendors.kms = round(vendor.distance.km, 1)

        vendor_count= vendors.count()
        context={
            'vendors': vendors,
            'vendor_count': vendor_count,
            'source_location': address,
        }
        return render(request, "marketplace/listings.html", context)
    
def checkout(request):
    form = OrderForm()
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <=0:
        return redirect("martketplace")
    context = {
        'form': form,
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/checkout.html', context=context)

