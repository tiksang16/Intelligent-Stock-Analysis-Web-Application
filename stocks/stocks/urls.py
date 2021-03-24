from django.contrib import admin
from django.urls import path, include
# from register import views as v


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('register/', v.register, name="register"),
    path('register/', include('register.urls')),
    path('', include('quotes.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]
