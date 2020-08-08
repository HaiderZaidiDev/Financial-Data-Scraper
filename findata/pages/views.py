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


def ratioScraper(ticker):
    URL = 'https://www.marketwatch.com/investing/stock/{}/profile'.format(ticker)
    page = r.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find_all(class_='section')
    ratios = {}

    for items in results:
        try:
            if items.p['class'][0] == 'column':
                ratioValueObj = items.p.next_sibling.next_sibling
                # The first sibling is whitespace, the 2nd one is the correct one.
                ratioValues = ratioValueObj.string
                ratioNames = items.p.string
                djangoSafeRatioNames = ratioNames.replace(' ','_').replace('/', '_').replace('(', '').replace(')','')
                # Django context variables don't work with spaces, so they must
                # be removed. The / in some ratios also need to be removed as
                # they create escape sequences.
                ratios[djangoSafeRatioNames] = ratioValues

        except: # Usually if Paragraph is NoneType
            pass
    return ratios



def homeView(request):
    form = TickerForm(request.POST or None)
    if form.is_valid():
        form.save()
        tickerClean = form.cleaned_data['symbol']




        context = {'form': form}
        context.update(ratioScraper(tickerClean))

        print(context)

        return render(request, 'ratios.html', context)


    context = {
    'form': form
    }

    return render(request, 'index.html', context)



# Create your views here.
