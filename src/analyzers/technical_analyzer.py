"""
Technical Analysis Module
Provides various technical indicators and analysis tools
"""
import pandas as pd
import numpy as np
import ta
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta


class TechnicalAnalyzer:
    """Technical analysis and indicators calculator"""
    
    def __init__(self):
        self.indicators = {}
        
    def calculate_sma(self, data: pd.Series, window: int = 20) -> pd.Series:
        """Calculate Simple Moving Average"""
        return data.rolling(window=window).mean()
    
    def calculate_ema(self, data: pd.Series, window: int = 20) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return data.ewm(span=window).mean()
    
    def calculate_rsi(self, data: pd.Series, window: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        return ta.momentum.RSIIndicator(close=data, window=window).rsi()
    
    def calculate_macd(self, data: pd.Series, window_slow: int = 26, window_fast: int = 12, window_sign: int = 9) -> Dict[str, pd.Series]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        macd_indicator = ta.trend.MACD(close=data, window_slow=window_slow, window_fast=window_fast, window_sign=window_sign)
        
        return {
            'macd': macd_indicator.macd(),
            'macd_signal': macd_indicator.macd_signal(),
            'macd_histogram': macd_indicator.macd_diff()
        }
    
    def calculate_bollinger_bands(self, data: pd.Series, window: int = 20, window_dev: int = 2) -> Dict[str, pd.Series]:
        """Calculate Bollinger Bands"""
        bb_indicator = ta.volatility.BollingerBands(close=data, window=window, window_dev=window_dev)
        
        return {
            'bb_upper': bb_indicator.bollinger_hband(),
            'bb_middle': bb_indicator.bollinger_mavg(),
            'bb_lower': bb_indicator.bollinger_lband(),
            'bb_width': bb_indicator.bollinger_wband(),
            'bb_percent': bb_indicator.bollinger_pband()
        }
    
    def calculate_stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series, 
                           k_window: int = 14, d_window: int = 3) -> Dict[str, pd.Series]:
        """Calculate Stochastic Oscillator"""
        stoch_indicator = ta.momentum.StochasticOscillator(high=high, low=low, close=close, 
                                                         window=k_window, smooth_window=d_window)
        
        return {
            'stoch_k': stoch_indicator.stoch(),
            'stoch_d': stoch_indicator.stoch_signal()
        }
    
    def calculate_williams_r(self, high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
        """Calculate Williams %R"""
        return ta.momentum.WilliamsRIndicator(high=high, low=low, close=close, lbp=window).williams_r()
    
    def calculate_cci(self, high: pd.Series, low: pd.Series, close: pd.Series, window: int = 20) -> pd.Series:
        """Calculate Commodity Channel Index"""
        return ta.trend.CCIIndicator(high=high, low=low, close=close, window=window).cci()
    
    def calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        return ta.volatility.AverageTrueRange(high=high, low=low, close=close, window=window).average_true_range()
    
    def calculate_obv(self, close: pd.Series, volume: pd.Series) -> pd.Series:
        """Calculate On-Balance Volume"""
        return ta.volume.OnBalanceVolumeIndicator(close=close, volume=volume).on_balance_volume()
    
    def calculate_adx(self, high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> Dict[str, pd.Series]:
        """Calculate Average Directional Index"""
        adx_indicator = ta.trend.ADXIndicator(high=high, low=low, close=close, window=window)
        
        return {
            'adx': adx_indicator.adx(),
            'adx_pos': adx_indicator.adx_pos(),
            'adx_neg': adx_indicator.adx_neg()
        }
    
    def calculate_fibonacci_retracement(self, high_price: float, low_price: float) -> Dict[str, float]:
        """Calculate Fibonacci retracement levels"""
        diff = high_price - low_price
        
        levels = {
            '0%': high_price,
            '23.6%': high_price - 0.236 * diff,
            '38.2%': high_price - 0.382 * diff,
            '50%': high_price - 0.5 * diff,
            '61.8%': high_price - 0.618 * diff,
            '78.6%': high_price - 0.786 * diff,
            '100%': low_price
        }
        
        return levels
    
    def analyze_stock(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Comprehensive technical analysis of stock data"""
        if df.empty or len(df) < 50:
            raise ValueError("Insufficient data for technical analysis")
        
        analysis = {}
        
        # Price data
        close = df['Close']
        high = df['High']
        low = df['Low']
        volume = df['Volume']
        open_price = df['Open']
        
        # Moving Averages
        analysis['sma_20'] = self.calculate_sma(close, 20)
        analysis['sma_50'] = self.calculate_sma(close, 50)
        analysis['ema_12'] = self.calculate_ema(close, 12)
        analysis['ema_26'] = self.calculate_ema(close, 26)
        
        # Momentum Indicators
        analysis['rsi'] = self.calculate_rsi(close)
        analysis.update(self.calculate_macd(close))
        analysis.update(self.calculate_stochastic(high, low, close))
        analysis['williams_r'] = self.calculate_williams_r(high, low, close)
        
        # Volatility Indicators
        analysis.update(self.calculate_bollinger_bands(close))
        analysis['atr'] = self.calculate_atr(high, low, close)
        
        # Volume Indicators
        analysis['obv'] = self.calculate_obv(close, volume)
        
        # Trend Indicators
        analysis['cci'] = self.calculate_cci(high, low, close)
        analysis.update(self.calculate_adx(high, low, close))
        
        # Support and Resistance
        analysis['support_resistance'] = self.find_support_resistance(close)
        
        # Fibonacci levels
        period_high = high.max()
        period_low = low.min()
        analysis['fibonacci'] = self.calculate_fibonacci_retracement(period_high, period_low)
        
        return analysis
    
    def find_support_resistance(self, close: pd.Series, window: int = 20) -> Dict[str, List[float]]:
        """Find support and resistance levels"""
        # Simple method using local minima and maxima
        support_levels = []
        resistance_levels = []
        
        # Rolling minima and maxima
        rolling_min = close.rolling(window=window, center=True).min()
        rolling_max = close.rolling(window=window, center=True).max()
        
        for i in range(window, len(close) - window):
            if close.iloc[i] == rolling_min.iloc[i]:
                support_levels.append(close.iloc[i])
            if close.iloc[i] == rolling_max.iloc[i]:
                resistance_levels.append(close.iloc[i])
        
        # Remove duplicates and sort
        support_levels = sorted(list(set(support_levels)))
        resistance_levels = sorted(list(set(resistance_levels)), reverse=True)
        
        return {
            'support': support_levels[:5],  # Top 5 support levels
            'resistance': resistance_levels[:5]  # Top 5 resistance levels
        }
    
    def generate_signals(self, analysis: Dict[str, Any]) -> Dict[str, str]:
        """Generate trading signals based on technical indicators"""
        signals = {}
        current_data = {}
        
        # Get latest values
        for key, value in analysis.items():
            if isinstance(value, pd.Series) and not value.empty:
                current_data[key] = value.iloc[-1]
            elif isinstance(value, dict):
                current_data[key] = value
        
        # RSI Signal
        if 'rsi' in current_data:
            rsi = current_data['rsi']
            if rsi > 70:
                signals['rsi'] = 'OVERBOUGHT'
            elif rsi < 30:
                signals['rsi'] = 'OVERSOLD'
            else:
                signals['rsi'] = 'NEUTRAL'
        
        # MACD Signal
        if 'macd' in current_data and 'macd_signal' in current_data:
            macd = current_data['macd']
            macd_signal = current_data['macd_signal']
            if macd > macd_signal:
                signals['macd'] = 'BULLISH'
            else:
                signals['macd'] = 'BEARISH'
        
        # Bollinger Bands Signal
        if all(k in current_data for k in ['bb_upper', 'bb_lower']) and 'Close' in analysis:
            current_price = analysis['Close'].iloc[-1]
            bb_upper = current_data['bb_upper']
            bb_lower = current_data['bb_lower']
            
            if current_price > bb_upper:
                signals['bollinger'] = 'OVERBOUGHT'
            elif current_price < bb_lower:
                signals['bollinger'] = 'OVERSOLD'
            else:
                signals['bollinger'] = 'NEUTRAL'
        
        # Moving Average Signal
        if 'sma_20' in current_data and 'sma_50' in current_data:
            sma_20 = current_data['sma_20']
            sma_50 = current_data['sma_50']
            
            if sma_20 > sma_50:
                signals['ma_trend'] = 'BULLISH'
            else:
                signals['ma_trend'] = 'BEARISH'
        
        # Stochastic Signal
        if 'stoch_k' in current_data:
            stoch_k = current_data['stoch_k']
            if stoch_k > 80:
                signals['stochastic'] = 'OVERBOUGHT'
            elif stoch_k < 20:
                signals['stochastic'] = 'OVERSOLD'
            else:
                signals['stochastic'] = 'NEUTRAL'
        
        return signals
    
    def get_trend_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze overall trend of the stock"""
        close = df['Close']
        
        # Short, medium, and long term trends
        sma_10 = self.calculate_sma(close, 10).iloc[-1]
        sma_50 = self.calculate_sma(close, 50).iloc[-1]
        sma_200 = self.calculate_sma(close, 200).iloc[-1]
        current_price = close.iloc[-1]
        
        trends = {
            'short_term': 'BULLISH' if current_price > sma_10 else 'BEARISH',
            'medium_term': 'BULLISH' if current_price > sma_50 else 'BEARISH',
            'long_term': 'BULLISH' if current_price > sma_200 else 'BEARISH',
            'overall': 'NEUTRAL'
        }
        
        # Overall trend based on multiple timeframes
        bullish_count = sum(1 for trend in trends.values() if trend == 'BULLISH')
        
        if bullish_count >= 2:
            trends['overall'] = 'BULLISH'
        elif bullish_count <= 1:
            trends['overall'] = 'BEARISH'
        
        return trends
    
    def calculate_volatility(self, df: pd.DataFrame, window: int = 20) -> Dict[str, float]:
        """Calculate various volatility measures"""
        close = df['Close']
        returns = close.pct_change().dropna()
        
        return {
            'historical_volatility': returns.std() * np.sqrt(252),  # Annualized
            'rolling_volatility': returns.rolling(window=window).std().iloc[-1] * np.sqrt(252),
            'average_true_range_pct': (self.calculate_atr(df['High'], df['Low'], df['Close']).iloc[-1] / close.iloc[-1]) * 100
        }
