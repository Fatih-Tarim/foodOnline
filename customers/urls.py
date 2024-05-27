from django.urls import path
from accounts import views as AccountViews
from . import views

urlpatterns = [
    path("", AccountViews.customerDashboard, name="customer"),
    path("profile/", views.cprofile, name="cprofile"),
    path('myOrders', views.myOrders, name='customer_my_orders'),
    path('order_details/<int:order_number>/', views.order_detail, name='order_details'),
] 
