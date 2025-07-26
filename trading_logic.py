"""
Trading Logic Module
"""
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime

from config import *
from data_fetcher import DataFetcher
from portfolio import Portfolio, PositionType

class TradingEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_fetcher = DataFetcher()
        self.portfolio = Portfolio()
    
    def scan_for_opportunities(self, tickers: List[str]) -> Tuple[List[str], List[str]]:
        """
        Scan stocks for trading opportunities
        Returns: (long_candidates, short_candidates)
        """
        self.logger.info(f"Scanning {len(tickers)} stocks for opportunities...")
        
        # Get stock data
        stock_data = self.data_fetcher.get_stock_data(tickers)
        
        long_candidates = []
        short_candidates = []
        
        for ticker in tickers:
            # Skip if we already have a position in this stock
            if ticker in self.portfolio.positions:
                continue
            
            if ticker not in stock_data:
                continue
            
            # Calculate price change over lookback period
            price_change = self.data_fetcher.calculate_price_change(
                stock_data[ticker], LOOKBACK_DAYS
            )
            
            if price_change is None:
                continue
            
            # Check for short opportunity (stock jumped 10%)
            if price_change >= SHORT_TRIGGER:
                short_candidates.append(ticker)
                self.logger.info(f"SHORT candidate: {ticker} (+{price_change:.2%})")
            
            # Check for long opportunity (stock dropped 5%)
            elif price_change <= BUY_TRIGGER:
                long_candidates.append(ticker)
                self.logger.info(f"LONG candidate: {ticker} ({price_change:.2%})")
        
        return long_candidates, short_candidates
    
    def execute_trades(self, long_candidates: List[str], short_candidates: List[str]):
        """Execute trades for the identified candidates"""
        
        # Execute long trades
        for ticker in long_candidates:
            if not self.portfolio.can_open_position():
                self.logger.info("Cannot open more positions - budget limit reached")
                break
            
            current_price = self.data_fetcher.get_current_price(ticker)
            if current_price:
                success = self.portfolio.open_long_position(ticker, current_price)
                if success:
                    self.logger.info(f"Executed LONG trade: {ticker} at ${current_price:.2f}")
        
        # Execute short trades  
        for ticker in short_candidates:
            if not self.portfolio.can_open_position():
                self.logger.info("Cannot open more positions - budget limit reached")
                break
            
            current_price = self.data_fetcher.get_current_price(ticker)
            if current_price:
                success = self.portfolio.open_short_position(ticker, current_price)
                if success:
                    self.logger.info(f"Executed SHORT trade: {ticker} at ${current_price:.2f}")
    
    def check_exit_conditions(self):
        """Check all open positions for exit conditions"""
        positions_to_close = []
        
        for ticker in self.portfolio.positions.keys():
            current_price = self.data_fetcher.get_current_price(ticker)
            if current_price:
                reason = self.portfolio.should_close_position(ticker, current_price)
                if reason:
                    positions_to_close.append((ticker, current_price, reason))
        
        # Close positions
        for ticker, price, reason in positions_to_close:
            success = self.portfolio.close_position(ticker, price, reason)
            if success:
                self.logger.info(f"Position closed: {ticker} - {reason}")
    
    def run_trading_cycle(self):
        """Run a complete trading cycle"""
        self.logger.info("=== Starting Trading Cycle ===")
        
        try:
            # Get list of companies to track
            tickers = self.data_fetcher.get_sp500_companies()
            
            # Check exit conditions for existing positions first
            self.check_exit_conditions()
            
            # Look for new opportunities
            long_candidates, short_candidates = self.scan_for_opportunities(tickers)
            
            # Execute trades
            self.execute_trades(long_candidates, short_candidates)
            
            # Save portfolio state
            self.portfolio.save_portfolio()
            
            # Log current status
            stats = self.portfolio.get_statistics()
            self.logger.info(f"Portfolio Status: Cash=${stats['cash']:.2f}, "
                           f"Positions={stats['active_positions']}, "
                           f"Total Trades={stats['total_trades']}, "
                           f"Win Rate={stats['win_rate']:.1%}")
            
            self.logger.info("=== Trading Cycle Complete ===")
            
        except Exception as e:
            self.logger.error(f"Error in trading cycle: {e}")
    
    def get_portfolio_summary(self) -> Dict:
        """Get detailed portfolio summary"""
        stats = self.portfolio.get_statistics()
        
        # Get current portfolio value
        current_prices = {}
        for ticker in self.portfolio.positions.keys():
            price = self.data_fetcher.get_current_price(ticker)
            if price:
                current_prices[ticker] = price
        
        portfolio_value = self.portfolio.get_portfolio_value(current_prices)
        total_return = (portfolio_value - INITIAL_BUDGET) / INITIAL_BUDGET
        
        summary = {
            'initial_budget': INITIAL_BUDGET,
            'current_value': portfolio_value,
            'total_return': total_return,
            'cash': stats['cash'],
            'active_positions': stats['active_positions'],
            'total_trades': stats['total_trades'],
            'profitable_trades': stats['profitable_trades'],
            'losing_trades': stats['losing_trades'],
            'win_rate': stats['win_rate'],
            'total_profit': stats['total_profit']
        }
        
        return summary 