import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import '../App.css';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('user');
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      alert('請輸入有效的電子郵件格式！');
      return;
    }
    console.log('Login attempt:', { email, password, role });
    // TODO: Connect to backend API
    // 模擬登入成功後跳轉
    if (role === 'admin') {
      navigate('/admin');
    } else {
      navigate('/home');
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1 className="login-title">不揪ㄛ</h1>
          <p className="login-subtitle">尋找你的球友與牌咖，隨時開局！</p>
        </div>
        
        <div className="role-toggle">
          <button 
            className={`role-btn ${role === 'user' ? 'active' : ''}`}
            onClick={() => setRole('user')}
            type="button"
          >
            使用者
          </button>
          <button 
            className={`role-btn ${role === 'admin' ? 'active' : ''}`}
            onClick={() => setRole('admin')}
            type="button"
          >
            管理員
          </button>
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

          <div className="forgot-password">
            <a href="#forgot">忘記密碼？</a>
          </div>
          
          <button type="submit" className="login-button">
            登入
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
