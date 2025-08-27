# DATASYNC Market Tool Configuration

# API Configuration
YF_ENABLED = True  # Yahoo Finance
ALPHA_VANTAGE_API_KEY = ""  # Free API key from Alpha Vantage
FRED_API_KEY = ""  # Federal Reserve Economic Data

# Application Settings
APP_NAME = "DATASYNC Market Tool"
APP_VERSION = "2.0.0"
APP_AUTHOR = "Guilherme Rosental"

# Data Update Intervals (in seconds)
REAL_TIME_UPDATE_INTERVAL = 5
PRICE_UPDATE_INTERVAL = 10
NEWS_UPDATE_INTERVAL = 300  # 5 minutes

# Default Markets and Exchanges
DEFAULT_MARKETS = {
    'US': ['NYSE', 'NASDAQ'],
    'BR': ['B3'],
    'UK': ['LSE'],
    'IN': ['BSE', 'NSE'],
    'DE': ['XETRA'],
    'JP': ['TSE'],
    'CA': ['TSX'],
    'AU': ['ASX']
}

# Default Currency Pairs
DEFAULT_CURRENCIES = [
    'USD', 'EUR', 'BRL', 'GBP', 'JPY', 'CAD', 'AUD', 
    'CNY', 'INR', 'CHF', 'KRW', 'MXN', 'SGD', 'HKD'
]

# Technical Analysis Indicators
TECHNICAL_INDICATORS = [
    'SMA', 'EMA', 'RSI', 'MACD', 'Bollinger Bands',
    'Stochastic', 'Williams %R', 'CCI', 'ATR', 'OBV'
]

# Chart Settings
DEFAULT_CHART_PERIOD = "1y"
DEFAULT_CHART_INTERVAL = "1d"
CHART_THEMES = ['plotly', 'seaborn', 'ggplot', 'dark']

# News Sources (RSS Feeds - Free)
NEWS_SOURCES = {
    'yahoo_finance': 'https://feeds.finance.yahoo.com/rss/2.0/headline',
    'marketwatch': 'https://feeds.marketwatch.com/marketwatch/topstories/',
    'reuters_business': 'https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best',
    'bloomberg': 'https://feeds.bloomberg.com/markets/news.rss',
    'cnbc': 'https://www.cnbc.com/id/100003114/device/rss/rss.html'
}

# UI Settings
STREAMLIT_CONFIG = {
    'page_title': 'DATASYNC Market Tool',
    'page_icon': '📈',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# Data Storage
DATA_CACHE_TTL = 300  # 5 minutes
MAX_CACHE_SIZE = 1000

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
