from project import (get_input, process_data, cagr)
from fundanalyzer import Fundanalyzer
import pytest
import pandas as pd


@pytest.fixture
def sample_fund():
    return FundAnalyzer(ticker="AVUV", region="United States", currency="USD", window=36)


def test_process_data(sample_fund):
    y, X = process_data(sample_fund)

    assert type(y) == pd.Series
    assert type(X) == pd.DataFrame
    assert not y.isnull().any()
    assert not X.isnull().any().any()
    assert "Fund-RF" in y.name
    for name in ["Mkt-RF", "SMB", "HML", "RMW", "CMA", "WML"]:
        assert name in X.columns


@pytest.fixture
def sample_series():
    date = pd.period_range(start="2000-01", end="2023-12", freq="M")
    data = [100 * (1.1**(1/12))**i for i in range(len(date))]
    return pd.Series(data, index=date)

def test_cagr(sample_series):
    assert cagr(sample_series) == "CAGR from 2000-01 to 2023-12: 10.00 %."


def test_get_input(monkeypatch):
    inputs = iter(["AVUV", "USD", "United States", "36"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    result = get_input(None)
    assert result == {"ticker": "AVUV", "currency": "USD", "region": "United States", "file": None, "window": "36"}
    inputs2 = iter(["USD", "United States", "36"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs2))
    result2 = get_input("file.xls")
    assert result2 == {"ticker": None, "currency": "USD", "region": "United States", "file": "file.xls", "window": "36"}
