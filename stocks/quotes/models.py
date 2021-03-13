from django.db import models
from django.contrib.auth.models import User

# class Stock(models.Model):
#     ticker = models.CharField(max_length=10)

#     def __str__(self):
        
#         return self.ticker

class StockList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    def __str__(self):    
        return self.name

class StockItem(models.Model):
    stocklist = models.ForeignKey(StockList, on_delete=models.CASCADE)
    ticker = models.CharField(max_length=10)

    def __str__(self):
        return self.ticker
    