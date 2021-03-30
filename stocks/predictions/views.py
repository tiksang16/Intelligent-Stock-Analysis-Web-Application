from django.shortcuts import render, redirect
import quandl
import pandas as pd
import numpy as np
# import datetime
from sklearn.linear_model import LinearRegression
from sklearn import preprocessing, model_selection, svm


from alpha_vantage.timeseries import TimeSeries
from statsmodels.tsa.arima_model import ARIMA
from sklearn.metrics import mean_squared_error
# import matplotlib.pyplot as plt
# plt.style.use('ggplot')
import math, random
from datetime import datetime
import datetime as dt
import yfinance as yf
import tweepy
import preprocessor as p
import re
from textblob import TextBlob
from . import constants as ct
from . import Tweet
import nltk
nltk.download('punkt')

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
# Create your views here.

def home(request):
    return render(request,'arima.html')


# def linerregression(request):
#     # Quandl API key. Create your own key via registering at quandl.com
#     quandl.ApiConfig.api_key = "9LyAs6SMpaowFKBPiBRT"
#     #personalapikey=
#     #other'skey=RHVBxuQQR_xxy8SPBDGV
#     # Getting input from Templates for ticker_value and number_of_days
#     ticker_value = request.POST.get('ticker')
#     number_of_days = request.POST.get('days')
#     number_of_days = int(number_of_days)
#     # Fetching ticker values from Quandl API 
#     df = quandl.get("WIKI/"+ticker_value+"")
#     df = df[['Adj. Close']]
#     forecast_out = int(number_of_days)
#     df['Prediction'] = df[['Adj. Close']].shift(-forecast_out)
#     # Splitting data for Test and Train
#     X = np.array(df.drop(['Prediction'],1))
#     X = preprocessing.scale(X)
#     X_forecast = X[-forecast_out:]
#     X = X[:-forecast_out]
#     y = np.array(df['Prediction'])
#     y = y[:-forecast_out]
#     X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size = 0.2)
#     # Applying Linear Regression
#     clf = LinearRegression()
#     clf.fit(X_train,y_train)
#     # Prediction Score
#     confidence = clf.score(X_test, y_test)
#     # Predicting for 'n' days stock data
#     forecast_prediction = clf.predict(X_forecast)
#     forecast = forecast_prediction.tolist()
#     return render(request,'predict.html',{'confidence' : confidence,'forecast': forecast,'ticker_value':ticker_value,'number_of_days':number_of_days})

def insertintotable(request):
    nm = request.POST.get('nm')

    #**************** FUNCTIONS TO FETCH DATA ***************************
    def get_historical(quote):
        end = datetime.now()
        start = datetime(end.year-2,end.month,end.day)
        data = yf.download(quote, start=start, end=end)
        df = pd.DataFrame(data=data)
        df.to_csv(''+quote+'.csv')
        if(df.empty):
            ts = TimeSeries(key='N6A6QT6IBFJOPJ70',output_format='pandas')
            data, meta_data = ts.get_daily_adjusted(symbol='NSE:'+quote, outputsize='full')
            #Format df
            #Last 2 yrs rows => 502, in ascending order => ::-1
            data=data.head(503).iloc[::-1]
            data=data.reset_index()
            #Keep Required cols only
            df=pd.DataFrame()
            df['Date']=data['date']
            df['Open']=data['1. open']
            df['High']=data['2. high']
            df['Low']=data['3. low']
            df['Close']=data['4. close']
            df['Adj Close']=data['5. adjusted close']
            df['Volume']=data['6. volume']
            df.to_csv(''+quote+'.csv',index=False)
        return

    #******************** ARIMA SECTION ********************
    def ARIMA_ALGO(df):
        uniqueVals = df["Code"].unique()  
        len(uniqueVals)
        df=df.set_index("Code")
        #for daily basis
        def parser(x):
            return datetime.strptime(x, '%Y-%m-%d')
        def arima_model(train, test):
            history = [x for x in train]
            predictions = list()
            for t in range(len(test)):
                model = ARIMA(history, order=(6,1 ,0))
                model_fit = model.fit(disp=0)
                output = model_fit.forecast()
                yhat = output[0]
                predictions.append(yhat[0])
                obs = test[t]
                history.append(obs)
            return predictions
        for company in uniqueVals[:10]:
            data=(df.loc[company,:]).reset_index()
            data['Price'] = data['Close']
            Quantity_date = data[['Price','Date']]
            Quantity_date.index = Quantity_date['Date'].map(lambda x: parser(x))
            Quantity_date['Price'] = Quantity_date['Price'].map(lambda x: float(x))
            Quantity_date = Quantity_date.fillna(Quantity_date.bfill())
            Quantity_date = Quantity_date.drop(['Date'],axis =1)
            # fig = plt.figure(figsize=(7.2,4.8),dpi=65)
            # plt.plot(Quantity_date)
            # plt.savefig('static/Trends.png')
            # plt.close(fig)
            
            quantity = Quantity_date.values
            size = int(len(quantity) * 0.80)
            train, test = quantity[0:size], quantity[size:len(quantity)]
            #fit in model
            predictions = arima_model(train, test)
            
            #plot graph
            # fig = plt.figure(figsize=(7.2,4.8),dpi=65)
            # plt.plot(test,label='Actual Price')
            # plt.plot(predictions,label='Predicted Price')
            # plt.legend(loc=4)
            # plt.savefig('static/ARIMA.png')
            # plt.close(fig)
            # print()
            print("##############################################################################")
            arima_pred=predictions[-2]
            print("Tomorrow's",quote," Closing Price Prediction by ARIMA:",arima_pred)
            #rmse calculation
            error_arima = math.sqrt(mean_squared_error(test, predictions))
            print("ARIMA RMSE:",error_arima)
            print("##############################################################################")
            return arima_pred, error_arima
        
    #***************** LINEAR REGRESSION SECTION ******************       
    def LIN_REG_ALGO(df):
        #No of days to be forcasted in future
        forecast_out = int(7)
        #Price after n days
        df['Close after n days'] = df['Close'].shift(-forecast_out)
        #New df with only relevant data
        df_new=df[['Close','Close after n days']]

        #Structure data for train, test & forecast
        #lables of known data, discard last 35 rows
        y =np.array(df_new.iloc[:-forecast_out,-1])
        y=np.reshape(y, (-1,1))
        #all cols of known data except lables, discard last 35 rows
        X=np.array(df_new.iloc[:-forecast_out,0:-1])
        #Unknown, X to be forecasted
        X_to_be_forecasted=np.array(df_new.iloc[-forecast_out:,0:-1])
        
        #Traning, testing to plot graphs, check accuracy
        X_train=X[0:int(0.8*len(df)),:]
        X_test=X[int(0.8*len(df)):,:]
        y_train=y[0:int(0.8*len(df)),:]
        y_test=y[int(0.8*len(df)):,:]
        
        # Feature Scaling===Normalization
        from sklearn.preprocessing import StandardScaler
        sc = StandardScaler()
        X_train = sc.fit_transform(X_train)
        X_test = sc.transform(X_test)
        
        X_to_be_forecasted=sc.transform(X_to_be_forecasted)
        
        #Training
        clf = LinearRegression(n_jobs=-1)
        clf.fit(X_train, y_train)
        
        #Testing
        y_test_pred=clf.predict(X_test)
        y_test_pred=y_test_pred*(1.04)
        # import matplotlib.pyplot as plt2
        # fig = plt2.figure(figsize=(7.2,4.8),dpi=65)
        # plt2.plot(y_test,label='Actual Price' )
        # plt2.plot(y_test_pred,label='Predicted Price')
        
        # plt2.legend(loc=4)
        # plt2.savefig('static/LR.png')
        # plt2.close(fig)
        
        error_lr = math.sqrt(mean_squared_error(y_test, y_test_pred))
        
        
        #Forecasting
        forecast_set = clf.predict(X_to_be_forecasted)
        forecast_set=forecast_set*(1.04)
        mean=forecast_set.mean()
        lr_pred=forecast_set[0,0]
        print()
        print("##############################################################################")
        print("Tomorrow's ",quote," Closing Price Prediction by Linear Regression: ",lr_pred)
        print("Linear Regression RMSE:",error_lr)
        print("##############################################################################")
        return df, lr_pred, forecast_set, mean, error_lr
    #**************** SENTIMENT ANALYSIS **************************
    def retrieving_tweets_polarity(symbol):
        stock_ticker_map = pd.read_csv('Yahoo-Finance-Ticker-Symbols.csv')
        stock_full_form = stock_ticker_map[stock_ticker_map['Ticker']==symbol]
        symbol = stock_full_form['Name'].to_list()[0][0:12]

        auth = tweepy.OAuthHandler(ct.consumer_key, ct.consumer_secret)
        auth.set_access_token(ct.access_token, ct.access_token_secret)
        user = tweepy.API(auth)
        
        tweets = tweepy.Cursor(user.search, q=symbol, tweet_mode='extended', lang='en',exclude_replies=True).items(ct.num_of_tweets)
        
        tweet_list = [] #List of tweets alongside polarity
        global_polarity = 0 #Polarity of all tweets === Sum of polarities of individual tweets
        tw_list=[] #List of tweets only => to be displayed on web page
        #Count Positive, Negative to plot pie chart
        pos=0 #Num of pos tweets
        neg=1 #Num of negative tweets
        for tweet in tweets:
            count=20 #Num of tweets to be displayed on web page
            #Convert to Textblob format for assigning polarity
            tw2 = tweet.full_text
            tw = tweet.full_text
            #Clean
            tw=p.clean(tw)
            #print("-------------------------------CLEANED TWEET-----------------------------")
            #print(tw)
            #Replace &amp; by &
            tw=re.sub('&amp;','&',tw)
            #Remove :
            tw=re.sub(':','',tw)
            #print("-------------------------------TWEET AFTER REGEX MATCHING-----------------------------")
            #print(tw)
            #Remove Emojis and Hindi Characters
            tw=tw.encode('ascii', 'ignore').decode('ascii')

            #print("-------------------------------TWEET AFTER REMOVING NON ASCII CHARS-----------------------------")
            #print(tw)
            blob = TextBlob(tw)
            polarity = 0 #Polarity of single individual tweet
            for sentence in blob.sentences:
                   
                polarity += sentence.sentiment.polarity
                if polarity>0:
                    pos=pos+1
                if polarity<0:
                    neg=neg+1
                
                global_polarity += sentence.sentiment.polarity
            if count > 0:
                tw_list.append(tw2)
                
            tweet_list.append(Tweet.Tweet(tw, polarity))
            count=count-1
        if len(tweet_list) != 0:
            global_polarity = global_polarity / len(tweet_list)
        else:
            global_polarity = global_polarity
        neutral=ct.num_of_tweets-pos-neg
        if neutral<0:
        	neg=neg+neutral
        	neutral=20
        print()
        print("##############################################################################")
        print("Positive Tweets :",pos,"Negative Tweets :",neg,"Neutral Tweets :",neutral)
        print("##############################################################################")
        labels=['Positive','Negative','Neutral']
        sizes = [pos,neg,neutral]
        explode = (0, 0, 0)
        # fig = plt.figure(figsize=(7.2,4.8),dpi=65)
        # fig1, ax1 = plt.subplots(figsize=(7.2,4.8),dpi=65)
        # ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', startangle=90)
        # Equal aspect ratio ensures that pie is drawn as a circle
        # ax1.axis('equal')  
        # plt.tight_layout()
        # plt.savefig('static/SA.png')
        # plt.close(fig)
        #plt.show()
        if global_polarity>0:
            print()
            print("##############################################################################")
            print("Tweets Polarity: Overall Positive")
            print("##############################################################################")
            tw_pol="Overall Positive"
        else:
            print()
            print("##############################################################################")
            print("Tweets Polarity: Overall Negative")
            print("##############################################################################")
            tw_pol="Overall Negative"
        tweeters_list=[]
        for i in range(0,5):
            tweeters_list.append(tw_list[i])

        return global_polarity,tweeters_list,tw_pol,pos,neg,neutral


    def recommending(df, global_polarity,today_stock,mean):
        if today_stock.iloc[-1]['Close'] < mean:
            if global_polarity > 0:
                idea="RISE"
                decision="BUY"
                print()
                print("##############################################################################")
                print("According to the ML Predictions and Sentiment Analysis of Tweets, a",idea,"in",quote,"stock is expected => ",decision)
            elif global_polarity <= 0:
                idea="FALL"
                decision="SELL"
                print()
                print("##############################################################################")
                print("According to the ML Predictions and Sentiment Analysis of Tweets, a",idea,"in",quote,"stock is expected => ",decision)
        else:
            idea="FALL"
            decision="SELL"
            print()
            print("##############################################################################")
            print("According to the ML Predictions and Sentiment Analysis of Tweets, a",idea,"in",quote,"stock is expected => ",decision)
        return idea, decision


    #**************GET DATA ***************************************
    quote=nm
    #Try-except to check if valid stock symbol
    try:
        get_historical(quote)
    except:
        return render_template('index.html',not_found=True)
    else:
    
        #************** PREPROCESSUNG ***********************
        df = pd.read_csv(''+quote+'.csv')
        print("##############################################################################")
        print("Today's",quote,"Stock Data: ")
        today_stock=df.iloc[-1:]
        print(today_stock)
        print("##############################################################################")
        df = df.dropna()
        code_list=[]
        for i in range(0,len(df)):
            code_list.append(quote)
        df2=pd.DataFrame(code_list,columns=['Code'])
        df2 = pd.concat([df2, df], axis=1)
        df=df2


        arima_pred, error_arima=ARIMA_ALGO(df)
        df, lr_pred, forecast_set,mean,error_lr=LIN_REG_ALGO(df)
        polarity,tweeters_list,tw_pol,pos,neg,neutral = retrieving_tweets_polarity(quote)
        
        idea, decision=recommending(df, polarity,today_stock,mean)
        print()
        print("Forecasted Prices for Next 7 days:")
        print(forecast_set)
        today_stock=today_stock.round(2)
        # return render('arima.html',quote=quote,arima_pred=round(arima_pred,2),
        #                        lr_pred=round(lr_pred,2),open_s=today_stock['Open'].to_string(index=False),
        #                        close_s=today_stock['Close'].to_string(index=False),adj_close=today_stock['Adj Close'].to_string(index=False),
        #                        tw_list=tw_list,tw_pol=tw_pol,idea=idea,decision=decision,high_s=today_stock['High'].to_string(index=False),
        #                        low_s=today_stock['Low'].to_string(index=False),vol=today_stock['Volume'].to_string(index=False),
        #                        forecast_set=forecast_set,error_lr=round(error_lr,2),error_arima=round(error_arima,2))

        return render(request,'arima.html',{'quote':quote,'arima_pred':round(arima_pred,2),
                               'lr_pred':round(lr_pred,2),'open_s':today_stock['Open'].to_string(index=False),
                               'close_s':today_stock['Close'].to_string(index=False),'adj_close':today_stock['Adj Close'].to_string(index=False),
                               'tweeters_list':tweeters_list,'tw_pol':tw_pol,'idea':idea,'decision':decision,'high_s':today_stock['High'].to_string(index=False),
                               'low_s':today_stock['Low'].to_string(index=False),'vol':today_stock['Volume'].to_string(index=False),
                               'forecast_set':forecast_set,'error_lr':round(error_lr,2),'error_arima':round(error_arima,2)})
    