from os import stat
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import login_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('Home/', views.Home, name = 'home'),
    path('shop/', include('shop.urls')),
    path('auth/', include('accounts.urls'))
    
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
