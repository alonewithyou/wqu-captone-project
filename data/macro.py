import yfinance as yf
import pandas as pd
import os
from datetime import datetime
import pandas_datareader.data as web


def get_vix_data(start_date="2010-01-01", end_date="2025-05-01"):
    vix_data = yf.download("^VIX", start=start_date, end=end_date)
    vix_series = pd.Series(vix_data['Close'].squeeze(), index=vix_data.index, name='VIX')
    return vix_series.dropna()


def get_epu_data(start_date="2010-01-01", end_date="2025-05-01"):
    epu_file = "macro/Global_Policy_Uncertainty_Data.csv"
    epu_df = pd.read_csv(epu_file)
    epu_df['Date'] = pd.to_datetime(epu_df[['Year', 'Month']].assign(DAY=1))
    epu_df.set_index('Date', inplace=True)
    epu_series = pd.Series(epu_df['GEPU_current'].values, index=epu_df.index, name='GEPU')
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    return epu_series[start_date:end_date].dropna()


def get_skew_data(start_date="2010-01-01", end_date="2025-05-01"):
    skew_file = "macro/SKEW_History.csv"
    skew_df = pd.read_csv(skew_file)
    skew_df['DATE'] = pd.to_datetime(skew_df['DATE'])
    skew_df.set_index('DATE', inplace=True)
    skew_series = pd.Series(skew_df['SKEW'].values, index=skew_df.index, name='SKEW')
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    return skew_series[start_date:end_date].dropna()


def get_dtb3_data(start_date="2010-01-01", end_date="2025-05-01"):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    dtb3_series = web.DataReader('DTB3', 'fred', start_date, end_date)
    return pd.Series(dtb3_series['DTB3'].values, index=dtb3_series.index, name='DTB3')


def get_gs10_data(start_date="2010-01-01", end_date="2025-05-01"):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    gs10_series = web.DataReader('GS10', 'fred', start_date, end_date)
    return pd.Series(gs10_series['GS10'].values, index=gs10_series.index, name='GS10')


def get_hy_spread_data(start_date="2010-01-01", end_date="2025-05-01"):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    hy_series = web.DataReader('BAMLH0A0HYM2', 'fred', start_date, end_date)
    return pd.Series(hy_series['BAMLH0A0HYM2'].values, index=hy_series.index, name='HY_SPREAD')


def get_indpro_data(start_date="2010-01-01", end_date="2025-05-01"):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    indpro_series = web.DataReader('INDPRO', 'fred', start_date, end_date)
    return pd.Series(indpro_series['INDPRO'].values, index=indpro_series.index, name='INDPRO')


def get_cpi_data(start_date="2010-01-01", end_date="2025-05-01"):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    cpi_series = web.DataReader('CPIAUCSL', 'fred', start_date, end_date)
    return pd.Series(cpi_series['CPIAUCSL'].values, index=cpi_series.index, name='CPI')


def get_unrate_data(start_date="2010-01-01", end_date="2025-05-01"):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    unrate_series = web.DataReader('UNRATE', 'fred', start_date, end_date)
    return pd.Series(unrate_series['UNRATE'].values, index=unrate_series.index, name='UNRATE')


def combine_macro_data(vix_data, epu_data, skew_data, dtb3_data, gs10_data, hy_spread_data, indpro_data, cpi_data, unrate_data):    
    trading_days = vix_data.index

    def to_trading_daily(series):    
        full_daily_index = pd.date_range(start=series.index.min(), end=series.index.max(), freq='D')
        daily_filled = series.reindex(full_daily_index).ffill()
        return daily_filled.reindex(trading_days).ffill()

    macro_df = pd.DataFrame(index=trading_days)
    macro_df['VIX'] = vix_data
    macro_df['SKEW'] = skew_data.reindex(trading_days).ffill()
    macro_df['GEPU'] = to_trading_daily(epu_data)
    macro_df['DTB3'] = to_trading_daily(dtb3_data)
    macro_df['GS10'] = to_trading_daily(gs10_data)
    macro_df['HY_SPREAD'] = to_trading_daily(hy_spread_data)
    macro_df['INDPRO'] = to_trading_daily(indpro_data)
    macro_df['CPI'] = to_trading_daily(cpi_data)
    macro_df['UNRATE'] = to_trading_daily(unrate_data)

    return macro_df


def save_macro_data(macro_df, output_dir="macro"):
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, "macro_indicators.csv")
    macro_df.to_csv(file_path)
    print(f"Saved macroeconomic indicators to {file_path}")


if __name__ == "__main__":
    vix_data = get_vix_data()
    epu_data = get_epu_data()
    skew_data = get_skew_data()
    dtb3_data = get_dtb3_data()
    gs10_data = get_gs10_data()
    hy_spread_data = get_hy_spread_data()
    indpro_data = get_indpro_data()
    cpi_data = get_cpi_data()
    unrate_data = get_unrate_data()
    
    macro_df = combine_macro_data(vix_data, epu_data, skew_data, dtb3_data, gs10_data, 
                                hy_spread_data, indpro_data, cpi_data, unrate_data)
    save_macro_data(macro_df)
