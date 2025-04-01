import os
import sys
import django
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('movie_scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Set up Django environment
# Change 'movie_fastshop' to your actual project name
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie_fastshop.settings')
django.setup()

# Import your models - adjust 'tickets' to your actual app name
from tickets.models import Movie

def scrape_vscinemas():
    """Scrape movie data from VSCinemas website"""
    logging.info("Starting movie scraping from VSCinemas...")
    
    url = "https://www.vscinemas.com.tw/vsweb/film/index.aspx"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            logging.error(f"Failed to fetch data: Status code {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all movie items
        movie_elements = soup.select('.movieList .filmInfo')
        movies_data = []
        
        for movie in movie_elements:
            try:
                title_element = movie.select_one('.filmTitle')
                title = title_element.text.strip() if title_element else "Unknown Title"
                
                img_element = movie.find_previous('img')
                poster_url = img_element['src'] if img_element and 'src' in img_element.attrs else ""
                if poster_url and not poster_url.startswith('http'):
                    poster_url = f"https://www.vscinemas.com.tw{poster_url}"
                
                # Try to find description
                description_element = movie.select_one('.filmIntroduction')
                description = description_element.text.strip() if description_element else ""
                
                # Try to find duration
                duration_text = ""
                info_elements = movie.select('.filmInfo span')
                for info in info_elements:
                    if "分鐘" in info.text:
                        duration_text = info.text
                        break
                
                # Extract duration as integer
                duration = 0
                if duration_text:
                    # Find all numbers in the string
                    import re
                    numbers = re.findall(r'\d+', duration_text)
                    if numbers:
                        duration = int(numbers[0])
                
                movies_data.append({
                    'title': title,
                    'poster_url': poster_url,
                    'description': description,
                    'duration': duration,
                    'is_showing': True
                })
                
                logging.info(f"Scraped movie: {title}")
            except Exception as e:
                logging.error(f"Error processing movie element: {e}")
        
        return movies_data
    
    except Exception as e:
        logging.error(f"Error scraping movies: {e}")
        return []

def update_database(movies_data):
    """Update the database with scraped movie data"""
    logging.info(f"Updating database with {len(movies_data)} movies...")
    
    # Keep track of movies we've seen to mark others as not showing
    updated_titles = []
    
    # Update or create movies
    for movie_data in movies_data:
        title = movie_data['title']
        updated_titles.append(title)
        
        try:
            movie, created = Movie.objects.update_or_create(
                title=title,
                defaults={
                    'poster_url': movie_data['poster_url'],
                    'description': movie_data['description'],
                    'duration': movie_data['duration'],
                    'is_showing': True
                }
            )
            
            if created:
                logging.info(f"Added new movie: {title}")
            else:
                logging.info(f"Updated existing movie: {title}")
        
        except Exception as e:
            logging.error(f"Error saving movie {title}: {e}")
    
    # Mark movies not in the scraped data as not showing
    Movie.objects.filter(is_showing=True).exclude(title__in=updated_titles).update(is_showing=False)
    logging.info("Database update complete.")

def run_scraper():
    """Main function to run the scraper"""
    logging.info("Starting movie database update process...")
    
    # Scrape movies
    movies_data = scrape_vscinemas()
    
    if movies_data:
        # Update database
        update_database(movies_data)
        logging.info(f"Successfully processed {len(movies_data)} movies.")
    else:
        logging.warning("No movie data retrieved. Database not updated.")
    
    logging.info("Movie database update process completed.")

if __name__ == "__main__":
    run_scraper()