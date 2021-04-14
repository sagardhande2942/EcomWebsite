from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('about/', views.about, name = 'about'),
    path('contact', views.contact, name = 'contact'),
    path('tracker/', views.tracker, name = 'tracker'),
    path('products/<int:myid>', views.productView, name = 'productView'),
    path('checkout/', views.checkout, name = 'checkout'),
    path('search/', views.search, name = 'search'),
    path('timepass/', views.search, name = 'checkemailavailability'),
    path('cart/', views.showCart, name = 'cart'),
    path('config/', views.stripe_config),
    path('create-checkout-session/', views.create_checkout_session),
    path('success/', views.successPay, name = "success"),
    path('cancel/', views.cancelPay, name = 'cancel'),
    path('getPrice/', views.getPrice, name = 'getPrice'),
    path('getLogoutData/', views.getLogoutData, name='getLogoutData'),
    path('getCart/', views.getCart, name='getCart'),
    path('trackCart/', views.trackCart)
]