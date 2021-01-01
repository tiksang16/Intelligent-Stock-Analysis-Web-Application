from django.shortcuts import render

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

def about(request):
    return render(request,'about.html',{})


def add_stock(request):
    
    ticker = Stock.object.all()
    return render(request,'add_stock.html',{'ticker':ticker})