from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="predict"),
    path('predict/', views.insertstockdata, name="insertstockdata"),
]
