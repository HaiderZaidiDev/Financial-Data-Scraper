from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from .forms import TickerForm
from alpha_vantage.timeseries import TimeSeries
import plotly
import pandas as pd

import requests
import os
import requests as r
from bs4 import BeautifulSoup

def infoScraper(ticker):
    """ Scrapes company and price data from market watch"""
    URL = 'https://www.marketwatch.com/investing/stock/{}/profile'.format(ticker)
    page = r.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
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
    return companyInfo


def ratioScraper(ticker):
    """ Scrapes financial ratios from Market Watch"""
    URL = 'https://www.marketwatch.com/investing/stock/{}/profile'.format(ticker)
    page = r.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find_all(class_='section')
    ratios = {}
    ratioPreSplit = {}
    category = None

    for items in results:
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
    return ratios

def homeView(request):
    form = TickerForm(request.POST or None)
    if form.is_valid():
        form.save()
        tickerClean = form.cleaned_data['symbol']
        ratios = ratioScraper(tickerClean)
        companyInfo = infoScraper(tickerClean)
        categories = ['Valuation', 'Efficiency', 'Liquidity', 'Profitability', 'Capital Structure']

        # Variables to be passed through context
        name = companyInfo['name']
        market = companyInfo['market']
        currency = companyInfo['priceData']['currency']
        price = companyInfo['priceData']['price']
        priceStatus = companyInfo['priceData']['priceStatus']


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
        }

        print(context)

        return render(request, 'ratios.html', context)


    context = {
    'form': form
    }

    return render(request, 'index.html', context)



# Create your views here.
