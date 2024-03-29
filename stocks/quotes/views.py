from django.shortcuts import render, redirect
# from .models import Stock
from .models import StockItem
from .forms import StockForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# from django.http import HttpResponse, HttpResponseRedirect

#pk_8e85210a28d7425eadcbe2bf2a7b1072

def home(request):
    import requests
    import json

    if request.method == 'POST':
        ticker = request.POST['ticker']
        api_request = requests.get("https://cloud.iexapis.com/stable/stock/" + ticker + "/quote?token=pk_8e85210a28d7425eadcbe2bf2a7b1072")

        try:
            api = json.loads(api_request.content)
        except Exception as e:
            api = "Error..."
        return render(request, 'home.html', {'api': api})
    
    else:
        return render(request, 'home.html', {'ticker': "Enter a Ticker Symbol Above..."})

    return render(request, 'home.html', {'api': api})

@login_required
def about(request):
    return render(request,'about.html',{})

@login_required
def add_stock(request, pk):
    import requests
    import json
    if request.method == 'POST':
        form = StockForm(request.POST or None)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.stockuser = request.user
            obj.save()
            # form.save()
            messages.success(request, ("Stock Has Been Added!"))
            # request.user.stockuser.add()
            # request.user.stockitem.add(t)
            return redirect('add_stock', pk=request.user.pk)
            

    else:
        # ticker = StockItem.objects.all()
        ticker = StockItem.objects.filter(stockuser_id=pk)
        output = []
        for ticker_item in ticker:
            api_request = requests.get("https://cloud.iexapis.com/stable/stock/" + str(ticker_item) + "/quote?token=pk_8e85210a28d7425eadcbe2bf2a7b1072")
            try:
                api = json.loads(api_request.content)
                output.append(api)
            except Exception as e:
                api = "Error..."


        return render(request,'add_stock.html',{'ticker': ticker, 'output': output})




@login_required
def delete(request, stock_id):
    item = StockItem.objects.get(pk=stock_id)
    item.delete()
    messages.success(request,("Stock Has Been Deleted!"))
    return redirect('delete_stock',pk=request.user.pk)

@login_required
def delete_stock(request, pk):
    # ticker = StockItem.objects.all()
    ticker = StockItem.objects.filter(stockuser_id = pk)
    return render(request,'delete_stock.html',{'ticker': ticker})

@login_required
def chart(request):
    return render(request,'chart.html')