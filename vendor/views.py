from django.shortcuts import render, get_object_or_404

#Vendor App
from vendor.forms import VendorForm
from vendor.models import Vendor

#Account App
from accounts.forms import UserProfileForm
from accounts.models import UserProfile

def v_profile(request):
    #Instances
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    #Forms
    profile_form = UserProfileForm(instance=profile)
    vendor_form = VendorForm(instance=vendor)

    context = {
        'profile_form': profile_form,
        'vendor_form': vendor_form,
        'profile': profile,
        'vendor': vendor,
    }
    return render(request, "vendor/v_profile.html", context=context)