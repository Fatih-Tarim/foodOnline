from django.shortcuts import render
from django.http import HttpResponse

def registerUser(request):
    return HttpResponse("registerUser")

def registerRestaurant(request):
    return HttpResponse("registerRestaurant")