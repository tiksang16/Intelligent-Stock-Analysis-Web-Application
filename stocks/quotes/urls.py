from django.urls import path
from . import views
from predictions import views as pv

urlpatterns = [
    path('', views.home, name="home"),
    path('about.html', views.about, name="about"),
    # path('add_stock.html', views.add_stock, name="add_stock"),
    path('add_stock/<pk>', views.add_stock, name="add_stock"),
    path('delete/<stock_id>', views.delete, name="delete"),
    path('delete_stock/<pk>', views.delete_stock, name="delete_stock"),
    path('chart.html', views.chart, name="chart"),
    # path('predict.html', pv.home, name="arima")
]