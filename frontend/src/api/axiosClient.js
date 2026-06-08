import axios from 'axios';

// 建立 Axios 實體
const axiosClient = axios.create({
  // baseURL: 'https://spore-easily-detective.ngrok-free.dev/api', // 原本的 ngrok 網址
  baseURL: 'https://spore-easily-detective.ngrok-free.dev/api', // 本地端測試網址 (自己跑 backend 時用這個)
  headers: {
    'Content-Type': 'application/json',
    'ngrok-skip-browser-warning': 'true', // 繞過 ngrok 的免費警告頁面
  },
  timeout: 10000, // 10秒超時
});

// 請求攔截器 (Interceptor)
// 我們可以在這裡統一處理 Token 或是加入其他設定
axiosClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    // Django REST Framework 預設使用 Token 關鍵字而不是 Bearer
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 回應攔截器 (Interceptor)
// 我們可以在這裡統一處理錯誤，例如 401 未授權、500 伺服器錯誤
axiosClient.interceptors.response.use(
  (response) => {
    // 通常 axios 會把資料包裝在 response.data 裡面
    return response.data;
  },
  (error) => {
    // 如果遇到 401 未授權 (Invalid token)，代表 Token 過期或無效，將其清除
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
    }
    // 可以集中處理各種錯誤代碼
    console.error('API Error:', error.response || error.message);
    return Promise.reject(error);
  }
);

export default axiosClient;
