from fastapi import FastAPI
from fastapi.responses import FileResponse
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
from shapely.geometry import Point

app = FastAPI()

# Function to make the GET request and load data
def fetch_data():
    base_url = "https://hubeau.eaufrance.fr/api"
    endpoint = "/v2/qualite_rivieres/analyse_pc"

    # Define any parameters you want to pass
    # For example, you might want to specify a bounding box (bbox)
    params = {
        'bbox': '2.35,48.85,2.36,48.86',  # Replace these with actual coordinates
        'page': 1,
        'size': 10
    }

    # Construct the full URL
    url = f"{base_url}{endpoint}"
    response = requests.get(url)
    if response.ok:
        return response.json()['data']
    else:
        raise Exception(f"Failed to fetch data: {response.status_code}")

# Function to process and return a DataFrame
def process_data(data):
    df = pd.json_normalize(data)
    # Convert date to datetime, process or filter data as needed
    #breakpoint()
    df['date_prelevement'] = pd.to_datetime(df['date_prelevement'])
    return df

@app.get("/visualizations/temporal")
async def temporal_trends():
    data = fetch_data()
    df = process_data(data)
    # Generate visualization (similar to the previous example)
    parameter = 'temperature'
    if parameter not in df.columns:
    # Selecting the first numerical column as a placeholder if 'temperature' is not available
        parameter = df.select_dtypes(include='number').columns[0]

    # 1. Temporal Trends of a Specific Parameter
    # Assuming 'temperature' data is available and is the parameter of interest
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df, x='date_prelevement', y=parameter)
    plt.title(f'Temporal Variation of {parameter.capitalize()}')
    plt.xlabel('Date')
    plt.ylabel(f'{parameter.capitalize()} Value')
    plt.xticks(rotation=45)
    plt.tight_layout()
    # Save and return the image
    plt.savefig('temporal_trends.png')
    plt.close()
    return FileResponse('temporal_trends.png')

@app.get("/visualizations/comparative")
async def comparative_analysis():
    data = fetch_data()
    df = process_data(data)
    # Generate the comparative analysis visualization
    parameter = 'temperature'
    if parameter not in df.columns:
        # Selecting the first numerical column as a placeholder if 'temperature' is not available
        parameter = df.select_dtypes(include='number').columns[0]
    avg_parameter_by_station = df.groupby('code_station')[parameter].mean().reset_index()
    plt.figure(figsize=(12, 6))
    sns.barplot(data=avg_parameter_by_station, x='code_station', y=parameter)
    plt.title(f'Average {parameter.capitalize()} by Station')
    plt.xlabel('Station Code')
    plt.ylabel(f'Average {parameter.capitalize()}')
    plt.xticks(rotation=90)
    plt.tight_layout()
    # Save the figure
    plt.savefig('comparative_analysis.png')
    plt.close()
    return FileResponse('comparative_analysis.png')

@app.get("/visualizations/geographical")
async def geographical_distribution():
    data = fetch_data()
    df = process_data(data)
    # Generate the geographical distribution visualization
    parameter = 'temperature'
    if parameter not in df.columns:
        # Selecting the first numerical column as a placeholder if 'temperature' is not available
        parameter = df.select_dtypes(include='number').columns[0]
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude))
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    world.plot(ax=ax, color='lightgrey')
    gdf.plot(ax=ax, markersize=20, color='blue', alpha=0.5, label=parameter)
    plt.title(f'Geographical Distribution of {parameter.capitalize()}')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.legend()
    # Save the figure
    plt.savefig('geographical_distribution.png')
    plt.close()
    return FileResponse('geographical_distribution.png')

# Add other endpoints as needed
