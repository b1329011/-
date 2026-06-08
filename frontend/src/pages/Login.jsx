import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import authApi from '../api/auth';
import '../App.css';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      alert('請輸入有效的電子郵件格式！');
      return;
    }

    setIsLoading(true);
    try {
      // 登入前先清空可能殘留的舊 Token
      localStorage.removeItem('token');
      localStorage.removeItem('role');
      const response = await authApi.login({ email, password });
      
      // 儲存 Django 回傳的 token
      if (response && response.token) {
        localStorage.setItem('token', response.token);
      }
      if (response && response.user_id) {
        localStorage.setItem('user_id', response.user_id);
      }
      if (response && response.role) {
        localStorage.setItem('role', response.role);
      }
      
      // 登入成功後一律先進入使用者大廳頁面
      navigate('/home');
    } catch (error) {
      console.error('Login error:', error);
      const errorMsg = error.response?.data?.detail || '登入失敗，請檢查帳號密碼或確認伺服器狀態！';
      alert(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1 className="login-title">不揪ㄛ</h1>
          <p className="login-subtitle">尋找你的球友與牌咖，隨時開局！</p>
        </div>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="email">電子信箱</label>
            <input
              id="email"
              type="email"
              className="form-input"
              placeholder="輸入你的信箱"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          
          <div className="form-group">
            <label className="form-label" htmlFor="password">密碼</label>
            <input
              id="password"
              type="password"
              className="form-input"
              placeholder="輸入密碼"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          
          <button type="submit" className="login-button" disabled={isLoading}>
            {isLoading ? '登入中...' : '登入'}
          </button>
        </form>

        <div className="register-link">
          還沒有帳號嗎？
          <Link to="/register">立即註冊</Link>
        </div>
      </div>
    </div>
  );
}

export default Login;
