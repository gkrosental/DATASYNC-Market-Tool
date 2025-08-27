"""
DATASYNC Market Tool - Console Interface
Enhanced command-line interface for the DATASYNC Market Analysis Tool
"""
import os
import sys
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime
from colorama import init, Fore, Style
from prettytable import PrettyTable

# Add src and config directories to path
current_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(current_dir, 'src'))
sys.path.append(os.path.join(current_dir, 'config'))

from src.data_providers.data_manager import DataProviderManager
from src.analyzers.technical_analyzer import TechnicalAnalyzer
from src.analyzers.portfolio_analyzer import PortfolioAnalyzer
from src.utils.helpers import *
from src.utils.plotting import ChartManager
from src.localization import get_text, set_language, get_language, get_available_languages
from config.settings import *

# Initialize colorama for Windows
init(autoreset=True)


class DataSyncConsole:
    """Enhanced console interface for DATASYNC Market Tool"""
    
    def __init__(self):
        self.data_manager = DataProviderManager()
        self.technical_analyzer = TechnicalAnalyzer()
        self.portfolio_analyzer = PortfolioAnalyzer()
        self.chart_manager = ChartManager()
        self.portfolio = {}
        
    def show_banner(self):
        """Display enhanced ASCII banner"""
        banner = f"""
{Fore.CYAN}
██████╗  █████╗ ████████╗ █████╗ ███████╗██╗   ██╗███╗   ██╗ ██████╗
██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗██╔════╝╚██╗ ██╔╝████╗  ██║██╔════╝
██║  ██║███████║   ██║   ███████║███████╗ ╚████╔╝ ██╔██╗ ██║██║     
██║  ██║██╔══██║   ██║   ██╔══██║╚════██║  ╚██╔╝  ██║╚██╗██║██║     
██████╗╝██║  ██║   ██║   ██║  ██║███████║   ██║   ██║ ╚████║╚██████╗
╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═══╝ ╚═════╝
{Style.RESET_ALL}
{Fore.YELLOW}{get_text('app.subtitle')} {get_text('app.version')}{Style.RESET_ALL}
{Fore.GREEN}{get_text('app.developer')}{Style.RESET_ALL}
{Fore.BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}
"""
        print(banner)
    
    def show_main_menu(self):
        """Display the main menu"""
        table = PrettyTable()
        table.field_names = [f"{Fore.CYAN}Option{Style.RESET_ALL}", f"{Fore.CYAN}Description{Style.RESET_ALL}"]
        table.add_row(["1", get_text('menu.main.language')])
        table.add_row(["2", get_text('menu.main.market_overview')])
        table.add_row(["3", get_text('menu.main.stock_analysis')])
        table.add_row(["4", get_text('menu.main.portfolio')])
        table.add_row(["5", get_text('menu.main.technical_analysis')])
        table.add_row(["6", get_text('menu.main.currency')])
        table.add_row(["7", get_text('menu.main.news')])
        table.add_row(["8", get_text('menu.main.web_interface')])
        table.add_row(["0", get_text('menu.main.exit')])
        
        print(f"\n{Fore.GREEN}=== {get_text('menu.main.title')} ==={Style.RESET_ALL}")
        print(table)
    
    def get_user_choice(self) -> str:
        """Get user menu choice"""
        return input(f"\n{Fore.YELLOW}{get_text('input.choose_option')}{Style.RESET_ALL}").strip()
    
    def language_menu(self):
        """Language selection menu"""
        print(f"\n{Fore.GREEN}=== {get_text('menu.language.title')} ==={Style.RESET_ALL}")
        print(f"{get_text('menu.language.current', language=get_available_languages()[get_language()])}")
        
        table = PrettyTable()
        table.field_names = [f"{Fore.CYAN}Option{Style.RESET_ALL}", f"{Fore.CYAN}Language{Style.RESET_ALL}"]
        table.add_row(["1", "🇧🇷 Português"])
        table.add_row(["2", "🇺� English"])
        table.add_row(["3", "🇪🇸 Español"])
        table.add_row(["0", get_text('menu.language.back')])
        
        print(table)
        
        choice = input(f"\n{Fore.YELLOW}{get_text('input.choose_option')}{Style.RESET_ALL}").strip()
        
        if choice == "1":
            set_language('pt')
            print(f"\n{Fore.GREEN}{get_text('success.language_changed', language='Português')}{Style.RESET_ALL}")
        elif choice == "2":
            set_language('en')
            print(f"\n{Fore.GREEN}{get_text('success.language_changed', language='English')}{Style.RESET_ALL}")
        elif choice == "3":
            set_language('es')
            print(f"\n{Fore.GREEN}{get_text('success.language_changed', language='Español')}{Style.RESET_ALL}")
        elif choice == "0":
            return
        else:
            print(f"\n{Fore.RED}{get_text('input.invalid_option')}{Style.RESET_ALL}")
        
        input(f"\n{get_text('input.press_enter')}")
    
    def stock_analysis_menu(self):
        """Stock analysis submenu"""
        while True:
            print(f"\n{Fore.GREEN}=== STOCK ANALYSIS ==={Style.RESET_ALL}")
            
            symbol = input(f"{Fore.YELLOW}Enter stock symbol (or 'back' to return): {Style.RESET_ALL}").strip().upper()
            
            if symbol.lower() == 'back':
                break
            
            if not validate_symbol(symbol):
                print(f"{Fore.RED}Invalid symbol format. Please try again.{Style.RESET_ALL}")
                continue
            
            try:
                self.analyze_stock(symbol)
            except Exception as e:
                print(f"{Fore.RED}Error analyzing {symbol}: {str(e)}{Style.RESET_ALL}")
    
    def analyze_stock(self, symbol: str):
        """Perform comprehensive stock analysis"""
        print(f"\n{Fore.BLUE}Analyzing {symbol}...{Style.RESET_ALL}")
        
        try:
            # Get real-time data
            real_time_data = self.data_manager.get_real_time_price(symbol)
            
            # Get historical data
            df = self.data_manager.get_stock_data(symbol, "1y", "1d")
            
            # Get company info
            company_info = self.data_manager.get_company_info(symbol)
            
            # Display basic info
            self.display_stock_info(symbol, real_time_data, company_info)
            
            # Technical analysis
            print(f"\n{Fore.BLUE}Performing technical analysis...{Style.RESET_ALL}")
            analysis = self.technical_analyzer.analyze_stock(df)
            signals = self.technical_analyzer.generate_signals(analysis)
            trends = self.technical_analyzer.get_trend_analysis(df)
            
            self.display_technical_analysis(signals, trends)
            
            # Ask if user wants to see charts
            show_charts = input(f"\n{Fore.YELLOW}Show charts? (y/n): {Style.RESET_ALL}").strip().lower()
            if show_charts == 'y':
                self.show_stock_charts(df, analysis, symbol)
            
        except Exception as e:
            raise Exception(f"Failed to analyze stock: {str(e)}")
    
    def display_stock_info(self, symbol: str, real_time_data: dict, company_info: dict):
        """Display stock information"""
        print(f"\n{Fore.CYAN}=== {company_info.get('company_name', symbol)} ({symbol}) ==={Style.RESET_ALL}")
        
        # Price information
        table = PrettyTable()
        table.field_names = ["Metric", "Value"]
        
        # Price with color coding
        price_color = Fore.GREEN if real_time_data['change'] >= 0 else Fore.RED
        change_arrow = "↗" if real_time_data['change'] >= 0 else "↘"
        
        table.add_row(["Current Price", 
                      f"{price_color}{format_currency(real_time_data['price'], real_time_data.get('currency', 'USD'))}{Style.RESET_ALL}"])
        table.add_row(["Change", 
                      f"{price_color}{change_arrow} {real_time_data['change']:+.2f} ({real_time_data['change_percent']:+.2f}%){Style.RESET_ALL}"])
        table.add_row(["Volume", format_volume(real_time_data['volume'])])
        table.add_row(["Market Cap", format_market_cap(company_info.get('market_cap', 0))])
        table.add_row(["P/E Ratio", f"{company_info.get('pe_ratio', 'N/A')}"])
        table.add_row(["52W High", format_currency(company_info.get('52_week_high', 0), real_time_data.get('currency', 'USD'))])
        table.add_row(["52W Low", format_currency(company_info.get('52_week_low', 0), real_time_data.get('currency', 'USD'))])
        table.add_row(["Beta", f"{company_info.get('beta', 'N/A')}"])
        table.add_row(["Dividend Yield", f"{format_percentage(company_info.get('dividend_yield', 0) * 100 if company_info.get('dividend_yield') else 0)}"])
        
        print(table)
        
        # Company details
        if company_info.get('sector'):
            print(f"\n{Fore.BLUE}Sector:{Style.RESET_ALL} {company_info['sector']}")
        if company_info.get('industry'):
            print(f"{Fore.BLUE}Industry:{Style.RESET_ALL} {company_info['industry']}")
        if company_info.get('business_summary'):
            print(f"{Fore.BLUE}Business Summary:{Style.RESET_ALL}")
            print(company_info['business_summary'][:300] + "...")
    
    def display_technical_analysis(self, signals: dict, trends: dict):
        """Display technical analysis results"""
        print(f"\n{Fore.CYAN}=== TECHNICAL ANALYSIS ==={Style.RESET_ALL}")
        
        # Signals table
        signals_table = PrettyTable()
        signals_table.field_names = ["Indicator", "Signal"]
        
        for indicator, signal in signals.items():
            color = Fore.GREEN if signal == "BULLISH" else Fore.RED if signal == "BEARISH" else Fore.YELLOW
            signals_table.add_row([indicator.upper(), f"{color}{signal}{Style.RESET_ALL}"])
        
        print("\n📊 Trading Signals:")
        print(signals_table)
        
        # Trends table
        trends_table = PrettyTable()
        trends_table.field_names = ["Timeframe", "Trend"]
        
        for timeframe, trend in trends.items():
            color = Fore.GREEN if trend == "BULLISH" else Fore.RED if trend == "BEARISH" else Fore.YELLOW
            trends_table.add_row([timeframe.replace('_', ' ').title(), f"{color}{trend}{Style.RESET_ALL}"])
        
        print("\n📈 Trend Analysis:")
        print(trends_table)
    
    def show_stock_charts(self, df, analysis, symbol):
        """Display stock charts"""
        print(f"\n{Fore.BLUE}Generating charts for {symbol}...{Style.RESET_ALL}")
        
        try:
            # Candlestick chart
            fig = self.chart_manager.create_candlestick_chart(df, f"{symbol} Stock Price")
            fig.show()
            
            # RSI chart
            fig_rsi = self.chart_manager.create_rsi_chart(df, analysis['rsi'], f"{symbol} RSI")
            fig_rsi.show()
            
            # MACD chart
            macd_data = {
                'macd': analysis['macd'],
                'macd_signal': analysis['macd_signal'],
                'macd_histogram': analysis['macd_histogram']
            }
            fig_macd = self.chart_manager.create_macd_chart(df, macd_data, f"{symbol} MACD")
            fig_macd.show()
            
            print(f"{Fore.GREEN}Charts displayed in browser.{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}Error displaying charts: {str(e)}{Style.RESET_ALL}")
    
    def technical_analysis_menu(self):
        """Technical analysis standalone menu"""
        print(f"\n{Fore.GREEN}=== {get_text('technical.analysis')} ==={Style.RESET_ALL}")
        
        symbol = input(f"{Fore.YELLOW}{get_text('input.enter_symbol')}{Style.RESET_ALL}").strip().upper()
        
        if not symbol:
            return
        
        try:
            print(f"\n{Fore.BLUE}{get_text('stock.fetching_data', symbol=symbol)}{Style.RESET_ALL}")
            
            # Get historical data for technical analysis
            df = self.data_manager.get_stock_data(symbol, "6mo", "1d")
            
            if df is None or df.empty:
                print(f"{Fore.RED}{get_text('errors.no_data', symbol=symbol)}{Style.RESET_ALL}")
                return
            
            # Perform technical analysis
            analysis = self.technical_analyzer.analyze_stock(df)
            signals = self.technical_analyzer.generate_signals(analysis)
            
            # Display results
            print(f"\n{Fore.CYAN}=== {get_text('technical.analysis')} - {symbol} ==={Style.RESET_ALL}")
            
            table = PrettyTable()
            table.field_names = [get_text('technical.indicators'), get_text('technical.signals')]
            
            signal_colors = {
                'BULLISH': Fore.GREEN,
                'BEARISH': Fore.RED,
                'NEUTRAL': Fore.YELLOW,
                'ALTA': Fore.GREEN,
                'BAIXA': Fore.RED,
                'NEUTRO': Fore.YELLOW,
                'ALCISTA': Fore.GREEN,
                'BAJISTA': Fore.RED,
                'NEUTRAL': Fore.YELLOW
            }
            
            for indicator, signal in signals.items():
                color = signal_colors.get(signal, Fore.WHITE)
                table.add_row([get_text(f'technical.{indicator}'), f"{color}{get_text(f'technical.{signal.lower()}')}{Style.RESET_ALL}"])
            
            print(table)
            
            # Show specific indicator values
            print(f"\n{Fore.BLUE}Valores dos Indicadores:{Style.RESET_ALL}")
            print(f"RSI: {analysis['rsi'].iloc[-1]:.2f}")
            print(f"MACD: {analysis['macd'].iloc[-1]:.4f}")
            print(f"Bollinger Upper: {analysis['bollinger_upper'].iloc[-1]:.2f}")
            print(f"Bollinger Lower: {analysis['bollinger_lower'].iloc[-1]:.2f}")
            
        except Exception as e:
            print(f"{Fore.RED}{get_text('errors.general', error=str(e))}{Style.RESET_ALL}")
        
        input(f"\n{get_text('input.press_enter')}")
    
    def portfolio_menu(self):
        """Portfolio management menu"""
        while True:
            print(f"\n{Fore.GREEN}=== PORTFOLIO MANAGEMENT ==={Style.RESET_ALL}")
            
            table = PrettyTable()
            table.field_names = ["Option", "Description"]
            table.add_row(["1", "📊 View Portfolio"])
            table.add_row(["2", "➕ Add Stock"])
            table.add_row(["3", "➖ Remove Stock"])
            table.add_row(["4", "📈 Analyze Portfolio"])
            table.add_row(["5", "🎯 Optimize Portfolio"])
            table.add_row(["6", "🧹 Clear Portfolio"])
            table.add_row(["0", "🔙 Back to Main Menu"])
            
            print(table)
            
            choice = input(f"\n{Fore.YELLOW}Select option: {Style.RESET_ALL}").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self.view_portfolio()
            elif choice == "2":
                self.add_to_portfolio()
            elif choice == "3":
                self.remove_from_portfolio()
            elif choice == "4":
                self.analyze_portfolio()
            elif choice == "5":
                self.optimize_portfolio()
            elif choice == "6":
                self.clear_portfolio()
            else:
                print(f"{Fore.RED}Invalid option. Please try again.{Style.RESET_ALL}")
    
    def view_portfolio(self):
        """Display current portfolio"""
        if not self.portfolio:
            print(f"{Fore.YELLOW}Portfolio is empty.{Style.RESET_ALL}")
            return
        
        table = PrettyTable()
        table.field_names = ["Symbol", "Weight (%)", "Current Price", "Market Value"]
        
        total_value = 0
        for symbol, weight in self.portfolio.items():
            try:
                data = self.data_manager.get_real_time_price(symbol)
                price = data['price']
                market_value = weight * 10000  # Assuming $10,000 portfolio
                total_value += market_value
                
                table.add_row([
                    symbol,
                    f"{weight * 100:.1f}%",
                    format_currency(price, data.get('currency', 'USD')),
                    format_currency(market_value, 'USD')
                ])
            except:
                table.add_row([symbol, f"{weight * 100:.1f}%", "N/A", "N/A"])
        
        print(f"\n{Fore.CYAN}Current Portfolio:{Style.RESET_ALL}")
        print(table)
        print(f"Total Portfolio Value: {format_currency(total_value, 'USD')}")
    
    def add_to_portfolio(self):
        """Add stock to portfolio"""
        symbol = input(f"{Fore.YELLOW}Enter symbol to add: {Style.RESET_ALL}").strip().upper()
        
        if not validate_symbol(symbol):
            print(f"{Fore.RED}Invalid symbol format.{Style.RESET_ALL}")
            return
        
        try:
            weight = float(input(f"{Fore.YELLOW}Enter weight (0-100%): {Style.RESET_ALL}"))
            if 0 <= weight <= 100:
                self.portfolio[symbol] = weight / 100
                print(f"{Fore.GREEN}Added {symbol} with {weight}% weight to portfolio.{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Weight must be between 0 and 100.{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Invalid weight value.{Style.RESET_ALL}")
    
    def remove_from_portfolio(self):
        """Remove stock from portfolio"""
        if not self.portfolio:
            print(f"{Fore.YELLOW}Portfolio is empty.{Style.RESET_ALL}")
            return
        
        symbol = input(f"{Fore.YELLOW}Enter symbol to remove: {Style.RESET_ALL}").strip().upper()
        
        if symbol in self.portfolio:
            del self.portfolio[symbol]
            print(f"{Fore.GREEN}Removed {symbol} from portfolio.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Symbol {symbol} not found in portfolio.{Style.RESET_ALL}")
    
    def analyze_portfolio(self):
        """Analyze portfolio performance"""
        if not self.portfolio:
            print(f"{Fore.YELLOW}Portfolio is empty.{Style.RESET_ALL}")
            return
        
        try:
            print(f"\n{Fore.BLUE}Analyzing portfolio...{Style.RESET_ALL}")
            
            # Get portfolio data
            portfolio_data = {}
            for symbol in self.portfolio.keys():
                df = self.data_manager.get_stock_data(symbol, "1y", "1d")
                portfolio_data[symbol] = df['Close']
            
            portfolio_df = pd.DataFrame(portfolio_data).fillna(method='forward').dropna()
            returns = self.portfolio_analyzer.calculate_returns(portfolio_df)
            
            weights = np.array(list(self.portfolio.values()))
            weights = weights / weights.sum()  # Normalize
            
            metrics = self.portfolio_analyzer.calculate_portfolio_metrics(returns, weights)
            
            # Display metrics
            table = PrettyTable()
            table.field_names = ["Metric", "Value"]
            table.add_row(["Annual Return", format_percentage(metrics['annual_return'] * 100)])
            table.add_row(["Annual Volatility", format_percentage(metrics['annual_volatility'] * 100)])
            table.add_row(["Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}"])
            table.add_row(["Sortino Ratio", f"{metrics['sortino_ratio']:.2f}"])
            table.add_row(["Max Drawdown", format_percentage(metrics['max_drawdown'] * 100)])
            table.add_row(["Win Rate", format_percentage(metrics['win_rate'] * 100)])
            
            print(f"\n{Fore.CYAN}Portfolio Performance Metrics:{Style.RESET_ALL}")
            print(table)
            
        except Exception as e:
            print(f"{Fore.RED}Error analyzing portfolio: {str(e)}{Style.RESET_ALL}")
    
    def optimize_portfolio(self):
        """Optimize portfolio weights"""
        if not self.portfolio:
            print(f"{Fore.YELLOW}Portfolio is empty.{Style.RESET_ALL}")
            return
        
        try:
            print(f"\n{Fore.BLUE}Optimizing portfolio...{Style.RESET_ALL}")
            
            portfolio_data = {}
            for symbol in self.portfolio.keys():
                df = self.data_manager.get_stock_data(symbol, "1y", "1d")
                portfolio_data[symbol] = df['Close']
            
            portfolio_df = pd.DataFrame(portfolio_data).fillna(method='forward').dropna()
            returns = self.portfolio_analyzer.calculate_returns(portfolio_df)
            
            # Optimize for Sharpe ratio
            result = self.portfolio_analyzer.optimize_portfolio(returns, 'sharpe')
            
            if result['optimization_success']:
                print(f"{Fore.GREEN}Optimization successful!{Style.RESET_ALL}")
                
                table = PrettyTable()
                table.field_names = ["Symbol", "Current Weight (%)", "Optimal Weight (%)"]
                
                for symbol in self.portfolio.keys():
                    current_weight = self.portfolio[symbol] * 100
                    optimal_weight = result['weights'][symbol] * 100
                    table.add_row([symbol, f"{current_weight:.1f}%", f"{optimal_weight:.1f}%"])
                
                print(table)
                
                # Show optimized metrics
                metrics = result['metrics']
                print(f"\nOptimized Portfolio Metrics:")
                print(f"Annual Return: {format_percentage(metrics['annual_return'] * 100)}")
                print(f"Annual Volatility: {format_percentage(metrics['annual_volatility'] * 100)}")
                print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
                
                apply_weights = input(f"\n{Fore.YELLOW}Apply optimized weights? (y/n): {Style.RESET_ALL}").strip().lower()
                if apply_weights == 'y':
                    self.portfolio = result['weights']
                    print(f"{Fore.GREEN}Portfolio weights updated!{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Optimization failed: {result.get('error', 'Unknown error')}{Style.RESET_ALL}")
        
        except Exception as e:
            print(f"{Fore.RED}Error optimizing portfolio: {str(e)}{Style.RESET_ALL}")
    
    def clear_portfolio(self):
        """Clear the portfolio"""
        confirm = input(f"{Fore.YELLOW}Are you sure you want to clear the portfolio? (y/n): {Style.RESET_ALL}").strip().lower()
        if confirm == 'y':
            self.portfolio.clear()
            print(f"{Fore.GREEN}Portfolio cleared.{Style.RESET_ALL}")
    
    def currency_menu(self):
        """Currency exchange menu"""
        print(f"\n{Fore.GREEN}=== {get_text('currency.converter')} ==={Style.RESET_ALL}")
        
        # Currency converter
        try:
            amount = float(input(f"{Fore.YELLOW}{get_text('currency.amount')}: {Style.RESET_ALL}"))
            from_currency = input(f"{Fore.YELLOW}{get_text('input.enter_currency_from')}{Style.RESET_ALL}").strip().upper()
            to_currency = input(f"{Fore.YELLOW}{get_text('input.enter_currency_to')}{Style.RESET_ALL}").strip().upper()
            
            print(f"{Fore.BLUE}{get_text('currency.fetching_rate')}{Style.RESET_ALL}")
            rate = self.data_manager.get_currency_rate(from_currency, to_currency)
            converted_amount = amount * rate
            
            print(f"\n{Fore.GREEN}{get_text('currency.exchange_rates')}:{Style.RESET_ALL}")
            print(f"{format_currency(amount, from_currency)} = {format_currency(converted_amount, to_currency)}")
            print(f"{get_text('currency.rate')}: 1 {from_currency} = {rate:.4f} {to_currency}")
            
        except ValueError:
            print(f"{Fore.RED}{get_text('errors.general', error='Invalid amount')}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}{get_text('errors.general', error=str(e))}{Style.RESET_ALL}")
        
        input(f"\n{get_text('input.press_enter')}")
    
    def show_market_news(self):
        """Display market news"""
        print(f"\n{Fore.GREEN}=== {get_text('news.market_news')} ==={Style.RESET_ALL}")
        
        try:
            print(f"{Fore.BLUE}{get_text('news.loading')}{Style.RESET_ALL}")
            news = self.data_manager.get_market_news(10)
            
            if not news:
                print(f"{Fore.YELLOW}{get_text('news.no_news')}{Style.RESET_ALL}")
                return
            
            for i, article in enumerate(news, 1):
                print(f"\n{Fore.CYAN}{i}. {article['title']}{Style.RESET_ALL}")
                print(f"   {get_text('news.source')}: {article['source']} | {get_text('news.published')}: {article['published'].strftime('%Y-%m-%d %H:%M')}")
                print(f"   {article['summary'][:150]}...")
                print(f"   Link: {article['link']}")
        
        except Exception as e:
            print(f"{Fore.RED}{get_text('errors.general', error=str(e))}{Style.RESET_ALL}")
        
        input(f"\n{get_text('input.press_enter')}")
    
    def show_market_overview(self):
        """Display market overview"""
        print(f"\n{Fore.GREEN}=== {get_text('market.overview')} ==={Style.RESET_ALL}")
        
        try:
            print(f"{Fore.BLUE}{get_text('market.loading')}{Style.RESET_ALL}")
            overview = self.data_manager.get_market_overview()
            
            # Major indices
            print(f"\n{Fore.CYAN}{get_text('market.indices')}:{Style.RESET_ALL}")
            indices_table = PrettyTable()
            indices_table.field_names = ["Index", get_text('market.price'), get_text('market.change'), get_text('market.change') + " %"]
            
            index_names = {
                '^GSPC': 'S&P 500',
                '^DJI': 'Dow Jones',
                '^IXIC': 'NASDAQ',
                '^BVSP': 'Bovespa',
                '^FTSE': 'FTSE 100'
            }
            
            for symbol, data in overview['indices'].items():
                name = index_names.get(symbol, symbol)
                color = Fore.GREEN if data['change'] >= 0 else Fore.RED
                arrow = "↗" if data['change'] >= 0 else "↘"
                
                indices_table.add_row([
                    name,
                    f"{data['price']:.2f}",
                    f"{color}{arrow} {data['change']:+.2f}{Style.RESET_ALL}",
                    f"{color}{data['change_percent']:+.2f}%{Style.RESET_ALL}"
                ])
            
            print(indices_table)
            
            # Currency pairs
            if overview['currencies']:
                print(f"\n{Fore.CYAN}Currency Pairs:{Style.RESET_ALL}")
                currency_table = PrettyTable()
                currency_table.field_names = ["Pair", "Rate", "Change", "Change %"]
                
                for symbol, data in overview['currencies'].items():
                    color = Fore.GREEN if data['change'] >= 0 else Fore.RED
                    arrow = "↗" if data['change'] >= 0 else "↘"
                    
                    currency_table.add_row([
                        symbol.replace('=X', ''),
                        f"{data['price']:.4f}",
                        f"{color}{arrow} {data['change']:+.6f}{Style.RESET_ALL}",
                        f"{color}{data['change_percent']:+.2f}%{Style.RESET_ALL}"
                    ])
                
                print(currency_table)
        
        except Exception as e:
            print(f"{Fore.RED}Error fetching market overview: {str(e)}{Style.RESET_ALL}")
    
    def symbol_search(self):
        """Search for stock symbols"""
        print(f"\n{Fore.GREEN}=== SYMBOL SEARCH ==={Style.RESET_ALL}")
        
        query = input(f"{Fore.YELLOW}Enter company name or symbol: {Style.RESET_ALL}").strip()
        
        if not query:
            print(f"{Fore.RED}Please enter a search term.{Style.RESET_ALL}")
            return
        
        try:
            results = self.data_manager.search_symbols(query)
            
            if results:
                table = PrettyTable()
                table.field_names = ["Symbol", "Name", "Type", "Exchange"]
                
                for result in results[:10]:  # Show top 10 results
                    table.add_row([
                        result.get('symbol', 'N/A'),
                        result.get('name', 'N/A')[:40],  # Truncate long names
                        result.get('type', 'N/A'),
                        result.get('exchange', 'N/A')
                    ])
                
                print(f"\n{Fore.CYAN}Search Results:{Style.RESET_ALL}")
                print(table)
            else:
                print(f"{Fore.YELLOW}No results found for '{query}'.{Style.RESET_ALL}")
        
        except Exception as e:
            print(f"{Fore.RED}Error searching symbols: {str(e)}{Style.RESET_ALL}")
    
    def show_system_status(self):
        """Display system status"""
        print(f"\n{Fore.GREEN}=== SYSTEM STATUS ==={Style.RESET_ALL}")
        
        # Data provider status
        provider_status = self.data_manager.get_provider_status()
        
        table = PrettyTable()
        table.field_names = ["Provider", "Status", "Last Update"]
        
        for provider, info in provider_status.items():
            status = f"{Fore.GREEN}✓ Connected{Style.RESET_ALL}" if info.get('connected', False) else f"{Fore.RED}✗ Disconnected{Style.RESET_ALL}"
            last_update = calculate_age_of_data(info['last_update']) if info.get('last_update') else "Never"
            table.add_row([provider.title(), status, last_update])
        
        print(table)
        
        # Cache status
        print(f"\nCache Status: {cache.size()} items")
        print(f"Market Hours: {'Open' if is_market_hours() else 'Closed'}")
    
    def show_about(self):
        """Display about information"""
        print(f"\n{Fore.GREEN}=== ABOUT DATASYNC ==={Style.RESET_ALL}")
        print(f"""
{Fore.CYAN}DATASYNC Market Tool v{APP_VERSION}{Style.RESET_ALL}
{Fore.YELLOW}Developed by {APP_AUTHOR}{Style.RESET_ALL}

{Fore.BLUE}Features:{Style.RESET_ALL}
• Real-time stock quotes and analysis
• Technical indicators and signals
• Portfolio management and optimization
• Currency exchange rates
• Market news and trends
• Interactive charts and visualizations

{Fore.BLUE}Data Sources:{Style.RESET_ALL}
• Yahoo Finance (Primary)
• Various financial news RSS feeds

{Fore.BLUE}Available Indicators:{Style.RESET_ALL}
• SMA, EMA, RSI, MACD
• Bollinger Bands, Stochastic
• Williams %R, CCI, ATR, OBV

{Fore.RED}Disclaimer:{Style.RESET_ALL}
This tool is for educational and informational purposes only.
Not financial advice. Consult with a qualified financial advisor
before making investment decisions.
""")
    
    def launch_web_interface(self):
        """Launch the Streamlit web interface"""
        print(f"\n{Fore.BLUE}Launching web interface...{Style.RESET_ALL}")
        
        try:
            import subprocess
            
            # Path to streamlit app
            app_path = os.path.join(os.path.dirname(__file__), 'src', 'ui', 'streamlit_app.py')
            
            # Launch streamlit
            cmd = [sys.executable, '-m', 'streamlit', 'run', app_path, '--server.headless', 'false']
            
            print(f"{Fore.GREEN}Starting web interface...{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}The web interface will open in your browser.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Close this terminal to stop the web server.{Style.RESET_ALL}")
            
            subprocess.run(cmd)
            
        except ImportError:
            print(f"{Fore.RED}Streamlit not installed. Please install with: pip install streamlit{Style.RESET_ALL}")
        except FileNotFoundError:
            print(f"{Fore.RED}Streamlit app file not found.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error launching web interface: {str(e)}{Style.RESET_ALL}")
    
    def run(self):
        """Main application loop"""
        self.show_banner()
        
        while True:
            try:
                self.show_main_menu()
                choice = self.get_user_choice()
                
                if choice == "0":
                    print(f"\n{Fore.BLUE}Thank you for using DATASYNC Market Tool!{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}Goodbye! 👋{Style.RESET_ALL}")
                    break
                
                elif choice == "1":
                    self.language_menu()
                
                elif choice == "2":
                    self.show_market_overview()
                
                elif choice == "3":
                    self.stock_analysis_menu()
                
                elif choice == "4":
                    self.portfolio_menu()
                
                elif choice == "5":
                    self.technical_analysis_menu()
                
                elif choice == "6":
                    self.currency_menu()
                
                elif choice == "7":
                    self.show_market_news()
                
                elif choice == "8":
                    self.launch_web_interface()
                
                elif choice == "7":
                    self.show_system_status()
                
                elif choice == "8":
                    self.show_about()
                
                elif choice == "9":
                    self.launch_web_interface()
                
                else:
                    print(f"{Fore.RED}Invalid option. Please select 0-9.{Style.RESET_ALL}")
                
                # Wait for user to continue
                if choice != "0" and choice != "9":
                    input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            
            except KeyboardInterrupt:
                print(f"\n\n{Fore.YELLOW}Interrupted by user. Exiting...{Style.RESET_ALL}")
                break
            except Exception as e:
                print(f"\n{Fore.RED}An error occurred: {str(e)}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Please try again or contact support.{Style.RESET_ALL}")


def main():
    """Main entry point"""
    try:
        app = DataSyncConsole()
        app.run()
    except Exception as e:
        print(f"{Fore.RED}Failed to start application: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()
