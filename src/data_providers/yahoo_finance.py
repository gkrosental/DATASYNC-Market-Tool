"""
Yahoo Finance Data Provider
Free and reliable source for stock market data
"""
import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import requests
from .base_provider import BaseDataProvider


class YahooFinanceProvider(BaseDataProvider):
    """Yahoo Finance data provider implementation"""
    
    def __init__(self):
        super().__init__("Yahoo Finance")
        self.base_url = "https://query1.finance.yahoo.com"
        
    def get_stock_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """Get historical stock data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                raise ValueError(f"No data found for symbol {symbol}")
                
            self.last_update = datetime.now()
            return data
            
        except Exception as e:
            raise Exception(f"Error fetching data for {symbol}: {str(e)}")
    
    def get_real_time_price(self, symbol: str) -> Dict[str, Any]:
        """Get real-time stock price information"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            history = ticker.history(period="2d", interval="1m")
            
            if history.empty:
                raise ValueError(f"No recent data found for {symbol}")
            
            latest = history.tail(1).iloc[0]
            previous_close = info.get('previousClose', latest['Close'])
            current_price = latest['Close']
            
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100 if previous_close != 0 else 0
            
            return {
                'symbol': symbol,
                'price': current_price,
                'change': change,
                'change_percent': change_percent,
                'volume': latest['Volume'],
                'high': latest['High'],
                'low': latest['Low'],
                'open': latest['Open'],
                'previous_close': previous_close,
                'timestamp': history.index[-1],
                'currency': info.get('currency', 'USD'),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'dividend_yield': info.get('dividendYield'),
                'company_name': info.get('longName', symbol)
            }
            
        except Exception as e:
            raise Exception(f"Error fetching real-time data for {symbol}: {str(e)}")
    
    def get_currency_rate(self, from_currency: str, to_currency: str) -> float:
        """Get currency exchange rate"""
        if from_currency == to_currency:
            return 1.0
            
        try:
            # Yahoo Finance uses format like "EURUSD=X" for forex
            symbol = f"{from_currency}{to_currency}=X"
            ticker = yf.Ticker(symbol)
            history = ticker.history(period="1d")
            
            if history.empty:
                raise ValueError(f"No exchange rate data found for {from_currency}/{to_currency}")
            
            rate = history['Close'].iloc[-1]
            self.last_update = datetime.now()
            return float(rate)
            
        except Exception as e:
            raise Exception(f"Error fetching exchange rate {from_currency}/{to_currency}: {str(e)}")
    
    def search_symbols(self, query: str) -> List[Dict[str, str]]:
        """Search for stock symbols using Yahoo Finance API"""
        try:
            url = f"{self.base_url}/v1/finance/search"
            params = {
                'q': query,
                'quotesCount': 10,
                'newsCount': 0
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            if 'quotes' in data:
                for quote in data['quotes']:
                    results.append({
                        'symbol': quote.get('symbol', ''),
                        'name': quote.get('longname') or quote.get('shortname', ''),
                        'type': quote.get('typeDisp', ''),
                        'exchange': quote.get('exchange', ''),
                        'currency': quote.get('currency', '')
                    })
            
            return results
            
        except Exception as e:
            # Fallback: try to get info directly if it's a valid symbol
            try:
                ticker = yf.Ticker(query.upper())
                info = ticker.info
                if info and 'symbol' in info:
                    return [{
                        'symbol': info['symbol'],
                        'name': info.get('longName', ''),
                        'type': 'Equity',
                        'exchange': info.get('exchange', ''),
                        'currency': info.get('currency', '')
                    }]
            except:
                pass
            
            return []
    
    def get_market_status(self, symbol: str) -> Dict[str, Any]:
        """Get market status for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'market_state': info.get('marketState', 'UNKNOWN'),
                'exchange_timezone': info.get('exchangeTimezoneName', ''),
                'regular_market_time': info.get('regularMarketTime'),
                'gmt_offset': info.get('gmtOffSetMilliseconds')
            }
        except:
            return {'market_state': 'UNKNOWN'}
    
    def get_company_info(self, symbol: str) -> Dict[str, Any]:
        """Get detailed company information"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'company_name': info.get('longName', ''),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'market_cap': info.get('marketCap'),
                'enterprise_value': info.get('enterpriseValue'),
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'peg_ratio': info.get('pegRatio'),
                'price_to_book': info.get('priceToBook'),
                'debt_to_equity': info.get('debtToEquity'),
                'return_on_equity': info.get('returnOnEquity'),
                'revenue_growth': info.get('revenueGrowth'),
                'earnings_growth': info.get('earningsGrowth'),
                'dividend_yield': info.get('dividendYield'),
                'dividend_rate': info.get('dividendRate'),
                'beta': info.get('beta'),
                '52_week_high': info.get('fiftyTwoWeekHigh'),
                '52_week_low': info.get('fiftyTwoWeekLow'),
                'avg_volume': info.get('averageVolume'),
                'website': info.get('website', ''),
                'business_summary': info.get('businessSummary', ''),
                'employees': info.get('fullTimeEmployees'),
                'country': info.get('country', ''),
                'city': info.get('city', ''),
                'phone': info.get('phone', ''),
                'currency': info.get('currency', 'USD')
            }
        except Exception as e:
            raise Exception(f"Error fetching company info for {symbol}: {str(e)}")
    
    def get_financial_data(self, symbol: str) -> Dict[str, pd.DataFrame]:
        """Get financial statements data"""
        try:
            ticker = yf.Ticker(symbol)
            
            return {
                'income_statement': ticker.financials,
                'balance_sheet': ticker.balance_sheet,
                'cash_flow': ticker.cashflow,
                'quarterly_income': ticker.quarterly_financials,
                'quarterly_balance_sheet': ticker.quarterly_balance_sheet,
                'quarterly_cash_flow': ticker.quarterly_cashflow
            }
        except Exception as e:
            raise Exception(f"Error fetching financial data for {symbol}: {str(e)}")
    
    def is_connected(self) -> bool:
        """Check if Yahoo Finance is accessible"""
        try:
            response = requests.get("https://finance.yahoo.com", timeout=5)
            return response.status_code == 200
        except:
            return False
