"""
Main Streamlit application for DATASYNC Market Tool
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio
import sys
import os

# Add src directory to path
current_dir = os.path.dirname(__file__)
root_dir = os.path.join(current_dir, '..', '..')
src_dir = os.path.join(root_dir, 'src')
config_dir = os.path.join(root_dir, 'config')

sys.path.insert(0, root_dir)
sys.path.insert(0, src_dir)
sys.path.insert(0, config_dir)

try:
    from src.data_providers.data_manager import DataProviderManager
    from src.analyzers.technical_analyzer import TechnicalAnalyzer
    from src.analyzers.portfolio_analyzer import PortfolioAnalyzer
    from src.utils.helpers import *
    from src.utils.plotting import ChartManager
    from config.settings import *
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Please ensure all modules are properly installed and paths are correct.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="DATASYNC Market Tool",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .positive { color: #00C853; }
    .negative { color: #FF1744; }
    .neutral { color: #757575; }
    .big-font { font-size: 24px !important; }
    .medium-font { font-size: 18px !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_data_manager():
    """Get cached data manager instance"""
    return DataProviderManager()

@st.cache_data(ttl=300)
def get_stock_data(symbol, period, interval):
    """Get cached stock data"""
    dm = get_data_manager()
    return dm.get_stock_data(symbol, period, interval)

@st.cache_data(ttl=60)  # Cache for 1 minute for real-time data
def get_real_time_data(symbol):
    """Get cached real-time data"""
    dm = get_data_manager()
    return dm.get_real_time_price(symbol)

@st.cache_data(ttl=300)
def get_market_news(limit=20):
    """Get cached market news"""
    dm = get_data_manager()
    try:
        return dm.get_market_news(limit)
    except:
        return []

def main():
    # Initialize components
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataProviderManager()
    
    if 'technical_analyzer' not in st.session_state:
        st.session_state.technical_analyzer = TechnicalAnalyzer()
    
    if 'portfolio_analyzer' not in st.session_state:
        st.session_state.portfolio_analyzer = PortfolioAnalyzer()
    
    if 'chart_manager' not in st.session_state:
        st.session_state.chart_manager = ChartManager()
    
    # Sidebar
    with st.sidebar:
        st.title("📈 DATASYNC")
        st.markdown("### Market Analysis Tool")
        st.markdown("---")
        
        # Navigation
        page = st.selectbox(
            "Navigate to:",
            ["🏠 Dashboard", "📊 Stock Analysis", "💰 Portfolio", "📰 News", "💱 Currency", "⚙️ Settings"]
        )
        
        st.markdown("---")
        
        # Quick stock lookup
        st.markdown("### Quick Lookup")
        quick_symbol = st.text_input("Enter Symbol:", placeholder="e.g., AAPL")
        
        if quick_symbol and st.button("Quick View"):
            try:
                data = get_real_time_data(clean_symbol(quick_symbol))
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Price", format_currency(data['price'], data.get('currency', 'USD')))
                
                with col2:
                    change_color = "positive" if data['change'] >= 0 else "negative"
                    st.markdown(f"<span class='{change_color}'>{get_arrow_for_change(data['change'])} {format_percentage(data['change_percent'])}</span>", 
                               unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        st.markdown("---")
        st.markdown("*Developed by Guilherme Rosental*")
    
    # Main content based on selected page
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "📊 Stock Analysis":
        show_stock_analysis()
    elif page == "💰 Portfolio":
        show_portfolio()
    elif page == "📰 News":
        show_news()
    elif page == "💱 Currency":
        show_currency()
    elif page == "⚙️ Settings":
        show_settings()

def show_dashboard():
    """Display main dashboard"""
    st.title("🏠 Market Dashboard")
    
    # Market Overview
    st.header("📈 Market Overview")
    
    # Get major indices
    indices_symbols = ['^GSPC', '^DJI', '^IXIC', '^BVSP', '^FTSE']
    indices_names = ['S&P 500', 'Dow Jones', 'NASDAQ', 'Bovespa', 'FTSE 100']
    
    try:
        col1, col2, col3, col4, col5 = st.columns(5)
        columns = [col1, col2, col3, col4, col5]
        
        for i, (symbol, name) in enumerate(zip(indices_symbols, indices_names)):
            try:
                data = get_real_time_data(symbol)
                with columns[i]:
                    change_color = "positive" if data['change'] >= 0 else "negative"
                    st.metric(
                        name,
                        f"{data['price']:.2f}",
                        f"{data['change']:+.2f} ({data['change_percent']:+.2f}%)"
                    )
            except:
                with columns[i]:
                    st.metric(name, "N/A", "N/A")
    
    except Exception as e:
        st.error(f"Error loading market overview: {e}")
    
    st.markdown("---")
    
    # Market News
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📰 Latest Market News")
        news = get_market_news(10)
        
        if news:
            for article in news[:5]:
                with st.expander(f"📰 {article['title'][:100]}..."):
                    st.write(f"**Source:** {article['source']}")
                    st.write(f"**Published:** {article['published'].strftime('%Y-%m-%d %H:%M')}")
                    st.write(article['summary'][:300] + "...")
                    st.markdown(f"[Read more]({article['link']})")
        else:
            st.info("No news available at the moment.")
    
    with col2:
        st.header("🔥 Trending")
        try:
            trending = st.session_state.data_manager.get_trending_topics()
            
            if trending:
                for topic in trending[:5]:
                    st.write(f"• **{topic['topic']}** ({topic['mentions']} mentions)")
            else:
                st.info("No trending topics available.")
        except:
            st.info("Trending topics unavailable.")
        
        st.markdown("---")
        
        # Quick stats
        st.subheader("⚡ Quick Stats")
        st.write("• Market Status: Open" if is_market_hours() else "• Market Status: Closed")
        st.write(f"• Last Update: {datetime.now().strftime('%H:%M:%S')}")

def show_stock_analysis():
    """Display stock analysis page"""
    st.title("📊 Stock Analysis")
    
    # Stock selection
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        symbol = st.text_input("Enter Stock Symbol:", placeholder="e.g., AAPL, MSFT, TSLA").upper()
    
    with col2:
        period = st.selectbox("Period:", ['1mo', '3mo', '6mo', '1y', '2y', '5y'], index=3)
    
    with col3:
        interval = st.selectbox("Interval:", ['1d', '1wk', '1mo'], index=0)
    
    if symbol and st.button("Analyze Stock", type="primary"):
        try:
            # Get stock data
            with st.spinner(f"Fetching data for {symbol}..."):
                df = get_stock_data(symbol, period, interval)
                real_time_data = get_real_time_data(symbol)
                company_info = st.session_state.data_manager.get_company_info(symbol)
            
            # Stock header with company info
            st.header(f"{company_info.get('company_name', symbol)} ({symbol})")
            
            # Key metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Current Price", 
                         format_currency(real_time_data['price'], real_time_data.get('currency', 'USD')))
            
            with col2:
                change_color = "🟢" if real_time_data['change'] >= 0 else "🔴"
                st.metric("Change", 
                         f"{change_color} {real_time_data['change']:+.2f}",
                         f"{real_time_data['change_percent']:+.2f}%")
            
            with col3:
                st.metric("Volume", format_volume(real_time_data['volume']))
            
            with col4:
                st.metric("Market Cap", format_market_cap(company_info.get('market_cap', 0)))
            
            with col5:
                st.metric("P/E Ratio", f"{company_info.get('pe_ratio', 'N/A')}")
            
            st.markdown("---")
            
            # Charts section
            st.subheader("📈 Price Charts")
            
            chart_type = st.selectbox("Chart Type:", ["Candlestick", "Line", "Volume"])
            
            if chart_type == "Candlestick":
                fig = st.session_state.chart_manager.create_candlestick_chart(df, f"{symbol} Stock Price")
                st.plotly_chart(fig, use_container_width=True)
            
            elif chart_type == "Line":
                fig = st.session_state.chart_manager.create_line_chart(df, ['Close'], f"{symbol} Stock Price")
                st.plotly_chart(fig, use_container_width=True)
            
            elif chart_type == "Volume":
                fig = st.session_state.chart_manager.create_volume_chart(df, f"{symbol} Volume Analysis")
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Technical Analysis
            st.subheader("🔍 Technical Analysis")
            
            with st.spinner("Calculating technical indicators..."):
                analysis = st.session_state.technical_analyzer.analyze_stock(df)
                signals = st.session_state.technical_analyzer.generate_signals(analysis)
                trends = st.session_state.technical_analyzer.get_trend_analysis(df)
            
            # Signals
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Trading Signals:**")
                for indicator, signal in signals.items():
                    color = "🟢" if signal == "BULLISH" else "🔴" if signal == "BEARISH" else "🟡"
                    st.write(f"{color} {indicator.upper()}: {signal}")
            
            with col2:
                st.write("**Trend Analysis:**")
                for timeframe, trend in trends.items():
                    color = "🟢" if trend == "BULLISH" else "🔴" if trend == "BEARISH" else "🟡"
                    st.write(f"{color} {timeframe.replace('_', ' ').title()}: {trend}")
            
            # Technical Indicators Charts
            st.subheader("📊 Technical Indicators")
            
            indicator_choice = st.selectbox("Select Indicator:", 
                                          ["RSI", "MACD", "Bollinger Bands", "Moving Averages"])
            
            if indicator_choice == "RSI":
                fig = st.session_state.chart_manager.create_rsi_chart(df, analysis['rsi'], f"{symbol} RSI")
                st.plotly_chart(fig, use_container_width=True)
            
            elif indicator_choice == "MACD":
                macd_data = {
                    'macd': analysis['macd'],
                    'macd_signal': analysis['macd_signal'],
                    'macd_histogram': analysis['macd_histogram']
                }
                fig = st.session_state.chart_manager.create_macd_chart(df, macd_data, f"{symbol} MACD")
                st.plotly_chart(fig, use_container_width=True)
            
            elif indicator_choice == "Bollinger Bands":
                bb_data = {
                    'bb_upper': analysis['bb_upper'],
                    'bb_middle': analysis['bb_middle'],
                    'bb_lower': analysis['bb_lower']
                }
                fig = st.session_state.chart_manager.create_bollinger_bands_chart(df, bb_data, f"{symbol} Bollinger Bands")
                st.plotly_chart(fig, use_container_width=True)
            
            elif indicator_choice == "Moving Averages":
                ma_data = {
                    'Close': df['Close'],
                    'SMA 20': analysis['sma_20'],
                    'SMA 50': analysis['sma_50'],
                    'EMA 12': analysis['ema_12'],
                    'EMA 26': analysis['ema_26']
                }
                fig = st.session_state.chart_manager.create_line_chart(
                    pd.DataFrame(ma_data), 
                    ['Close', 'SMA 20', 'SMA 50', 'EMA 12', 'EMA 26'],
                    f"{symbol} Moving Averages"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Company Information
            st.subheader("🏢 Company Information")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Sector:** {company_info.get('sector', 'N/A')}")
                st.write(f"**Industry:** {company_info.get('industry', 'N/A')}")
                st.write(f"**Country:** {company_info.get('country', 'N/A')}")
                st.write(f"**Employees:** {format_number(company_info.get('employees', 0))}")
            
            with col2:
                st.write(f"**52W High:** {format_currency(company_info.get('52_week_high', 0), real_time_data.get('currency', 'USD'))}")
                st.write(f"**52W Low:** {format_currency(company_info.get('52_week_low', 0), real_time_data.get('currency', 'USD'))}")
                st.write(f"**Beta:** {company_info.get('beta', 'N/A')}")
                st.write(f"**Dividend Yield:** {format_percentage(company_info.get('dividend_yield', 0) * 100 if company_info.get('dividend_yield') else 0)}")
            
            if company_info.get('business_summary'):
                st.write("**Business Summary:**")
                st.write(company_info['business_summary'][:500] + "...")
            
        except Exception as e:
            st.error(f"Error analyzing stock {symbol}: {str(e)}")
            st.error("Please check if the symbol is correct and try again.")

def show_portfolio():
    """Display portfolio analysis page"""
    st.title("💰 Portfolio Analysis")
    
    st.header("📊 Portfolio Builder")
    
    # Portfolio input
    st.subheader("Add Stocks to Portfolio")
    
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = {}
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        new_symbol = st.text_input("Stock Symbol:", placeholder="e.g., AAPL").upper()
    
    with col2:
        new_weight = st.number_input("Weight (%):", min_value=0.0, max_value=100.0, value=10.0, step=0.1)
    
    with col3:
        if st.button("Add to Portfolio"):
            if new_symbol and new_weight > 0:
                st.session_state.portfolio[new_symbol] = new_weight / 100
                st.success(f"Added {new_symbol} with {new_weight}% weight")
    
    # Display current portfolio
    if st.session_state.portfolio:
        st.subheader("Current Portfolio")
        
        portfolio_df = pd.DataFrame(list(st.session_state.portfolio.items()), 
                                  columns=['Symbol', 'Weight'])
        portfolio_df['Weight (%)'] = portfolio_df['Weight'] * 100
        
        st.dataframe(portfolio_df[['Symbol', 'Weight (%)']], use_container_width=True)
        
        # Portfolio controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Analyze Portfolio", type="primary"):
                analyze_portfolio()
        
        with col2:
            if st.button("Optimize Portfolio"):
                optimize_portfolio()
        
        with col3:
            if st.button("Clear Portfolio"):
                st.session_state.portfolio = {}
                st.rerun()
    else:
        st.info("Add stocks to your portfolio to get started.")

def analyze_portfolio():
    """Analyze the current portfolio"""
    try:
        with st.spinner("Analyzing portfolio..."):
            # Get data for all stocks
            portfolio_data = {}
            for symbol in st.session_state.portfolio.keys():
                df = get_stock_data(symbol, "1y", "1d")
                portfolio_data[symbol] = df['Close']
            
            # Create portfolio DataFrame
            portfolio_df = pd.DataFrame(portfolio_data).fillna(method='forward').dropna()
            
            # Calculate returns
            returns = st.session_state.portfolio_analyzer.calculate_returns(portfolio_df)
            
            # Portfolio weights
            weights = np.array(list(st.session_state.portfolio.values()))
            
            # Normalize weights
            weights = weights / weights.sum()
            
            # Calculate metrics
            metrics = st.session_state.portfolio_analyzer.calculate_portfolio_metrics(returns, weights)
            
            # Display metrics
            st.subheader("📈 Portfolio Performance")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Annual Return", format_percentage(metrics['annual_return'] * 100))
            
            with col2:
                st.metric("Annual Volatility", format_percentage(metrics['annual_volatility'] * 100))
            
            with col3:
                st.metric("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")
            
            with col4:
                st.metric("Max Drawdown", format_percentage(metrics['max_drawdown'] * 100))
            
            # Portfolio composition chart
            st.subheader("🥧 Portfolio Composition")
            fig = st.session_state.chart_manager.create_pie_chart(
                {symbol: weight for symbol, weight in st.session_state.portfolio.items()},
                "Portfolio Allocation"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Correlation matrix
            st.subheader("🔗 Correlation Matrix")
            correlation_matrix = st.session_state.portfolio_analyzer.calculate_correlation_matrix(returns)
            fig = st.session_state.chart_manager.create_correlation_heatmap(correlation_matrix)
            st.plotly_chart(fig, use_container_width=True)
            
            # Performance comparison
            st.subheader("📊 Performance Comparison")
            normalized_data = {}
            for symbol in portfolio_data.keys():
                series = portfolio_data[symbol]
                normalized_data[symbol] = series
            
            fig = st.session_state.chart_manager.create_comparison_chart(normalized_data)
            st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error analyzing portfolio: {str(e)}")

def optimize_portfolio():
    """Optimize the current portfolio"""
    try:
        with st.spinner("Optimizing portfolio..."):
            # Get data for all stocks
            portfolio_data = {}
            for symbol in st.session_state.portfolio.keys():
                df = get_stock_data(symbol, "1y", "1d")
                portfolio_data[symbol] = df['Close']
            
            portfolio_df = pd.DataFrame(portfolio_data).fillna(method='forward').dropna()
            returns = st.session_state.portfolio_analyzer.calculate_returns(portfolio_df)
            
            # Optimize for different objectives
            optimization_methods = ['sharpe', 'min_volatility', 'max_return']
            
            st.subheader("🎯 Portfolio Optimization")
            
            for method in optimization_methods:
                result = st.session_state.portfolio_analyzer.optimize_portfolio(returns, method)
                
                if result['optimization_success']:
                    st.write(f"**{method.replace('_', ' ').title()} Optimization:**")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        weights_df = pd.DataFrame(list(result['weights'].items()), 
                                                columns=['Symbol', 'Optimal Weight'])
                        weights_df['Optimal Weight (%)'] = weights_df['Optimal Weight'] * 100
                        st.dataframe(weights_df[['Symbol', 'Optimal Weight (%)']])
                    
                    with col2:
                        metrics = result['metrics']
                        st.write(f"Annual Return: {format_percentage(metrics['annual_return'] * 100)}")
                        st.write(f"Annual Volatility: {format_percentage(metrics['annual_volatility'] * 100)}")
                        st.write(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
                        st.write(f"Max Drawdown: {format_percentage(metrics['max_drawdown'] * 100)}")
                
                st.markdown("---")
    
    except Exception as e:
        st.error(f"Error optimizing portfolio: {str(e)}")

def show_news():
    """Display news page"""
    st.title("📰 Market News")
    
    # News controls
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input("Search news:", placeholder="Enter keywords...")
    
    with col2:
        news_limit = st.selectbox("Number of articles:", [10, 20, 30, 50], index=1)
    
    if st.button("Refresh News", type="primary"):
        st.cache_data.clear()
    
    # Get news
    try:
        if search_query:
            news = st.session_state.data_manager.search_news(search_query, news_limit)
            st.subheader(f"🔍 Search Results for '{search_query}'")
        else:
            news = get_market_news(news_limit)
            st.subheader("📰 Latest Market News")
        
        if news:
            for i, article in enumerate(news):
                with st.expander(f"📰 {article['title']}", expanded=(i < 3)):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(article['summary'])
                        st.markdown(f"[Read full article]({article['link']})")
                    
                    with col2:
                        st.write(f"**Source:** {article['source']}")
                        st.write(f"**Published:** {article['published'].strftime('%Y-%m-%d %H:%M')}")
                        st.write(f"**Author:** {article.get('author', 'N/A')}")
        else:
            st.info("No news articles found.")
    
    except Exception as e:
        st.error(f"Error loading news: {str(e)}")

def show_currency():
    """Display currency exchange page"""
    st.title("💱 Currency Exchange")
    
    # Currency converter
    st.header("💰 Currency Converter")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        amount = st.number_input("Amount:", min_value=0.01, value=1.0, step=0.01)
    
    with col2:
        from_currency = st.selectbox("From:", DEFAULT_CURRENCIES, index=0)
    
    with col3:
        to_currency = st.selectbox("To:", DEFAULT_CURRENCIES, index=2)  # BRL
    
    with col4:
        if st.button("Convert", type="primary"):
            try:
                rate = st.session_state.data_manager.get_currency_rate(from_currency, to_currency)
                converted_amount = amount * rate
                
                st.success(f"{format_currency(amount, from_currency)} = {format_currency(converted_amount, to_currency)}")
                st.info(f"Exchange Rate: 1 {from_currency} = {rate:.4f} {to_currency}")
            
            except Exception as e:
                st.error(f"Error converting currency: {str(e)}")
    
    st.markdown("---")
    
    # Currency rates table
    st.header("📊 Currency Rates")
    
    base_currency = st.selectbox("Base Currency:", DEFAULT_CURRENCIES, index=0, key="base_curr")
    
    if st.button("Get Rates", type="primary"):
        try:
            with st.spinner("Fetching currency rates..."):
                target_currencies = [curr for curr in DEFAULT_CURRENCIES if curr != base_currency]
                rates = st.session_state.data_manager.get_currency_rates(base_currency, target_currencies)
                
                rates_data = []
                for currency, rate in rates.items():
                    if rate is not None:
                        rates_data.append({
                            'Currency Pair': f"{base_currency}/{currency}",
                            'Exchange Rate': f"{rate:.4f}",
                            'Inverse Rate': f"{1/rate:.4f}" if rate != 0 else "N/A"
                        })
                
                if rates_data:
                    rates_df = pd.DataFrame(rates_data)
                    st.dataframe(rates_df, use_container_width=True)
                else:
                    st.warning("No currency rates available.")
        
        except Exception as e:
            st.error(f"Error fetching currency rates: {str(e)}")

def show_settings():
    """Display settings page"""
    st.title("⚙️ Settings")
    
    st.header("🔧 Application Settings")
    
    # Data provider settings
    st.subheader("📡 Data Providers")
    
    provider_status = st.session_state.data_manager.get_provider_status()
    
    for provider, info in provider_status.items():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write(f"**{provider.title()}**: {info.get('name', 'Unknown')}")
            if 'last_update' in info and info['last_update']:
                st.write(f"Last Update: {calculate_age_of_data(info['last_update'])}")
        
        with col2:
            status = "🟢 Connected" if info.get('connected', False) else "🔴 Disconnected"
            st.write(status)
    
    if st.button("Refresh Providers"):
        with st.spinner("Refreshing data providers..."):
            st.session_state.data_manager.refresh_providers()
            st.success("Data providers refreshed!")
            st.rerun()
    
    st.markdown("---")
    
    # Chart settings
    st.subheader("📊 Chart Settings")
    
    chart_theme = st.selectbox("Chart Theme:", CHART_THEMES, index=0)
    default_period = st.selectbox("Default Period:", ['1mo', '3mo', '6mo', '1y', '2y', '5y'], index=3)
    default_interval = st.selectbox("Default Interval:", ['1d', '1wk', '1mo'], index=0)
    
    # Cache settings
    st.subheader("💾 Cache Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        cache_size = cache.size()
        st.metric("Cache Size", f"{cache_size} items")
    
    with col2:
        if st.button("Clear Cache"):
            cache.clear()
            st.cache_data.clear()
            st.success("Cache cleared!")
    
    st.markdown("---")
    
    # About
    st.subheader("ℹ️ About")
    
    st.markdown(f"""
    **DATASYNC Market Tool v{APP_VERSION}**
    
    Developed by {APP_AUTHOR}
    
    This application provides comprehensive market analysis tools including:
    - Real-time stock prices and charts
    - Technical analysis indicators
    - Portfolio analysis and optimization
    - Market news and trends
    - Currency exchange rates
    
    **Data Sources:**
    - Yahoo Finance (Primary)
    - Various news RSS feeds
    
    **Disclaimer:** This tool is for educational and informational purposes only. 
    Not financial advice. Please consult with a qualified financial advisor before making investment decisions.
    """)

if __name__ == "__main__":
    main()
