"""
Portfolio Analyzer
Provides portfolio analysis, risk metrics, and performance evaluation
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import scipy.optimize as sco
from scipy import stats


class PortfolioAnalyzer:
    """Portfolio analysis and optimization tools"""
    
    def __init__(self):
        self.risk_free_rate = 0.02  # Default 2% risk-free rate
        
    def calculate_returns(self, prices: pd.DataFrame) -> pd.DataFrame:
        """Calculate returns for multiple assets"""
        return prices.pct_change().dropna()
    
    def calculate_portfolio_metrics(self, returns: pd.DataFrame, weights: np.array) -> Dict[str, float]:
        """Calculate key portfolio metrics"""
        # Portfolio returns
        portfolio_returns = (returns * weights).sum(axis=1)
        
        # Annualized metrics
        annual_return = portfolio_returns.mean() * 252
        annual_volatility = portfolio_returns.std() * np.sqrt(252)
        sharpe_ratio = (annual_return - self.risk_free_rate) / annual_volatility
        
        # Downside metrics
        negative_returns = portfolio_returns[portfolio_returns < 0]
        downside_deviation = negative_returns.std() * np.sqrt(252)
        sortino_ratio = (annual_return - self.risk_free_rate) / downside_deviation if downside_deviation != 0 else 0
        
        # Maximum drawdown
        cumulative_returns = (1 + portfolio_returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Value at Risk (VaR)
        var_95 = np.percentile(portfolio_returns, 5)
        var_99 = np.percentile(portfolio_returns, 1)
        
        # Conditional Value at Risk (CVaR)
        cvar_95 = portfolio_returns[portfolio_returns <= var_95].mean()
        cvar_99 = portfolio_returns[portfolio_returns <= var_99].mean()
        
        return {
            'annual_return': annual_return,
            'annual_volatility': annual_volatility,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'var_95': var_95,
            'var_99': var_99,
            'cvar_95': cvar_95,
            'cvar_99': cvar_99,
            'calmar_ratio': annual_return / abs(max_drawdown) if max_drawdown != 0 else 0,
            'total_return': (1 + portfolio_returns).prod() - 1,
            'win_rate': (portfolio_returns > 0).mean(),
            'best_day': portfolio_returns.max(),
            'worst_day': portfolio_returns.min()
        }
    
    def optimize_portfolio(self, returns: pd.DataFrame, method: str = 'sharpe') -> Dict[str, Any]:
        """Optimize portfolio weights using different methods"""
        n_assets = len(returns.columns)
        
        # Constraints and bounds
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 1) for _ in range(n_assets))
        
        # Initial guess (equal weights)
        x0 = np.array([1/n_assets] * n_assets)
        
        if method == 'sharpe':
            # Maximize Sharpe ratio
            def objective(weights):
                metrics = self.calculate_portfolio_metrics(returns, weights)
                return -metrics['sharpe_ratio']  # Negative for minimization
                
        elif method == 'min_volatility':
            # Minimize volatility
            def objective(weights):
                portfolio_returns = (returns * weights).sum(axis=1)
                return portfolio_returns.std() * np.sqrt(252)
                
        elif method == 'max_return':
            # Maximize return
            def objective(weights):
                portfolio_returns = (returns * weights).sum(axis=1)
                return -portfolio_returns.mean() * 252  # Negative for minimization
        
        else:
            raise ValueError("Method must be 'sharpe', 'min_volatility', or 'max_return'")
        
        # Optimization
        result = sco.minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
        
        if result.success:
            optimal_weights = result.x
            optimal_metrics = self.calculate_portfolio_metrics(returns, optimal_weights)
            
            return {
                'weights': dict(zip(returns.columns, optimal_weights)),
                'metrics': optimal_metrics,
                'optimization_success': True
            }
        else:
            return {
                'weights': dict(zip(returns.columns, x0)),
                'metrics': self.calculate_portfolio_metrics(returns, x0),
                'optimization_success': False,
                'error': result.message
            }
    
    def efficient_frontier(self, returns: pd.DataFrame, num_portfolios: int = 100) -> pd.DataFrame:
        """Calculate efficient frontier"""
        n_assets = len(returns.columns)
        results = np.zeros((3, num_portfolios))
        
        # Target returns for efficient frontier
        min_ret = returns.mean().min() * 252
        max_ret = returns.mean().max() * 252
        target_returns = np.linspace(min_ret, max_ret, num_portfolios)
        
        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},  # Weights sum to 1
        ]
        bounds = tuple((0, 1) for _ in range(n_assets))
        
        for i, target in enumerate(target_returns):
            # Add return constraint
            cons = constraints + [{'type': 'eq', 'fun': lambda x, target=target: 
                                 (returns * x).sum(axis=1).mean() * 252 - target}]
            
            # Minimize volatility for target return
            def objective(weights):
                portfolio_returns = (returns * weights).sum(axis=1)
                return portfolio_returns.std() * np.sqrt(252)
            
            x0 = np.array([1/n_assets] * n_assets)
            result = sco.minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=cons)
            
            if result.success:
                portfolio_returns = (returns * result.x).sum(axis=1)
                results[0, i] = target  # Return
                results[1, i] = portfolio_returns.std() * np.sqrt(252)  # Volatility
                results[2, i] = (target - self.risk_free_rate) / results[1, i]  # Sharpe ratio
            else:
                results[:, i] = np.nan
        
        return pd.DataFrame({
            'Return': results[0],
            'Volatility': results[1],
            'Sharpe': results[2]
        }).dropna()
    
    def calculate_correlation_matrix(self, returns: pd.DataFrame) -> pd.DataFrame:
        """Calculate correlation matrix"""
        return returns.corr()
    
    def calculate_beta(self, asset_returns: pd.Series, market_returns: pd.Series) -> Dict[str, float]:
        """Calculate beta and alpha relative to market"""
        # Remove NaN values
        combined = pd.concat([asset_returns, market_returns], axis=1).dropna()
        if len(combined) < 10:
            return {'beta': np.nan, 'alpha': np.nan, 'r_squared': np.nan}
        
        asset_clean = combined.iloc[:, 0]
        market_clean = combined.iloc[:, 1]
        
        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(market_clean, asset_clean)
        
        return {
            'beta': slope,
            'alpha': intercept * 252,  # Annualized alpha
            'r_squared': r_value ** 2,
            'p_value': p_value
        }
    
    def monte_carlo_simulation(self, returns: pd.DataFrame, weights: np.array, 
                             days: int = 252, simulations: int = 1000) -> Dict[str, Any]:
        """Monte Carlo simulation for portfolio"""
        portfolio_returns = (returns * weights).sum(axis=1)
        
        mean_return = portfolio_returns.mean()
        std_return = portfolio_returns.std()
        
        # Simulate future returns
        simulated_returns = np.random.normal(mean_return, std_return, (days, simulations))
        
        # Calculate cumulative returns
        cumulative_returns = (1 + simulated_returns).cumprod(axis=0)
        
        # Final portfolio values (assuming initial value of 1)
        final_values = cumulative_returns[-1]
        
        return {
            'final_values': final_values,
            'mean_final_value': final_values.mean(),
            'std_final_value': final_values.std(),
            'percentile_5': np.percentile(final_values, 5),
            'percentile_95': np.percentile(final_values, 95),
            'probability_loss': (final_values < 1).mean(),
            'expected_return': final_values.mean() - 1,
            'worst_case': final_values.min(),
            'best_case': final_values.max(),
            'cumulative_paths': cumulative_returns
        }
    
    def risk_parity_weights(self, returns: pd.DataFrame) -> np.array:
        """Calculate risk parity weights"""
        # Covariance matrix
        cov_matrix = returns.cov() * 252  # Annualized
        
        n_assets = len(returns.columns)
        
        def calculate_risk_contrib(weights, cov_matrix):
            portfolio_var = np.dot(weights, np.dot(cov_matrix, weights))
            marginal_contrib = np.dot(cov_matrix, weights)
            contrib = np.multiply(marginal_contrib, weights.T) / portfolio_var
            return contrib
        
        def risk_budget_objective(weights, cov_matrix):
            weights = np.array(weights)
            sig_p = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
            risk_contrib = calculate_risk_contrib(weights, cov_matrix)
            target_contrib = np.ones(len(weights)) / len(weights)
            diffs = risk_contrib - target_contrib
            return np.sum(diffs**2)
        
        # Constraints and bounds
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0.01, 0.99) for _ in range(n_assets))  # Minimum 1% allocation
        
        # Initial guess
        x0 = np.array([1/n_assets] * n_assets)
        
        # Optimization
        result = sco.minimize(risk_budget_objective, x0, args=(cov_matrix,), 
                            method='SLSQP', bounds=bounds, constraints=constraints)
        
        return result.x if result.success else x0
    
    def calculate_information_ratio(self, portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> float:
        """Calculate Information Ratio"""
        excess_returns = portfolio_returns - benchmark_returns
        return excess_returns.mean() / excess_returns.std() * np.sqrt(252)
    
    def performance_attribution(self, portfolio_weights: Dict[str, float], 
                              asset_returns: Dict[str, float], 
                              benchmark_weights: Dict[str, float],
                              benchmark_returns: Dict[str, float]) -> Dict[str, float]:
        """Performance attribution analysis"""
        allocation_effect = 0
        selection_effect = 0
        interaction_effect = 0
        
        for asset in portfolio_weights.keys():
            if asset in benchmark_weights:
                weight_diff = portfolio_weights[asset] - benchmark_weights[asset]
                return_diff = asset_returns[asset] - benchmark_returns[asset]
                
                allocation_effect += weight_diff * benchmark_returns[asset]
                selection_effect += benchmark_weights[asset] * return_diff
                interaction_effect += weight_diff * return_diff
        
        return {
            'allocation_effect': allocation_effect,
            'selection_effect': selection_effect,
            'interaction_effect': interaction_effect,
            'total_active_return': allocation_effect + selection_effect + interaction_effect
        }
