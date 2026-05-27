import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CloudSun, MapPin, Clock } from 'lucide-react';
import '../App.css';

function Home() {
  const navigate = useNavigate();

  // 模擬大廳假資料
  const [parties, setParties] = useState([
    { id: 1, title: '今晚巨蛋鬥牛', type: '籃球', level: '高手', time: '今晚 20:00', location: '桃園市桃園區 桃園巨蛋室外籃球場', facilities: ['飲水機', '廁所'], currentPlayers: 5, maxPlayers: 6, currentWaitlist: 0, maxWaitlist: 2, participants: ['阿傑', '小明', '老王', '建國', '阿翔'], waitlist: [] },
    { id: 2, title: '假日缺一咖打牌', type: '麻將', level: '休閒', time: '本週六 14:00', location: '桃園市中壢區 中壢車站附近桌遊店', facilities: ['冷氣', '飲水機', '廁所'], currentPlayers: 4, maxPlayers: 4, currentWaitlist: 1, maxWaitlist: 2, participants: ['主揪A', '玩家B', '玩家C', '玩家D'], waitlist: ['候補仔'] },
    { id: 3, title: '下班輕鬆打羽球', type: '羽球', level: '新手', time: '明天 19:00', location: '桃園市桃園區 桃園國民運動中心', facilities: ['冷氣', '飲水機', '廁所', '淋浴間'], currentPlayers: 2, maxPlayers: 4, currentWaitlist: 0, maxWaitlist: 2, participants: ['羽球控', '小白'], waitlist: [] },
    { id: 4, title: '週末休閒打桌球', type: '桌球', level: '休閒', time: '週日 10:00', location: '桃園市平鎮區 平鎮國民運動中心', facilities: ['冷氣', '飲水機', '廁所', '淋浴間'], currentPlayers: 1, maxPlayers: 2, currentWaitlist: 0, maxWaitlist: 2, participants: ['桌球大師'], waitlist: [] },
    { id: 5, title: '虎頭山排球友誼賽', type: '排球', level: '休閒', time: '週六 16:00', location: '桃園市龜山區 桃園虎頭山公園', facilities: ['廁所'], currentPlayers: 12, maxPlayers: 12, currentWaitlist: 2, maxWaitlist: 2, participants: ['P1','P2','P3','P4','P5','P6','P7','P8','P9','P10','P11','P12'], waitlist: ['W1', 'W2'] },
  ]);

  // 台灣行政區與球場資料 (縣市 -> 區域 -> 球場)
  const taiwanRegions = {
    '桃園市': {
      '桃園區': ['桃園國民運動中心', '桃園巨蛋室外籃球場', '陽明運動公園', '其他'],
      '中壢區': ['中壢國民運動中心', '中原大學體育館', '中壢車站附近桌遊店', '其他'],
      '平鎮區': ['平鎮國民運動中心', '新勢公園籃球場', '其他'],
      '蘆竹區': ['蘆竹國民運動中心', '光明河濱公園', '其他'],
      '龜山區': ['桃園虎頭山公園', '長庚大學體育館', '其他'],
      '其他區': ['其他']
    },
    '台北市': {
      '大安區': ['大安運動中心', '台大體育館', '和平東路球場', '其他'],
      '信義區': ['信義運動中心', '象山公園球場', '其他'],
      '中山區': ['中山運動中心', '新生公園', '其他'],
      '內湖區': ['內湖運動中心', '彩虹河濱公園', '其他'],
      '其他區': ['其他']
    },
    '新北市': {
      '板橋區': ['板橋體育館', '板橋國民運動中心', '板橋羽球館', '其他'],
      '新莊區': ['新莊體育館', '新莊國民運動中心', '其他'],
      '三重區': ['三重國民運動中心', '三重球場', '其他'],
      '中和區': ['中和運動中心', '錦和運動公園', '其他'],
      '其他區': ['其他']
    },
    '台中市': {
      '西屯區': ['台中市政府球場', '逢甲大學體育館', '台中陽光球場', '其他'],
      '北屯區': ['台中洲際棒球場', '北屯球場', '其他'],
      '其他區': ['其他']
    }
  };

  // 場地設施資料庫
  const venueFacilities = {
    '桃園國民運動中心': ['冷氣', '飲水機', '廁所', '淋浴間'],
    '桃園巨蛋室外籃球場': ['飲水機', '廁所'],
    '中壢國民運動中心': ['冷氣', '飲水機', '廁所', '淋浴間'],
    '平鎮國民運動中心': ['冷氣', '飲水機', '廁所', '淋浴間'],
    '蘆竹國民運動中心': ['冷氣', '飲水機', '廁所', '淋浴間'],
    '大安運動中心': ['冷氣', '飲水機', '廁所', '淋浴間'],
    '信義運動中心': ['冷氣', '飲水機', '廁所', '淋浴間'],
    '中山運動中心': ['冷氣', '飲水機', '廁所', '淋浴間'],
    '內湖運動中心': ['冷氣', '飲水機', '廁所', '淋浴間'],
    '板橋國民運動中心': ['冷氣', '飲水機', '廁所', '淋浴間'],
    '新莊國民運動中心': ['冷氣', '飲水機', '廁所', '淋浴間'],
    '三重國民運動中心': ['冷氣', '飲水機', '廁所', '淋浴間'],
    '中和運動中心': ['冷氣', '飲水機', '廁所', '淋浴間'],
    '台中市政府球場': ['飲水機', '廁所'],
    '逢甲大學體育館': ['冷氣', '飲水機', '廁所'],
    '中原大學體育館': ['冷氣', '飲水機', '廁所'],
    '長庚大學體育館': ['冷氣', '飲水機', '廁所'],
    '台大體育館': ['冷氣', '飲水機', '廁所'],
    '新勢公園籃球場': ['飲水機', '廁所'],
    '光明河濱公園': ['廁所'],
    '陽明運動公園': ['廁所'],
    '桃園虎頭山公園': ['廁所'],
    '象山公園球場': ['飲水機', '廁所'],
    '新生公園': ['廁所'],
    '彩虹河濱公園': ['廁所'],
    '其他': ['基本設施']
  };

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isFeedbackOpen, setIsFeedbackOpen] = useState(false);
  const [feedback, setFeedback] = useState({ type: '建議', content: '' });
  const [selectedFilterRegion, setSelectedFilterRegion] = useState('all');
  const [selectedCategory, setSelectedCategory] = useState('全部');
  const [newParty, setNewParty] = useState({ 
    title: '', 
    type: '籃球', 
    level: '休閒', 
    city: '桃園市', 
    district: '桃園區', 
    venue: '桃園國民運動中心',
    note: '', 
    description: '',
    isFree: true,
    price: '',
    time: '', 
    duration: '2 小時',
    minPlayers: 2,
    maxPlayers: 4 
  });

  const handleLogout = () => {
    navigate('/');
  };

  const handleSendFeedback = (e) => {
    e.preventDefault();
    console.log('Feedback submitted:', feedback);
    alert('感謝您的回饋！管理員將會盡快查看。');
    setIsFeedbackOpen(false);
    setFeedback({ type: '建議', content: '' });
  };

  const handleCreateParty = (e) => {
    e.preventDefault();

    // 費用驗證
    if (!newParty.isFree) {
      const priceNum = parseFloat(newParty.price);
      if (priceNum < 0 || priceNum > 10000) {
        alert('費用金額必須在 0 到 10,000 之間喔！');
        return;
      }
    }

    const venueDisplay = newParty.venue === '其他' ? '' : newParty.venue;
    const fullLocation = `${newParty.city}${newParty.district} ${venueDisplay} ${newParty.note}`.trim();
    
    const priceDisplay = newParty.isFree ? '免費' : (newParty.price ? `$${newParty.price} (總額分攤)` : '面議');
    
    const party = {
      id: Date.now(),
      title: newParty.title,
      type: newParty.type,
      level: newParty.level,
      time: newParty.time.replace('T', ' '),
      duration: newParty.duration,
      location: fullLocation,
      price: priceDisplay,
      currentPlayers: 1, // 發起人自己
      minPlayers: parseInt(newParty.minPlayers, 10),
      maxPlayers: parseInt(newParty.maxPlayers, 10),
      currentWaitlist: 0,
      maxWaitlist: 2,
      participants: ['我 (主揪)'],
      waitlist: [],
      facilities: venueFacilities[newParty.venue] || ['基本設施'],
      description: newParty.description || '這是我剛發起的揪團，歡迎大家來玩！'
    };
    setParties([party, ...parties]);
    setIsModalOpen(false);
    setNewParty({ 
      title: '', 
      type: '籃球', 
      level: '休閒', 
      city: '桃園市', 
      district: '桃園區', 
      venue: '桃園國民運動中心',
      note: '', 
      description: '',
      isFree: true,
      price: '',
      time: '', 
      duration: '2 小時',
      minPlayers: 2,
      maxPlayers: 4 
    });
  };

  const handleCityChange = (e) => {
    const selectedCity = e.target.value;
    const firstDistrict = Object.keys(taiwanRegions[selectedCity])[0];
    const firstVenue = taiwanRegions[selectedCity][firstDistrict][0];
    setNewParty({
      ...newParty,
      city: selectedCity,
      district: firstDistrict,
      venue: firstVenue
    });
  };

  const handleDistrictChange = (e) => {
    const selectedDistrict = e.target.value;
    const firstVenue = taiwanRegions[newParty.city][selectedDistrict][0];
    setNewParty({
      ...newParty,
      district: selectedDistrict,
      venue: firstVenue
    });
  };

  return (
    <div className="home-container">
      {/* 導覽列 */}
      <nav className="navbar">
        <div className="navbar-logo">不揪ㄛ</div>
        <div className="navbar-actions">
          <button className="btn-outline" onClick={() => setIsFeedbackOpen(true)}>意見回饋</button>
          <button className="btn-primary" onClick={() => navigate('/profile')}>個人</button>
          <button className="btn-outline" onClick={handleLogout}>登出</button>
        </div>
      </nav>

      {/* 內容區塊 */}
      <main className="main-content">
        <div className="content-header">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h2 style={{ marginBottom: 0 }}>揪團大廳</h2>
            <div className="weather-widget">
              <span className="weather-icon" style={{ display: 'flex' }}><CloudSun size={18} /></span>
              <span>桃園市 26°C 適合運動的好天氣</span>
            </div>
          </div>
          <div style={{ display: 'flex', gap: '16px', alignItems: 'center', flexWrap: 'wrap' }}>
            <select className="region-select" value={selectedFilterRegion} onChange={e => setSelectedFilterRegion(e.target.value)}>
              <option value="all">所有地區</option>
              {Object.keys(taiwanRegions).map(city => (
                <option key={city} value={city}>{city}</option>
              ))}
            </select>
            <div className="filter-chips">
              {['全部', '籃球', '麻將', '桌球', '羽球', '排球'].map(cat => (
                <span 
                  key={cat} 
                  className={`chip ${selectedCategory === cat ? 'active' : ''}`}
                  onClick={() => setSelectedCategory(cat)}
                  style={{ cursor: 'pointer' }}
                >
                  {cat}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* 卡片列表 */}
        <div className="party-grid">
          {parties
            .filter(party => selectedFilterRegion === 'all' || party.location.includes(selectedFilterRegion))
            .filter(party => selectedCategory === '全部' || party.type === selectedCategory)
            .map(party => {
            const isFull = party.currentPlayers >= party.maxPlayers;
            const isWaitlistFull = party.currentWaitlist >= party.maxWaitlist;
            let statusText = `缺 ${party.maxPlayers - party.currentPlayers} 人`;
            let statusColor = '#ef4444'; // Red

            if (isFull && isWaitlistFull) {
              statusText = '已完全額滿';
              statusColor = '#94a3b8'; // Gray
            } else if (isFull) {
              statusText = `候補 ${party.currentWaitlist}/${party.maxWaitlist}`;
              statusColor = '#f59e0b'; // Orange
            }

            return (
              <div key={party.id} className="party-card clickable-card" onClick={() => navigate(`/party/${party.id}`, { state: { party } })}>
                <div className="party-card-header">
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <span className="party-type">{party.type}</span>
                    <span className="party-level">{party.level}</span>
                  </div>
                  <span className="party-status" style={{ color: statusColor }}>{statusText}</span>
                </div>
                <h3 className="party-title">{party.title}</h3>
                <div className="party-info">
                  <p style={{ gap: '6px' }}><MapPin size={16} /> {party.location}</p>
                  <p style={{ gap: '6px' }}><Clock size={16} /> {party.time}</p>
                </div>
                <div className="party-card-footer">
                  <span className="player-count">目前人數: {party.currentPlayers} / {party.maxPlayers}</span>
                  <button className="btn-join" onClick={(e) => {
                    e.stopPropagation();
                    navigate(`/party/${party.id}`, { state: { party } });
                  }}>
                    {isFull && isWaitlistFull ? '查看詳情' : isFull ? '排候補' : '報名參加'}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </main>

      {/* 右下角浮動發起按鈕 */}
      <div className="fab-container">
        <button className="fab-btn" onClick={() => setIsModalOpen(true)}>
          <span className="fab-icon">+</span>
          發起揪團
        </button>
      </div>

      {/* 發起揪團 Modal */}
      {isModalOpen && (
        <div className="modal-overlay" onClick={() => setIsModalOpen(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()} style={{ maxWidth: '750px' }}>
            <div className="modal-header">
              <h3>發起新揪團</h3>
              <button className="modal-close" onClick={() => setIsModalOpen(false)}>×</button>
            </div>
            <form onSubmit={handleCreateParty}>
              <div className="form-group">
                <label className="form-label">揪團標題</label>
                <input required type="text" className="form-input" placeholder="例如：今晚巨蛋鬥牛缺二" value={newParty.title} onChange={e => setNewParty({...newParty, title: e.target.value})} />
              </div>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 24px' }}>
                {/* 左欄：活動細節 */}
                <div>
                  <div className="form-group">
                    <label className="form-label">活動類型</label>
                    <select className="form-input" value={newParty.type} onChange={e => setNewParty({...newParty, type: e.target.value})}>
                      <option value="籃球">籃球</option>
                      <option value="麻將">麻將</option>
                      <option value="桌球">桌球</option>
                      <option value="羽球">羽球</option>
                      <option value="排球">排球</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">程度</label>
                    <select className="form-input" value={newParty.level} onChange={e => setNewParty({...newParty, level: e.target.value})}>
                      <option value="新手">新手</option>
                      <option value="休閒">休閒</option>
                      <option value="高手">高手</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">活動時間</label>
                    <input type="datetime-local" className="form-input" value={newParty.time} onChange={e => setNewParty({...newParty, time: e.target.value})} required />
                  </div>
                  <div className="form-group">
                    <label className="form-label">預計時長</label>
                    <select className="form-input" value={newParty.duration} onChange={e => setNewParty({...newParty, duration: e.target.value})}>
                      <option value="1 小時">1 小時</option>
                      <option value="1.5 小時">1.5 小時</option>
                      <option value="2 小時">2 小時</option>
                      <option value="2.5 小時">2.5 小時</option>
                      <option value="3 小時">3 小時</option>
                      <option value="4 小時">4 小時</option>
                      <option value="5 小時">5 小時</option>
                    </select>
                  </div>
                </div>

                {/* 右欄：地點資訊 */}
                <div>
                  <div className="form-group">
                    <label className="form-label">地點 (縣市)</label>
                    <select className="form-input" value={newParty.city} onChange={handleCityChange}>
                      {Object.keys(taiwanRegions).map(city => (
                        <option key={city} value={city}>{city}</option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">地點 (區域)</label>
                    <select className="form-input" value={newParty.district} onChange={handleDistrictChange}>
                      {Object.keys(taiwanRegions[newParty.city]).map(dist => (
                        <option key={dist} value={dist}>{dist}</option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">地點 (場館/球場)</label>
                    <select className="form-input" value={newParty.venue} onChange={e => setNewParty({...newParty, venue: e.target.value})}>
                      {taiwanRegions[newParty.city][newParty.district].map(v => (
                        <option key={v} value={v}>{v}</option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">詳細地點說明 (選填)</label>
                    <input type="text" className="form-input" placeholder="例如：第 3 面場地、或是具體路口" value={newParty.note} onChange={e => setNewParty({...newParty, note: e.target.value})} />
                  </div>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
                <div className="form-group">
                  <label className="form-label">人數需求 (最少 ~ 最多)</label>
                  <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                    <input required type="number" min="1" max="20" className="form-input" value={newParty.minPlayers} onChange={e => setNewParty({...newParty, minPlayers: e.target.value})} />
                    <span style={{ color: '#64748b' }}>~</span>
                    <input required type="number" min="2" max="20" className="form-input" value={newParty.maxPlayers} onChange={e => setNewParty({...newParty, maxPlayers: e.target.value})} />
                  </div>
                </div>
                <div className="form-group">
                  <label className="form-label">入場費 / 費用</label>
                  <div style={{ display: 'flex', gap: '12px', marginBottom: '8px' }}>
                    <button 
                      type="button" 
                      className={`role-btn ${newParty.isFree ? 'active' : ''}`} 
                      style={{ border: '1px solid #e2e8f0', flex: 1 }}
                      onClick={() => setNewParty({...newParty, isFree: true})}
                    >
                      免費
                    </button>
                    <button 
                      type="button" 
                      className={`role-btn ${!newParty.isFree ? 'active' : ''}`} 
                      style={{ border: '1px solid #e2e8f0', flex: 1 }}
                      onClick={() => setNewParty({...newParty, isFree: false})}
                    >
                      付費 / 均分
                    </button>
                  </div>
                  {!newParty.isFree && (
                    <input 
                      type="number" 
                      className="form-input" 
                      placeholder="輸入總額(自動平分)" 
                      value={newParty.price} 
                      onChange={e => setNewParty({...newParty, price: e.target.value})}
                      min="0"
                      max="10000"
                      required
                    />
                  )}
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">揪團說明 / 備註 (選填)</label>
                <textarea 
                  className="form-input" 
                  rows="3" 
                  placeholder="寫下你的規則、或想對大家說的話..." 
                  value={newParty.description} 
                  onChange={e => setNewParty({...newParty, description: e.target.value})}
                  style={{ resize: 'none' }}
                />
              </div>

              <button type="submit" className="login-button" style={{ marginTop: '16px' }}>確認發起</button>
            </form>
          </div>
        </div>
      )}

      {/* 意見回饋 Modal */}
      {isFeedbackOpen && (
        <div className="modal-overlay" onClick={() => setIsFeedbackOpen(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>意見回饋</h3>
              <button className="modal-close" onClick={() => setIsFeedbackOpen(false)}>×</button>
            </div>
            <form onSubmit={handleSendFeedback}>
              <div className="form-group">
                <label className="form-label">回饋類型</label>
                <select className="form-input" value={feedback.type} onChange={e => setFeedback({...feedback, type: e.target.value})}>
                  <option value="建議">功能建議</option>
                  <option value="錯誤">問題回報 (Bug)</option>
                  <option value="場地">場地相關</option>
                  <option value="其他">其他</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">內容說明</label>
                <textarea 
                  required 
                  className="form-input" 
                  rows="5" 
                  placeholder="請詳細描述您的想法或遇到的問題..." 
                  value={feedback.content} 
                  onChange={e => setFeedback({...feedback, content: e.target.value})}
                  style={{ resize: 'none' }}
                />
              </div>
              <button type="submit" className="login-button" style={{ marginTop: '10px' }}>送出回饋</button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default Home;
