from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from .forms import TickerForm
import plotly.graph_objects as go
from plotly.offline import plot
from alpha_vantage.timeseries import TimeSeries
import pandas as pd
from datetime import datetime
import requests
import os
import requests as r
from bs4 import BeautifulSoup
import plotly.express as px
from bs4 import BeautifulSoup
import requests as r


def candleStick(ticker):
    ts = TimeSeries(key=os.environ['ALPHA_VANTAGE_API_KEY'], output_format='pandas')
    data, meta_data = ts.get_daily(symbol=ticker, outputsize='compact')
    layout = go.Layout(
        width= 724,
        height = 241,
        margin = dict(t=25, r=5, l=5, b=5),
        paper_bgcolor = "#090909",
        plot_bgcolor = "#1B1B1B",
        font_color = "white",
        font_family = "Roboto"
    )
    fig = go.Figure([go.Scatter(x=data.index, y=data['4. close'], line=dict(color="#00ff88"))], layout=layout)
    fig.update_layout(xaxis_rangeslider_visible=False)
    candleStick = plot(fig, output_type='div')
    return candleStick


def marketWatchScraper(ticker):
    """ Scrapes financial data from Market Watch """
    URL = 'https://www.marketwatch.com/investing/stock/{}/profile'.format(ticker)
    page = r.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    ratioResults = soup.find_all(class_="table__cell w75") # Class for ratio name.
    companyResults = soup.find_all(class_="intraday__price")

    valuation = {}
    efficiency = {}
    liquidity = {}
    profitability = {}
    capitalization = {}
    companyInfo = {}
    currency = None
    price = None

    for items in ratioResults:
        try:
            name = items.string # Ratio name.
            value = items.next_sibling.next_sibling.string # Ratio value.
            category = items.parent.parent.parent.parent.h2.span.string.lower()
            # Look into dynamic splitting.
            if category == 'valuation':
                valuation[name] = value
            if category == 'efficiency':
                efficiency[name] = value
            if category == "liquidity":
                liquidity[name] = value
            if category == "profitability":
                profitability[name] = value
            if category == "capitalization":
                capitalization[name] = value
        except:
            pass

    for items in companyResults:
        currency = items.sup.string
        price = items.sup.next_sibling.next_sibling.string
        statusRaw = items.next_sibling.next_sibling.span
        statusPoint = statusRaw.contents[0].string
        statusPercent = statusRaw.next_sibling.next_sibling.contents[0].string
        status = "{0} {1}".format(statusPoint, statusPercent)
        companyName = items.parent.parent.parent.previous_sibling.previous_sibling.h1.string
        companyInfo['currency'] = currency
        companyInfo['price'] = price
        companyInfo['status'] = status
        companyInfo['name'] = companyName

    ratios = {
    'valuation': valuation,
    'efficiency': efficiency,
    'liquidity': liquidity,
    'profitability': profitability,
    'capitalization': capitalization,

    }

    return ratios, companyInfo




def homeView(request):
    form = TickerForm(request.POST or None)
    if form.is_valid():
        form.save()
        tickerClean = form.cleaned_data['symbol']
        ratios, companyInfo = marketWatchScraper(tickerClean)
        categories = ['valuation', 'efficiency', 'liquidity', 'profitability', 'capitalization']

        # Variables to be passed through context
        name = companyInfo['name']
        #market = companyInfo['market']
        currency = companyInfo['currency']
        price = companyInfo['price']
        status = companyInfo['status']
        graph = candleStick(tickerClean)


        for i in range(len(categories)):
            if categories[i] not in ratios:
                errorMsg = {}
                errorMsg['Error:'] = " {} ratios for this stock aren't available (were not found on Market Watch).".format(categories[i])
                ratios[categories[i]] = errorMsg

        valuation = ratios['valuation']
        efficiency = ratios['efficiency']
        liquidity = ratios['liquidity']
        profitability = ratios['profitability']
        capitalization= ratios['capitalization']

        context = {
        'form'              : form,
        'ticker'            : tickerClean,
        'name'              : name,
        'currency'          : currency,
        'price'             : price,
        'status'       : status,
        'valuation'         : valuation,
        'efficiency'        : efficiency ,
        'liquidity'         : liquidity,
        'profitability'     : profitability ,
        'capitalization'  : capitalization,
        'graph'             : graph
        }

        return render(request, 'ratios.html', context)


    context = {
    'form': form
    }

    return render(request, 'index.html', context)

def error500View(request):
    return render(request, 'error500.html', {})

def error404View(request):
    return render(request, 'error404.html', {})

# Create your views here.
