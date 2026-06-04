import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { LayoutDashboard, MapPinned, Bell, Plus, Trash2, ArrowLeft, TrendingUp, BarChart3, MessageSquarePlus, MessageSquareText, Wrench, RefreshCcw, UserCircle, CloudRain, CheckCircle, XCircle } from 'lucide-react';
import '../App.css';

function Admin() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('dashboard');

  // 模擬場地資料庫
  const [venues, setVenues] = useState([
    { id: 1, name: '桃園國民運動中心', city: '桃園市', district: '桃園區', facilities: ['冷氣', '飲水機', '廁所', '淋浴間'] },
    { id: 2, name: '桃園巨蛋室外籃球場', city: '桃園市', district: '桃園區', facilities: ['飲水機', '廁所'] },
    { id: 3, name: '台大體育館', city: '台北市', district: '大安區', facilities: ['冷氣', '飲水機', '廁所'] },
  ]);

  // 模擬揪團房間資料 (用於 Demo 工具)
  const [parties, setParties] = useState([
    { id: 1, title: '今晚巨蛋鬥牛', status: '招募中', time: '今日 20:00', location: '桃園市桃園區 桃園巨蛋室外籃球場' },
    { id: 2, title: '假日缺一咖打牌', status: '招募中', time: '本週六 14:00', location: '桃園市中壢區 中壢車站附近桌遊店' },
    { id: 3, title: '下班輕鬆打羽球', status: '招募中', time: '明日 19:00', location: '桃園市桃園區 桃園國民運動中心' },
  ]);

  // 模擬公告資料
  const [announcements, setAnnouncements] = useState([
    { id: 1, title: '系統維護通知', content: '我們將於週日凌晨進行系統更新。', date: '2026-05-24' },
    { id: 2, title: '新場地上線！', content: '現在可以選擇「台中洲際棒球場」進行揪團囉。', date: '2026-05-20' },
  ]);

  // 模擬使用者回饋資料
  const [feedbacks, setFeedbacks] = useState([
    { id: 1, user: '運動愛好者', type: '建議', content: '希望可以增加羽球的場地篩選功能。', date: '2026-05-25', is_handled: false },
    { id: 2, user: '小白', type: '錯誤', content: '在手機版瀏覽時，發起按鈕有時候會擋到文字。', date: '2026-05-25', is_handled: false },
    { id: 3, user: '羽球控', type: '場地', content: '桃園運動中心的淋浴間最近在維修喔，建議更新資訊。', date: '2026-05-24', is_handled: false },
  ]);

  const [newVenue, setNewVenue] = useState({ name: '', city: '桃園市', district: '', facilities: '' });
  const [newAnnouncement, setNewAnnouncement] = useState({ title: '', content: '' });

  // 模擬使用者資料 (用於 Demo 工具)
  const [users, setUsers] = useState([
    { id: 1, name: '運動愛好者', reputation: 90 },
    { id: 2, name: '小白', reputation: 65 },
    { id: 3, name: '羽球控', reputation: 98 },
    { id: 4, name: '阿傑', reputation: 45 },
  ]);

  const [selectedUser, setSelectedUser] = useState(users[0]);
  const [weatherIndex, setWeatherIndex] = useState(80);

  // Demo 工具相關邏輯
  const handleUpdateReputation = (score) => {
    setUsers(users.map(u => u.id === selectedUser.id ? { ...u, reputation: score } : u));
    setSelectedUser({ ...selectedUser, reputation: score });
    alert(`玩家 ${selectedUser.name} 的信譽積分已調整為：${score}`);
  };

  const handleUpdatePartyStatus = (id, newStatus, newTime) => {
    setParties(parties.map(p => p.id === id ? { ...p, status: newStatus, time: newTime || p.time } : p));
    alert(`房間狀態已變更為：${newStatus}`);
  };

  const getReputationStatus = (score) => {
    if (score <= 40) return { label: '永久停權 (Ban Forever)', color: '#ef4444' };
    if (score <= 50) return { label: '觀察中 (重回 65, +0.5d 懲罰)', color: '#f59e0b' };
    if (score <= 60) return { label: '警告 (禁開房間)', color: '#fcd34d' };
    return { label: '狀態良好', color: '#10b981' };
  };

  const handleAddVenue = (e) => {
    e.preventDefault();
    if (!newVenue.name) return;
    const venue = {
      id: Date.now(),
      name: newVenue.name,
      city: newVenue.city,
      district: newVenue.district,
      facilities: newVenue.facilities.split(',').map(f => f.trim())
    };
    setVenues([...venues, venue]);
    setNewVenue({ name: '', city: '桃園市', district: '', facilities: '' });
    alert('場地已新增！');
  };

  const handleDeleteVenue = (id) => {
    const venueToDelete = venues.find(v => v.id === id);
    if (!venueToDelete) return;

    // 檢查是否有正在進行中的揪團使用此場地
    const isVenueInUse = parties.some(p => p.location && p.location.includes(venueToDelete.name));
    
    if (isVenueInUse) {
      alert(`無法刪除！目前有揪團正在使用「${venueToDelete.name}」。\n請先確保該場地無人使用後再嘗試刪除。`);
      return;
    }

    if (window.confirm(`確定要刪除場地「${venueToDelete.name}」嗎？`)) {
      if (window.confirm('請再次確認，刪除後將無法復原！確定要刪除嗎？')) {
        setVenues(venues.filter(v => v.id !== id));
        alert('場地已成功刪除。');
      }
    }
  };

  const handleAddAnnouncement = (e) => {
    e.preventDefault();
    if (!newAnnouncement.title) return;
    const announcement = {
      id: Date.now(),
      title: newAnnouncement.title,
      content: newAnnouncement.content,
      date: new Date().toISOString().split('T')[0]
    };
    setAnnouncements([announcement, ...announcements]);
    setNewAnnouncement({ title: '', content: '' });
    alert('公告已發佈！');
  };

  const handleDeleteAnnouncement = (id) => {
    if (window.confirm('確定要刪除此公告嗎？')) {
      setAnnouncements(announcements.filter(a => a.id !== id));
    }
  };

  return (
    <div className="admin-container" style={{ display: 'flex', minHeight: '100vh', backgroundColor: '#f8fafc' }}>
      {/* 側邊欄 */}
      <aside style={{ width: '260px', backgroundColor: '#1e293b', color: 'white', padding: '24px', display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '40px', cursor: 'pointer' }} onClick={() => navigate('/home')}>
          <div style={{ width: '32px', height: '32px', backgroundColor: '#7995a5', borderRadius: '8px', display: 'flex', justifyContent: 'center', alignItems: 'center', fontWeight: 'bold' }}>不</div>
          <span style={{ fontSize: '20px', fontWeight: '800' }}>管理後台</span>
        </div>

        <nav style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <button 
            className={`admin-nav-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <LayoutDashboard size={20} /> 數據分析
          </button>
          <button 
            className={`admin-nav-btn ${activeTab === 'venues' ? 'active' : ''}`}
            onClick={() => setActiveTab('venues')}
          >
            <MapPinned size={20} /> 場地管理
          </button>
          <button 
            className={`admin-nav-btn ${activeTab === 'announcements' ? 'active' : ''}`}
            onClick={() => setActiveTab('announcements')}
          >
            <Bell size={20} /> 系統公告
          </button>
          <button 
            className={`admin-nav-btn ${activeTab === 'feedbacks' ? 'active' : ''}`}
            onClick={() => setActiveTab('feedbacks')}
          >
            <MessageSquareText size={20} /> 使用者回饋
          </button>
          <div style={{ margin: '20px 0', borderTop: '1px solid rgba(255,255,255,0.1)' }}></div>
          <button 
            className={`admin-nav-btn ${activeTab === 'demo' ? 'active' : ''}`}
            onClick={() => setActiveTab('demo')}
            style={{ color: '#fcd34d' }}
          >
            <Wrench size={20} /> Demo 工具箱
          </button>
        </nav>

        <button 
          onClick={() => navigate('/')}
          style={{ marginTop: 'auto', display: 'flex', alignItems: 'center', gap: '8px', background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', padding: '12px' }}
        >
          <ArrowLeft size={18} /> 退出管理員
        </button>
      </aside>

      {/* 主內容區 */}
      <main style={{ flex: 1, padding: '40px', overflowY: 'auto' }}>
        
        {/* 數據分析 Tab */}
        {activeTab === 'dashboard' && (
          <div>
            <h2 style={{ marginBottom: '32px' }}>揪團數據統計</h2>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '24px', marginBottom: '40px' }}>
              <div className="stat-card" style={{ backgroundColor: 'white', padding: '24px', borderRadius: '16px', border: '1px solid #e2e8f0' }}>
                <div style={{ color: '#64748b', fontSize: '14px', fontWeight: '700', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <TrendingUp size={16} color="#7995a5" /> 今日活躍人數
                </div>
                <div style={{ fontSize: '32px', fontWeight: '800', color: '#1e293b' }}>1,284</div>
                <div style={{ color: '#10b981', fontSize: '13px', marginTop: '8px', fontWeight: '600' }}>↑ 12% 較昨日增長</div>
              </div>
              <div className="stat-card" style={{ backgroundColor: 'white', padding: '24px', borderRadius: '16px', border: '1px solid #e2e8f0' }}>
                <div style={{ color: '#64748b', fontSize: '14px', fontWeight: '700', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <BarChart3 size={16} color="#10b981" /> 進行中揪團
                </div>
                <div style={{ fontSize: '32px', fontWeight: '800', color: '#1e293b' }}>42</div>
                <div style={{ color: '#64748b', fontSize: '13px', marginTop: '8px', fontWeight: '600' }}>目前最受歡迎：籃球</div>
              </div>
              <div className="stat-card" style={{ backgroundColor: 'white', padding: '24px', borderRadius: '16px', border: '1px solid #e2e8f0' }}>
                <div style={{ color: '#64748b', fontSize: '14px', fontWeight: '700', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Bell size={16} color="#f59e0b" /> 系統訊息
                </div>
                <div style={{ fontSize: '32px', fontWeight: '800', color: '#1e293b' }}>5</div>
                <div style={{ color: '#f59e0b', fontSize: '13px', marginTop: '8px', fontWeight: '600' }}>有 3 條建議回饋</div>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '24px' }}>
              <div style={{ backgroundColor: 'white', padding: '24px', borderRadius: '16px', border: '1px solid #e2e8f0' }}>
                <h3 style={{ marginBottom: '20px' }}>近期活動熱度</h3>
                <div style={{ height: '200px', display: 'flex', alignItems: 'flex-end', gap: '12px', paddingBottom: '20px' }}>
                  {[40, 70, 45, 90, 65, 80, 50].map((h, i) => (
                    <div key={i} style={{ flex: 1, backgroundColor: '#f1f5f9', borderRadius: '4px', height: '100%', position: 'relative' }}>
                      <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, backgroundColor: '#7995a5', height: `${h}%`, borderRadius: '4px' }}></div>
                    </div>
                  ))}
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', color: '#94a3b8', fontSize: '12px' }}>
                  <span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span><span>Sun</span>
                </div>
              </div>

              <div style={{ backgroundColor: 'white', padding: '24px', borderRadius: '16px', border: '1px solid #e2e8f0' }}>
                <h3 style={{ marginBottom: '20px' }}>熱門運動比例</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  {[['籃球', '45%'], ['麻將', '25%'], ['羽球', '15%'], ['其他', '15%']].map(([name, pct], i) => (
                    <div key={i}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px', fontSize: '14px' }}>
                        <span>{name}</span><span>{pct}</span>
                      </div>
                      <div style={{ height: '8px', backgroundColor: '#f1f5f9', borderRadius: '4px' }}>
                        <div style={{ height: '100%', backgroundColor: '#7995a5', width: pct, borderRadius: '4px' }}></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 場地管理 Tab */}
        {activeTab === 'venues' && (
          <div className="admin-content">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
              <h2 style={{ margin: 0 }}>場地管理</h2>
              <button className="btn-primary" onClick={() => document.getElementById('add-venue-form').scrollIntoView({ behavior: 'smooth' })}>
                <Plus size={18} /> 新增場地
              </button>
            </div>

            <div style={{ backgroundColor: 'white', borderRadius: '16px', border: '1px solid #e2e8f0', overflow: 'hidden' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead style={{ backgroundColor: '#f1f5f9' }}>
                  <tr>
                    <th style={{ padding: '16px' }}>場地名稱</th>
                    <th style={{ padding: '16px' }}>縣市/區域</th>
                    <th style={{ padding: '16px' }}>設施</th>
                    <th style={{ padding: '16px' }}>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {venues.map(v => (
                    <tr key={v.id} style={{ borderBottom: '1px solid #e2e8f0' }}>
                      <td style={{ padding: '16px', fontWeight: '700' }}>{v.name}</td>
                      <td style={{ padding: '16px' }}>{v.city} {v.district}</td>
                      <td style={{ padding: '16px' }}>
                        <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                          {v.facilities.map((f, i) => (
                            <span key={i} style={{ fontSize: '11px', backgroundColor: '#e2e8f0', padding: '2px 6px', borderRadius: '4px' }}>{f}</span>
                          ))}
                        </div>
                      </td>
                      <td style={{ padding: '16px' }}>
                        <button onClick={() => handleDeleteVenue(v.id)} style={{ color: '#ef4444', background: 'none', border: 'none', cursor: 'pointer' }}>
                          <Trash2 size={18} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div id="add-venue-form" style={{ marginTop: '40px', backgroundColor: 'white', padding: '32px', borderRadius: '16px', border: '1px solid #e2e8f0' }}>
              <h3 style={{ marginBottom: '24px' }}>新增場地資料</h3>
              <form onSubmit={handleAddVenue} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                <div className="form-group">
                  <label className="form-label">場地名稱</label>
                  <input required type="text" className="form-input" placeholder="例如：板橋第二運動場" value={newVenue.name} onChange={e => setNewVenue({...newVenue, name: e.target.value})} />
                </div>
                <div className="form-group">
                  <label className="form-label">縣市</label>
                  <select className="form-input" value={newVenue.city} onChange={e => setNewVenue({...newVenue, city: e.target.value})}>
                    <option value="桃園市">桃園市</option>
                    <option value="台北市">台北市</option>
                    <option value="新北市">新北市</option>
                    <option value="台中市">台中市</option>
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">區域</label>
                  <input required type="text" className="form-input" placeholder="例如：板橋區" value={newVenue.district} onChange={e => setNewVenue({...newVenue, district: e.target.value})} />
                </div>
                <div className="form-group">
                  <label className="form-label">設施 (以逗號分隔)</label>
                  <input required type="text" className="form-input" placeholder="例如：冷氣, 飲水機, 廁所" value={newVenue.facilities} onChange={e => setNewVenue({...newVenue, facilities: e.target.value})} />
                </div>
                <div style={{ gridColumn: 'span 2' }}>
                  <button type="submit" className="login-button" style={{ width: '200px' }}>確認新增場地</button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* 系統公告 Tab */}
        {activeTab === 'announcements' && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
              <h2 style={{ margin: 0 }}>系統公告管理</h2>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr', gap: '32px' }}>
              {/* 發佈公告表單 */}
              <div style={{ backgroundColor: 'white', padding: '32px', borderRadius: '16px', border: '1px solid #e2e8f0', height: 'fit-content' }}>
                <h3 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}><MessageSquarePlus size={20} /> 發佈新公告</h3>
                <form onSubmit={handleAddAnnouncement}>
                  <div className="form-group">
                    <label className="form-label">公告標題</label>
                    <input required type="text" className="form-input" placeholder="輸入標題" value={newAnnouncement.title} onChange={e => setNewAnnouncement({...newAnnouncement, title: e.target.value})} />
                  </div>
                  <div className="form-group">
                    <label className="form-label">內容</label>
                    <textarea required className="form-input" rows="4" placeholder="輸入公告詳細內容..." value={newAnnouncement.content} onChange={e => setNewAnnouncement({...newAnnouncement, content: e.target.value})} style={{ resize: 'none' }}></textarea>
                  </div>
                  <button type="submit" className="login-button">發佈公告</button>
                </form>
              </div>

              {/* 已發佈公告列表 */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <h3 style={{ marginBottom: '4px' }}>已發佈公告</h3>
                {announcements.map(a => (
                  <div key={a.id} style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e2e8f0', position: 'relative' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <span style={{ fontWeight: '700', fontSize: '16px' }}>{a.title}</span>
                      <span style={{ color: '#94a3b8', fontSize: '13px' }}>{a.date}</span>
                    </div>
                    <p style={{ margin: 0, fontSize: '14px', color: '#64748b', lineHeight: '1.5', paddingRight: '40px' }}>{a.content}</p>
                    <button 
                      onClick={() => handleDeleteAnnouncement(a.id)}
                      style={{ position: 'absolute', right: '20px', top: '20px', color: '#ef4444', background: 'none', border: 'none', cursor: 'pointer' }}
                    >
                      <Trash2 size={18} />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* 使用者回饋 Tab */}
        {activeTab === 'feedbacks' && (
          <div>
            <h2 style={{ marginBottom: '32px' }}>使用者建議與回饋</h2>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              {feedbacks.filter(f => !f.is_handled).map(f => (
                <div key={f.id} style={{ backgroundColor: 'white', padding: '24px', borderRadius: '16px', border: '1px solid #e2e8f0', boxShadow: '0 2px 10px rgba(0,0,0,0.02)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <div style={{ width: '40px', height: '40px', backgroundColor: '#f1f5f9', borderRadius: '50%', display: 'flex', justifyContent: 'center', alignItems: 'center', fontWeight: 'bold', color: '#7995a5' }}>
                        {f.user.charAt(0)}
                      </div>
                      <div>
                        <div style={{ fontWeight: '700', fontSize: '15px' }}>{f.user}</div>
                        <div style={{ fontSize: '12px', color: '#94a3b8' }}>回報日期：{f.date}</div>
                      </div>
                    </div>
                    <span style={{ 
                      fontSize: '12px', 
                      fontWeight: '700', 
                      padding: '4px 10px', 
                      borderRadius: '6px',
                      backgroundColor: f.type === '錯誤' ? '#fee2e2' : (f.type === '場地' ? '#fef3c7' : '#e0f2fe'),
                      color: f.type === '錯誤' ? '#ef4444' : (f.type === '場地' ? '#d97706' : '#0284c7')
                    }}>
                      {f.type}
                    </span>
                  </div>
                  <p style={{ margin: 0, fontSize: '15px', color: '#475569', lineHeight: '1.6', paddingLeft: '52px' }}>
                    {f.content}
                  </p>
                  <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '16px', gap: '12px', alignItems: 'center' }}>
                    <button style={{ background: 'none', border: 'none', color: '#10b981', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', fontWeight: '700' }} onClick={() => {
                      setFeedbacks(feedbacks.map(fb => fb.id === f.id ? { ...fb, is_handled: true } : fb));
                    }}>
                      <CheckCircle size={18} /> 標記完成
                    </button>
                  </div>
                </div>
              ))}
              {feedbacks.filter(f => !f.is_handled).length === 0 && (
                <div style={{ textAlign: 'center', padding: '100px', color: '#94a3b8' }}>
                  目前沒有待處理的回饋。
                </div>
              )}
            </div>
          </div>
        )}

        {/* Demo 工具箱 Tab */}
        {activeTab === 'demo' && (
          <div className="admin-content">
            <h2 style={{ marginBottom: '8px', color: '#b45309' }}>🛠️ Demo 展示工具箱</h2>
            <p style={{ color: '#64748b', marginBottom: '32px' }}>這些功能僅供開發與展示使用，可快速改變系統狀態以利 Demo。</p>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px' }}>
              
              {/* 房間狀態控制 */}
              <div style={{ backgroundColor: 'white', padding: '24px', borderRadius: '16px', border: '1px solid #fcd34d' }}>
                <h3 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <MapPinned size={20} color="#b45309" /> 快速調整房間狀態
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  {parties.map(p => (
                    <div key={p.id} style={{ padding: '16px', backgroundColor: '#fffbeb', borderRadius: '12px', border: '1px solid #fef3c7' }}>
                      <div style={{ fontWeight: '700', marginBottom: '4px' }}>{p.title}</div>
                      <div style={{ fontSize: '12px', color: '#b45309', marginBottom: '12px' }}>
                        目前狀態：<span style={{ fontWeight: '800' }}>{p.status}</span> ({p.time})
                      </div>
                      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                        <button className="btn-outline" style={{ fontSize: '12px', padding: '4px 8px', borderColor: '#fcd34d' }} onClick={() => handleUpdatePartyStatus(p.id, '即將開始', '10 分鐘後')}>
                          即將開始
                        </button>
                        <button className="btn-outline" style={{ fontSize: '12px', padding: '4px 8px', borderColor: '#fcd34d' }} onClick={() => handleUpdatePartyStatus(p.id, '已開始', '進行中')}>
                          已開始
                        </button>
                        <button className="btn-outline" style={{ fontSize: '12px', padding: '4px 8px', borderColor: '#fcd34d' }} onClick={() => handleUpdatePartyStatus(p.id, '已結束', '昨天')}>
                          已結束
                        </button>
                        <button className="btn-outline" style={{ fontSize: '12px', padding: '4px 8px' }} onClick={() => handleUpdatePartyStatus(p.id, '招募中', '今日 20:00')}>
                          還原
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* 其他展示工具 */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                
                {/* 身份快速切換 */}
                <div style={{ backgroundColor: 'white', padding: '24px', borderRadius: '16px', border: '1px solid #e2e8f0' }}>
                  <h3 style={{ marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <UserCircle size={20} color="#7995a5" /> 模擬玩家信譽設定
                  </h3>
                  
                  {/* 玩家選擇 */}
                  <div className="form-group" style={{ marginBottom: '16px' }}>
                    <label className="form-label" style={{ fontSize: '13px' }}>選擇目標玩家</label>
                    <select 
                      className="form-input" 
                      value={selectedUser.id} 
                      onChange={(e) => {
                        const user = users.find(u => u.id === parseInt(e.target.value, 10));
                        setSelectedUser(user);
                      }}
                    >
                      {users.map(u => (
                        <option key={u.id} value={u.id}>{u.name} (現有積分: {u.reputation})</option>
                      ))}
                    </select>
                  </div>

                  <div style={{ padding: '12px', backgroundColor: '#f8fafc', borderRadius: '12px', marginBottom: '16px' }}>
                    <div style={{ fontSize: '14px', color: '#64748b' }}>目前選擇：<span style={{ fontWeight: '800', color: '#1e293b' }}>{selectedUser.name}</span></div>
                    <div style={{ fontSize: '14px', color: '#64748b', marginTop: '4px' }}>設定積分：<span style={{ fontWeight: '800', fontSize: '18px', color: '#1e293b' }}>{selectedUser.reputation}</span></div>
                    <div style={{ fontSize: '13px', fontWeight: '700', color: getReputationStatus(selectedUser.reputation).color, marginTop: '4px' }}>
                      系統狀態：{getReputationStatus(selectedUser.reputation).label}
                    </div>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                    <button className="btn-outline" style={{ fontSize: '13px', borderColor: '#ef4444' }} onClick={() => handleUpdateReputation(40)}>
                      40 (Ban Forever)
                    </button>
                    <button className="btn-outline" style={{ fontSize: '13px', borderColor: '#f59e0b' }} onClick={() => handleUpdateReputation(50)}>
                      50 (懲罰/觀察)
                    </button>
                    <button className="btn-outline" style={{ fontSize: '13px', borderColor: '#fcd34d' }} onClick={() => handleUpdateReputation(60)}>
                      60 (警告/禁創房)
                    </button>
                    <button className="btn-outline" style={{ fontSize: '13px', borderColor: '#10b981' }} onClick={() => handleUpdateReputation(90)}>
                      90 (恢復正常)
                    </button>
                  </div>
                </div>

                {/* 天氣/系統狀態控制 */}
                <div style={{ backgroundColor: 'white', padding: '24px', borderRadius: '16px', border: '1px solid #e2e8f0' }}>
                  <h3 style={{ marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <CloudRain size={20} color="#7995a5" /> 運動適合指數 (天氣系統)
                  </h3>
                  <div style={{ marginBottom: '20px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <span style={{ fontSize: '14px', fontWeight: '700' }}>適合程度</span>
                      <span style={{ fontSize: '16px', fontWeight: '800', color: weatherIndex > 50 ? '#10b981' : '#ef4444' }}>{weatherIndex}%</span>
                    </div>
                    <input 
                      type="range" 
                      min="0" 
                      max="100" 
                      value={weatherIndex} 
                      onChange={(e) => setWeatherIndex(parseInt(e.target.value, 10))}
                      style={{ width: '100%', cursor: 'pointer', accentColor: '#7995a5' }}
                    />
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: '#94a3b8', marginTop: '4px' }}>
                      <span>0% (暴雨危險)</span>
                      <span>100% (晴朗舒適)</span>
                    </div>
                  </div>
                  <button className="btn-outline" style={{ width: '100%' }} onClick={() => {
                    setUsers(users.map(u => ({ ...u, reputation: 90 })));
                    setSelectedUser({ ...selectedUser, reputation: 90 });
                    setWeatherIndex(80);
                    alert('系統已重置為初始狀態');
                  }}>
                    <RefreshCcw size={16} /> 重置所有 Demo 數據
                  </button>
                </div>

              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default Admin;
