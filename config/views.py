from django.shortcuts import render
from django.http import HttpResponse

#Vendor App
from vendor.models import Vendor

#Gis
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance



def home(request):
    if 'lat' and 'lng' in request.GET:
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')

        point = GEOSGeometry('POINT(%s %s)' %(lng, lat))
        vendors = Vendor.objects.filter(user_profile__location__distance_lte=(point, D(km=10))).annotate(distance=Distance("user_profile__location", point)).order_by("distance")

        for vendor in vendors:
            vendors.kms = round(vendor.distance.km, 1)
    else:  
        vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]
    context={
        'vendors': vendors,
    }
    return render(request, template_name='home.html', context=context)