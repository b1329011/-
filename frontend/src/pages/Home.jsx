import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { CloudSun, MapPin, Clock, Bell, HelpCircle, Star } from 'lucide-react';
import gamesApi from '../api/games';
import notificationsApi from '../api/notifications';
import weatherApi from '../api/weather';
import adminApi from '../api/admin';
import usersApi from '../api/users';
import venuesApi from '../api/venues';
import '../App.css';

function Home() {
  const navigate = useNavigate();

  // 狀態與 API 資料
  const [parties, setParties] = useState([]);
  const [reputationScore, setReputationScore] = useState(100);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showAqiInfo, setShowAqiInfo] = useState(false);
  const [showLevelInfo, setShowLevelInfo] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [aqi, setAqi] = useState('--');
  const [temperature, setTemperature] = useState('--');
  const [isPageLoading, setIsPageLoading] = useState(true);
  const [userProfile, setUserProfile] = useState(null);

  // 動態場地資料狀態
  const [allVenues, setAllVenues] = useState([]); // [{id, name, city, dist, sports, facilities}]
  const [taiwanRegions, setTaiwanRegions] = useState({
    '未選擇': { '未選擇': ['無場地'] }
  });
  const [venueFacilities, setVenueFacilities] = useState({});
  const [venueMap, setVenueMap] = useState({});

  // 載入初始資料
  useEffect(() => {
    const fetchData = async () => {
      try {
        // 並行取得多個 API，使用 allSettled 避免其中一個壞掉導致全掛
        const results = await Promise.allSettled([
          gamesApi.getGames(),
          notificationsApi.getNotifications(),
          weatherApi.getWeatherAqi(),
          usersApi.getUserProfile(),
          venuesApi.getCourts()
        ]);
        
        const gamesResult = results[0].status === 'fulfilled' ? results[0].value : [];
        const notificationsResult = results[1].status === 'fulfilled' ? results[1].value : [];
        const weatherResult = results[2].status === 'fulfilled' ? results[2].value : {};
        const userProfileResult = results[3].status === 'fulfilled' ? results[3].value : null;
        const venuesResult = results[4].status === 'fulfilled' ? results[4].value : [];
        
        if (userProfileResult) {
          setUserProfile(userProfileResult);
        }

        const venuesList = Array.isArray(venuesResult) ? venuesResult : (venuesResult.results || []);
        if (venuesList.length > 0) {
          const venueDict = {};
          
          // Aggregate courts into unique venues
          venuesList.forEach(court => {
            if (!court.venue_detail) return;
            const v = court.venue_detail;
            if (!venueDict[v.id]) {
              venueDict[v.id] = {
                id: v.id,
                name: v.name,
                city: v.address_detail?.city || '未分類縣市',
                district: v.address_detail?.district || '未分類區域',
                facilities: v.facilities || [],
                sports: new Set()
              };
            }
            if (court.sports && Array.isArray(court.sports)) {
              court.sports.forEach(s => venueDict[v.id].sports.add(s));
            }
          });
          
          const aggregatedVenues = Object.values(venueDict).map(v => ({
            ...v,
            sports: Array.from(v.sports)
          }));
          
          setAllVenues(aggregatedVenues);
        }

        const reverseLevelMap = {
          'C': '休閒',
          'B': '業餘',
          'A': '高手',
          'S': '高手',
          '新手': '休閒',
          '休閒': '休閒',
          '高手': '高手'
        };

        // 處理後端 API 欄位命名與前端元件不一致的問題 (snake_case vs camelCase)
        const formattedGames = (Array.isArray(gamesResult) ? gamesResult : gamesResult.results || []).map(party => {
          const rawType = party.type || party.sport_type || party.sport_name || '運動';
          const originalLevel = party.level || party.target_level || 'C';
          const rawLevel = reverseLevelMap[originalLevel] || originalLevel;
          let venueStatus = 'pending';
          if (party.booking_status === '已佔到/已預約') {
            venueStatus = 'confirmed';
          } else if (party.booking_status === '未佔到/未預約') {
            venueStatus = 'failed';
          }
          
          return {
            ...party,
            id: party.id,
            venueStatus: venueStatus,
            title: party.game_name || party.title || party.description?.substring(0, 10) || '無標題揪團',
            type: rawType,
            level: rawLevel,
            genderLimit: party.genderLimit || party.gender_limit || '不限',
            location: party.location || party.venue_name || (party.venue_id ? `場地 ID: ${party.venue_id}` : '地點未定'),
            time: party.time || (party.booking_date ? `${party.booking_date} ${party.time_slot || ''}` : '時間未定'),
            currentPlayers: party.currentPlayers ?? party.current_players ?? 0,
            maxPlayers: party.maxPlayers ?? party.most_players ?? party.max_players ?? 6,
            currentWaitlist: party.currentWaitlist ?? party.current_waitlist ?? 0,
            maxWaitlist: party.maxWaitlist ?? party.max_waitlist ?? 2,
            description: party.game_note || party.description,
            game_note: party.game_note,
            participants: party.participants || [],
            participant_ids: party.participant_ids || [],
            waitlist_ids: party.waitlist_ids || [],
            creator_id: party.creator_id,
          };
        });
        
        setParties(formattedGames);
        const mappedNotifications = (Array.isArray(notificationsResult) ? notificationsResult : []).map(n => ({
          id: n.notification_id || n.id,
          text: n.message || n.text || '',
          read: n.is_read !== undefined ? n.is_read : (n.read || false),
          time: n.created_at ? new Date(n.created_at).toLocaleString('zh-TW', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }) : (n.time || ''),
          match_id: n.match_id || n.game_id
        }));

        const validNotifications = mappedNotifications.filter(n => {
          if (n.text && n.text.includes('場地狀態已更新')) {
            const currentUserId = localStorage.getItem('user_id');
            const party = formattedGames.find(g => g.id === n.match_id);
            const isHost = party ? (party.creator_id === currentUserId || party.creator === currentUserId) : false;
            if (isHost) return false;
          }
          return true;
        });
        setNotifications(validNotifications);
        setAqi(weatherResult?.aqi ?? '--');
        setTemperature(weatherResult?.temperature ?? '--');
      } catch (error) {
        console.error('Home fetchData error:', error);
      } finally {
        setIsPageLoading(false);
      }
    };

    fetchData();
  }, []);


  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isFeedbackOpen, setIsFeedbackOpen] = useState(false);
  const [feedback, setFeedback] = useState({ type: '建議', content: '' });
  const [selectedFilterRegion, setSelectedFilterRegion] = useState('all');
  const [selectedCategory, setSelectedCategory] = useState('全部');
  const [newParty, setNewParty] = useState({ 
    title: '', 
    type: '籃球', 
    level: '休閒', 
    genderLimit: '不限',
    city: '桃園市', 
    district: '桃園區', 
    venue: '桃園國民運動中心',
    note: '', 
    description: '',
    price: '',
    time: '', 
    duration: '2 小時',
    minPlayers: 2,
    maxPlayers: 4 
  });

  const handleLogout = () => {
    navigate('/');
  };

  const handleSendFeedback = async (e) => {
    e.preventDefault();
    try {
      await adminApi.submitFeedback(feedback);
      alert('感謝您的回饋！管理員將會盡快查看。');
      setIsFeedbackOpen(false);
      setFeedback({ type: '建議', content: '' });
    } catch (error) {
      console.error('Feedback error:', error);
      alert('送出失敗，請稍後再試。');
    }
  };

  const handleCreateParty = async (e) => {
    e.preventDefault();

    if (newParty.genderLimit && newParty.genderLimit !== '不限') {
      const userGender = userProfile?.gender || '未公開';
      if (
        (newParty.genderLimit === '限男' && userGender !== '男') ||
        (newParty.genderLimit === '限女' && userGender !== '女')
      ) {
        alert(`主揪性別為「${userGender}」，無法發起「${newParty.genderLimit}」的揪團！`);
        return;
      }
    }

    // 檢查時間驗證
    const selectedTime = new Date(newParty.time);
    const now = new Date();
    if (selectedTime < now) {
      alert('活動時間不能設定在過去喔！');
      return;
    }

    const priceNum = parseFloat(newParty.price);
    if (isNaN(priceNum) || priceNum < 0 || priceNum > 10000) {
      alert('費用金額必須在 0 到 10,000 之間喔！');
      return;
    }

    // 程度驗證
    const rankValue = { 'C': 1, 'B': 2, 'A': 3, 'S': 4 };
    const requiredRank = {
      '休閒': 1,
      '業餘': 2,
      '高手': 3
    };
    const userLevels = userProfile?.levels || {};
    const userLevelInSport = userLevels[newParty.type] || 'C'; // 若未設定則預設為最低 C

    if (rankValue[userLevelInSport] < requiredRank[newParty.level]) {
      alert(`你的${newParty.type}程度為 ${userLevelInSport}，無法發起${newParty.level}喔！`);
      return;
    }

    const sportMap = {
      '籃球': 1,
      '羽球': 2,
      '排球': 3,
      '桌球': 4,
      '麻將': 5
    };

    const levelMap = {
      '休閒': 'C',
      '業餘': 'B',
      '高手': 'A'
    };

    const venue_id = venueMap[newParty.venue] || 1;

    // 計算時間
    const dateObj = new Date(newParty.time);
    const booking_date = dateObj.toISOString().split('T')[0]; // "YYYY-MM-DD"
    const startHour = dateObj.getHours().toString().padStart(2, '0');
    const startMin = dateObj.getMinutes().toString().padStart(2, '0');
    
    // Parse duration "2 小時" or "1.5 小時"
    const durationHours = parseFloat(newParty.duration);
    const endDateObj = new Date(dateObj.getTime() + durationHours * 60 * 60 * 1000);
    const endHour = endDateObj.getHours().toString().padStart(2, '0');
    const endMin = endDateObj.getMinutes().toString().padStart(2, '0');
    
    const time_slot = `${startHour}:${startMin}-${endHour}:${endMin}`;

    const payload = {
      sport_id: sportMap[newParty.type] || 1,
      venue_id: venue_id,
      most_players: parseInt(newParty.maxPlayers, 10),
      least_players: parseInt(newParty.minPlayers, 10),
      target_level: newParty.level || '休閒',
      booking_date: booking_date,
      start_time: `${startHour}:${startMin}`,
      time_slot: time_slot,
      duration: newParty.duration,
      total_price: parseFloat(newParty.price) || 0,
      gender_limit: newParty.genderLimit,
      game_name: newParty.title,
      game_note: newParty.description || '這是我剛發起的揪團，歡迎大家來玩！'
    };

    try {
      const newGame = await gamesApi.createGame(payload);
      
      // 為了讓前端能立刻顯示，需要把後端回傳的資料轉成前端需要的格式
      const rawType = newGame.type || newGame.sport_type || newGame.sport_name || newParty.type;
      const rawLevel = newGame.level || newGame.target_level || newParty.level;
      
      const formattedNewGame = {
        ...newGame,
        id: newGame.id || Date.now(),
        venueStatus: 'pending',
        title: newGame.title || newGame.description?.substring(0, 10) || newParty.title || '無標題揪團',
        type: rawType,
        level: rawLevel,
        genderLimit: newGame.genderLimit || newGame.gender_limit || newParty.genderLimit,
        location: newGame.location || newGame.venue_name || newParty.venue,
        description: newGame.game_note || newGame.description || newParty.description,
        time: newGame.time || (newGame.booking_date ? `${newGame.booking_date} ${newGame.time_slot || ''}` : newParty.time.replace('T', ' ')),
        currentPlayers: newGame.currentPlayers ?? newGame.current_players ?? 1,
        maxPlayers: newGame.maxPlayers ?? newGame.most_players ?? newGame.max_players ?? parseInt(newParty.maxPlayers, 10),
        currentWaitlist: newGame.currentWaitlist ?? newGame.current_waitlist ?? 0,
        maxWaitlist: newGame.maxWaitlist ?? newGame.max_waitlist ?? 2,
        participants: newGame.participants || ['我 (主揪)'],
      };

      setParties([formattedNewGame, ...parties]); 
      setIsModalOpen(false);
      setNewParty({ 
        title: '', type: '籃球', level: '休閒', genderLimit: '不限', city: '桃園市', district: '桃園區', venue: '桃園國民運動中心', description: '', price: '', time: '', duration: '2 小時', minPlayers: 2, maxPlayers: 4 
      });
      alert('發起成功！');
    } catch (error) {
      console.error('Create party error:', error);
      const backendError = error.response?.data ? JSON.stringify(error.response.data) : '伺服器未回應';
      alert(`發起揪團失敗：${backendError}`);
    }
  };

  // 當選擇的運動類型或場地清單改變時，重新計算下拉選單的選項
  useEffect(() => {
    if (allVenues.length === 0) return;

    // 後端資料庫裡的運動名稱是英文，需要對應
    const sportMap = {
      '籃球': 'Basketball',
      '排球': 'Volleyball',
      '羽球': 'Badminton',
      '麻將': 'Mahjohn',
      '桌球': 'Table Tennis'
    };
    const dbSportName = (sportMap[newParty.type] || newParty.type).toLowerCase();

    const filteredVenues = allVenues.filter(v => 
      v.sports.some(s => s.toLowerCase() === dbSportName || s.toLowerCase() === newParty.type.toLowerCase()) || 
      v.sports.length === 0
    );
    
    // 若該運動目前無可用場地，給個防呆
    if (filteredVenues.length === 0) {
      setTaiwanRegions({ '未選擇': { '未選擇': ['無適用場地'] } });
      setVenueFacilities({});
      setVenueMap({});
      setNewParty(prev => ({ ...prev, city: '未選擇', district: '未選擇', venue: '無適用場地' }));
      return;
    }

    const regions = {};
    const facilities = {};
    const vMap = {};

    filteredVenues.forEach(v => {
      if (!regions[v.city]) regions[v.city] = {};
      if (!regions[v.city][v.district]) regions[v.city][v.district] = [];
      regions[v.city][v.district].push(v.name);
      facilities[v.name] = v.facilities;
      vMap[v.name] = v.id;
    });

    setTaiwanRegions(regions);
    setVenueFacilities(facilities);
    setVenueMap(vMap);

    // 檢查目前選的場地是否還在新的清單裡，不在的話重設為第一個
    const currentCityValid = regions[newParty.city];
    const currentDistValid = currentCityValid && regions[newParty.city][newParty.district];
    const currentVenueValid = currentDistValid && regions[newParty.city][newParty.district].includes(newParty.venue);

    if (!currentVenueValid) {
      const firstCity = Object.keys(regions)[0];
      const firstDist = firstCity ? Object.keys(regions[firstCity])[0] : '未選擇';
      const firstVenue = firstDist ? regions[firstCity][firstDist][0] : '無適用場地';
      
      setNewParty(prev => ({
        ...prev,
        city: firstCity,
        district: firstDist,
        venue: firstVenue
      }));
    }
  }, [newParty.type, allVenues]);

  const handleCityChange = (e) => {
    const selectedCity = e.target.value;
    const firstDistrict = taiwanRegions[selectedCity] ? Object.keys(taiwanRegions[selectedCity])[0] : '';
    const firstVenue = taiwanRegions[selectedCity] && taiwanRegions[selectedCity][firstDistrict] ? taiwanRegions[selectedCity][firstDistrict][0] : '';
    setNewParty({
      ...newParty,
      city: selectedCity,
      district: firstDistrict,
      venue: firstVenue
    });
  };

  const handleDistrictChange = (e) => {
    const selectedDistrict = e.target.value;
    const firstVenue = taiwanRegions[newParty.city] && taiwanRegions[newParty.city][selectedDistrict] ? taiwanRegions[newParty.city][selectedDistrict][0] : '';
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
                    onClick={async () => {
                      const unreadNotifs = notifications.filter(n => !n.read);
                      if (unreadNotifs.length > 0) {
                        try {
                          await Promise.all(unreadNotifs.map(n => notificationsApi.markAsRead(n.id)));
                        } catch (e) { console.error('Failed to mark all as read', e); }
                      }
                      setNotifications(notifications.map(n => ({...n, read: true})));
                    }}
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
                        onClick={async () => {
                          if (!n.read) {
                            try {
                              await notificationsApi.markAsRead(n.id);
                            } catch (e) { console.error('Failed to mark as read', e); }
                          }
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
              <span>桃園市 {temperature === '--' ? '--' : `${temperature}°C`}</span>
              <div 
                style={{ position: 'relative', marginLeft: '8px', paddingLeft: '12px', borderLeft: '1px solid #cbd5e1', color: '#64748b', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '4px' }}
                onMouseEnter={() => setShowAqiInfo(true)}
                onMouseLeave={() => setShowAqiInfo(false)}
              >
                <span>空氣品質 (AQI)：{aqi}</span>
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
            {isPageLoading && <span style={{ color: '#94a3b8' }}>載入中...</span>}
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
            .sort((a, b) => {
              const currentUserId = localStorage.getItem('user_id');
              const isAHost = currentUserId && (a.creator_id && String(a.creator_id) === String(currentUserId));
              const isBHost = currentUserId && (b.creator_id && String(b.creator_id) === String(currentUserId));

              if (isAHost && !isBHost) return -1;
              if (!isAHost && isBHost) return 1;
              return 0;
            })
            .map(party => {
            const currentUserId = localStorage.getItem('user_id');
            const isHost = currentUserId && (party.creator_id && String(party.creator_id) === String(currentUserId));
            const isParticipant = currentUserId && (party.participant_ids?.some(id => String(id) === String(currentUserId)));
            const isWaitlisted = currentUserId && (party.waitlist_ids?.some(id => String(id) === String(currentUserId)));

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

            let badgeStatusText = '';
            let badgeStatusColor = '';

            const backendStatus = party.match_status || party.status || party.game_status;
            
            if (backendStatus === '已開始' || backendStatus === 'started' || backendStatus === 'playing') {
              badgeStatusText = '已開始';
              badgeStatusColor = '#10b981'; // Green
            } else if (backendStatus === '已關閉' || backendStatus === 'closed' || backendStatus === 'failed_to_start') {
              badgeStatusText = '已關閉';
              badgeStatusColor = '#64748b'; // Gray
            } else if (backendStatus === '已滿' || backendStatus === 'full') {
              if (!isWaitlistFull) {
                badgeStatusText = '可候補';
                badgeStatusColor = '#f59e0b'; // Orange
              } else {
                badgeStatusText = '已滿';
                badgeStatusColor = '#94a3b8'; // Gray
              }
            } else if (backendStatus === '可候補' || backendStatus === 'waitlisting') {
              badgeStatusText = '可候補';
              badgeStatusColor = '#f59e0b'; // Orange
            } else if (backendStatus === '缺人' || backendStatus === 'recruiting') {
              badgeStatusText = '缺人';
              badgeStatusColor = '#ef4444'; // Red
            } else {
              if (isFull && isWaitlistFull) {
                badgeStatusText = '已滿';
                badgeStatusColor = '#94a3b8';
              } else if (isFull) {
                badgeStatusText = '可候補';
                badgeStatusColor = '#f59e0b';
              } else {
                badgeStatusText = '缺人';
                badgeStatusColor = '#ef4444';
              }
            }



            return (
              <div key={party.id} className={`party-card clickable-card ${isHost ? 'hosted-party' : ''}`} onClick={() => navigate(`/party/${party.id}`, { state: { party } })}>
                <div className="party-card-header">
                  <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                    {isHost && (
                      <Star size={20} fill="#d8a7a7" color="#d8a7a7" style={{ marginRight: '4px' }} />
                    )}
                    <span className="party-type">{party.type}</span>
                    <span className="party-level">{party.level}</span>
                    {party.venueStatus === 'confirmed' && (
                      <span className="party-level" style={{ backgroundColor: '#10b981', color: 'white', fontWeight: 'bold' }}>
                        ✅ 場地已確認
                      </span>
                    )}
                    {party.venueStatus === 'failed' && (
                      <span className="party-level" style={{ backgroundColor: '#ef4444', color: 'white', fontWeight: 'bold' }}>
                        ❌ 未借到場地
                      </span>
                    )}
                    {party.genderLimit && party.genderLimit !== '不限' && (
                      <span className="party-level">{party.genderLimit}</span>
                    )}
                    {badgeStatusText && (
                      <span className="party-level" style={{ backgroundColor: badgeStatusColor, color: 'white', fontWeight: 'bold' }}>
                        {badgeStatusText}
                      </span>
                    )}
                  </div>
                  {badgeStatusText !== '已關閉' && (
                    <span className="party-status" style={{ color: statusColor }}>{statusText}</span>
                  )}
                </div>
                <h3 className="party-title">{party.title}</h3>
                <div className="party-info">
                  <p style={{ gap: '6px' }}><MapPin size={16} /> {party.location}</p>
                  <p style={{ gap: '6px' }}><Clock size={16} /> {party.time}</p>
                </div>
                <div className="party-card-footer">
                  {badgeStatusText !== '已關閉' ? (
                    <span className="player-count">目前人數: {party.currentPlayers} / {party.maxPlayers}</span>
                  ) : (
                    <span className="player-count"></span>
                  )}
                  <button className="btn-join" onClick={(e) => {
                    e.stopPropagation();
                    navigate(`/party/${party.id}`, { state: { party } });
                  }}>
                    {isHost ? '管理' : isParticipant ? '已報名' : isWaitlisted ? '已候補' : isFull && isWaitlistFull ? '查看詳情' : isFull ? '排候補' : '報名參加'}
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
                    <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '6px', overflow: 'visible' }}>
                      程度
                      <div 
                        style={{ position: 'relative', display: 'flex', alignItems: 'center' }}
                        onMouseEnter={() => setShowLevelInfo(true)}
                        onMouseLeave={() => setShowLevelInfo(false)}
                      >
                        <HelpCircle size={14} style={{ cursor: 'pointer', color: '#94a3b8' }} />
                        {showLevelInfo && (
                          <div style={{ position: 'absolute', bottom: '100%', left: '-8px', marginBottom: '8px', width: '240px', backgroundColor: '#1e293b', color: 'white', padding: '12px', borderRadius: '8px', fontSize: '13px', fontWeight: 'normal', zIndex: 50, boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)', lineHeight: '1.5', cursor: 'default' }}>
                            <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>各程度推薦參加者</div>
                            <ul style={{ margin: 0, paddingLeft: '16px', color: '#e2e8f0' }}>
                              <li style={{ marginBottom: '4px' }}><strong>休閒：</strong> 推薦 C (新手)、B (熟練)</li>
                              <li style={{ marginBottom: '4px' }}><strong>業餘：</strong> 推薦 A (高手)、B (熟練)</li>
                              <li><strong>高手：</strong> 推薦 S (菁英)、A (高手)</li>
                            </ul>
                            <div style={{ position: 'absolute', bottom: '-4px', left: '11px', width: '8px', height: '8px', backgroundColor: '#1e293b', borderRadius: '2px', rotate: '45deg' }}></div>
                          </div>
                        )}
                      </div>
                    </label>
                    <select className="form-input" value={newParty.level} onChange={e => setNewParty({...newParty, level: e.target.value})}>
                      <option value="休閒">休閒</option>
                      <option value="業餘">業餘</option>
                      <option value="高手">高手</option>
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
                    <input 
                      type="datetime-local" 
                      className="form-input custom-date-input" 
                      value={newParty.time} 
                      onChange={e => setNewParty({...newParty, time: e.target.value})} 
                      min={new Date().toISOString().slice(0, 16)}
                      required 
                    />
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
                      {Object.keys(taiwanRegions[newParty.city] || {}).map(dist => (
                        <option key={dist} value={dist}>{dist}</option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">地點 (場館/球場)</label>
                    <select className="form-input" value={newParty.venue} onChange={e => setNewParty({...newParty, venue: e.target.value})}>
                      {(taiwanRegions[newParty.city]?.[newParty.district] || []).map(v => (
                        <option key={v} value={v}>{v}</option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">總額費用</label>
                    <input 
                      type="number" 
                      className="form-input" 
                      placeholder="輸入場地總額 (若為免費請輸入 0)" 
                      value={newParty.price} 
                      onChange={e => setNewParty({...newParty, price: e.target.value})}
                      min="0"
                      max="10000"
                      required
                    />
                    <div style={{ fontSize: '12px', color: '#94a3b8', marginTop: '6px' }}>* 系統將會依據人數自動為您計算分攤金額</div>
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
                    <input required type="number" min="1" max="100" className="form-input" value={newParty.minPlayers} onChange={e => setNewParty({...newParty, minPlayers: e.target.value})} />
                    <span style={{ color: '#64748b' }}>~</span>
                    <input required type="number" min="2" max="100" className="form-input" value={newParty.maxPlayers} onChange={e => setNewParty({...newParty, maxPlayers: e.target.value})} />
                  </div>
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
