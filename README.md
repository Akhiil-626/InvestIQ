# Stock Market Decision Support System (DSS)

A Python-based system for analyzing historical stock market data of top companies, predicting future closing prices, and generating simple Buy/Hold/Sell decisions.
Dataset : Stock Market: Historical Data of Top 10 Companies from Kaggle

1. **Data Preprocessing**
   - Cleans price columns (removes `$`, converts to float)
   - Handles missing values
   - Parses date column safely
   - Creates lag features for previous closing prices

2. **Machine Learning Model**
   - Uses Linear Regression to predict future closing prices
   - Time-series safe train-test split
   - Metrics calculated: MAE and RMSE

3. **Decision Support System (DSS)**
   - Generates Buy/Hold/Sell signals based on predicted vs actual closing prices
   - Simple threshold-based logic


