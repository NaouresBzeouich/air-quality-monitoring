#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from datetime import datetime
import os

class AirQualityScraper:
    def __init__(self):
        # Base URLs for different air quality data sources
        self.waqi_url = "https://aqicn.org/city/"
        self.openaq_api = "https://api.openaq.org/v2/"
        
    def scrape_waqi_data(self, city):
        """
        Scrape air quality data from WAQI for a specific city
        """
        try:
            # Create URL for the city
            url = f"{self.waqi_url}{city}/"
            
            # Send HTTP request with headers to mimic a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract air quality data (example selectors - need to be adjusted for actual website)
            aqi = soup.find('div', {'class': 'aqi-value'}).text
            pollutants = {
                'pm25': soup.find('div', {'id': 'pm25'}).text,
                'pm10': soup.find('div', {'id': 'pm10'}).text,
                'no2': soup.find('div', {'id': 'no2'}).text,
                'o3': soup.find('div', {'id': 'o3'}).text,
                'co': soup.find('div', {'id': 'co'}).text
            }
            
            return {
                'city': city,
                'timestamp': datetime.now().isoformat(),
                'aqi': aqi,
                'pollutants': pollutants
            }
            
        except Exception as e:
            print(f"Error scraping WAQI data for {city}: {str(e)}")
            return None

    def fetch_openaq_data(self, city, parameter=None):
        """
        Fetch data from OpenAQ API for a specific city
        """
        try:
            # Build API endpoint
            endpoint = f"{self.openaq_api}measurements"
            
            # Set up parameters for the API request
            params = {
                'city': city,
                'limit': 100,
                'parameter': parameter if parameter else None
            }
            
            # Make API request
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error fetching OpenAQ data for {city}: {str(e)}")
            return None

    def save_to_csv(self, data, filename):
        """
        Save scraped data to CSV file
        """
        try:
            # Convert data to DataFrame
            df = pd.DataFrame(data)
            
            # Create output directory if it doesn't exist
            os.makedirs('scraped_data', exist_ok=True)
            
            # Save to CSV
            output_path = os.path.join('scraped_data', filename)
            df.to_csv(output_path, index=False)
            print(f"Data saved to {output_path}")
            
        except Exception as e:
            print(f"Error saving data to CSV: {str(e)}")

def main():
    # Initialize scraper
    scraper = AirQualityScraper()
    
    # List of cities to scrape
    cities = ['amsterdam', 'rotterdam', 'hague']
    
    # Store results
    waqi_results = []
    openaq_results = []
    
    # Scrape data for each city
    for city in cities:
        # Get WAQI data
        waqi_data = scraper.scrape_waqi_data(city)
        if waqi_data:
            waqi_results.append(waqi_data)
        
        # Get OpenAQ data
        openaq_data = scraper.fetch_openaq_data(city)
        if openaq_data:
            openaq_results.append(openaq_data)
    
    # Save results
    if waqi_results:
        scraper.save_to_csv(waqi_results, 'waqi_data.csv')
    if openaq_results:
        scraper.save_to_csv(openaq_results, 'openaq_data.csv')

if __name__ == "__main__":
    main() 