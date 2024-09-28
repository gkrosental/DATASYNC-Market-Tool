import os
import sys

try:
    import asciichartpy
except ImportError:
    print("asciichartpy not found. Installing now...")
    os.system(f"{sys.executable} -m pip install asciichartpy")
    import asciichartpy  # Import again after installation

import yfinance as yf
from colorama import Fore, Style, init
from prettytable import PrettyTable
import matplotlib.pyplot as plt
import asciichartpy  # For ASCII graph plotting
from datetime import datetime, timedelta

# Initialize colorama
init(autoreset=True)

# Market and stock database
markets = {
    '1': ('NYSE', [
        ('AAPL', 'Apple Inc.'),
        ('MSFT', 'Microsoft Corporation'),
        ('GOOGL', 'Alphabet Inc.'),
        ('AMZN', 'Amazon.com, Inc.'),
        ('FB', 'Meta Platforms, Inc.'),
        ('TSLA', 'Tesla, Inc.'),
        ('BRK.B', 'Berkshire Hathaway Inc.'),
        ('JNJ', 'Johnson & Johnson'),
        ('V', 'Visa Inc.'),
        ('PG', 'Procter & Gamble Co.')
    ]),
    '2': ('NASDAQ', [
        ('NFLX', 'Netflix, Inc.'),
        ('NVDA', 'NVIDIA Corporation'),
        ('ADBE', 'Adobe Inc.'),
        ('CSCO', 'Cisco Systems, Inc.'),
        ('INTC', 'Intel Corporation'),
        ('CMCSA', 'Comcast Corporation'),
        ('PEP', 'PepsiCo, Inc.'),
        ('AVGO', 'Broadcom Inc.'),
        ('AMGN', 'Amgen Inc.'),
        ('COST', 'Costco Wholesale Corporation')
    ]),
    '3': ('B3', [
        ('VALE3.SA', 'Vale S.A.'),
        ('PETR3.SA', 'Petrobras S.A.'),
        ('ITUB4.SA', 'Itaú Unibanco Holding S.A.'),
        ('B3SA3.SA', 'B3 S.A.'),
        ('ABEV3.SA', 'Ambev S.A.'),
        ('BBAS3.SA', 'Banco do Brasil S.A.'),
        ('LREN3.SA', 'Lojas Renner S.A.'),
        ('MGLU3.SA', 'Magazine Luiza S.A.'),
        ('WEGE3.SA', 'WEG S.A.'),
        ('HGTX3.SA', 'HGTX3 S.A.')
    ]),
    '4': ('LSE', [
        ('HSBA', 'HSBC Holdings plc'),
        ('BP', 'BP plc'),
        ('RDSA', 'Royal Dutch Shell plc'),
        ('GSK', 'GlaxoSmithKline plc'),
        ('VOD', 'Vodafone Group plc'),
        ('RIO', 'Rio Tinto plc'),
        ('BHP', 'BHP Group plc'),
        ('LON', 'London Stock Exchange Group plc'),
        ('AZN', 'AstraZeneca plc'),
        ('DGE', 'Diageo plc')
    ]),
    '5': ('BSE', [
        ('RELIANCE.BO', 'Reliance Industries Limited'),
        ('HDFCBANK.BO', 'HDFC Bank Limited'),
        ('HINDUNILVR.BO', 'Hindustan Unilever Limited'),
        ('INFY.BO', 'Infosys Limited'),
        ('ITC.BO', 'ITC Limited'),
        ('TCS.BO', 'Tata Consultancy Services'),
        ('SBIN.BO', 'State Bank of India'),
        ('LT.BO', 'Larsen & Toubro Limited'),
        ('ICICIBANK.BO', 'ICICI Bank Limited'),
        ('BAJFINANCE.BO', 'Bajaj Finance Limited')
    ]),
}

# Currency rates
currency_rates = {
    'USD': 1.0,
    'EUR': 0.85,
    'BRL': 5.25,
    'GBP': 0.75,
    'JPY': 110.0,
    'CAD': 1.25,
    'AUD': 1.35,
    'CNY': 6.5,
    'INR': 75.0,
}

def fetch_stock_data(symbol):
    """Fetch stock data from Yahoo Finance using yfinance."""
    try:
        stock = yf.Ticker(symbol)
        today = datetime.now().date()
        
        # Fetch intraday data (hourly) for today
        stock_info = stock.history(period="1d", interval="1h")
        
        # If no data for today, fetch the last available data
        if stock_info.empty:
            print(Fore.YELLOW + f"Market closed, showing latest available data for {symbol}.")
            stock_info = stock.history(period="5d")  # Fetch last 5 days of data
            if stock_info.empty:
                raise Exception("No historical data available.")
            last_quote = stock_info.tail(1)
            latest_price = last_quote['Close'].iloc[-1]
            high_price = last_quote['High'].max()
            low_price = last_quote['Low'].min()
            time_of_quote = last_quote.index[-1]  # Get the timestamp of the last quote
            return latest_price, high_price, low_price, stock.info['currency'], stock_info, time_of_quote
        
        # Extract latest, high, low prices from the hourly data
        latest_price = stock_info['Close'].iloc[-1]
        high_price = stock_info['High'].max()
        low_price = stock_info['Low'].min()
        time_of_quote = stock_info.index[-1]  # Get the timestamp of the last quote
        return latest_price, high_price, low_price, stock.info['currency'], stock_info, time_of_quote

    except Exception as e:
        print(Fore.RED + f"Error fetching data for {symbol}: {str(e)}")
    return None

def plot_ascii_graph(stock_data, symbol, market_open):
    """Plot ASCII graph of stock price history for the current day."""
    stock_info = stock_data[4]  # Extract the stock information (DataFrame)
    
    if stock_info.empty:
        print(Fore.RED + "No data available to plot.")
        return

    # If the market is closed, show the latest available data
    if not market_open:
        print(Fore.YELLOW + f"Market closed. Showing latest available price for {symbol}.")
        return

    # Extract hourly data from stock_info
    hourly_prices = stock_info['Close'].tolist()
    
    # Normalize data for better representation in ASCII
    chart_data = [round(price) for price in hourly_prices]  # Round to integers for ASCII charting
    
    # Generate ASCII chart
    ascii_chart = asciichartpy.plot(chart_data, {'height': 10})  # Adjust height as needed
    print(Fore.GREEN + f"Hourly price graph for {symbol}:")
    print(Fore.CYAN + ascii_chart)

def plot_stock_data(stock_data, symbol):
    """Plot stock data (price history)"""
    stock_info = stock_data[4]  # Extract stock DataFrame
    time_of_quote = stock_data[5]  # Extract time of the quote

    # Check if stock_info is empty
    if stock_info.empty:
        print(Fore.RED + "No historical data found for plotting.")
        return

    plt.figure(figsize=(10, 5))
    plt.plot(stock_info.index, stock_info['Close'], label='Close Price', color='blue')
    plt.title(f'Stock Price History for {symbol} (as of {time_of_quote})')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    plt.legend()
    plt.grid()
    plt.tight_layout()  # Adjust layout to prevent clipping
    plt.show()

def plot_intraday_price_history(symbol, interval="1h"):
    """Plot hourly price history for the current day."""
    try:
        stock = yf.Ticker(symbol)
        # Fetching 1-day history with hourly intervals
        stock_history = stock.history(period="1d", interval=interval)  
        
        if stock_history.empty:
            print(Fore.RED + f"No intraday data found for {symbol}.")
            return

        plt.figure(figsize=(10, 5))
        plt.plot(stock_history.index, stock_history['Close'], label='Close Price', color='blue')
        plt.title(f'Hourly Price History for {symbol} (Today)')
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
        plt.legend()
        plt.grid()
        plt.tight_layout()  # Adjust layout to prevent clipping
        plt.show()
    except Exception as e:
        print(Fore.RED + f"Error fetching hourly price history for {symbol}: {str(e)}")


def display_markets():
    """Display available markets."""
    market_table = PrettyTable()
    market_table.field_names = [Fore.CYAN + "Market ID", Fore.CYAN + "Market Name"]
    for market_id, (market_name, _) in markets.items():
        market_table.add_row([market_id, market_name])
    print(Fore.YELLOW + str(market_table))

def display_stocks(market_id):
    """Display stocks from the selected market.""" 
    stock_table = PrettyTable()
    stock_table.field_names = [Fore.CYAN + "Symbol", Fore.CYAN + "Company Name"]
    for stock in markets[market_id][1]:
        stock_table.add_row(stock)
    print(Fore.YELLOW + str(stock_table))

def fetch_currency_exchange(base_currency, target_currency):
    """Fetch currency exchange rates.""" 
    base_rate = currency_rates.get(base_currency)
    target_rate = currency_rates.get(target_currency)
    if base_rate and target_rate:
        return round(target_rate / base_rate, 2)
    return None

def main():
    """Main function to run the DATASYNC software.""" 

   # ASCII banner
    banner = """
8888888b.        d8888 88888888888     d8888  .d8888b. Y88b   d88P 888b    888  .d8888b.  
888  "Y88b      d88888     888        d88888 d88P  Y88b Y88b d88P  8888b   888 d88P  Y88b 
888    888     d88P888     888       d88P888 Y88b.       Y88o88P   88888b  888 888    888 
888    888    d88P 888     888      d88P 888  "Y888b.     Y888P    888Y88b 888 888        
888    888   d88P  888     888     d88P  888     "Y88b.    888     888 Y88b888 888        
888    888  d88P   888     888    d88P   888       "888    888     888  Y88888 888    888 
888  .d88P d8888888888     888   d8888888888 Y88b  d88P    888     888   Y8888 Y88b  d88P 
8888888P" d88P     888     888  d88P     888  "Y8888P"     888     888    Y888  "Y8888P"                                                                                                                                                                                                                                                                           
    """
    print(Fore.YELLOW + "This software was developed by Guilherme Rosental for studying purposes.")
    print(Fore.CYAN + banner + Style.RESET_ALL)  # Display the ASCII banner in cyan
    print(Fore.BLUE + "Welcome to the DATASYNC Market Tool!" + Style.RESET_ALL)

    while True:
        print(Fore.GREEN + "\nMain Menu:") 
        menu_table = PrettyTable()
        menu_table.field_names = [Fore.CYAN + "Option ID", Fore.CYAN + "Description"]
        menu_table.add_row(["1", "Fetch Stock Prices"])
        menu_table.add_row(["2", "Fetch Currency Exchange"])
        menu_table.add_row(["3", "About Us"])
        menu_table.add_row(["4", "Exit"])
        print(Fore.YELLOW + str(menu_table))

        choice = input("Select an option (1-4): ")
        if choice == '1':
            display_markets()
            market_id = input("Select a market by ID: ")
            if market_id in markets:
                display_stocks(market_id)
                stock_symbol = input("Select a stock symbol: ")
                stock_data = fetch_stock_data(stock_symbol)
                if stock_data:
                    latest_price, high_price, low_price, currency, stock_info, time_of_quote = stock_data
                    quote_table = PrettyTable()
                    quote_table.field_names = ["Metric", "Value"]
                    quote_table.add_row(["Latest Price", Fore.GREEN + f"{round(latest_price, 2)} {currency}"])
                    quote_table.add_row(["Highest Price", Fore.YELLOW + f"{round(high_price, 2)} {currency}"])
                    quote_table.add_row(["Lowest Price", Fore.RED + f"{round(low_price, 2)} {currency}"])
                    quote_table.add_row(["Time of Quote", Fore.BLUE + f"{time_of_quote}"])
                    print(Fore.YELLOW + str(quote_table))
                    
                    # Offer to plot the stock data
                    show_graph = input("Would you like to see the stock price graph? (yes/no): ").strip().lower()
                    if show_graph == 'yes':
                        plot_stock_data(stock_data, stock_symbol)
                else:
                    print(Fore.RED + f"Failed to retrieve data for: {stock_symbol}")
            else:
                print(Fore.RED + "Invalid market ID.")

        elif choice == '2':
            currency_table = PrettyTable()
            currency_table.field_names = [Fore.CYAN + "Available Currencies"]
            for currency in currency_rates.keys():
                currency_table.add_row([currency])
            print(Fore.YELLOW + str(currency_table))
            
            base_currency = input("Select base currency: ").strip().upper()
            if base_currency in currency_rates:
                target_currency = input("Select target currency: ").strip().upper()
                if target_currency in currency_rates:
                    exchange_rate = fetch_currency_exchange(base_currency, target_currency)
                    if exchange_rate:
                        currency_table = PrettyTable()
                        currency_table.field_names = ["Currency Pair", "Exchange Rate"]
                        currency_table.add_row([f"{base_currency}/{target_currency}", Fore.GREEN + f"{exchange_rate}"])
                        print(Fore.YELLOW + str(currency_table))
                    else:
                        print(Fore.RED + "Failed to retrieve the exchange rate.")
                else:
                    print(Fore.RED + "Invalid target currency.")
            else:
                print(Fore.RED + "Invalid base currency.")

        elif choice == '3':
            print(Fore.CYAN + "\nAbout Us")
            print(Fore.YELLOW + "This software was developed by Guilherme Rosental for studying purposes.")

        elif choice == '4':
            print(Fore.BLUE + "Exiting DATASYNC. Goodbye!")
            break

        else:
            print(Fore.RED + "Invalid option. Please select a valid option from the menu.")

if __name__ == "__main__":
    main()

