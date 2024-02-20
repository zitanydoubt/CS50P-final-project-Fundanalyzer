from statsmodels.regression.rolling import RollingOLS
import matplotlib.pyplot as plt
import statsmodels.api as sm
from fundanalyzer import Fundanalyzer
from fpdf import FPDF
import io


def main(args):
    fund = Fundanalyzer(**get_input(args.filename))
    create_pdf(fund)


class PDF(FPDF):

    def __init__(self, fund):
        super().__init__()
        self.fund = fund

    #print fund name as header
    def header(self):
        self.set_font("helvetica", "B", 20)
        self.cell(190, 10, self.fund.name, align="C")
        self.ln(90)

# creata data pdf
def create_pdf(fund):
    pdf = PDF(fund)
    pdf.add_page()
    pdf.image(save_fig(plot_return(fund)), 45, 35, 120)
    pdf.set_font("helvetica", "", 10)
    pdf.image(save_fig(regression(fund)), 20, 120, 250)
    pdf.add_page()
    pdf.image(save_fig(rolling_regression(fund)), 45, 35, 120)
    pdf.output(f"{fund.name}.pdf")

#save figure for plotting
def save_fig(figure):
    fig = io.BytesIO()
    figure.savefig(fig, format="png")
    return fig


def plot_return(fund):
    try:
        df = fund.data_df.iloc[-120:].copy() # limits data to last 10 years
    except IndexError: # in case of limited data
        pass
    finally:
        df["Growth"] = df["NAV"]/df["NAV"].iloc[0]
        fig, ax = plt.subplots()
        df["Growth"].plot(ax=ax)
        plt.title(f"Fund Return since {df.index[0]}", y=1, pad=14)
        plt.grid(axis="y", linestyle="--") #start line
        plt.axhline(y=1, color="k")
        plt.ylabel("Growth")
        plt.text(0.4, 0.05, s=cagr(df["Growth"]), transform=ax.transAxes)
        return fig


#merge fund data with fama data
def process_data(fund):
    df = fund.data_df.merge(fund.fama_data_df,
                                  how="inner",
                                  left_index=True,
                                  right_index=True)
    df = df[["return_USD", "Mkt-RF", "SMB", "HML", "RMW", "CMA", "WML", "RF"]]
    df["Fund-RF"] = df["return_USD"].pct_change() * 100 - df["RF"]
    df.dropna(subset = ["Fund-RF"], inplace=True)
    X = df[["Mkt-RF", "SMB", "HML", "RMW", "CMA", "WML"]]
    X = sm.add_constant(X)
    y = df["Fund-RF"]
    return y, X

#linear regression
def regression(fund):
    y, X = process_data(fund)
    model = sm.OLS(y, X).fit()
    fig, ax = plt.subplots(figsize=(16, 8))
    plt.text(0.01, 0.05, str(model.summary()), {"fontsize": 10}, fontproperties = "monospace")
    ax.axis("off")
    return fig

#rolling linear regression
def rolling_regression(fund):
    if len(fund.data_df) < fund.window:
        raise ValueError("Regression window too big for data")
    else:
        y, X = process_data(fund)
        results = RollingOLS(y, X, fund.window).fit().params
        results = results.rename(columns={"const": "alpha"})
        results = results.dropna()
        fig, ax = plt.subplots()
        results.plot(ax=ax)
        plt.title(f"{fund.window}-month rolling regression", y=1, pad=14)
        plt.grid(axis="y", linestyle="--")
        plt.axhline(y=0, color="k")
        plt.ylabel("Value")
        plt.legend(loc="upper left")
        return fig

#calculate commpound annual growth rate
def cagr(ds):
    time = (ds.index[-1]-ds.index[0]).n/12
    cagr = ((ds.iloc[-1]/ds.iloc[0]) ** ((1/time)) - 1) * 100
    return f"CAGR from {ds.index[0]} to {ds.index[-1]}: {cagr:.2f} %."

# get user input and filepath if provided as command line argument
def get_input(file):
    if file:
        cur = input("Currency denomination of the fund (supported: EUR, USD): ").upper().strip()
        loc = input("Region in which fund invests (supported: Unites States, Developed, Europe, Emerging): ").title().strip()
        win = input("Window for rolling regression (in months, defaults to 36): ").strip()
        return {"ticker": None, "currency": cur, "region": loc, "file":file, "window": win}
    else:
        tick = input("Yahoo-Ticker of fund: ")
        cur = input("Currency denomination of the fund (supported: EUR, USD): ").upper().strip()
        loc = input("Region in which fund invests (supported: Unites States, Developed, Europe, Emerging): ").title().strip()
        win = input("Window for rolling regression (in months, defaults to 36): ").strip()
        return {"ticker": tick, "currency": cur, "region": loc, "file": None, "window": win}



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Regression tool for funds")
    parser.add_argument("filename", help="filename for Excel file with MSCI data", nargs="?")
    args = parser.parse_args()
    main(args)
