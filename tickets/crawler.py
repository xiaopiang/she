import sqlite3
import requests
from bs4 import BeautifulSoup

def fetch_vieshow_movies():
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    url = "https://www.vscinemas.com.tw/vsweb/film/index.aspx"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    movies = []
    for item in soup.select('.movieList li'):
        title = item.select_one('.infoArea h2').text.strip()
        link = item.select_one('a')['href']
        movies.append({
            'title': title,
            'link': f"https://www.vscinemas.com.tw{link}",
        })
    return movies

def save_to_database(movies):
    # 連接到 SQLite 資料庫（如果不存在則創建）
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    
    # 創建資料表（如果不存在）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        link TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 插入電影資料
    for movie in movies:
        cursor.execute('''
        INSERT INTO movies (title, link) VALUES (?, ?)
        ''', (movie['title'], movie['link']))
    
    # 提交並關閉連接
    conn.commit()
    conn.close()

if __name__ == "__main__":
    movies = fetch_vieshow_movies()
    save_to_database(movies)
    print(f"成功儲存 {len(movies)} 部電影資料到資料庫")
    