import yfinance as yf
import pandas as pd
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator, ROCIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator
from datetime import datetime
import os


def download_etf_data(tickers, start_date="2010-01-01", end_date=None):
    if end_date is None:
        end_date = "2024-05-01"
    etf_data = {}
    for ticker in tickers:
        df = yf.download(ticker, start=start_date, end=end_date)
        df['Ticker'] = ticker
        etf_data[ticker] = df
    return etf_data


def extract_technical_indicators(etf_data):
    indicator_data = {}
    for ticker, df in etf_data.items():        
        df_ind = df.copy()
        
        # Flatten MultiIndex columns
        if isinstance(df_ind.columns, pd.MultiIndex):
            df_ind.columns = [col[0] for col in df_ind.columns.values]
        
        # Convert required columns to numeric
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_columns:
            if col not in df_ind.columns:
                raise ValueError(f"Missing required column: {col}")
            df_ind[col] = pd.to_numeric(df_ind[col], errors='coerce')
        
        # Clean data
        df_ind = df_ind.dropna(subset=required_columns)
        if not isinstance(df_ind.index, pd.DatetimeIndex):
            df_ind.index = pd.to_datetime(df_ind.index)
        df_ind = df_ind.reset_index()
        
        # Calculate specific technical indicators
        # Trend indicators
        df_ind['SMA_20'] = SMAIndicator(close=df_ind['Close'], window=20).sma_indicator()
        df_ind['EMA_20'] = EMAIndicator(close=df_ind['Close'], window=20).ema_indicator()
        
        # MACD
        macd = MACD(close=df_ind['Close'])
        df_ind['MACD'] = macd.macd()
        df_ind['MACD_Signal'] = macd.macd_signal()
        df_ind['MACD_Hist'] = macd.macd_diff()
        
        # Momentum indicators
        df_ind['RSI'] = RSIIndicator(close=df_ind['Close']).rsi()
        df_ind['ROC'] = ROCIndicator(close=df_ind['Close']).roc()
        
        # Volatility indicators
        bb = BollingerBands(close=df_ind['Close'])
        df_ind['BB_Width'] = bb.bollinger_wband()
        df_ind['ATR'] = AverageTrueRange(
            high=df_ind['High'],
            low=df_ind['Low'],
            close=df_ind['Close']
        ).average_true_range()
        
        # Volume indicators
        df_ind['OBV'] = OnBalanceVolumeIndicator(
            close=df_ind['Close'],
            volume=df_ind['Volume']
        ).on_balance_volume()
        
        # Set date as index
        df_ind = df_ind.set_index('Date')
        indicator_data[ticker] = df_ind
        print(f"Processed {ticker}")
            
    return indicator_data


def flatten_columns(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns.values]
    return df


def save_etf_data(etf_data, output_dir="raw"):
    os.makedirs(output_dir, exist_ok=True)
    for ticker, df in etf_data.items():
        df = flatten_columns(df)
        file_path = os.path.join(output_dir, f"{ticker}_data.csv")
        df.to_csv(file_path)
        print(f"Saved {ticker} data")


def save_technical_indicators(indicator_data, output_dir="indicators"):
    os.makedirs(output_dir, exist_ok=True)
    for ticker, df in indicator_data.items():
        # Select only the technical indicators we want to save
        indicator_columns = [
            'SMA_20', 'EMA_20', 'MACD', 'MACD_Signal', 'MACD_Hist',
            'RSI', 'ROC', 'BB_Width', 'ATR', 'OBV'
        ]
        df = df[['Close'] + indicator_columns]
        df = flatten_columns(df)
        file_path = os.path.join(output_dir, f"{ticker}_indicators.csv")
        df.to_csv(file_path)
        print(f"Saved {ticker} indicators")


if __name__ == "__main__":
    tickers = ["SPY", "QQQ", "IWM", "EFA", "VWO", "VNQ", "TLT"]    
    etf_data = download_etf_data(tickers)
    tech_indicators = extract_technical_indicators(etf_data)
    
    save_etf_data(etf_data)
    save_technical_indicators(tech_indicators)
