import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

def generate_mock_data(days=365):
    dates = [datetime.now() - timedelta(days=i) for i in range(days)]
    demand = np.random.randint(50, 200, size=days) + np.sin(np.arange(days) * 2 * np.pi / 30) * 20 + np.random.normal(0, 10, days)
    supply = np.random.randint(40, 180, size=days) + np.cos(np.arange(days) * 2 * np.pi / 30) * 15 + np.random.normal(0, 8, days)
    price = np.random.uniform(1.5, 5.0, size=days) + np.sin(np.arange(days) * 2 * np.pi / 60) * 0.5 + np.random.normal(0, 0.2, days)
    weather = np.random.normal(20, 5, size=days) + np.sin(np.arange(days) * 2 * np.pi / 365) * 10
    return dates, demand.astype(np.float64), supply.astype(np.float64), price.astype(np.float64), weather.astype(np.float64)

def predict_demand_supply(product_name):
    dates, demand, supply, price, weather = generate_mock_data()
    
    # Prepare data for Prophet
    df_demand = pd.DataFrame({'ds': dates, 'y': demand})
    df_supply = pd.DataFrame({'ds': dates, 'y': supply})
    
    # Add weather as an additional regressor
    df_demand['weather'] = weather
    df_supply['weather'] = weather
    
    # Fit Prophet models with additional regressor
    model_demand = Prophet()
    model_supply = Prophet()
    model_demand.add_regressor('weather')
    model_supply.add_regressor('weather')
    model_demand.fit(df_demand)
    model_supply.fit(df_supply)
    
    # Make future predictions
    future_dates = model_demand.make_future_dataframe(periods=30)
    future_dates['weather'] = np.random.normal(20, 5, size=len(future_dates)) + np.sin(np.arange(len(future_dates)) * 2 * np.pi / 365) * 10
    forecast_demand = model_demand.predict(future_dates)
    forecast_supply = model_supply.predict(future_dates)
    
    return {
        'product': product_name,
        'dates': future_dates['ds'].dt.strftime('%Y-%m-%d').tolist()[-30:],
        'predicted_demand': forecast_demand['yhat'].tolist()[-30:],
        'predicted_supply': forecast_supply['yhat'].tolist()[-30:],
        'demand_lower': forecast_demand['yhat_lower'].tolist()[-30:],
        'demand_upper': forecast_demand['yhat_upper'].tolist()[-30:],
        'supply_lower': forecast_supply['yhat_lower'].tolist()[-30:],
        'supply_upper': forecast_supply['yhat_upper'].tolist()[-30:]
    }

def get_market_insights(product_name):
    dates, demand, supply, price, weather = generate_mock_data()
    
    # ARIMA model for price forecasting
    model = ARIMA(price, order=(1,1,1))
    results = model.fit()
    price_forecast = results.forecast(steps=30)
    
    # Advanced metrics
    avg_demand = np.mean(demand)
    avg_supply = np.mean(supply)
    avg_price = np.mean(price)
    
    demand_trend = 'increasing' if demand[-30:].mean() > demand[:30].mean() else 'decreasing'
    supply_trend = 'increasing' if supply[-30:].mean() > supply[:30].mean() else 'decreasing'
    price_trend = 'increasing' if price[-30:].mean() > price[:30].mean() else 'decreasing'
    
    demand_volatility = np.std(demand) / avg_demand
    supply_volatility = np.std(supply) / avg_supply
    price_volatility = np.std(price) / avg_price
    
    seasonal_demand = np.correlate(demand, np.sin(np.arange(len(demand)) * 2 * np.pi / 30))[0]
    seasonal_supply = np.correlate(supply, np.sin(np.arange(len(supply)) * 2 * np.pi / 30))[0]
    
    demand_supply_ratio = avg_demand / avg_supply if avg_supply != 0 else float('inf')
    price_elasticity = (np.diff(demand) / demand[:-1]).mean() / (np.diff(price) / price[:-1]).mean()
    
    # Weather impact analysis
    weather_demand_corr = np.corrcoef(weather, demand)[0, 1]
    weather_supply_corr = np.corrcoef(weather, supply)[0, 1]
    
    return {
        'product': product_name,
        'average_demand': avg_demand,
        'average_supply': avg_supply,
        'average_price': avg_price,
        'demand_trend': demand_trend,
        'supply_trend': supply_trend,
        'price_trend': price_trend,
        'demand_volatility': demand_volatility,
        'supply_volatility': supply_volatility,
        'price_volatility': price_volatility,
        'seasonal_demand': 'High' if seasonal_demand > 0 else 'Low',
        'seasonal_supply': 'High' if seasonal_supply > 0 else 'Low',
        'demand_supply_ratio': demand_supply_ratio,
        'price_elasticity': price_elasticity,
        'price_forecast': price_forecast.tolist(),
        'weather_demand_correlation': weather_demand_corr,
        'weather_supply_correlation': weather_supply_corr
    }

def get_product_recommendations(product_name):
    all_products = ["Tomatoes", "Lettuce", "Carrots", "Cucumbers", "Peppers", "Squash", "Strawberries", "Herbs", "Onions", "Potatoes"]
    
    # Simulate a more sophisticated recommendation system
    product_features = {p: np.random.rand(5) for p in all_products}
    target_features = product_features[product_name]
    
    similarities = {p: np.dot(target_features, f) / (np.linalg.norm(target_features) * np.linalg.norm(f)) 
                    for p, f in product_features.items() if p != product_name}
    
    recommendations = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:3]
    return [r[0] for r in recommendations]

def get_optimal_price(product_name):
    dates, demand, supply, price, weather = generate_mock_data()
    
    X = np.column_stack((demand, supply, weather))
    y = price
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    # Generate a range of possible demand, supply, and weather values
    possible_demand = np.linspace(np.min(demand), np.max(demand), 100)
    possible_supply = np.linspace(np.min(supply), np.max(supply), 100)
    possible_weather = np.linspace(np.min(weather), np.max(weather), 100)
    
    # Create a grid of all possible combinations
    demand_grid, supply_grid, weather_grid = np.meshgrid(possible_demand, possible_supply, possible_weather)
    X_grid = np.column_stack((demand_grid.ravel(), supply_grid.ravel(), weather_grid.ravel()))
    
    # Predict prices for all combinations
    predicted_prices = model.predict(X_grid)
    
    # Find the optimal price (maximum in this case, but could be adjusted based on business logic)
    optimal_price = np.max(predicted_prices)
    
    return {
        'optimal_price': optimal_price,
        'model_mse': mse,
        'model_r2': r2
    }
