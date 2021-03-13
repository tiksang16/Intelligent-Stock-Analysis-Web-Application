from django import forms
from .models import Stock
# from .models import StockList, StockItem

class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ["ticker"]