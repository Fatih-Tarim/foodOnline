from django.urls import path
from . import views
from accounts import views as AccountViews


urlpatterns = [
    path("", AccountViews.vendorDashboard, name="vendor"),
    path('profile/', views.v_profile, name='v_profile'),
    path('menu-builder/', views.menu_builder, name='menu_builder'),
]
