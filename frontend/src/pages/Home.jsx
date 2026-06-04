import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CloudSun, MapPin, Clock, Bell, HelpCircle } from 'lucide-react';
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

  const [reputationScore, setReputationScore] = useState(100); // 模擬信譽分數
  const [showNotifications, setShowNotifications] = useState(false);
  const [showAqiInfo, setShowAqiInfo] = useState(false);
  const [notifications, setNotifications] = useState([
    { id: 1, text: '你報名的「歡樂衛生麻將局」場地已確認！', time: '10 分鐘前', read: false },
    { id: 2, text: '⏰ 系統提醒：你報名的「今晚巨蛋鬥牛」即將在 1 小時後開始，請準備出發！', time: '12 分鐘前', read: false },
    { id: 3, text: '📅 系統提醒：你報名的「週末休閒打桌球」將在明天開始，請記得準時出席喔！', time: '1 小時前', read: true },
    { id: 4, text: '系統提醒：主揪更新了揪團注意事項', time: '2 小時前', read: true }
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
    level: '不限', 
    genderLimit: '不限',
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
      genderLimit: newParty.genderLimit,
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
      level: '不限', 
      genderLimit: '不限',
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
        <div className="navbar-actions" style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <div style={{ position: 'relative' }}>
            <button 
              className="btn-outline" 
              style={{ position: 'relative', padding: '6px 10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
              onClick={() => setShowNotifications(!showNotifications)}
            >
              <Bell size={18} color="#475569" />
              {notifications.some(n => !n.read) && (
                <span style={{ position: 'absolute', top: '-2px', right: '-2px', backgroundColor: '#ef4444', width: '10px', height: '10px', borderRadius: '50%' }}></span>
              )}
            </button>
            
            {/* 通知中心下拉選單 */}
            {showNotifications && (
              <div style={{ position: 'absolute', top: '100%', right: '0', marginTop: '12px', width: '300px', backgroundColor: 'white', borderRadius: '12px', boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)', zIndex: 1000, overflow: 'hidden', border: '1px solid #e2e8f0', textAlign: 'left' }}>
                <div style={{ padding: '12px 16px', borderBottom: '1px solid #f1f5f9', fontWeight: '700', color: '#1e293b', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  通知中心
                  <span 
                    style={{ fontSize: '12px', color: '#7995a5', cursor: 'pointer', fontWeight: 'normal' }}
                    onClick={() => setNotifications(notifications.map(n => ({...n, read: true})))}
                  >
                    全部標示為已讀
                  </span>
                </div>
                <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                  {notifications.length > 0 ? (
                    notifications.map(n => (
                      <div 
                        key={n.id} 
                        style={{ padding: '12px 16px', borderBottom: '1px solid #f8fafc', display: 'flex', gap: '12px', cursor: 'pointer', backgroundColor: n.read ? 'white' : '#f0f9ff' }}
                        onClick={() => {
                          setNotifications(notifications.map(item => item.id === n.id ? {...item, read: true} : item));
                        }}
                      >
                        <div style={{ width: '8px', display: 'flex', justifyContent: 'center', paddingTop: '6px' }}>
                          {!n.read && <div style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#0284c7' }}></div>}
                        </div>
                        <div style={{ flex: 1 }}>
                          <p style={{ margin: '0 0 4px 0', fontSize: '13px', color: n.read ? '#64748b' : '#0f172a', lineHeight: '1.4' }}>{n.text}</p>
                          <p style={{ margin: 0, fontSize: '11px', color: '#94a3b8' }}>{n.time}</p>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div style={{ padding: '24px', textAlign: 'center', color: '#94a3b8', fontSize: '13px' }}>目前沒有新通知</div>
                  )}
                </div>
              </div>
            )}
          </div>

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
              <span>桃園市 26°C</span>
              <div 
                style={{ position: 'relative', marginLeft: '8px', paddingLeft: '12px', borderLeft: '1px solid #cbd5e1', color: '#64748b', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '4px' }}
                onMouseEnter={() => setShowAqiInfo(true)}
                onMouseLeave={() => setShowAqiInfo(false)}
              >
                <span>空氣品質 (AQI)：45</span>
                <HelpCircle size={14} style={{ cursor: 'pointer', color: '#94a3b8' }} />
                
                {showAqiInfo && (
                  <div style={{ position: 'absolute', top: '100%', left: '50%', transform: 'translateX(-50%)', marginTop: '8px', width: '360px', backgroundColor: '#1e293b', color: 'white', padding: '16px', borderRadius: '8px', fontSize: '13px', fontWeight: 'normal', zIndex: 10, boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)', lineHeight: '1.5', cursor: 'default' }}>
                    <div style={{ fontWeight: 'bold', fontSize: '16px', marginBottom: '16px' }}>空氣品質指標 (AQI) 與建議</div>
                    
                    <div style={{ display: 'grid', gridTemplateColumns: '70px 80px 1fr', gap: '12px', marginBottom: '8px', color: '#94a3b8', fontSize: '13px' }}>
                      <div>AQI 區間</div>
                      <div>空氣品質</div>
                      <div>活動建議</div>
                    </div>
                    
                    <div style={{ display: 'grid', gridTemplateColumns: '70px 80px 1fr', gap: '12px', padding: '12px 0', borderTop: '1px solid #334155' }}>
                      <div>0 - 50</div>
                      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '6px' }}><span style={{ color: '#22c55e', fontSize: '14px', lineHeight: '1' }}>●</span> 良好</div>
                      <div style={{ color: '#e2e8f0' }}>空氣品質極佳，非常適合戶外活動。</div>
                    </div>
                    
                    <div style={{ display: 'grid', gridTemplateColumns: '70px 80px 1fr', gap: '12px', padding: '12px 0', borderTop: '1px solid #334155' }}>
                      <div>51 - 100</div>
                      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '6px' }}><span style={{ color: '#eab308', fontSize: '14px', lineHeight: '1' }}>●</span> 普通</div>
                      <div style={{ color: '#e2e8f0' }}>空氣品質尚可，極少數敏感族群可能產生症狀。</div>
                    </div>
                    
                    <div style={{ display: 'grid', gridTemplateColumns: '70px 80px 1fr', gap: '12px', padding: '12px 0', borderTop: '1px solid #334155' }}>
                      <div>101 - 150</div>
                      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '6px' }}><span style={{ color: '#f97316', fontSize: '14px', lineHeight: '1' }}>●</span> 敏感族群<br/>不健康</div>
                      <div style={{ color: '#e2e8f0' }}>敏感族群可能會產生健康影響，應減少戶外劇烈活動。</div>
                    </div>
                    
                    <div style={{ display: 'grid', gridTemplateColumns: '70px 80px 1fr', gap: '12px', padding: '12px 0', borderTop: '1px solid #334155' }}>
                      <div>151 - 200</div>
                      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '6px' }}><span style={{ color: '#ef4444', fontSize: '14px', lineHeight: '1' }}>●</span> 所有族群<br/>不健康</div>
                      <div style={{ color: '#e2e8f0' }}>對所有人的健康開始產生影響，應減少戶外活動。</div>
                    </div>
                    
                    <div style={{ position: 'absolute', top: '-4px', left: '50%', transform: 'translateX(-50%)', width: '8px', height: '8px', backgroundColor: '#1e293b', borderRadius: '2px', rotate: '45deg' }}></div>
                  </div>
                )}
              </div>
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
                    {party.genderLimit && party.genderLimit !== '不限' && (
                      <span className="party-level">{party.genderLimit}</span>
                    )}
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
                    {party.participants[0] === '我 (主揪)' || party.participants[0] === '主揪人' ? '管理' : isFull && isWaitlistFull ? '查看詳情' : isFull ? '排候補' : '報名參加'}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </main>

      {/* 右下角浮動發起按鈕 */}
      <div className="fab-container">
        <button className="fab-btn" onClick={() => {
          if (reputationScore <= 60) {
            alert(`⚠️ 你的信譽分數過低（目前：${reputationScore}分），已遭到警告，目前無法發起新揪團。請保持良好參與紀錄以恢復信譽。`);
            return;
          }
          setIsModalOpen(true);
        }}>
          <span className="fab-icon">+</span>
          發起揪團
        </button>
      </div>

      {/* 發起揪團 Modal */}
      {isModalOpen && (
        <div className="modal-overlay" onClick={() => setIsModalOpen(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()} style={{ maxWidth: '750px', maxHeight: '90vh', overflowY: 'auto' }}>
            <div className="modal-header">
              <h3>發起新揪團</h3>
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
                      <option value="不限">不限</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">性別限制</label>
                    <div style={{ display: 'flex', gap: '12px' }}>
                      <button type="button" className={`role-btn ${newParty.genderLimit === '不限' ? 'active' : ''}`} style={{ flex: 1, border: '1px solid #e2e8f0', padding: '8px' }} onClick={() => setNewParty({...newParty, genderLimit: '不限'})}>不限</button>
                      <button type="button" className={`role-btn ${newParty.genderLimit === '限男' ? 'active' : ''}`} style={{ flex: 1, border: '1px solid #e2e8f0', padding: '8px' }} onClick={() => setNewParty({...newParty, genderLimit: '限男'})}>限男</button>
                      <button type="button" className={`role-btn ${newParty.genderLimit === '限女' ? 'active' : ''}`} style={{ flex: 1, border: '1px solid #e2e8f0', padding: '8px' }} onClick={() => setNewParty({...newParty, genderLimit: '限女'})}>限女</button>
                    </div>
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
                  <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
                    人數需求 (最少 ~ 最多)
                  </label>
                  <div style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '8px' }}>* 請填寫包含主揪在內的總人數！</div>
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
