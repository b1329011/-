import { useState, useMemo } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { MapPin, Clock, ArrowLeft, Timer, DollarSign, Info, CheckCircle2, Users, AlertTriangle, Eye, Bell, MessageCircle } from 'lucide-react';
import '../App.css';

function PartyDetail() {
  const { id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();

  const defaultParty = useMemo(() => ({
    id: id,
    title: '未知的揪團',
    type: '未知',
    level: '休閒',
    genderLimit: '不限',
    time: '未知時間',
    location: '未知地點',
    duration: '2 小時',
    price: '免費',
    facilities: ['冷氣', '飲水機', '廁所', '淋浴間'],
    currentPlayers: 1,
    maxPlayers: 4,
    currentWaitlist: 0,
    maxWaitlist: 2,
    host: '主揪人',
    description: '這是一個預設的揪團說明。大家一起開心打球，友誼第一！記得帶自己的裝備喔。',
    participants: [{ name: '主揪人', phone: '0912-345-678', line: 'host_id' }],
    waitlist: []
  }), [id]);

  const initialParty = useMemo(() => {
    const party = location.state?.party || defaultParty;
    const processedParty = { ...party };

    // 確保 participants 是物件陣列格式
    if (processedParty.participants && typeof processedParty.participants[0] === 'string') {
      processedParty.participants = processedParty.participants.map((p, idx) => ({
        name: p,
        phone: idx === 0 ? '0912-345-678' : '0911-222-333',
        line: `${p.replace(/\s+/g, '_').toLowerCase()}_line`,
        age: 20 + (idx * 2), // 固定 mock 數據避免 Math.random()
        level: ['S', 'A', 'B', 'C'][idx % 4]
      }));
    }
    if (processedParty.waitlist && typeof processedParty.waitlist[0] === 'string') {
      processedParty.waitlist = processedParty.waitlist.map((p, idx) => ({
        name: p,
        phone: '0911-222-333',
        line: `${p.replace(/\s+/g, '_').toLowerCase()}_line`,
        age: 25 + idx,
        level: ['B', 'C'][idx % 2]
      }));
    }
    return processedParty;
  }, [location.state, defaultParty]);

  const [party, setParty] = useState(initialParty);
  
  // 判斷當前使用者是否為主揪或已加入
  const isUserHost = initialParty.participants?.[0]?.name === '我 (主揪)' || initialParty.participants?.[0]?.name === '主揪人';
  const initialHasJoined = isUserHost || 
                           initialParty.participants?.some(p => p.name === '我 (使用者)') || 
                           initialParty.waitlist?.some(p => p.name === '我 (使用者)');

  const [hasJoined, setHasJoined] = useState(initialHasJoined);
  const [joinType, setJoinType] = useState(null);
  const [toastMsg, setToastMsg] = useState('');
  const [showListModal, setShowListModal] = useState(null); // 'participants' | 'waitlist' | null
  const [selectedMember, setSelectedMember] = useState(null); // 新增：被選擇查看資料的成員
  
  // 新增：場地狀態與檢舉功能狀態
  const [isHostView, setIsHostView] = useState(isUserHost); // 根據是否為主揪動態切換
  const [isTimeApproaching, setIsTimeApproaching] = useState(false); // 測試用：模擬距離活動小於30分
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState([
    { id: 1, text: '你報名的「歡樂衛生麻將局」場地已確認！', time: '10 分鐘前', read: false },
    { id: 2, text: '系統提醒：主揪更新了揪團注意事項', time: '1 小時前', read: true }
  ]);
  const [showReportModal, setShowReportModal] = useState(false);
  const [reportReason, setReportReason] = useState('未出現');
  const [reportDetail, setReportDetail] = useState('');
  const [reportingUser, setReportingUser] = useState(null);
  const [reportedUsers, setReportedUsers] = useState([]); // 新增：紀錄已檢舉的用戶名
  const [showLevelWarningModal, setShowLevelWarningModal] = useState(false); // 等級不符警告
  
  // 新增：佈告欄狀態
  const [showAnnouncementModal, setShowAnnouncementModal] = useState(false);
  const [announcements, setAnnouncements] = useState([
    { id: 1, text: '大家記得帶自己的球具跟水壺喔！', time: '10:00 AM' }
  ]);
  const [newAnnouncement, setNewAnnouncement] = useState('');

  const getLevelColor = (lv) => {
    switch(lv) {
      case 'S': return '#ef4444'; // Red
      case 'A': return '#f59e0b'; // Orange
      case 'B': return '#10b981'; // Green
      case 'C': return '#94a3b8'; // Gray
      default: return '#7995a5';
    }
  };

  const showToast = (msg) => {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(''), 3000);
  };

  const confirmJoin = () => {
    const newMember = { 
      name: '我 (使用者)', 
      phone: '0987-654-321', 
      line: 'my_id_888',
      age: 20,
      level: 'A'
    };
    if (party.currentPlayers < party.maxPlayers) {
      setParty(prev => ({
        ...prev,
        currentPlayers: prev.currentPlayers + 1,
        participants: [...prev.participants, newMember]
      }));
      setJoinType('normal');
      setHasJoined(true);
      showToast('報名成功！你已在正取名單中。');
    } else if (party.currentWaitlist < party.maxWaitlist) {
      setParty(prev => ({
        ...prev,
        currentWaitlist: prev.currentWaitlist + 1,
        waitlist: [...prev.waitlist, newMember]
      }));
      setJoinType('waitlist');
      setHasJoined(true);
      showToast('已進入候補名單！有人退出時系統會依序遞補。');
    }
  };

  const handleJoin = () => {
    const mockUserLevel = 'A'; // 假設使用者等級為 A
    const partyLevel = party.level || '休閒';
    
    // 檢查等級是否匹配 (如果不限或休閒則略過，這裡簡單判斷如果不同就跳警告)
    if (partyLevel !== '休閒' && partyLevel !== '不限' && partyLevel !== mockUserLevel) {
      setShowLevelWarningModal(true);
    } else {
      confirmJoin();
    }
  };

  const handleCancel = () => {
    if (joinType === 'normal') {
      setParty(prev => ({
        ...prev,
        currentPlayers: prev.currentPlayers - 1,
        participants: prev.participants.filter(p => p.name !== '我 (使用者)')
      }));
    } else if (joinType === 'waitlist') {
      setParty(prev => ({
        ...prev,
        currentWaitlist: prev.currentWaitlist - 1,
        waitlist: prev.waitlist.filter(p => p.name !== '我 (使用者)')
      }));
    }
    setHasJoined(false);
    setJoinType(null);
    showToast('已成功取消報名。');
  };

  const isFull = party.currentPlayers >= party.maxPlayers;
  const isWaitlistFull = party.currentWaitlist >= party.maxWaitlist;
  
  return (
    <div className="home-container">
      <nav className="navbar">
        <div className="navbar-logo" style={{ cursor: 'pointer' }} onClick={() => navigate('/home')}>不揪ㄛ</div>
        <div className="navbar-actions" style={{ display: 'flex', gap: '10px', position: 'relative' }}>
          <button className="btn-outline" onClick={() => setIsTimeApproaching(!isTimeApproaching)} style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', padding: '6px 10px', borderColor: isTimeApproaching ? '#f59e0b' : '#e2e8f0', color: isTimeApproaching ? '#f59e0b' : '#64748b' }}>
            <Clock size={14} /> {isTimeApproaching ? '活動快開始了' : '距離活動還很久'}
          </button>
          <button className="btn-outline" onClick={() => setIsHostView(!isHostView)} style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', padding: '6px 10px' }}>
            <Eye size={14} /> {isHostView ? '主揪視角' : '一般視角'}
          </button>
          
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
            <div style={{ position: 'absolute', top: '100%', right: '40px', marginTop: '12px', width: '300px', backgroundColor: 'white', borderRadius: '12px', boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)', zIndex: 1000, overflow: 'hidden', border: '1px solid #e2e8f0', textAlign: 'left' }}>
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

          <button className="btn-outline" onClick={() => navigate(-1)} style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: '700' }}>
            <ArrowLeft size={16} /> 返回大廳
          </button>
        </div>
      </nav>

      <main className="main-content" style={{ maxWidth: '800px', margin: '0 auto', paddingTop: '20px' }}>
        
        <div className="detail-card" style={{ padding: 0, overflow: 'hidden', position: 'relative' }}>
          
          {/* 標題與設施 (背景透明度調整) */}
          <div style={{ minHeight: '220px', background: 'linear-gradient(135deg, rgba(121, 149, 165, 0.85), rgba(75, 98, 114, 0.85))', padding: '60px 40px 30px 40px', color: 'white', display: 'flex', flexDirection: 'column', justifyContent: 'flex-end' }}>
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              <span className="party-type" style={{ backgroundColor: 'rgba(255,255,255,0.2)', color: 'white' }}>{party.type}</span>
              <span className="party-level" style={{ backgroundColor: 'rgba(255,255,255,0.2)', color: 'white', border: 'none', padding: '4px 10px', borderRadius: '6px', fontSize: '12px', fontWeight: '700' }}>{party.level || '休閒'}</span>
              {party.genderLimit && party.genderLimit !== '不限' && (
                <span className="party-level" style={{ backgroundColor: 'rgba(255,255,255,0.2)', color: 'white', border: 'none', padding: '4px 10px', borderRadius: '6px', fontSize: '12px', fontWeight: '700' }}>{party.genderLimit}</span>
              )}
              <span style={{ 
                backgroundColor: party.venueStatus === 'confirmed' ? '#10b981' : party.venueStatus === 'failed' ? '#ef4444' : '#f59e0b', 
                color: 'white', border: 'none', padding: '4px 10px', borderRadius: '6px', fontSize: '12px', fontWeight: '700' 
              }}>
                {party.venueStatus === 'confirmed' ? '✅ 場地已確認' : party.venueStatus === 'failed' ? '❌ 場地未借到' : '⏳ 場地確認中'}
              </span>
            </div>
            
            <h1 className="detail-title" style={{ color: 'white', marginTop: '16px', marginBottom: '16px' }}>{party.title}</h1>
            
            {/* 設施標籤移到標題下方 */}
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              {(party.facilities || ['冷氣', '飲水機', '廁所', '淋浴間']).map((f, i) => (
                <span key={i} style={{ backgroundColor: 'rgba(255,255,255,0.2)', color: 'white', padding: '4px 12px', borderRadius: '20px', fontSize: '13px', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <CheckCircle2 size={14} /> {f}
                </span>
              ))}
            </div>
          </div>

          <div style={{ padding: '40px' }}>
            {isHostView && isTimeApproaching && (
              <div style={{ backgroundColor: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '20px', marginBottom: '32px' }}>
                <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', color: '#1e293b' }}>👑 是否借到場地？</h3>
                <div style={{ display: 'flex', gap: '12px' }}>
                  <button className="btn-primary" style={{ flex: 1, backgroundColor: '#10b981', border: 'none' }} onClick={() => { setParty({...party, venueStatus: 'confirmed'}); showToast('已通知所有成員：場地確認成功！'); }}>
                    ✅ 確認借到場地
                  </button>
                  <button className="btn-outline" style={{ flex: 1, color: '#ef4444', borderColor: '#ef4444' }} onClick={() => { setParty({...party, venueStatus: 'failed'}); showToast('已通知所有成員：活動取消！'); }}>
                    ❌ 場地未借到 (取消)
                  </button>
                </div>
              </div>
            )}

            <div className="detail-info-row" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', paddingBottom: '32px' }}>
              <div className="detail-info-item" style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '16px', backgroundColor: '#f8fafc', padding: '16px 20px', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
                <Clock size={20} color="#7995a5" />
                <span style={{ color: '#64748b', fontWeight: '600' }}>時間：</span>
                <span style={{ fontWeight: '800' }}>{party.time}</span>
              </div>

              <div className="detail-info-item" style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '16px', backgroundColor: '#f8fafc', padding: '16px 20px', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
                <Timer size={20} color="#7995a5" />
                <span style={{ color: '#64748b', fontWeight: '600' }}>時長：</span>
                <span style={{ fontWeight: '800' }}>{party.duration || '2 小時'}</span>
              </div>

              <div className="detail-info-item" style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '16px', backgroundColor: '#f8fafc', padding: '16px 20px', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
                <MapPin size={20} color="#7995a5" />
                <span style={{ color: '#64748b', fontWeight: '600' }}>地點：</span>
                <span style={{ fontWeight: '800' }}>{party.location}</span>
              </div>

              <div className="detail-info-item" style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '16px', backgroundColor: '#f8fafc', padding: '16px 20px', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
                <DollarSign size={20} color="#7995a5" />
                <span style={{ color: '#64748b', fontWeight: '600' }}> 價格：</span>
                <span style={{ fontWeight: '800', color: '#1e293b' }}>
                  {party.price && party.price.includes('總額分攤') ? (
                    <>
                      {party.price}
                      <span style={{ marginLeft: '8px', color: '#ef4444', fontSize: '14px' }}>
                        (${Math.ceil(parseFloat(party.price.replace(/[^0-9.]/g, '')) / party.maxPlayers)} / 人)
                      </span>
                    </>
                  ) : (
                    party.price || '免費'
                  )}
                </span>
              </div>

            </div>

            <div className="detail-section">
              <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}><Info size={20} /> 備註與說明</h3>
              <div style={{ backgroundColor: '#f8fafc', padding: '20px', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
                <p className="detail-desc" style={{ margin: 0, lineHeight: '1.6' }}>{party.description || '大家一起開心打球，友誼第一！記得帶自己的水壺與毛巾。'}</p>
              </div>
            </div>

            {/* 參與與候補名單按鈕 */}
            <div className="detail-section" style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', marginTop: '32px', marginBottom: '32px' }}>
              <button className="btn-outline" style={{ flex: '1 1 200px', padding: '16px', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px', fontSize: '16px', fontWeight: '700', borderRadius: '12px', backgroundColor: '#f8fafc' }} onClick={() => setShowListModal('participants')}>
                <Users size={20} /> 查看參與名單 ({party.currentPlayers}/{party.maxPlayers})
              </button>
              {(party.currentWaitlist > 0 || isFull) && (
                <button className="btn-outline" style={{ flex: '1 1 200px', padding: '16px', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px', fontSize: '16px', fontWeight: '700', borderRadius: '12px', borderColor: '#fcd34d', color: '#d97706', backgroundColor: '#fffbeb' }} onClick={() => setShowListModal('waitlist')}>
                  ⏳ 查看候補名單 ({party.currentWaitlist}/{party.maxWaitlist})
                </button>
              )}
            </div>

            {/* 報名參加按鈕 (居中顯示於名單按鈕下方) */}
            {!isHostView && (
              <div style={{ fontSize: '12px', color: '#64748b', textAlign: 'center', margin: '20px auto 12px auto', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '4px', backgroundColor: '#f1f5f9', padding: '8px', borderRadius: '8px', maxWidth: '600px' }}>
                <span style={{ color: '#f59e0b' }}>⚠️</span> 取消截止時間：05/28 20:00，逾期將無法取消報名
              </div>
            )}
            <div style={{ display: 'flex', justifyContent: 'center' }}>
              {isHostView ? (
                <button className="btn-action cancel" style={{ width: '100%' }} onClick={() => { alert('球局已取消！'); navigate('/home'); }}>
                  取消揪團
                </button>
              ) : hasJoined ? (
                <button className="btn-action cancel" onClick={handleCancel}>
                  取消報名
                </button>
              ) : isFull && isWaitlistFull ? (
                <button className="btn-action disabled" disabled>
                  已完全額滿
                </button>
              ) : isFull ? (
                <button className="btn-action waitlist" style={{ width: '100%' }} onClick={handleJoin}>
                  排候補
                </button>
              ) : (
                <button className="btn-action join" style={{ width: '100%' }} onClick={handleJoin}>
                  報名參加
                </button>
              )}
            </div>
          </div>
        </div>

      </main>

      {/* 底部報名列 */}
      {/* 名單 Modal */}
      {showListModal && (
        <div className="modal-overlay" onClick={() => setShowListModal(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()} style={{ maxWidth: '400px' }}>
            <div className="modal-header">
              <h3>{showListModal === 'participants' ? `👥 參與名單 (${party.currentPlayers}/${party.maxPlayers})` : `⏳ 候補名單 (${party.currentWaitlist}/${party.maxWaitlist})`}</h3>
              <button className="modal-close" onClick={() => setShowListModal(null)}>&times;</button>
            </div>
            <div className="participant-list-vertical" style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxHeight: '400px', overflowY: 'auto' }}>
              {(showListModal === 'participants' ? party.participants : party.waitlist).map((p, idx) => (
                <div key={idx} className="participant-item-row" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', backgroundColor: '#f8fafc', borderRadius: '12px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div className="participant-avatar" style={showListModal === 'waitlist' ? { backgroundColor: '#94a3b8' } : {}}>{p.name.charAt(0)}</div>
                    <div style={{ display: 'flex', flexDirection: 'column' }}>
                      <span style={{ fontWeight: '700' }}>
                        {p.name}
                        {showListModal === 'participants' && idx === 0 && (
                          <span style={{ marginLeft: '8px', padding: '2px 8px', backgroundColor: '#7995a5', color: 'white', fontSize: '11px', borderRadius: '4px', fontWeight: '800' }}>主揪</span>
                        )}
                      </span>
                      <div style={{ display: 'flex', gap: '8px', marginTop: '2px' }}>
                        <span style={{ fontSize: '12px', color: '#64748b' }}>{p.age} 歲</span>
                        <span style={{ fontSize: '12px', fontWeight: '800', color: '#7995a5' }}>等級: <span style={{ color: getLevelColor(p.level) }}>{p.level}</span></span>
                      </div>
                    </div>
                  </div>
                  <button 
                    className="btn-outline" 
                    style={{ padding: '6px 12px', fontSize: '13px', borderRadius: '8px' }}
                    onClick={() => setSelectedMember(p)}
                  >
                    查看資料
                  </button>
                </div>
              ))}
              {showListModal === 'waitlist' && party.waitlist.length === 0 && (
                <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '20px' }}>目前無人候補</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 成員詳細資料 Modal */}
      {selectedMember && (
        <div className="modal-overlay" onClick={() => setSelectedMember(null)} style={{ zIndex: 1100 }}>
          <div className="modal-content" onClick={e => e.stopPropagation()} style={{ maxWidth: '320px', textAlign: 'center', position: 'relative' }}>
            {(isHostView || party.participants.some(p => p.name === '我 (使用者)')) && selectedMember.name !== '我 (使用者)' && selectedMember.name !== '我 (主揪)' && (
              reportedUsers.includes(selectedMember.name) ? (
                <button 
                  disabled
                  style={{ position: 'absolute', top: '16px', right: '16px', background: 'none', border: 'none', cursor: 'not-allowed', display: 'flex', alignItems: 'center', gap: '4px', color: '#94a3b8', fontSize: '13px', fontWeight: '700' }}
                >
                  <AlertTriangle size={16} /> 已檢舉
                </button>
              ) : (
                <button 
                  onClick={() => { setShowReportModal(true); setReportingUser(selectedMember.name); setSelectedMember(null); }}
                  style={{ position: 'absolute', top: '16px', right: '16px', background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px', color: '#ef4444', fontSize: '13px', fontWeight: '700' }}
                >
                  <AlertTriangle size={16} /> 檢舉
                </button>
              )
            )}
            <div className="avatar-placeholder" style={{ width: '80px', height: '80px', fontSize: '32px', marginBottom: '16px', margin: '0 auto 16px auto' }}>
              {selectedMember.name.charAt(0)}
            </div>
            <h3 style={{ marginBottom: '8px' }}>{selectedMember.name}</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '14px', marginBottom: '24px' }}>成員聯繫資訊</p>
            
            <div style={{ textAlign: 'left', backgroundColor: '#f1f5f9', padding: '16px', borderRadius: '12px', marginBottom: '24px' }}>
              <div style={{ marginBottom: '12px', display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#64748b', fontSize: '13px' }}>電話號碼</span>
                <span style={{ fontWeight: '700' }}>{selectedMember.phone}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#64748b', fontSize: '13px' }}>LINE / 通訊</span>
                <span style={{ fontWeight: '700' }}>{selectedMember.line}</span>
              </div>
            </div>
            
            <button className="login-button" onClick={() => setSelectedMember(null)}>關閉</button>
          </div>
        </div>
      )}

      {/* 等級不符警告 Modal */}
      {showLevelWarningModal && (
        <div className="modal-overlay" onClick={() => setShowLevelWarningModal(false)} style={{ zIndex: 1200 }}>
          <div className="modal-content" onClick={e => e.stopPropagation()} style={{ maxWidth: '320px', textAlign: 'center' }}>
            <div style={{ color: '#f59e0b', marginBottom: '16px' }}>
              <AlertTriangle size={48} style={{ margin: '0 auto' }} />
            </div>
            <h3 style={{ marginBottom: '12px', fontSize: '18px' }}>等級不符</h3>
            <p style={{ color: '#64748b', fontSize: '14px', marginBottom: '24px', lineHeight: '1.5' }}>
              這個揪團設定的等級是「{party.level}」，但你目前的等級為「A」。<br/><br/>
              與目前level不符，確定要加入？
            </p>
            <div style={{ display: 'flex', gap: '12px' }}>
              <button className="btn-outline" style={{ flex: 1 }} onClick={() => setShowLevelWarningModal(false)}>取消</button>
              <button className="btn-primary" style={{ flex: 1, backgroundColor: '#f59e0b', border: 'none' }} onClick={() => {
                setShowLevelWarningModal(false);
                confirmJoin();
              }}>確定加入</button>
            </div>
          </div>
        </div>
      )}

      {/* 檢舉 Modal */}
      {showReportModal && (
        <div className="modal-overlay" onClick={() => setShowReportModal(false)} style={{ zIndex: 1200 }}>
          <div className="modal-content" onClick={e => e.stopPropagation()} style={{ maxWidth: '400px' }}>
            <div className="modal-header">
              <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#ef4444' }}>
                <AlertTriangle size={20} /> 檢舉用戶
              </h3>
              <button className="modal-close" onClick={() => setShowReportModal(false)}>&times;</button>
            </div>
            <div style={{ marginBottom: '20px' }}>
              <p style={{ fontSize: '13px', color: '#64748b', marginBottom: '16px' }}>我們致力於維護良好的揪團環境，如果該用戶有違規行為，請協助我們進行舉發。</p>
              
              <div className="form-group">
                <label className="form-label">檢舉原因</label>
                <select className="form-input" value={reportReason} onChange={(e) => setReportReason(e.target.value)}>
                  <optgroup label="一般原因">
                    <option value="未出現">未出現</option>
                    <option value="沒交錢">沒交錢</option>
                    <option value="球品不好">球品不好</option>
                    <option value="言語攻擊">言語攻擊</option>
                    <option value="態度不佳">態度不佳</option>
                    <option value="等級不符">等級不符</option>
                    <option value="騷擾與人身攻擊">騷擾與人身攻擊</option>
                    <option value="肢體暴力">肢體暴力</option>
                  </optgroup>
                  {reportingUser === party.participants?.[0]?.name && (
                    <optgroup label="主揪專屬原因">
                      <option value="未回報場地">未回報場地</option>
                      <option value="惡意抬價">惡意抬價</option>
                      <option value="沒預約場地">沒預約場地</option>
                      <option value="回報與實際場地不符">回報與實際場地不符</option>
                    </optgroup>
                  )}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">詳細說明 (選填)</label>
                <textarea 
                  className="form-input" 
                  rows="3" 
                  placeholder="請簡單描述發生的狀況..."
                  value={reportDetail}
                  onChange={(e) => setReportDetail(e.target.value)}
                ></textarea>
              </div>
            </div>
            
            <div style={{ display: 'flex', gap: '12px' }}>
              <button className="btn-outline" style={{ flex: 1 }} onClick={() => setShowReportModal(false)}>取消</button>
              <button className="login-button" style={{ flex: 1, backgroundColor: '#ef4444' }} onClick={() => {
                if (reportingUser) {
                  setReportedUsers([...reportedUsers, reportingUser]);
                }
                setShowReportModal(false);
                setReportingUser(null);
                showToast('檢舉已送出，管理團隊將會盡快審查。');
                setReportDetail('');
              }}>送出檢舉</button>
            </div>
          </div>
        </div>
      )}

      {/* 浮動佈告欄按鈕 (所有人皆可見，但只有主揪能發言) */}
      <button 
        onClick={() => setShowAnnouncementModal(true)}
        style={{
          position: 'fixed',
          bottom: '24px',
          right: '24px',
          width: '56px',
          height: '56px',
          borderRadius: '28px',
          backgroundColor: '#0284c7',
          color: 'white',
          border: 'none',
          boxShadow: '0 4px 12px rgba(2, 132, 199, 0.4)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          cursor: 'pointer',
          zIndex: 1000
        }}
      >
        <MessageCircle size={28} />
      </button>

      {/* 佈告欄 Modal */}
      {showAnnouncementModal && (
        <div className="modal-overlay" onClick={() => setShowAnnouncementModal(false)} style={{ zIndex: 1200 }}>
          <div className="modal-content" onClick={e => e.stopPropagation()} style={{ maxWidth: '400px', display: 'flex', flexDirection: 'column', height: '80vh', maxHeight: '600px' }}>
            <div className="modal-header">
              <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <MessageCircle size={20} color="#0284c7" /> 佈告欄
              </h3>
              <button className="modal-close" onClick={() => setShowAnnouncementModal(false)}>&times;</button>
            </div>
            
            <div style={{ flex: 1, overflowY: 'auto', padding: '16px 0', display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {announcements.length === 0 ? (
                <div style={{ textAlign: 'center', color: '#94a3b8', marginTop: '40px' }}>目前沒有公告</div>
              ) : (
                announcements.map(a => (
                  <div key={a.id} style={{ backgroundColor: '#f8fafc', padding: '12px 16px', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
                    <p style={{ margin: '0 0 8px 0', fontSize: '14px', lineHeight: '1.5', color: '#334155' }}>{a.text}</p>
                    <div style={{ fontSize: '11px', color: '#94a3b8', textAlign: 'right' }}>{a.time}</div>
                  </div>
                ))
              )}
            </div>

            {isHostView && (
              <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: '16px', display: 'flex', gap: '8px' }}>
                <input 
                  type="text" 
                  className="form-input" 
                  placeholder="輸入要發布的公告..." 
                  value={newAnnouncement}
                  onChange={e => setNewAnnouncement(e.target.value)}
                  style={{ flex: 1, margin: 0 }}
                  onKeyPress={e => {
                    if (e.key === 'Enter' && newAnnouncement.trim()) {
                      setAnnouncements([...announcements, { id: Date.now(), text: newAnnouncement, time: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) }]);
                      setNewAnnouncement('');
                    }
                  }}
                />
                <button 
                  className="login-button" 
                  style={{ padding: '0 16px', whiteSpace: 'nowrap', width: 'auto' }}
                  onClick={() => {
                    if (newAnnouncement.trim()) {
                      setAnnouncements([...announcements, { id: Date.now(), text: newAnnouncement, time: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) }]);
                      setNewAnnouncement('');
                    }
                  }}
                >
                  發布
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Toast Notification */}
      {toastMsg && (
        <div className="toast-message">
          {toastMsg}
        </div>
      )}
    </div>
  );
}

export default PartyDetail;
