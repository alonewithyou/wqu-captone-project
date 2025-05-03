import yfinance as yf
import pandas as pd
import numpy as np
from ta import add_all_ta_features
from datetime import datetime
import os


# 1. Download historical ETF data
def download_etf_data(tickers, start_date="2010-01-01", end_date=None):
    if end_date is None:
        end_date = datetime.today().strftime('%Y-%m-%d')
    etf_data = {}
    for ticker in tickers:
        df = yf.download(ticker, start=start_date, end=end_date)
        df['Ticker'] = ticker
        etf_data[ticker] = df
    return etf_data

# 2. Extract technical indicators for each ETF
def extract_technical_indicators(etf_data):
    indicator_data = {}
    for ticker, df in etf_data.items():
        try:
            # Create a copy of the dataframe
            df_ind = df.copy()
            
            # Ensure all required columns are present and numeric
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            for col in required_columns:
                if col not in df_ind.columns:
                    raise ValueError(f"Missing required column: {col}")
                df_ind[col] = pd.to_numeric(df_ind[col], errors='coerce')
            
            # Drop any rows with NaN values in required columns
            df_ind = df_ind.dropna(subset=required_columns)
            
            # Calculate technical indicators
            df_ind = add_all_ta_features(
                df_ind,
                open="Open",
                high="High",
                low="Low",
                close="Close",
                volume="Volume",
                fillna=True
            )
            
            indicator_data[ticker] = df_ind
            print(f"Successfully calculated technical indicators for {ticker}")
            
        except Exception as e:
            print(f"Error processing {ticker}: {str(e)}")
            continue
            
    return indicator_data

# 3. Download macroeconomic indicators from FRED (mocked as placeholder for now)
def get_macro_indicators():
    try:
        # Download VIX data
        vix_data = yf.download("^VIX", start="2010-01-01", end="2024-05-01")
        if 'Close' not in vix_data.columns:
            raise ValueError("VIX data does not contain 'Close' price")
        
        # Download Treasury data
        treasury_data = yf.download("^TNX", start="2010-01-01", end="2024-05-01")
        if 'Close' not in treasury_data.columns:
            raise ValueError("Treasury data does not contain 'Close' price")
        
        macro_data = {
            "VIX": vix_data['Close'],
            "10Y_Treasury": treasury_data['Close'],
            "EPU": pd.Series(dtype=float),  # Placeholder: real source is not yfinance
            "Unemployment_Rate": pd.Series(dtype=float),  # Placeholder: would need FRED API or manually downloaded data
        }
        return pd.DataFrame(macro_data)
    except Exception as e:
        print(f"Error downloading macro indicators: {str(e)}")
        return pd.DataFrame()

# Helper function to flatten MultiIndex columns
def flatten_columns(df):
    if isinstance(df.columns, pd.MultiIndex):
        # Flatten the MultiIndex columns
        df.columns = ['_'.join(col).strip() for col in df.columns.values]
    return df

# 4. Save ETF data to CSV files
def save_etf_data(etf_data, output_dir="data/raw"):
    os.makedirs(output_dir, exist_ok=True)
    for ticker, df in etf_data.items():
        # Flatten the columns before saving
        df = flatten_columns(df)
        file_path = os.path.join(output_dir, f"{ticker}_data.csv")
        df.to_csv(file_path)
        print(f"Saved {ticker} data to {file_path}")

# 5. Save technical indicators to CSV files
def save_technical_indicators(indicator_data, output_dir="data/indicators"):
    os.makedirs(output_dir, exist_ok=True)
    for ticker, df in indicator_data.items():
        # Flatten the columns before saving
        df = flatten_columns(df)
        file_path = os.path.join(output_dir, f"{ticker}_indicators.csv")
        df.to_csv(file_path)
        print(f"Saved {ticker} technical indicators to {file_path}")

# 6. Save macroeconomic indicators to CSV
def save_macro_indicators(macro_data, output_dir="data/macro"):
    os.makedirs(output_dir, exist_ok=True)
    # Flatten the columns before saving
    macro_data = flatten_columns(macro_data)
    file_path = os.path.join(output_dir, "macro_indicators.csv")
    macro_data.to_csv(file_path)
    print(f"Saved macroeconomic indicators to {file_path}")


if __name__ == "__main__":
    tickers = ["SPY", "QQQ", "IWM", "EFA", "VWO", "VNQ", "TLT"]
    etf_data = download_etf_data(tickers)
    tech_indicators = extract_technical_indicators(etf_data)
    macro_indicators = get_macro_indicators()
    
    # Save all data to CSV files
    save_etf_data(etf_data)
    save_technical_indicators(tech_indicators)
    save_macro_indicators(macro_indicators) 