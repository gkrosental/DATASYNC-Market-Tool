"""
Plotting utilities for creating various types of financial charts
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import plotly.graph_objects as go
import plotly.subplots as sp
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import seaborn as sns
from datetime import datetime


class ChartManager:
    """Manages creation of various financial charts"""
    
    def __init__(self, style: str = 'plotly'):
        self.style = style
        self.setup_style()
    
    def setup_style(self):
        """Setup chart styling"""
        if self.style == 'seaborn':
            sns.set_style("whitegrid")
            plt.style.use('seaborn-v0_8')
        elif self.style == 'dark':
            plt.style.use('dark_background')
        else:
            plt.style.use('default')
    
    def create_candlestick_chart(self, df: pd.DataFrame, title: str = "Stock Price", 
                               volume: bool = True, indicators: Dict[str, pd.Series] = None) -> go.Figure:
        """Create interactive candlestick chart"""
        if volume:
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                subplot_titles=(title, 'Volume'),
                row_width=[0.2, 0.7]
            )
        else:
            fig = go.Figure()
        
        # Candlestick chart
        candlestick = go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="Price",
            increasing_line_color='green',
            decreasing_line_color='red'
        )
        
        if volume:
            fig.add_trace(candlestick, row=1, col=1)
        else:
            fig.add_trace(candlestick)
        
        # Add technical indicators
        if indicators:
            for name, data in indicators.items():
                if data is not None and not data.empty:
                    if volume:
                        fig.add_trace(go.Scatter(
                            x=df.index,
                            y=data,
                            mode='lines',
                            name=name,
                            line=dict(width=2)
                        ), row=1, col=1)
                    else:
                        fig.add_trace(go.Scatter(
                            x=df.index,
                            y=data,
                            mode='lines',
                            name=name,
                            line=dict(width=2)
                        ))
        
        # Volume bars
        if volume and 'Volume' in df.columns:
            colors = ['green' if close >= open else 'red' 
                     for close, open in zip(df['Close'], df['Open'])]
            
            fig.add_trace(go.Bar(
                x=df.index,
                y=df['Volume'],
                name="Volume",
                marker_color=colors,
                opacity=0.7
            ), row=2, col=1)
        
        # Update layout
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Price",
            template="plotly_white",
            showlegend=True,
            height=600 if volume else 400,
            hovermode='x unified'
        )
        
        # Remove range slider
        fig.update_layout(xaxis_rangeslider_visible=False)
        
        return fig
    
    def create_line_chart(self, df: pd.DataFrame, columns: List[str], 
                         title: str = "Price Chart", colors: List[str] = None) -> go.Figure:
        """Create multi-line chart"""
        fig = go.Figure()
        
        if colors is None:
            colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
        
        for i, col in enumerate(columns):
            if col in df.columns:
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=df[col],
                    mode='lines',
                    name=col,
                    line=dict(color=colors[i % len(colors)], width=2)
                ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Value",
            template="plotly_white",
            showlegend=True,
            height=400,
            hovermode='x unified'
        )
        
        return fig
    
    def create_comparison_chart(self, data: Dict[str, pd.Series], 
                              title: str = "Performance Comparison") -> go.Figure:
        """Create normalized comparison chart"""
        fig = go.Figure()
        
        colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
        
        for i, (name, series) in enumerate(data.items()):
            # Normalize to percentage change from first value
            normalized = (series / series.iloc[0] - 1) * 100
            
            fig.add_trace(go.Scatter(
                x=series.index,
                y=normalized,
                mode='lines',
                name=name,
                line=dict(color=colors[i % len(colors)], width=2)
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Return (%)",
            template="plotly_white",
            showlegend=True,
            height=400,
            hovermode='x unified'
        )
        
        # Add horizontal line at 0%
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        
        return fig
    
    def create_correlation_heatmap(self, correlation_matrix: pd.DataFrame, 
                                 title: str = "Correlation Matrix") -> go.Figure:
        """Create correlation heatmap"""
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.index,
            colorscale='RdBu',
            zmid=0,
            text=correlation_matrix.values.round(2),
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title=title,
            template="plotly_white",
            height=600,
            width=600
        )
        
        return fig
    
    def create_pie_chart(self, data: Dict[str, float], title: str = "Allocation") -> go.Figure:
        """Create pie chart"""
        fig = go.Figure(data=[go.Pie(
            labels=list(data.keys()),
            values=list(data.values()),
            hole=0.3,
            textinfo='label+percent',
            textposition='outside'
        )])
        
        fig.update_layout(
            title=title,
            template="plotly_white",
            height=400,
            showlegend=True
        )
        
        return fig
    
    def create_histogram(self, data: pd.Series, bins: int = 50, 
                        title: str = "Distribution") -> go.Figure:
        """Create histogram"""
        fig = go.Figure(data=[go.Histogram(
            x=data,
            nbinsx=bins,
            name="Distribution",
            opacity=0.7
        )])
        
        # Add vertical line for mean
        fig.add_vline(x=data.mean(), line_dash="dash", line_color="red", 
                     annotation_text=f"Mean: {data.mean():.4f}")
        
        fig.update_layout(
            title=title,
            xaxis_title="Value",
            yaxis_title="Frequency",
            template="plotly_white",
            height=400
        )
        
        return fig
    
    def create_rsi_chart(self, df: pd.DataFrame, rsi_data: pd.Series, 
                        title: str = "RSI Chart") -> go.Figure:
        """Create RSI chart with price"""
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=("Price", "RSI"),
            row_heights=[0.7, 0.3]
        )
        
        # Price chart
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Close'],
            mode='lines',
            name='Close Price',
            line=dict(color='blue', width=2)
        ), row=1, col=1)
        
        # RSI chart
        fig.add_trace(go.Scatter(
            x=df.index,
            y=rsi_data,
            mode='lines',
            name='RSI',
            line=dict(color='orange', width=2)
        ), row=2, col=1)
        
        # RSI levels
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        fig.add_hline(y=50, line_dash="dot", line_color="gray", row=2, col=1)
        
        fig.update_layout(
            title=title,
            template="plotly_white",
            height=600,
            showlegend=True,
            hovermode='x unified'
        )
        
        return fig
    
    def create_macd_chart(self, df: pd.DataFrame, macd_data: Dict[str, pd.Series], 
                         title: str = "MACD Chart") -> go.Figure:
        """Create MACD chart with price"""
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=("Price", "MACD"),
            row_heights=[0.7, 0.3]
        )
        
        # Price chart
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Close'],
            mode='lines',
            name='Close Price',
            line=dict(color='blue', width=2)
        ), row=1, col=1)
        
        # MACD line
        fig.add_trace(go.Scatter(
            x=df.index,
            y=macd_data['macd'],
            mode='lines',
            name='MACD',
            line=dict(color='blue', width=2)
        ), row=2, col=1)
        
        # Signal line
        fig.add_trace(go.Scatter(
            x=df.index,
            y=macd_data['macd_signal'],
            mode='lines',
            name='Signal',
            line=dict(color='red', width=2)
        ), row=2, col=1)
        
        # Histogram
        colors = ['green' if val >= 0 else 'red' for val in macd_data['macd_histogram']]
        fig.add_trace(go.Bar(
            x=df.index,
            y=macd_data['macd_histogram'],
            name='Histogram',
            marker_color=colors,
            opacity=0.7
        ), row=2, col=1)
        
        fig.update_layout(
            title=title,
            template="plotly_white",
            height=600,
            showlegend=True,
            hovermode='x unified'
        )
        
        return fig
    
    def create_bollinger_bands_chart(self, df: pd.DataFrame, bb_data: Dict[str, pd.Series], 
                                   title: str = "Bollinger Bands") -> go.Figure:
        """Create Bollinger Bands chart"""
        fig = go.Figure()
        
        # Price line
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Close'],
            mode='lines',
            name='Close Price',
            line=dict(color='blue', width=2)
        ))
        
        # Upper band
        fig.add_trace(go.Scatter(
            x=df.index,
            y=bb_data['bb_upper'],
            mode='lines',
            name='Upper Band',
            line=dict(color='red', width=1),
            fillcolor='rgba(255,0,0,0.1)',
            fill='tonexty'
        ))
        
        # Middle band (SMA)
        fig.add_trace(go.Scatter(
            x=df.index,
            y=bb_data['bb_middle'],
            mode='lines',
            name='Middle Band (SMA)',
            line=dict(color='orange', width=1, dash='dash')
        ))
        
        # Lower band
        fig.add_trace(go.Scatter(
            x=df.index,
            y=bb_data['bb_lower'],
            mode='lines',
            name='Lower Band',
            line=dict(color='green', width=1),
            fillcolor='rgba(0,255,0,0.1)',
            fill='tonexty'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Price",
            template="plotly_white",
            height=500,
            showlegend=True,
            hovermode='x unified'
        )
        
        return fig
    
    def create_volume_chart(self, df: pd.DataFrame, title: str = "Volume Analysis") -> go.Figure:
        """Create volume chart with price overlay"""
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Volume bars
        colors = ['green' if close >= open else 'red' 
                 for close, open in zip(df['Close'], df['Open'])]
        
        fig.add_trace(go.Bar(
            x=df.index,
            y=df['Volume'],
            name="Volume",
            marker_color=colors,
            opacity=0.7
        ), secondary_y=False)
        
        # Price line
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Close'],
            mode='lines',
            name='Close Price',
            line=dict(color='blue', width=2)
        ), secondary_y=True)
        
        # Update axes
        fig.update_xaxis(title_text="Date")
        fig.update_yaxis(title_text="Volume", secondary_y=False)
        fig.update_yaxis(title_text="Price", secondary_y=True)
        
        fig.update_layout(
            title=title,
            template="plotly_white",
            height=500,
            showlegend=True,
            hovermode='x unified'
        )
        
        return fig
