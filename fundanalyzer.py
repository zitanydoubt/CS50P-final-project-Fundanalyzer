import yfinance as yf
import pandas_datareader.data as web
from datetime import datetime
import pandas as pd
import warnings

"""
Fundanalyzer class loads return data from yahoo finance (ticker) or from from excel file (file) into self.data_df, converts it into USD if necessary (currency, from EUR only so far)
and loads Fama French 6-Factor data from Ken-French-library depending on the region into self.fama_data_df

"""

class Fundanalyzer:

    def __init__(self, currency, region, window, ticker=None, file=None):
        self.start = datetime(1990, 1, 1) #reference time frame, data does not go further back than this usually
        self.end = datetime.now()
        self.ticker = ticker
        self.file = file
        self.currency = currency
        self.region = region
        self.window = window # time window for rolling regression
        self.name = self.get_name()
        self.fama_data_df = self.fetch_fama_data() #needs to be called before get_data as get_data overrides pandas datareader
        self.data_df = self.get_fund_data()




    @property
    def ticker(self):
        return self._ticker
    @ticker.setter
    def ticker(self, ticker):
        if ticker:
            try:
                yf.Ticker(ticker).info
            except:
                raise ValueError("Invalid ticker")
        self._ticker = ticker

    @property
    def file(self):
        return self._file

    @file.setter
    def file(self, file):
        if file:
            if "xls" in file:
                self._file = file
            else:
                raise ValueError("Invalid format, only Excel files supported")
    @property
    def region(self):
        return self._region

    @region.setter
    def region(self, region):
        if region not in ["United States", "Developed", "Europe", "Emerging"]:
            raise ValueError("Invalid Region")
        else:
            self._region = region

    @property
    def currency(self):
        return self._currency

    @currency.setter
    def currency(self, currency):
        if currency not in ["USD", "EUR"]:
            raise ValueError("Invalid currency")
        else:
            self._currency = currency

    @property
    def window(self):
        return self._window

    @window.setter
    def window(self, window):
        if window:
            try:
                window = int(window)
            except ValueError:
                raise ValueError("Window must be an integer")
            else:
                self._window = window
        else:
            self._window = 36

    # get fund name frome file or yahoo finance
    def get_name(self):
        if self.ticker:
            self.name = yf.Ticker(self.ticker).info["longName"]
            return self.name
        elif self.file:
            self.name = pd.read_excel(self.file, index_col=[0]).columns[0]
            return self.name
    # get fund data from file or yahoo finance
    def get_fund_data(self):
        if self.ticker:
            df = self.fetch_yahoo_data(self.ticker)
            df = df[["NAV"]]
        elif self.file:
            df = self.read_excel()
            df = df[["NAV"]]
        df = self.convert_currency(df)
        df = df[["NAV", "EUR_USD", "return_USD"]]
        self.data_df = df
        return self.data_df

    def fetch_yahoo_data(self, ticker):
        yf.pdr_override() #necessary to override pandas datareader with yfinance
        ds = web.get_data_yahoo(ticker, start=self.start, end=self.end)["Adj Close"] #loads end of day NAV data for ticker adjusted for dividends and capital gains (only relevant for US funds)
        df = ds.to_frame("NAV")
        df = df.resample("M").last()
        df.index = df.index.to_period("M")
        df = df[:-1] #drop current month as any day of the current month would be set as the end of the month value
        return df


    def read_excel(self):
        df = pd.read_excel(self.file, index_col=[0])
        df.iloc[:, 0] = pd.to_numeric(df.iloc[:, 0])
        df = df.rename(columns={df.columns[0]: "NAV" })
        df.index = df.index.to_period("M")
        df = df.dropna()
        return df

    def convert_currency(self, df):
        df_eur = self.fetch_yahoo_data("EURUSD=X") # get eur usd exchange rate
        df_eur = df_eur.rename(columns={"NAV": "EUR_USD"})
        df_eur = df_eur[["EUR_USD"]]
        df_merged = df.merge(df_eur,
                              how="left",
                              left_index=True,
                              right_index=True) #left merge with return data to preserve usd data that can go farther back than EURUSD exchange rate that started in 2003
        df_merged = df_merged[["NAV", "EUR_USD"]]
        if self.currency == "EUR":
            df_merged["return_USD"] = df_merged["NAV"] * df_merged["EUR_USD"]
        else:
            df_merged["return_USD"] = df_merged["NAV"]
        return df_merged


    def fetch_fama_data(self):
        warnings.simplefilter(action="ignore", category=(FutureWarning, DeprecationWarning)) #https://github.com/pydata/pandas-datareader/issues/972
        datasets = { # names of datasets in library
            "United States": ["F-F_Research_Data_5_Factors_2x3", "F-F_Momentum_Factor"],
            "Developed": ["Developed_5_Factors", "Developed_Mom_Factor"],
            "Europe": ["Europe_5_Factors", "Europe_Mom_Factor"],
            "Emerging": ["Emerging_5_Factors", "Emerging_MOM_Factor"]
        }
        df_ff5  = web.DataReader(datasets[self.region][0], "famafrench", start=self.start, end=self.end) # Fama French 5 Factor data
        df_mom = web.DataReader(datasets[self.region][1], "famafrench", start=self.start, end=self.end) # Fama French Momentum Factor data
        if self.region == "United States":
            df_mom[0] = df_mom[0].rename(columns={"Mom   ": "WML"}) # WML in US data is called Mom with three whitespaces wtf
        df_ff6 = df_ff5[0].merge(df_mom[0],
                                 how="inner",
                                 left_index=True,
                                 right_index=True)
        df_ff6 = df_ff6[["Mkt-RF", "SMB", "HML", "RMW", "CMA", "RF", "WML"]]
        self.fama_data_df = df_ff6
        return self.fama_data_df
