from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from .forms import TickerForm
from alpha_vantage.timeseries import TimeSeries
import plotly.express as px
import pandas as pd

import requests
import os

def financeAPI(function, ticker):
    call = 'https://www.alphavantage.co/query?function={0}&symbol={1}&apikey={2}'.format(function, ticker, '5R0NUWKOB76JU3EC')
    data = requests.get(call).json()
    return data

def fundamentals(ticker):
    fundamentalData = financeAPI('OVERVIEW', ticker)
    return fundamentalData

def latestQuaterly(ticker):
    report = financeAPI('INCOME_STATEMENT', tickerClean)['quarterlyReports'][0]
    return report

def currentStockPrice(ticker):
    call = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={0}&apikey={1}'.format(ticker, '5R0NUWKOB76JU3EC')
    data = requests.get(call).json()
    fiveMinPrice = data['Global Quote']['05. price']
    return fiveMinPrice




def homeView(request):
    form = TickerForm(request.POST or None)
    if form.is_valid():
        form.save()
        tickerClean = form.cleaned_data['symbol']
        print(tickerClean)

        # Calculations
        try:

            # Identifiying info.
            name = fundamentals(tickerClean)['Name']
            exchange = '{0}: {1}'.format(fundamentals(tickerClean)['Exchange'], tickerClean)
            price = currentStockPrice(tickerClean)

            # Time Series Graph
            ts = TimeSeries(key='5R0NUWKOB76JU3EC', output_format='pandas')
            data, meta_data = ts.get_intraday(symbol=tickerClean, interval='1min', outputsize='full')
            grpah_div = plotly.offline.plot(fig, auto_open=False, output_type='div')


            # Valuation
            PERatio = fundamentals(tickerClean)['PERatio']
            PriceToSalesRatioTTM = fundamentals(tickerClean)['PriceToSalesRatioTTM']
            PriceToBookRatio = fundamentals(tickerClean)
            EVToEBITDA = fundamentals(tickerClean)['EVToEBITDA']

            # Profitability
            profitMargin = latestQuarterly(tickerClean)['ProfitMargin']
            operatingMarginTTM = fundamentals(tickerClean)['OperatingMarginTTM']
            ReturnOnAssetsTTM = fundamentals(tickerClean)['ReturnOnAssetsTTM']
            ReturnOnEquityTTM = fundamentals(tickerClean)['ReturnOnEquityTTM']

            # Capital Structure
            ## Debt to Equity
            totalLiabilities = latestQuarterly(tickerClean)['totalLiabilities']
            equity = latestQuarterly(tickerClean)['totalShareholderEquity']
            totalAssets = latestQuarterly(tickerClean)['totalAssets']


            debtToEquity = totalLiabilities/equity
            debtToAssets = totalLiabilities/totalAssets

            ##Liquidity
            totalCurrentAssets = latestQuarterly(tickerClean)['totalCurrentAssets']
            totalCurrentLiabilities = latestQuarterly(tickerClean)['totalCurrentLiabilities']

            currentRatio = totalCurrentAssets/totalCurrentLiabilities


        except:
            return HttpResponse("Sorry, too many requests are being made for financial data at this time. Please try again later. ")

        context = {}
        context.update({
            'form'                  : form,
            'symbol'                : tickerClean,
            'name'                  : name,
            'exchange'              : exchange,
            'price'                 : price,
            'PERatio'               : PERatio,
            'PriceToSalesRatioTTM'  : PriceToSalesRatioTTM,
            'PriceToBookRatio'      : PriceToBookRatio,
            'EVToEBITDA'            : EVToEBITDA,
            'profitMargin'          : profitMargin,
            'operatingMarginTTM'    : operatingMarginTTM,
            'ReturnOnAssetsTTM'     : ReturnOnAssetsTTM,
            'ReturnOnEquityTTM'     : ReturnOnEquityTTM,
            'debtToEquity'          : debtToEquity,
            'debtToAssets'          : debtToAssets,
            'currentRatio'          : currentRatio,
            'graph'                 : graph_div,

        })

        print(context)

        return render(request, 'ratios.html', context)


    context = {
    'form': form
    }

    return render(request, 'index.html', context)



# Create your views here.
