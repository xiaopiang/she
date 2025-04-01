from flask import Flask, jsonify
from flask_cors import CORS  # 避免 CORS 問題
from crawler import fetch_vieshow_movies  # 引入剛剛的爬蟲函數

app = Flask(__name__)
CORS(app)  # 允許跨域請求，避免瀏覽器攔截

@app.route("/api/movies/")
def movies_api():
    movies = fetch_vieshow_movies()
    return jsonify(movies)

if __name__ == "__main__":
    app.run(debug=True)
