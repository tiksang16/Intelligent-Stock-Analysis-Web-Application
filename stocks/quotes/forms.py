from django import forms
# from .models import Stock
from .models import StockItem

class StockForm(forms.ModelForm):
    class Meta:
        model = StockItem
        fields = ["ticker"]