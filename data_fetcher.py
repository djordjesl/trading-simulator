"""
Stock Data Fetcher Module
"""
import yfinance as yf
import pandas as pd
import requests
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import time

from config import *

class DataFetcher:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def get_sp500_companies(self) -> List[str]:
        """
        Get S&P 500 company tickers from Wikipedia
        """
        try:
            # Try to load from cache first
            if COMPANIES_FILE.exists():
                with open(COMPANIES_FILE, 'r') as f:
                    data = json.load(f)
                    if datetime.now().timestamp() - data['last_updated'] < 86400:  # 24 hours
                        return data['tickers']
            
            # Fetch from Wikipedia
            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            tables = pd.read_html(url)
            sp500_table = tables[0]
            tickers = sp500_table['Symbol'].tolist()
            
            # Clean tickers (remove dots, etc.)
            clean_tickers = []
            for ticker in tickers:
                # Replace dots with dashes (Yahoo Finance format)
                clean_ticker = ticker.replace('.', '-')
                clean_tickers.append(clean_ticker)
            
            # Limit to MAX_COMPANIES
            tickers = clean_tickers[:MAX_COMPANIES]
            
            # Cache the results
            cache_data = {
                'tickers': tickers,
                'last_updated': datetime.now().timestamp()
            }
            with open(COMPANIES_FILE, 'w') as f:
                json.dump(cache_data, f)
                
            self.logger.info(f"Loaded {len(tickers)} S&P 500 companies")
            return tickers
            
        except Exception as e:
            self.logger.error(f"Error fetching S&P 500 companies: {e}")
            # Fallback to extended S&P 500 list
            return self._get_fallback_sp500_list()
    
    def _get_fallback_sp500_list(self) -> List[str]:
        """
        Extended S&P 500 fallback list - top 100+ companies
        """
        return [
            # Technology
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'ADBE',
            'CSCO', 'AVGO', 'ORCL', 'INTC', 'QCOM', 'AMAT', 'TXN', 'IBM', 'KLAC', 'LRCX',
            'MRVL', 'FTNT', 'ANET', 'PANW', 'CDNS', 'SNPS', 'ADSK', 'INTU', 'CTSH', 'FISV',
            
            # Healthcare & Pharmaceuticals
            'JNJ', 'PFE', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR', 'BMY', 'AMGN', 'MDT',
            'GILD', 'CVS', 'UNH', 'ANTM', 'CI', 'HUM', 'BIIB', 'REGN', 'VRTX', 'ISRG',
            
            # Financial Services
            'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'AXP', 'BLK', 'SCHW', 'CB',
            'SPGI', 'ICE', 'CME', 'COF', 'TFC', 'USB', 'PNC', 'AON', 'MMC', 'AJG',
            
            # Consumer & Retail
            'WMT', 'HD', 'PG', 'KO', 'PEP', 'DIS', 'NKE', 'MCD', 'SBUX', 'TGT',
            'COST', 'LOW', 'CRM', 'TJX', 'BKNG', 'EL', 'MDLZ', 'GIS', 'K', 'HSY',
            
            # Industrial
            'GE', 'MMM', 'CAT', 'UPS', 'HON', 'RTX', 'LMT', 'BA', 'UNP', 'FDX',
            'DE', 'NSC', 'CSX', 'NOC', 'GD', 'EMR', 'ETN', 'PH', 'CMI', 'ITW',
            
            # Energy & Utilities
            'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'PSX', 'VLO', 'MPC', 'KMI', 'OKE',
            'NEE', 'SO', 'DUK', 'AEP', 'EXC', 'XEL', 'D', 'PCG', 'SRE', 'PEG',
            
            # Communication Services
            'T', 'VZ', 'CMCSA', 'CHTR', 'TMUS', 'DISH',
            
            # Materials & Chemicals
            'LIN', 'APD', 'ECL', 'DD', 'DOW', 'PPG', 'SHW', 'FCX', 'NEM', 'GOLD',
            
            # Real Estate & REITs
            'AMT', 'PLD', 'CCI', 'EQIX', 'PSA', 'WELL', 'DLR', 'O', 'SPG', 'AVB',
            
            # Consumer Staples
            'WMT', 'PG', 'KO', 'PEP', 'COST', 'CL', 'KHC', 'GIS', 'K', 'CAG'
        ]
    
    def get_stock_data(self, tickers: List[str], period: str = "1mo") -> Dict[str, pd.DataFrame]:
        """
        Fetch stock data for multiple tickers
        """
        stock_data = {}
        
        # Process in batches to avoid overwhelming the API
        for i in range(0, len(tickers), BATCH_SIZE):
            batch = tickers[i:i+BATCH_SIZE]
            batch_str = ' '.join(batch)
            
            try:
                self.logger.info(f"Fetching data for batch {i//BATCH_SIZE + 1}/{(len(tickers)-1)//BATCH_SIZE + 1}")
                
                # Fetch data for the batch
                data = yf.download(batch_str, period=period, group_by='ticker', 
                                 timeout=YFINANCE_TIMEOUT, progress=False)
                
                # Process each ticker in the batch
                for ticker in batch:
                    try:
                        if len(batch) == 1:
                            ticker_data = data
                        else:
                            ticker_data = data[ticker] if ticker in data.columns.levels[0] else None
                        
                        if ticker_data is not None and not ticker_data.empty:
                            # Clean the data
                            ticker_data = ticker_data.dropna()
                            if len(ticker_data) > 0:
                                stock_data[ticker] = ticker_data
                        
                    except Exception as e:
                        self.logger.warning(f"Error processing {ticker}: {e}")
                        continue
                
                # Rate limiting
                time.sleep(0.5)  # Wait 0.5 seconds between batches
                
            except Exception as e:
                self.logger.error(f"Error fetching batch {batch}: {e}")
                continue
        
        self.logger.info(f"Successfully fetched data for {len(stock_data)} stocks")
        return stock_data
    
    def calculate_price_change(self, data: pd.DataFrame, days: int = LOOKBACK_DAYS) -> Optional[float]:
        """
        Calculate percentage price change over specified days
        """
        try:
            if len(data) < days + 1:
                return None
            
            current_price = data['Close'].iloc[-1]
            past_price = data['Close'].iloc[-(days + 1)]
            
            change = (current_price - past_price) / past_price
            return change
            
        except Exception as e:
            self.logger.warning(f"Error calculating price change: {e}")
            return None
    
    def get_current_price(self, ticker: str) -> Optional[float]:
        """
        Get current price for a single ticker
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.history(period="1d", timeout=YFINANCE_TIMEOUT)
            if not info.empty:
                return info['Close'].iloc[-1]
            return None
        except Exception as e:
            self.logger.warning(f"Error getting current price for {ticker}: {e}")
            return None 