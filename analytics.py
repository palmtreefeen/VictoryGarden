import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from models import Product, User

def generate_mock_data(days=365):
    dates = [datetime.now() - timedelta(days=i) for i in range(days)]
    demand = np.random.randint(50, 200, size=days) + np.sin(np.arange(days) * 2 * np.pi / 30) * 20 + np.random.normal(0, 10, days)
    supply = np.random.randint(40, 180, size=days) + np.cos(np.arange(days) * 2 * np.pi / 30) * 15 + np.random.normal(0, 8, days)
    price = np.random.uniform(1.5, 5.0, size=days) + np.sin(np.arange(days) * 2 * np.pi / 60) * 0.5 + np.random.normal(0, 0.2, days)
    weather = np.random.normal(20, 5, size=days) + np.sin(np.arange(days) * 2 * np.pi / 365) * 10
    return dates, demand.astype(np.float64), supply.astype(np.float64), price.astype(np.float64), weather.astype(np.float64)

def predict_demand_supply(product_name):
    dates, demand, supply, price, weather = generate_mock_data()
    
    df = pd.DataFrame({
        'date': dates,
        'demand': demand,
        'supply': supply,
        'price': price,
        'weather': weather
    })
    df.set_index('date', inplace=True)
    
    model_demand = SARIMAX(df['demand'], exog=df[['weather', 'price']], order=(1,1,1), seasonal_order=(1,1,1,12))
    model_supply = SARIMAX(df['supply'], exog=df[['weather', 'price']], order=(1,1,1), seasonal_order=(1,1,1,12))
    
    results_demand = model_demand.fit()
    results_supply = model_supply.fit()
    
    future_dates = pd.date_range(start=df.index[-1] + timedelta(days=1), periods=30)
    future_weather = np.random.normal(20, 5, size=30) + np.sin(np.arange(30) * 2 * np.pi / 365) * 10
    future_price = np.random.uniform(1.5, 5.0, size=30) + np.sin(np.arange(30) * 2 * np.pi / 60) * 0.5
    
    future_exog = pd.DataFrame({'weather': future_weather, 'price': future_price}, index=future_dates)
    
    forecast_demand = results_demand.get_forecast(steps=30, exog=future_exog)
    forecast_supply = results_supply.get_forecast(steps=30, exog=future_exog)
    
    return {
        'product': product_name,
        'dates': future_dates.strftime('%Y-%m-%d').tolist(),
        'predicted_demand': forecast_demand.predicted_mean.tolist(),
        'predicted_supply': forecast_supply.predicted_mean.tolist(),
        'demand_lower': forecast_demand.conf_int()['lower demand'].tolist(),
        'demand_upper': forecast_demand.conf_int()['upper demand'].tolist(),
        'supply_lower': forecast_supply.conf_int()['lower supply'].tolist(),
        'supply_upper': forecast_supply.conf_int()['upper supply'].tolist(),
        'model_summary_demand': results_demand.summary().as_text(),
        'model_summary_supply': results_supply.summary().as_text()
    }

def get_market_insights(product_name):
    dates, demand, supply, price, weather = generate_mock_data()
    
    model = SARIMAX(price, order=(1,1,1), seasonal_order=(1,1,1,12))
    results = model.fit()
    price_forecast = results.forecast(steps=30)
    
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
        'weather_supply_correlation': weather_supply_corr,
        'model_summary': results.summary().as_text()
    }

def get_product_recommendations(user):
    all_products = Product.query.all()
    
    user_preferences = {
        'experience': user.experience,
        'interests': user.interests.split(',') if user.interests else [],
        'garden_size': user.garden_size,
        'preferred_products': user.preferred_products.split(',') if user.preferred_products else [],
        'organic_preference': user.organic_preference
    }
    
    recommended_products = []
    for product in all_products:
        score = 0
        
        # Check if the product matches user's interests
        if any(interest.lower() in product.tags.lower() for interest in user_preferences['interests']):
            score += 2
        
        # Check if the product is in user's preferred products list
        if product.name in user_preferences['preferred_products']:
            score += 3
        
        # Check if the product matches user's organic preference
        if user_preferences['organic_preference'] and product.is_organic:
            score += 2
        
        # Adjust score based on user's experience level
        if user_preferences['experience'] == 'beginner' and 'easy' in product.tags.lower():
            score += 1
        elif user_preferences['experience'] == 'expert' and 'advanced' in product.tags.lower():
            score += 1
        
        # Adjust score based on garden size
        if user_preferences['garden_size'] == 'small' and 'compact' in product.tags.lower():
            score += 1
        elif user_preferences['garden_size'] == 'large' and 'large-scale' in product.tags.lower():
            score += 1
        
        recommended_products.append((product, score))
    
    # Sort products by score in descending order and return top 5
    recommended_products.sort(key=lambda x: x[1], reverse=True)
    return [product for product, score in recommended_products[:5]]

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
    
    possible_demand = np.linspace(np.min(demand), np.max(demand), 100)
    possible_supply = np.linspace(np.min(supply), np.max(supply), 100)
    possible_weather = np.linspace(np.min(weather), np.max(weather), 100)
    
    demand_grid, supply_grid, weather_grid = np.meshgrid(possible_demand, possible_supply, possible_weather)
    X_grid = np.column_stack((demand_grid.ravel(), supply_grid.ravel(), weather_grid.ravel()))
    
    predicted_prices = model.predict(X_grid)
    
    optimal_price = np.max(predicted_prices)
    
    feature_importance = pd.DataFrame({
        'feature': ['demand', 'supply', 'weather'],
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    return {
        'optimal_price': optimal_price,
        'model_mse': mse,
        'model_r2': r2,
        'feature_importance': feature_importance.to_dict(orient='records')
    }
