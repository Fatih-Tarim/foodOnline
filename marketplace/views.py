from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404

#Vendor App
from vendor.models import Vendor

#Menu App

def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    context = {
        'vendors': vendors,
        'vendor_count': vendor_count,
    }
    return render(request, "marketplace/listings.html", context=context)

def vendor_detail(request, vendor_slug=None):
    # vendor = Vendor.objects.filter(vendor_slug=vendor_slug)
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    context= {
        'vendor': vendor,
    }
    return render(request, 'marketplace/vendor_detail.html', context)
