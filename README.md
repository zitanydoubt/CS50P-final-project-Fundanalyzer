# Fama-French-fund analyzer
#### Description:


##### What does the programm do
The programm runs a regression of the return of a fund on the Fama-French-5-factor model (plus momentum). The user is prompted to put in the yahoo finance ticker of the fund, its currency denomination, the region of the world it invests in and a time window for rolling regressions that show how the contributions of the factors change over time. Instead of providing the ticker there is also the possibility to provide a file path in the command-line to upload excel files with return data of indices or funds as most index returns are not readily available. The ouput is an pdf file that depicts the fund return over maximum the last ten years, calculates the compound annual growth rate (CAGR) over that time horizon, displays the regression results over the whole time frame of the available data and plots the results of the rolling regression to see how the contribution of these factors varied over time.

##### Background information
The evidence behind factor investing states that there exist (risk) factors that explain portfolio returns beyond the mere market risk. The main model is the 5-factor-model by Kenneth French and Nobel laureate Eugene Fama: the market risk (Mkt),  size (SMB), value (HML), profitability (RMW) and investment (CMA) explain most of the investment outcomes - and can be exploited to achieve better returns. I added one more factor to this model, the momentum factor (WML): stocks that go up continue to go up (for some time) and stocks that go down continue to do so (for some time) as investors might overreact to good and bad news - or underreact for that matter. The [Kenneth French data library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html) publishes the returns of each of these factors. Regressing the fund return on these factors reveals their contribution to the fund return. What the factors can't explain is called alpha (the intercept of the regression analysis).
