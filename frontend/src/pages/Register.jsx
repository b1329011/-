import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import authApi from '../api/auth';
import '../App.css';

function Register() {
  const [nickname, setNickname] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [passwordError, setPasswordError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      alert('請輸入有效的電子郵件格式！');
      return;
    }
    if (password.length < 6) {
      setPasswordError('密碼長度請至少包含 6 個字元！');
      return;
    } else {
      setPasswordError('');
    }
    if (password !== confirmPassword) {
      alert('兩次密碼輸入不一致喔！');
      return;
    }

    setIsLoading(true);
    try {
      // 註冊前先清空可能殘留的舊 Token，避免 DRF 報錯 (Invalid Token)
      localStorage.removeItem('token');
      localStorage.removeItem('role');
      const response = await authApi.register({ name: nickname, email, password });
      
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
      
      alert('註冊成功！請繼續完成個人檔案設定。');
      navigate('/setup-profile');
    } catch (error) {
      console.error('Register error:', error);
      alert('註冊失敗，請確認信箱是否已被使用或伺服器狀態！');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1 className="login-title">加入<span style={{ color: '#7995a5' }}>不揪ㄛ</span></h1>
          <p className="login-subtitle">註冊新帳號，開始你的第一局！</p>
        </div>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="nickname">暱稱 <span style={{ color: '#ef4444' }}>(必填)</span></label>
            <input
              id="nickname"
              type="text"
              className="form-input"
              placeholder="大家怎麼稱呼你？"
              value={nickname}
              onChange={(e) => setNickname(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="email">電子信箱 <span style={{ color: '#ef4444' }}>(必填)</span></label>
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
            <label className="form-label" htmlFor="password">密碼 <span style={{ color: '#ef4444' }}>(必填)</span></label>
            <input
              id="password"
              type="password"
              className="form-input"
              placeholder="設定密碼"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                if (passwordError) setPasswordError('');
              }}
              required
            />
            {passwordError && <div style={{ color: '#ef4444', fontSize: '12px', marginTop: '6px' }}>{passwordError}</div>}
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="confirmPassword">確認密碼 <span style={{ color: '#ef4444' }}>(必填)</span></label>
            <input
              id="confirmPassword"
              type="password"
              className="form-input"
              placeholder="再次輸入密碼"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
          </div>
          
          <button type="submit" className="login-button" style={{ marginTop: '10px' }} disabled={isLoading}>
            {isLoading ? '註冊中...' : '完成註冊'}
          </button>
        </form>

        <div className="register-link">
          已經有帳號了？
          <Link to="/">返回登入</Link>
        </div>
      </div>
    </div>
  );
}

export default Register;
