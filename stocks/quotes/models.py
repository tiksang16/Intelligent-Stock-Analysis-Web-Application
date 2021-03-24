from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin

# class Stock(models.Model):
#     ticker = models.CharField(max_length=10)

#     def __str__(self):
        
#         return self.ticker

# class StockUser(models.Model):
#     # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="stocklist", null="True")
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="stockuser", null=True)
#     # user = models.CharField(max_length=20)
#     name = models.CharField(max_length=200)

#     def __str__(self):    
#         return self.name

class StockItem(models.Model):
    stockuser = models.ForeignKey(User, on_delete=models.CASCADE, related_name="stockitem",null=True)
    ticker = models.CharField(max_length=10)

    def __str__(self):
        return self.ticker
