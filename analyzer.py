"""
Performance Analysis Module
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import logging

from config import *
from database import TradingLogger

class PerformanceAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db_logger = TradingLogger()
    
    def analyze_performance(self) -> Dict:
        """Comprehensive performance analysis"""
        try:
            # Get performance history
            performance_data = self.db_logger.get_performance_history()
            
            if not performance_data:
                return {"error": "No performance data available"}
            
            df = pd.DataFrame(performance_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Calculate key metrics
            analysis = {
                'summary': self._calculate_summary_stats(df),
                'returns': self._calculate_returns(df),
                'drawdown': self._calculate_drawdown(df),
                'trading_stats': self._calculate_trading_stats(df),
                'daily_stats': self._calculate_daily_stats(df)
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in performance analysis: {e}")
            return {"error": str(e)}
    
    def _calculate_summary_stats(self, df: pd.DataFrame) -> Dict:
        """Calculate summary statistics"""
        if len(df) == 0:
            return {}
        
        latest = df.iloc[-1]
        initial_value = INITIAL_BUDGET
        
        return {
            'initial_value': initial_value,
            'current_value': latest['portfolio_value'],
            'total_return': latest['total_return'],
            'total_profit': latest['total_profit'],
            'days_trading': len(df),
            'current_cash': latest['cash'],
            'active_positions': latest['active_positions'],
            'total_trades': latest['total_trades'],
            'overall_win_rate': latest['win_rate']
        }
    
    def _calculate_returns(self, df: pd.DataFrame) -> Dict:
        """Calculate return-based metrics"""
        if len(df) < 2:
            return {}
        
        # Calculate daily returns
        df['daily_return'] = df['portfolio_value'].pct_change()
        returns = df['daily_return'].dropna()
        
        if len(returns) == 0:
            return {}
        
        # Annualized metrics (assuming 252 trading days)
        mean_return = returns.mean()
        std_return = returns.std()
        
        annualized_return = mean_return * 252
        annualized_volatility = std_return * np.sqrt(252)
        sharpe_ratio = annualized_return / annualized_volatility if annualized_volatility != 0 else 0
        
        return {
            'daily_mean_return': mean_return,
            'daily_volatility': std_return,
            'annualized_return': annualized_return,
            'annualized_volatility': annualized_volatility,
            'sharpe_ratio': sharpe_ratio,
            'best_day': returns.max(),
            'worst_day': returns.min(),
            'positive_days': (returns > 0).sum(),
            'negative_days': (returns < 0).sum()
        }
    
    def _calculate_drawdown(self, df: pd.DataFrame) -> Dict:
        """Calculate drawdown metrics"""
        if len(df) == 0:
            return {}
        
        # Calculate running maximum and drawdown
        df['running_max'] = df['portfolio_value'].expanding().max()
        df['drawdown'] = (df['portfolio_value'] - df['running_max']) / df['running_max']
        
        max_drawdown = df['drawdown'].min()
        
        # Find max drawdown period
        drawdown_start = None
        drawdown_end = None
        current_drawdown_start = None
        
        for i, row in df.iterrows():
            if row['drawdown'] == 0:  # New high
                if current_drawdown_start is not None:
                    # End of drawdown period
                    current_drawdown_start = None
            else:  # In drawdown
                if current_drawdown_start is None:
                    current_drawdown_start = i
                
                if row['drawdown'] == max_drawdown:
                    drawdown_start = current_drawdown_start
                    drawdown_end = i
        
        return {
            'max_drawdown': max_drawdown,
            'current_drawdown': df['drawdown'].iloc[-1],
            'drawdown_start': drawdown_start,
            'drawdown_end': drawdown_end
        }
    
    def _calculate_trading_stats(self, df: pd.DataFrame) -> Dict:
        """Calculate trading-specific statistics"""
        if len(df) == 0:
            return {}
        
        # Read trades data for more detailed analysis
        try:
            trades_df = pd.read_csv(TRADES_FILE)
            if len(trades_df) == 0:
                return {}
            
            trades_df['timestamp'] = pd.to_datetime(trades_df['timestamp'])
            
            # Separate profitable and losing trades
            profitable_trades = trades_df[trades_df['profit_loss'] > 0]
            losing_trades = trades_df[trades_df['profit_loss'] < 0]
            
            # Calculate averages
            avg_profit = profitable_trades['profit_loss'].mean() if len(profitable_trades) > 0 else 0
            avg_loss = losing_trades['profit_loss'].mean() if len(losing_trades) > 0 else 0
            
            # Profit factor
            total_profits = profitable_trades['profit_loss'].sum()
            total_losses = abs(losing_trades['profit_loss'].sum())
            profit_factor = total_profits / total_losses if total_losses != 0 else float('inf')
            
            return {
                'total_trades': len(trades_df),
                'profitable_trades': len(profitable_trades),
                'losing_trades': len(losing_trades),
                'win_rate': len(profitable_trades) / len(trades_df) if len(trades_df) > 0 else 0,
                'average_profit': avg_profit,
                'average_loss': avg_loss,
                'profit_factor': profit_factor,
                'largest_profit': profitable_trades['profit_loss'].max() if len(profitable_trades) > 0 else 0,
                'largest_loss': losing_trades['profit_loss'].min() if len(losing_trades) > 0 else 0
            }
            
        except FileNotFoundError:
            return {}
    
    def _calculate_daily_stats(self, df: pd.DataFrame) -> Dict:
        """Calculate daily trading statistics"""
        if len(df) < 7:
            return {}
        
        # Last 7 days performance
        recent_df = df.tail(7)
        week_return = (recent_df['portfolio_value'].iloc[-1] - recent_df['portfolio_value'].iloc[0]) / recent_df['portfolio_value'].iloc[0]
        
        # Last 30 days if available
        month_return = 0
        if len(df) >= 30:
            monthly_df = df.tail(30)
            month_return = (monthly_df['portfolio_value'].iloc[-1] - monthly_df['portfolio_value'].iloc[0]) / monthly_df['portfolio_value'].iloc[0]
        
        return {
            'week_return': week_return,
            'month_return': month_return,
            'avg_daily_trades': df['total_trades'].diff().mean() if len(df) > 1 else 0
        }
    
    def generate_report(self) -> str:
        """Generate a comprehensive text report"""
        analysis = self.analyze_performance()
        
        if 'error' in analysis:
            return f"Error generating report: {analysis['error']}"
        
        report = []
        report.append("=" * 60)
        report.append("TRADING SIMULATOR PERFORMANCE REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary
        if 'summary' in analysis:
            summary = analysis['summary']
            report.append("PORTFOLIO SUMMARY")
            report.append("-" * 20)
            report.append(f"Initial Value:    ${summary.get('initial_value', 0):,.2f}")
            report.append(f"Current Value:    ${summary.get('current_value', 0):,.2f}")
            report.append(f"Total Return:     {summary.get('total_return', 0):.2%}")
            report.append(f"Total P&L:        ${summary.get('total_profit', 0):,.2f}")
            report.append(f"Current Cash:     ${summary.get('current_cash', 0):,.2f}")
            report.append(f"Active Positions: {summary.get('active_positions', 0)}")
            report.append(f"Days Trading:     {summary.get('days_trading', 0)}")
            report.append("")
        
        # Returns
        if 'returns' in analysis:
            returns = analysis['returns']
            report.append("RETURN METRICS")
            report.append("-" * 15)
            report.append(f"Annualized Return:     {returns.get('annualized_return', 0):.2%}")
            report.append(f"Annualized Volatility: {returns.get('annualized_volatility', 0):.2%}")
            report.append(f"Sharpe Ratio:          {returns.get('sharpe_ratio', 0):.2f}")
            report.append(f"Best Day:              {returns.get('best_day', 0):.2%}")
            report.append(f"Worst Day:             {returns.get('worst_day', 0):.2%}")
            report.append("")
        
        # Drawdown
        if 'drawdown' in analysis:
            drawdown = analysis['drawdown']
            report.append("DRAWDOWN ANALYSIS")
            report.append("-" * 18)
            report.append(f"Max Drawdown:     {drawdown.get('max_drawdown', 0):.2%}")
            report.append(f"Current Drawdown: {drawdown.get('current_drawdown', 0):.2%}")
            report.append("")
        
        # Trading Stats
        if 'trading_stats' in analysis:
            trading = analysis['trading_stats']
            report.append("TRADING STATISTICS")
            report.append("-" * 19)
            report.append(f"Total Trades:     {trading.get('total_trades', 0)}")
            report.append(f"Win Rate:         {trading.get('win_rate', 0):.1%}")
            report.append(f"Profit Factor:    {trading.get('profit_factor', 0):.2f}")
            report.append(f"Avg Profit:       ${trading.get('average_profit', 0):.2f}")
            report.append(f"Avg Loss:         ${trading.get('average_loss', 0):.2f}")
            report.append(f"Largest Profit:   ${trading.get('largest_profit', 0):.2f}")
            report.append(f"Largest Loss:     ${trading.get('largest_loss', 0):.2f}")
            report.append("")
        
        return "\n".join(report)
    
    def plot_performance(self, save_path: str = None):
        """Create performance visualization plots"""
        try:
            performance_data = self.db_logger.get_performance_history()
            
            if not performance_data:
                self.logger.warning("No performance data to plot")
                return
            
            df = pd.DataFrame(performance_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Create subplots
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('Trading Simulator Performance Dashboard', fontsize=16)
            
            # Portfolio value over time
            ax1.plot(df['timestamp'], df['portfolio_value'], label='Portfolio Value', color='blue', linewidth=2)
            ax1.axhline(y=INITIAL_BUDGET, color='red', linestyle='--', alpha=0.7, label='Initial Value')
            ax1.set_title('Portfolio Value Over Time')
            ax1.set_ylabel('Value ($)')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Total return
            ax2.plot(df['timestamp'], df['total_return'] * 100, label='Total Return', color='green', linewidth=2) 
            ax2.axhline(y=0, color='red', linestyle='--', alpha=0.7)
            ax2.set_title('Total Return (%)')
            ax2.set_ylabel('Return (%)')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            # Active positions
            ax3.plot(df['timestamp'], df['active_positions'], label='Active Positions', color='orange', linewidth=2)
            ax3.set_title('Active Positions Over Time')
            ax3.set_ylabel('Number of Positions')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            
            # Win rate
            ax4.plot(df['timestamp'], df['win_rate'] * 100, label='Win Rate', color='purple', linewidth=2)
            ax4.set_title('Win Rate Over Time')
            ax4.set_ylabel('Win Rate (%)')
            ax4.legend()
            ax4.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                self.logger.info(f"Performance plot saved to {save_path}")
            else:
                plt.savefig(DATA_DIR / 'performance_dashboard.png', dpi=300, bbox_inches='tight')
                self.logger.info(f"Performance plot saved to {DATA_DIR / 'performance_dashboard.png'}")
            
            plt.close()
            
        except Exception as e:
            self.logger.error(f"Error creating performance plot: {e}") 