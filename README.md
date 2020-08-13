# Financial Data

Financial Data is a Django app which provides financial data of a company (e.g ratios useful for investing, current share price) given a ticker symbol. The app scrapes financial ratio data from MarketWatch and plots a time series graph displaying the stock's daily performance over the last few months. 

The front-end of the app runs on HTML/CSS, Bootstrap, and JavaScript. The back-end is in Python and Django. 

## Demo

The app is currently live on my [personal website](https://haiderzaidi.ca/financial-ratios), here's a gif to demonstrate how it works. 

![Demo Gif](https://i.imgur.com/hMoUEXz.gif)



## Data Retrieval
The ratios and prices used on the app are scraped from [MarketWatch](https://www.marketwatch.com/)'s profile page, the data used to plot the time series graph is sourced from the [Alpha Vantage API](https://www.alphavantage.co/). 

I opted to scrape rather than pull data from an API, as most financial data API's are costly, also scraping is fun. Although, scraping does come with a trade off of higher load times (about 3 seconds). If you plan on having a lot of users, I wouldn't recommend scraping to retrieve data.


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


