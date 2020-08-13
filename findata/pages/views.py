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
    ratioResults = soup.find_all(class_='section')
    ratios = {}
    ratioPreSplit = {}
    category = None

    # Ratio scraping
    for items in ratioResults:
        try:
            if items.p['class'][0] == 'column':
                # The current item is a section object, the oen above is whitespace,
                # therefore the 2nd previous sibling is the header, which dictates
                # the category for the raito e.g Valuation, Profitability
                nestedSibling = items.previous_sibling.previous_sibling

                if nestedSibling.name == 'h2': # The ratio categories are in h2 tags.
                    category = nestedSibling.string
                    ratioPreSplit = {} # Clears the previous category's ratios


                ratioNames = items.p.string
                # Cuts loop once all ratios have been added to dict
                if ratioNames == 'Industry':
                    break
                ratioValueObj = items.p.next_sibling.next_sibling
                # The first sibling is whitespace, the 2nd one is the actual data.
                ratioValues = ratioValueObj.string
                ratioPreSplit[ratioNames] = ratioValues
                ratios[category] = ratioPreSplit

        except: # Usually if Paragraph is NoneType
            pass

    # Company info scraping
    nameResults = soup.find_all(id="instrumentname")
    priceResults = soup.find_all(class_="pricewrap")
    priceStatusResults = soup.find_all(class_="lastpricedetails")
    companyInfo = {}
    priceData = {} # Price is a seperate dictionary so we can track its currency.

    for items in nameResults:
        name = items.string
        market = items.next_sibling.next_sibling.string
        marketClean = market.replace('\r', '').replace('\n', '').strip()
        companyInfo['name'] = name
        companyInfo['market'] = marketClean

    for items in priceResults:
        if items.p['class'][0] == 'currency':
            currency = items.p.string
            price = items.p.next_sibling.next_sibling.string
            priceData['currency'] = currency
            priceData['price'] = price

    for items in priceStatusResults:
        points = items.span.string
        percentage = items.span.next_sibling.next_sibling.string
        priceStatus = '{0} {1}'.format(points, percentage)
        priceData['priceStatus'] = priceStatus
    companyInfo['priceData'] = priceData

    return ratios, companyInfo

def homeView(request):
    form = TickerForm(request.POST or None)
    if form.is_valid():
        form.save()
        tickerClean = form.cleaned_data['symbol']
        ratios, companyInfo = marketWatchScraper(tickerClean)
        categories = ['Valuation', 'Efficiency', 'Liquidity', 'Profitability', 'Capital Structure']

        # Variables to be passed through context
        name = companyInfo['name']
        market = companyInfo['market']
        currency = companyInfo['priceData']['currency']
        price = companyInfo['priceData']['price']
        priceStatus = companyInfo['priceData']['priceStatus']
        graph = candleStick(tickerClean)


        for i in range(len(categories)):
            if categories[i] not in ratios:
                errorMsg = {}
                errorMsg['Error:'] = " {} ratios for this stock aren't available (were not found on Market Watch).".format(categories[i])
                ratios[categories[i]] = errorMsg

        valuation = ratios['Valuation']
        efficiency = ratios['Efficiency']
        liquidity = ratios['Liquidity']
        profitability = ratios['Profitability']
        capitalStructure = ratios['Capital Structure']

        context = {
        'form'              : form,
        'ticker'            : tickerClean,
        'name'              : name,
        'market'            : market,
        'currency'          : currency,
        'price'             : price,
        'priceStatus'       : priceStatus,
        'valuation'         : valuation,
        'efficiency'        : efficiency ,
        'liquidity'         : liquidity,
        'profitability'     : profitability ,
        'capitalStructure'  : capitalStructure,
        'graph'             : graph
        }

        return render(request, 'ratios.html', context)


    context = {
    'form': form
    }

    return render(request, 'index.html', context)



# Create your views here.
