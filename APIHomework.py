#!/usr/bin/env python
# coding: utf-8

# ## Financial Planning

# In[45]:


# Initial imports
import os
import requests
import pandas as pd
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
from MCForecastTools import MCSimulation

get_ipython().run_line_magic('matplotlib', 'inline')


# In[46]:


# Load .env enviroment variables
load_dotenv()


# In[41]:


# Current amount of crypto assets
my_btc = 1.2
my_eth = 5.3


# ### Personal Finance Planner
# 
# #### Collect Crypto Prices Using the requests Library

# In[32]:


# Crypto API URLs
btc_url = "https://api.alternative.me/v2/ticker/Bitcoin/?convert=USD"
eth_url = "https://api.alternative.me/v2/ticker/Ethereum/?convert=USD"


# In[14]:


# Fetch current BTC price
response_btc_data = requests.get(btc_url).json()
# Fetch current ETH price
response_eth_data = requests.get(eth_url).json()


# In[15]:


# Compute current value of my BTC
my_btc_value = response_btc_data['data']['1']['quotes']['USD']['price']
my_btc_value


# In[16]:


# Compute current value of my ETH
my_eth_value = response_eth_data['data']['1027']['quotes']['USD']['price']
my_eth_value


# In[17]:


#Make it look nice by Printing
print(f"The current value of my {my_btc} BTC is ${my_btc_value:0.2f}")
print(f"The current value of my {my_eth} ETH is ${my_eth_value:0.2f}")


# ### Collect Investments Data Using Alpaca: SPY(Stocks) and AGG(bonds)

# In[18]:


#Current Shares
my_agg = 200
my_spy = 50


# In[47]:


# Set Alpaca API key and secret
alpaca_api_key = os.getenv("API_KEY")
alpaca_secret_key = os.getenv("SECRET_KEY")

# Create the Alpaca API object
alpaca = tradeapi.REST(
    alpaca_api_key,
    alpaca_secret_key,
    api_version="v2")


# In[52]:


# Format current date as ISO format
today = pd.Timestamp("2021-5-14", tz="America/New_York").isoformat()

# Set the tickers
tickers = ["AGG", "SPY"]

# Set timeframe to '1D' for Alpaca API
timeframe = "1D"

# Get current closing prices for SPY and AGG
df_portfolio = alpaca.get_barset(
    tickers,
    timeframe,
    start = today,
    end = today
).df


# Pick AGG and SPY close prices
agg_close_price = float(df_portfolio["AGG"]["close"])
spy_close_price = float(df_portfolio["SPY"]["close"])

# Print AGG and SPY close prices
print(f"Current AGG closing price: ${agg_close_price}")
print(f"Current SPY closing price: ${spy_close_price}")


# In[53]:


df_portfolio.head()


# In[56]:


# Compute the current value of shares
my_agg_value = agg_close_price * my_agg
my_spy_value = spy_close_price * my_spy

# Print current value of share
print(f"The current value of my {my_spy} SPY shares is ${my_spy_value:0.2f}")
print(f"The current value of my {my_agg} AGG shares is ${my_agg_value:0.2f}")


# ### Saving Health Analysis

# In[54]:


#Monthly Household income 
monthly_income = 12000


# In[65]:


#Create Savings Dataframe

my_crypto = my_btc_value + my_eth_value
my_shares = my_spy_value + my_agg_value

value_data = {
    "Amount in USD": {
       "Cryptocurrency": my_crypto,
       "Shares & Bonds": my_shares
    }
}

df_savings = pd.DataFrame(value_data)
df_savings
# Display savings DataFrame
display(df_savings)


# In[66]:


#Savings Pie Chart

df_savings.plot.pie(y="Amount in USD", title= "Personal Savings Distribution/Composition")


# In[68]:


# Set ideal emergency fund
rainy_day_fund = monthly_income * 3

# Calculate total amount of savings
my_savings = my_crypto + my_shares

# Validate saving health
if (my_savings > rainy_day_fund):
    print("You are flush with cash! You have enough money for not only a rainy day, but a flood!")
elif (my_savings == rainy_day_fund):
    print("You have reached your goal for saving for a rainy day! Now save more!")
else:
    diff = rainy_day_fund - my_savings
    print(f"You are ${diff} away from reaching your goal of even having an umbrella, try to hold off on the avocado toast.")


# ### Part 2-Retirement Planning
# 
# #### Monte Carlo Simulation

# In[72]:


# Set start and end dates of five years back from today.
# Sample results may vary from the solution based on the time frame chosen
start_date = pd.Timestamp('2016-05-14', tz='America/New_York').isoformat()
end_date = pd.Timestamp('2021-05-14', tz='America/New_York').isoformat()


# In[73]:


# Get 5 years' worth of historical data for SPY and AGG
df_stock_data = alpaca.get_barset(
    tickers,
    timeframe,
    start=start_date,
    end=end_date
).df

# Display sample data
df_stock_data.head()


# In[74]:


# Configuring a Monte Carlo simulation to forecast 30 years cumulative returns
MC_dist = MCSimulation(
    portfolio_data = df_stock_data,
    weights = [.4,.6],
    num_simulation = 500,
    num_trading_days = 252*30
)


# Print the simulation input data
MC_dist.portfolio_data.head()


# In[75]:


# Running a Monte Carlo simulation to forecast 30 years cumulative returns
MC_dist.calc_cumulative_return()


# In[76]:


# Plot simulation outcomes
MC_dist.plot_simulation()


# In[77]:


# Plot probability distribution and confidence intervals
MC_dist.plot_distribution()


# #### Retirement Analysis

# In[78]:


# Fetch summary statistics from the Monte Carlo simulation results
summary = MC_dist.summarize_cumulative_return()

# Print summary statistics
print(summary)


# #### Calculate expected portfolio return at the 95% Lower/Upper Confidence intervals based on a 20,000 USD initial Investment

# In[80]:


# Set initial investment
initial_investment = 20000

# Use the lower and upper `95%` confidence intervals to calculate the range of the possible outcomes of our $20,000
ci_lower = round(summary[8]*initial_investment,2)
ci_upper = round(summary[9]*initial_investment,2)

# Print results
print(f"There is a 95% chance that an initial investment of ${initial_investment} in the portfolio"
      f" over the next 30 years will end within in the range of"
      f" ${ci_lower} and ${ci_upper}")


# #### Calculate the expected portfolio return at the 95% lower and upper confidence intervals based on a 50% increase in the initial investment.

# In[82]:


# Set initial investment
initial_investment = 20000 * 1.5

# Use the lower and upper `95%` confidence intervals to calculate the range of the possible outcomes of our $30,000
ci_lower = round(summary[8]*initial_investment,2)
ci_upper = round(summary[9]*initial_investment,2)

# Print results
print(f"There is a 95% chance that an initial investment of ${initial_investment} in the portfolio"
      f" over the next 30 years will end within in the range of"
      f" ${ci_lower} and ${ci_upper}")


# ### Optional- Early Retirement Pipedream

# #### Five Year (Retirement) Plan

# In[84]:


# Configuring a Monte Carlo simulation to forecast 5 years cumulative returns
Five_Year_Plan = MCSimulation(
    portfolio_data = df_stock_data,
    weights = [0.2, 0.8],
    num_simulation = 500,
    num_trading_days = 252*5)


# In[85]:


# Running a Monte Carlo simulation to forecast 5 years cumulative returns
Five_Year_Plan.calc_cumulative_return()


# In[86]:


# Plot simulation outcomes
Five_Year_Plan.plot_simulation()


# In[87]:


# Plot probability distribution and confidence intervals
Five_Year_Plan.plot_distribution()


# In[89]:


# Fetch summary statistics from the Monte Carlo simulation results
FYP_summary = Five_Year_Plan.summarize_cumulative_return()

# Print summary statistics
print(FYP_summary)


# In[90]:


# Set initial investment
FYP_initial_investment = 60000

# Use the lower and upper `95%` confidence intervals to calculate the range of the possible outcomes of our $60,000
ci_lower_five = round(FYP_summary[8]*FYP_initial_investment,2)
ci_upper_five = round(FYP_summary[9]*FYP_initial_investment,2)

# Print results
print(f"There is a 95% chance that an initial investment of ${FYP_initial_investment} in the portfolio"
      f" over the next 5 years will end within in the range of"
      f" ${ci_lower_five} and ${ci_upper_five}")


# ### Ten Year (Retirement) Plan

# In[91]:


#Do the same thing but 10 years

Ten_Year_Plan = MCSimulation(
    portfolio_data = df_stock_data,
    weights = [0.2, 0.8],
    num_simulation = 500,
    num_trading_days = 252*5)


# In[92]:


# Running a Monte Carlo simulation to forecast 10 years cumulative returns
Ten_Year_Plan.calc_cumulative_return()


# In[93]:


# Plot simulation outcomes
Ten_Year_Plan.plot_simulation()


# In[94]:


# Plot probability distribution and confidence intervals
Ten_Year_Plan.plot_distribution()


# In[95]:


# Fetch summary statistics from the Monte Carlo simulation results
TYP_summary = Ten_Year_Plan.summarize_cumulative_return()

# Print summary statistics
print(TYP_summary)


# In[96]:


# Set initial investment
TYP_initial_investment = 60000

# Use the lower and upper `95%` confidence intervals to calculate the range of the possible outcomes of our $60,000
ci_lower_five = round(TYP_summary[8]*TYP_initial_investment,2)
ci_upper_five = round(TYP_summary[9]*TYP_initial_investment,2)

# Print results
print(f"There is a 95% chance that an initial investment of ${TYP_initial_investment} in the portfolio"
      f" over the next 5 years will end within in the range of"
      f" ${ci_lower_five} and ${ci_upper_five}")


# #### Don't Retire, or at least find some good hobbies if you do, gotta keep busy! 

# In[ ]:




