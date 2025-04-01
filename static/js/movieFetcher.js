const axios = require('axios');
const cheerio = require('cheerio');

// 綜合示例（第三方 API + 自定義爬蟲）
app.get('/api/movies', async (req, res) => {
  try {
    // 優先嘗試官方 API
    const tmdbResponse = await axios.get('https://api.themoviedb.org/3/movie/now_playing', {
      params: { api_key: 'YOUR_KEY' }
    });

    if (tmdbResponse.data.results.length > 0) {
      return res.json(tmdbResponse.data.results);
    } else {
      // 若 API 無數據，回退到爬蟲
      const crawledData = await fetch_vieshow_movies();
      return res.json(crawledData);
    }
  } catch (error) {
    console.error('電影數據獲取錯誤:', error);
    // 嘗試爬蟲作為備用方案
    try {
      const crawledData = await fetch_vieshow_movies();
      return res.json(crawledData);
    } catch (crawlError) {
      console.error('爬蟲獲取電影失敗:', crawlError);
      res.status(500).json({ error: '獲取數據失敗' });
    }
  }
});