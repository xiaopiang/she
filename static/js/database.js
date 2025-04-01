// const axios = require('axios');
// const cheerio = require('cheerio');
// const sqlite3 = require('sqlite3').verbose();
// const path = require('path');
// const express = require('express');

// const app = express();
// const port = 3000;

// // 設置視圖模板引擎
// app.set('view engine', 'ejs');
// app.use(express.static('public'));

// // 創建數據庫連接
// const dbPath = path.join(__dirname, 'movies.db');
// const db = new sqlite3.Database(dbPath);

// // 初始化數據庫表
// function initializeDatabase() {
//   return new Promise((resolve, reject) => {
//     db.run(`
//       CREATE TABLE IF NOT EXISTS movies (
//         id INTEGER PRIMARY KEY AUTOINCREMENT,
//         title TEXT NOT NULL,
//         poster_path TEXT,
//         detail_url TEXT,
//         rating TEXT,
//         release_date TEXT,
//         source TEXT,
//         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
//         updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
//       )
//     `, (err) => {
//       if (err) {
//         reject(err);
//       } else {
//         resolve();
//       }
//     });
//   });
// }

// // 威秀影城電影爬蟲函數
// async function fetch_vieshow_movies() {
//   try {
//     // 威秀影城官網上映中電影頁面
//     const url = 'https://www.vscinemas.com.tw/vsweb/film/index.aspx';
//     const response = await axios.get(url);
//     const $ = cheerio.load(response.data);
    
//     const movies = [];
    
//     // 根據威秀網站的HTML結構提取電影資訊
//     $('.movieItem').each((index, element) => {
//       const $element = $(element);
      
//       // 獲取電影標題
//       const title = $element.find('.title a').text().trim();
      
//       // 獲取電影海報圖片URL
//       const posterPath = $element.find('.poster img').attr('src');
      
//       // 獲取電影詳情頁URL
//       const detailUrl = $element.find('.title a').attr('href');
      
//       // 獲取電影類別/分級
//       const rating = $element.find('.tagArea span').text().trim();
      
//       // 獲取上映日期
//       const releaseDateText = $element.find('.date').text().trim();
//       const releaseDate = releaseDateText.replace('上映日期：', '');
      
//       movies.push({
//         title,
//         poster_path: posterPath,
//         detail_url: `https://www.vscinemas.com.tw/vsweb/film/${detailUrl}`,
//         rating,
//         release_date: releaseDate,
//         source: 'vieshow'
//       });
//     });
    
//     return movies;
//   } catch (error) {
//     console.error('威秀影城爬蟲錯誤:', error);
//     throw error;
//   }
// }

// // 保存電影數據到數據庫
// async function saveMoviesToDatabase(movies) {
//   const insertPromises = movies.map(movie => {
//     return new Promise((resolve, reject) => {
//       // 檢查電影是否已存在
//       db.get('SELECT id FROM movies WHERE title = ? AND release_date = ?', 
//         [movie.title, movie.release_date], (err, row) => {
//         if (err) {
//           reject(err);
//           return;
//         }
        
//         if (row) {
//           // 更新已存在的電影
//           db.run(`
//             UPDATE movies 
//             SET poster_path = ?, detail_url = ?, rating = ?, updated_at = CURRENT_TIMESTAMP 
//             WHERE id = ?
//           `, [movie.poster_path, movie.detail_url, movie.rating, row.id], (err) => {
//             if (err) {
//               reject(err);
//             } else {
//               resolve(row.id);
//             }
//           });
//         } else {
//           // 插入新電影
//           db.run(`
//             INSERT INTO movies (title, poster_path, detail_url, rating, release_date, source)
//             VALUES (?, ?, ?, ?, ?, ?)
//           `, [movie.title, movie.poster_path, movie.detail_url, movie.rating, movie.release_date, movie.source], 
//           function(err) {
//             if (err) {
//               reject(err);
//             } else {
//               resolve(this.lastID);
//             }
//           });
//         }
//       });
//     });
//   });
  
//   return Promise.all(insertPromises);
// }

// // 從數據庫獲取電影列表
// async function getMoviesFromDatabase() {
//   return new Promise((resolve, reject) => {
//     db.all('SELECT * FROM movies ORDER BY release_date DESC', (err, rows) => {
//       if (err) {
//         reject(err);
//       } else {
//         resolve(rows);
//       }
//     });
//   });
// }

// // 設置定時更新電影數據的任務
// async function scheduledMovieUpdate() {
//   try {
//     console.log('開始更新電影數據...');
//     await initializeDatabase();
    
//     // 獲取威秀電影數據
//     const movies = await fetch_vieshow_movies();
    
//     // 保存到數據庫
//     await saveMoviesToDatabase(movies);
//     console.log(`成功更新 ${movies.length} 部電影數據`);
//   } catch (error) {
//     console.error('更新電影數據失敗:', error);
//   }
// }

// // API 端點：獲取電影列表
// app.get('/api/movies', async (req, res) => {
//   try {
//     // 從數據庫獲取電影
//     const movies = await getMoviesFromDatabase();
    
//     // 如果數據庫沒有數據，嘗試重新爬取
//     if (movies.length === 0) {
//       await scheduledMovieUpdate();
//       const freshMovies = await getMoviesFromDatabase();
//       return res.json(freshMovies);
//     }
    
//     return res.json(movies);
//   } catch (error) {
//     console.error('獲取電影數據錯誤:', error);
//     res.status(500).json({ error: '獲取數據失敗' });
//   }
// });

// // 手動更新電影數據的端點
// app.post('/api/movies/update', async (req, res) => {
//   try {
//     await scheduledMovieUpdate();
//     res.json({ success: true, message: '電影數據已更新' });
//   } catch (error) {
//     console.error('手動更新電影數據錯誤:', error);
//     res.status(500).json({ error: '更新數據失敗' });
//   }
// });

// // 首頁路由 - 顯示電影訂票頁面
// app.get('/', async (req, res) => {
//   try {
//     const movies = await getMoviesFromDatabase();
    
//     // 如果數據庫沒有數據，嘗試重新爬取
//     if (movies.length === 0) {
//       await scheduledMovieUpdate();
//       const freshMovies = await getMoviesFromDatabase();
//       return res.render('index', { movies: freshMovies });
//     }
    
//     res.render('index', { movies: movies });
//   } catch (error) {
//     console.error('獲取電影數據錯誤:', error);
//     res.status(500).send('獲取電影數據失敗');
//   }
// });

// // 啟動服務器
// app.listen(port, async () => {
//   try {
//     await initializeDatabase();
//     await scheduledMovieUpdate();
    
//     // 設置定時任務，每6小時更新一次電影數據
//     setInterval(scheduledMovieUpdate, 6 * 60 * 60 * 1000);
    
//     console.log(`服務器已啟動，訪問 http://localhost:${port}`);
//   } catch (error) {
//     console.error('服務器啟動失敗:', error);
//   }
// });