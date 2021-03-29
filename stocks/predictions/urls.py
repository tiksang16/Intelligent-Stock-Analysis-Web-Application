from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="arima"),
    path('arima/', views.insertintotable, name="insertintotable"),
]