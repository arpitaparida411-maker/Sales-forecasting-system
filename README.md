# Intelligent Sales Forecasting Using Machine Learning and Time-Series Predictive Analytics

Author: Arpita Parida

A course project that forecasts weekly Walmart sales. It compares simple baselines, a time-series model and a machine learning model, and shows the results in a web dashboard (Flask backend + Streamlit frontend).

## Dataset

- Walmart weekly sales dataset from Kaggle (`Walmart.csv`, 6,435 rows, 45 stores, 143 weeks)
- Period: 5 Feb 2010 to 26 Oct 2012
- Columns: Store, Date, Weekly_Sales, Holiday_Flag, Temperature, Fuel_Price, CPI, Unemployment
- No missing values and no duplicate rows
- The sales of all 45 stores are added up to one weekly total, and that total is what we forecast

## Method

1. **EDA**: checked data types, missing values and duplicates, and plotted total weekly sales. Sales spike in the Thanksgiving and Christmas weeks every year.
2. **Time-based split** (no random split): the first 117 weeks are used for training and the last 26 weeks (4 May to 26 Oct 2012) for testing.
3. **Baselines**: naive (last value) and seasonal naive (same week last year).
4. **Time-series model**: Holt-Winters exponential smoothing with a 52-week seasonal cycle.
5. **Machine learning model**: Random Forest with lag features (sales 26 and 52 weeks earlier), week of year, month and a holiday flag.
6. **Forecast**: the best model (Holt-Winters) is retrained on all 143 weeks and forecasts the next 26 weeks (2 Nov 2012 to 26 Apr 2013).

## Results (26-week test set)

| Model | MAE | RMSE | MAPE |
|---|---|---|---|
| Holt-Winters | 953,039 | 1,168,319 | 2.02% |
| Random Forest (lag features) | 959,961 | 1,323,605 | 2.02% |
| Seasonal naive (52 weeks ago) | 1,181,619 | 1,455,381 | 2.50% |
| Naive (last value) | 3,157,980 | 3,583,173 | 6.62% |

MAE and RMSE are in US dollars. Both real models beat both baselines. Holt-Winters and Random Forest tie on MAPE, and Holt-Winters is slightly better on MAE and RMSE.

## Project structure

```
Sales-forecasting-system/
├── Data/raw/Walmart.csv        # original dataset
├── notebook/01_eda.ipynb       # EDA, models and forecast
├── outputs/                    # saved forecast and results (CSV)
├── backend/app.py              # Flask API
├── frontend/app.py             # Streamlit dashboard
├── .streamlit/config.toml      # dashboard theme
├── requirements.txt
└── README.md
```

## How to run

1. Install the packages:
   ```
   pip install -r requirements.txt
   ```
2. Run `notebook/01_eda.ipynb` from top to bottom. It creates the CSV files in `outputs/`.
3. Start the backend (keep this terminal open):
   ```
   python backend/app.py
   ```
4. In a second terminal, start the dashboard:
   ```
   streamlit run frontend/app.py
   ```
5. Open http://localhost:8501 in your browser.

## Backend API

| Endpoint | Returns |
|---|---|
| `/health` | status check |
| `/history` | weekly sales history |
| `/forecast?weeks=N` | next N forecast weeks (1 to 26) |
| `/models` | model comparison table |

## Dashboard features

- Slider for the number of weeks to forecast
- Summary cards: total forecast, weekly average, peak week and best model
- Chart of sales history and forecast
- Forecast table with CSV download
- Model comparison table and bar chart

## Notes and limitations

- The dataset is in US dollars. The dashboard converts it to Indian rupees (crore) with a fixed rate set in `frontend/app.py` (`USD_TO_INR`), so the rupee values are approximate.
- There are only about 2.7 years of data, so the Holt-Winters model shows a convergence warning. The forecast is usable but should be treated with caution.
- The data ends in October 2012, so the forecast for December 2012 is an extrapolation of the earlier Christmas patterns.
- Forecasts are for total sales across all stores, not for individual stores.