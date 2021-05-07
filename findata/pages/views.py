from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from .forms import TickerForm
import plotly.graph_objects as go
from plotly.offline import plot
from alpha_vantage.timeseries import TimeSeries
import pandas as pd
from datetime import datetime
import os
import requests as r
from bs4 import BeautifulSoup


def scatterPlot(ticker):
    """ Generates a time series graph of a stock's price activity.

    Parameters
    ----------
    Ticker: str
        Ticker symbol for a stock.

    Returns
    -------
    scatterPlot: html
        Div containing scatter graph of a stock's share price over 6 months.

    Notes
    -----
    Data is fetched from the alpha vantage API.

    """
    # Fetching time series from alpha vantage, as a Pandas DF.
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
    # Plotting scatter plot.
    fig = go.Figure([go.Scatter(x=data.index, y=data['4. close'], line=dict(color="#00ff88"))], layout=layout)
    fig.update_layout(xaxis_rangeslider_visible=False)
    scatterPlot = plot(fig, output_type='div')
    return scatterPlot


def marketWatchScraper(ticker):
    """ Scrapes financial data from Market Watch

    Parameters
    ----------
    Ticker: str
        Ticker symbol for a stock.

    Returns
    -------
    ratios: dict
        Valuation, efficiency, liquidities, profitability, and capitalization
        ratios of the ticker.

    companyInfo: dict
        General information about the company 'ticker' belongs to.

    Notes
    -----
    Data is scraped from market watch.

    """
    # Fetching page for 'ticker' from market watch.
    URL = 'https://www.marketwatch.com/investing/stock/{}/profile'.format(ticker)
    page = r.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    ratioResults = soup.find_all(class_="table__cell w75") # Class for ratio name.
    companyResults = soup.find_all(class_="intraday__price")

    # Initializing dicts, data scraped will be placed here.
    valuation = {}
    efficiency = {}
    liquidity = {}
    profitability = {}
    capitalization = {}
    companyInfo = {}
    currency = None
    price = None

    # Scraping ratios.
    for items in ratioResults:
        try:
            name = items.string
            value = items.next_sibling.next_sibling.string # Value/amount of the ratio.
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

    # Scraping company info.
    for items in companyResults:
        currency = items.sup.string
        price = items.sup.next_sibling.next_sibling.string

        # Fetching the status (e.g whether the stock is +/- from yesterday's closing price)
        # of the stock and formatting it.
        statusRaw = items.next_sibling.next_sibling.span
        statusPoint = statusRaw.contents[0].string
        statusPercent = statusRaw.next_sibling.next_sibling.contents[0].string
        status = f"{statusPoint} {statusPercent}"

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
    """ Renders home (main) page. """
    # Initializing and validating form.
    form = TickerForm(request.POST or None)
    if form.is_valid():
        form.save()
        # Fetching input from the ticker form.
        tickerClean = form.cleaned_data['symbol']
        ratios, companyInfo = marketWatchScraper(tickerClean)
        categories = ['valuation', 'efficiency', 'liquidity', 'profitability', 'capitalization']

        # Variables to be passed through context
        name = companyInfo['name']
        #market = companyInfo['market']
        currency = companyInfo['currency']
        price = companyInfo['price']
        status = companyInfo['status']
        graph = scatterPlot(tickerClean)

        # Cleansing context, in the case some ratios for a stock aren't available.
        # Usually occurs when the stock hasn't been listed publicly for long.
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
        'status'            : status,
        'valuation'         : valuation,
        'efficiency'        : efficiency,
        'liquidity'         : liquidity,
        'profitability'     : profitability ,
        'capitalization'    : capitalization,
        'graph'             : graph
        }

        return render(request, 'ratios.html', context)

    context = {
    'form': form
    }
    return render(request, 'index.html', context)

def error500View(request):
    """ Error 505 handler. """
    return render(request, 'error500.html', {})

def error404View(request):
    """ Error 404 handler. """
    return render(request, 'error404.html', {})
