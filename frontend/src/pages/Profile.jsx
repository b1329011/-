import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Cake, MapPin, Clock, Phone, Camera, HelpCircle, X } from 'lucide-react';
import '../App.css';

function Profile() {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const [isEditing, setIsEditing] = useState(false);
  const [showLevelHelp, setShowLevelHelp] = useState(false);
  const [userInfo, setUserInfo] = useState({
    nickname: '運動愛好者',
    email: 'user@example.com',
    birthday: '1998-05-20',
    gender: '男',
    phone: '0912345678',
    bio: '喜歡週末到處打球，偶爾打打衛生麻將。',
    region: '桃園市',
    levels: {
      '籃球': 'B',
      '排球': 'C',
      '羽球': 'A',
      '桌球': 'B',
      '麻將': 'B'
    },
    avatar: 'https://api.dicebear.com/9.x/adventurer/svg?seed=Lucky'
  });

  // 預設可愛頭貼清單 (精選 8 款)
  const presetAvatars = [
    'https://api.dicebear.com/9.x/adventurer/svg?seed=Lucky',
    'https://api.dicebear.com/9.x/adventurer/svg?seed=Mochi',
    'https://api.dicebear.com/9.x/adventurer/svg?seed=Cookie',
    'https://api.dicebear.com/9.x/adventurer/svg?seed=Sasha',
    'https://api.dicebear.com/9.x/adventurer/svg?seed=Pudding',
    'https://api.dicebear.com/9.x/adventurer/svg?seed=Jasmine',
    'https://api.dicebear.com/9.x/adventurer/svg?seed=Leo',
    'https://api.dicebear.com/9.x/adventurer/svg?seed=Willow',
  ];

  const handleSave = (e) => {
    e.preventDefault();
    
    // 手機號碼格式驗證
    const phoneRegex = /^09\d{8}$/;
    if (!phoneRegex.test(userInfo.phone)) {
      alert('請輸入正確的手機號碼格式 (例如: 0912345678)！');
      return;
    }

    setIsEditing(false);
    alert('個人資料已更新！');
  };

  const handleAvatarChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setUserInfo({ ...userInfo, avatar: reader.result });
      };
      reader.readAsDataURL(file);
    }
  };

  const handleLevelChange = (sport, value) => {
    setUserInfo({
      ...userInfo,
      levels: { ...userInfo.levels, [sport]: value }
    });
  };

  const getLevelColor = (lv) => {
    switch(lv) {
      case 'S': return '#ef4444'; // Red
      case 'A': return '#f59e0b'; // Orange
      case 'B': return '#10b981'; // Green
      case 'C': return '#94a3b8'; // Gray
      default: return '#7995a5';
    }
  };

  return (
    <div className="home-container">
      {/* 導覽列 */}
      <nav className="navbar">
        <div className="navbar-logo" style={{ cursor: 'pointer' }} onClick={() => navigate('/home')}>不揪ㄛ</div>
        <div className="navbar-actions">
          <button className="btn-outline" onClick={() => navigate('/home')}>返回大廳</button>
        </div>
      </nav>

      <main className="main-content">
        <div className="profile-layout">
          {/* 左側：個人資料與信譽積分 */}
          <div className="profile-sidebar">
            <div className="profile-card">
              <div 
                className="avatar-container" 
                style={{ position: 'relative', width: '100px', height: '100px', margin: '0 auto 20px auto' }}
              >
                <div className="avatar-placeholder" style={{ margin: 0, overflow: 'hidden' }}>
                  {userInfo.avatar ? (
                    <img src={userInfo.avatar} alt="avatar" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                  ) : (
                    userInfo.nickname.charAt(0)
                  )}
                </div>
                {isEditing && (
                  <button 
                    onClick={() => fileInputRef.current.click()}
                    style={{ position: 'absolute', bottom: 0, right: 0, backgroundColor: '#7995a5', border: 'none', borderRadius: '50%', width: '32px', height: '32px', display: 'flex', justifyContent: 'center', alignItems: 'center', color: 'white', cursor: 'pointer', boxShadow: '0 2px 5px rgba(0,0,0,0.2)' }}
                  >
                    <Camera size={16} />
                  </button>
                )}
                <input 
                  type="file" 
                  ref={fileInputRef} 
                  style={{ display: 'none' }} 
                  accept="image/*" 
                  onChange={handleAvatarChange} 
                />
              </div>

              {isEditing && (
                <div style={{ display: 'flex', justifyContent: 'center', gap: '8px', marginBottom: '24px', flexWrap: 'wrap' }}>
                  {presetAvatars.map((url, index) => (
                    <div 
                      key={index} 
                      onClick={() => setUserInfo({ ...userInfo, avatar: url })}
                      style={{ 
                        width: '36px', 
                        height: '36px', 
                        borderRadius: '50%', 
                        overflow: 'hidden', 
                        cursor: 'pointer',
                        border: userInfo.avatar === url ? '2px solid #7995a5' : '1px solid #e2e8f0',
                        padding: '1px'
                      }}
                    >
                      <img src={url} alt={`Preset ${index}`} style={{ width: '100%', height: '100%' }} />
                    </div>
                  ))}
                </div>
              )}
              
              {!isEditing ? (
                <>
                  <h2 className="profile-name">{userInfo.nickname}</h2>
                  <p className="profile-email">{userInfo.email}</p>
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', marginBottom: '20px' }}>
                    <p className="profile-email" style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <Cake size={16} /> {userInfo.birthday} ({userInfo.gender})
                    </p>
                    <p className="profile-email" style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <Phone size={16} /> {userInfo.phone}
                    </p>
                    <p className="profile-email" style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <MapPin size={16} /> {userInfo.region}
                    </p>
                  </div>
                  
                  <div style={{ marginBottom: '24px', textAlign: 'left' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                      <span style={{ fontSize: '14px', fontWeight: '700', color: '#64748b' }}>運動程度 (SABC)</span>
                      <HelpCircle size={16} color="#7995a5" style={{ cursor: 'pointer' }} onClick={() => setShowLevelHelp(true)} />
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                      {Object.entries(userInfo.levels).map(([sport, lv]) => (
                        <div key={sport} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 10px', backgroundColor: '#f1f5f9', borderRadius: '6px', fontSize: '13px' }}>
                          <span style={{ color: '#64748b' }}>{sport}</span>
                          <span style={{ fontWeight: '800', color: getLevelColor(lv) }}>{lv}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <p className="profile-bio">{userInfo.bio}</p>
                  
                  <div className="reputation-box">
                    <div className="reputation-title">信譽積分</div>
                    <div className="reputation-score">98<span>/100</span></div>
                    <p className="reputation-desc">優良玩家，從不爽約！</p>
                  </div>

                  <button className="btn-outline" style={{ width: '100%', marginTop: '20px' }} onClick={() => setIsEditing(true)}>
                    編輯個人資料
                  </button>
                </>
              ) : (
                <form onSubmit={handleSave} className="edit-profile-form">
                  <div className="form-group">
                    <label className="form-label">暱稱</label>
                    <input type="text" className="form-input" value={userInfo.nickname} onChange={e => setUserInfo({...userInfo, nickname: e.target.value})} required />
                  </div>
                  <div className="form-group">
                    <label className="form-label">生日 (不可修改)</label>
                    <input type="date" className="form-input" value={userInfo.birthday} readOnly style={{ backgroundColor: '#f1f5f9', color: '#94a3b8', cursor: 'not-allowed' }} />
                  </div>
                  <div className="form-group">
                    <label className="form-label">性別</label>
                    <div style={{ display: 'flex', gap: '16px', marginTop: '8px' }}>
                      <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
                        <input type="radio" name="gender" value="男" checked={userInfo.gender === '男'} onChange={(e) => setUserInfo({...userInfo, gender: e.target.value})} /> 男
                      </label>
                      <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
                        <input type="radio" name="gender" value="女" checked={userInfo.gender === '女'} onChange={(e) => setUserInfo({...userInfo, gender: e.target.value})} /> 女
                      </label>
                    </div>
                  </div>
                  <div className="form-group">
                    <label className="form-label">聯絡電話</label>
                    <input type="tel" className="form-input" placeholder="09xxxxxxxx" value={userInfo.phone} onChange={e => setUserInfo({...userInfo, phone: e.target.value})} required />
                  </div>
                  
                  <div style={{ marginBottom: '20px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                      <label className="form-label" style={{ marginBottom: 0 }}>各項程度 <span style={{ color: '#ef4444' }}>(必填)</span></label>
                      <HelpCircle size={16} color="#7995a5" style={{ cursor: 'pointer' }} onClick={() => setShowLevelHelp(true)} />
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                      {Object.keys(userInfo.levels).map(sport => (
                        <div key={sport}>
                          <label style={{ fontSize: '11px', color: '#94a3b8' }}>{sport}</label>
                          <select 
                            className="form-input" 
                            style={{ padding: '6px 10px', fontSize: '13px' }}
                            value={userInfo.levels[sport]} 
                            onChange={e => handleLevelChange(sport, e.target.value)}
                          >
                            <option value="S">S</option>
                            <option value="A">A</option>
                            <option value="B">B</option>
                            <option value="C">C</option>
                          </select>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="form-group">
                    <label className="form-label">常駐地區</label>
                    <select className="form-input" value={userInfo.region} onChange={e => setUserInfo({...userInfo, region: e.target.value})}>
                      <option value="桃園市">桃園市</option>
                      <option value="台北市">台北市</option>
                      <option value="新北市">新北市</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">個人簡介</label>
                    <textarea className="form-input" rows="3" value={userInfo.bio} onChange={e => setUserInfo({...userInfo, bio: e.target.value})}></textarea>
                  </div>
                  <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
                    <button type="button" className="btn-outline" style={{ flex: 1 }} onClick={() => setIsEditing(false)}>取消</button>
                    <button type="submit" className="btn-primary" style={{ flex: 1 }}>儲存</button>
                  </div>
                </form>
              )}
            </div>
          </div>

          {/* 右側：揪團紀錄 */}
          <div className="profile-content">
            <div className="content-header">
              <h2>我的揪團紀錄</h2>
            </div>
            
            <div className="party-grid">
              <div className="party-card">
                <div className="party-card-header">
                  <span className="party-type">籃球</span>
                  <span className="party-status" style={{ color: '#10b981' }}>已結束</span>
                </div>
                <h3 className="party-title">昨晚的巨蛋熱血籃球</h3>
                <div className="party-info">
                  <p style={{ gap: '6px' }}><MapPin size={16} /> 桃園巨蛋室外籃球場</p>
                  <p style={{ gap: '6px' }}><Clock size={16} /> 昨天 19:00</p>
                </div>
              </div>

              <div className="party-card">
                <div className="party-card-header">
                  <span className="party-type">麻將</span>
                  <span className="party-status" style={{ color: '#10b981' }}>已結束</span>
                </div>
                <h3 className="party-title">歡樂衛生麻將局</h3>
                <div className="party-info">
                  <p style={{ gap: '6px' }}><MapPin size={16} /> 中壢桌遊店</p>
                  <p style={{ gap: '6px' }}><Clock size={16} /> 上週五 20:00</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* 能力參考表 Modal */}
      {showLevelHelp && (
        <div className="modal-overlay" onClick={() => setShowLevelHelp(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()} style={{ maxWidth: '600px', maxHeight: '80vh', overflowY: 'auto' }}>
            <div className="modal-header">
              <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><HelpCircle size={24} color="#7995a5" /> 能力程度參考表</h3>
              <button className="modal-close" onClick={() => setShowLevelHelp(false)}><X size={24} /></button>
            </div>
            
            <div className="help-section" style={{ marginBottom: '32px' }}>
              <h4 style={{ color: '#7995a5', borderBottom: '2px solid #f1f5f9', paddingBottom: '8px', marginBottom: '16px' }}>🏀 球類運動 (Ball Games)</h4>
              <p style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '12px' }}>* 以排球為參考基準，其他球類以此類推</p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div>
                  <strong style={{ color: '#ef4444' }}>S 級 (菁英)：</strong>
                  <span style={{ fontSize: '14px', color: '#475569', lineHeight: '1.6' }}>大專公開一、甲組等級，具備強烈跳發、精準快攻與高強度攔網的神仙打架。</span>
                </div>
                <div>
                  <strong style={{ color: '#f59e0b' }}>A 級 (高手)：</strong>
                  <span style={{ fontSize: '14px', color: '#475569', lineHeight: '1.6' }}>大專一般組或校隊，能跑 5-1 戰術陣型、具備背舉與看手型重扣的流暢比賽。</span>
                </div>
                <div>
                  <strong style={{ color: '#10b981' }}>B 級 (熟練)：</strong>
                  <span style={{ fontSize: '14px', color: '#475569', lineHeight: '1.6' }}>系隊主力或熱門 Play 咖，一接二傳穩定不持球，攻擊手能包球壓腕的三下組織。</span>
                </div>
                <div>
                  <strong style={{ color: '#94a3b8' }}>C 級 (新手)：</strong>
                  <span style={{ fontSize: '14px', color: '#475569', lineHeight: '1.6' }}>剛入門的休閒玩家，以發球過網為目標，容易噴球、常直接送球過網的歡樂運動。</span>
                </div>
              </div>
            </div>

            <div className="help-section">
              <h4 style={{ color: '#7995a5', borderBottom: '2px solid #f1f5f9', paddingBottom: '8px', marginBottom: '16px' }}>🀄 麻將 (Mahjong)</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div>
                  <strong style={{ color: '#ef4444' }}>S 級 (菁英)：</strong>
                  <span style={{ fontSize: '14px', color: '#475569', lineHeight: '1.6' }}>職業賽事或頂尖老手等級，具備精準讀牌、扣死絕張與利用捨牌誘導對手放槍的神仙打架。</span>
                </div>
                <div>
                  <strong style={{ color: '#f59e0b' }}>A 級 (高手)：</strong>
                  <span style={{ fontSize: '14px', color: '#475569', lineHeight: '1.6' }}>長期牌桌常客或賽事玩家，能依進牌機率迅速轉圈、具備果斷防守下車與看穿多面聽的高強度心理戰。</span>
                </div>
                <div>
                  <strong style={{ color: '#10b981' }}>B 級 (熟練)：</strong>
                  <span style={{ fontSize: '14px', color: '#475569', lineHeight: '1.6' }}>週末固定牌咖或過年主力，吃碰槓反應順暢不拖台錢，具備看海底防守與穩定組出基本台數的流暢牌局。</span>
                </div>
                <div>
                  <strong style={{ color: '#94a3b8' }}>C 級 (新手)：</strong>
                  <span style={{ fontSize: '14px', color: '#475569', lineHeight: '1.6' }}>剛入門的休閒玩家，以知道自己聽什麼牌為目標，容易相公、常問「這張可以吃嗎」的歡樂麻將。</span>
                </div>
              </div>
            </div>
            
            <button className="login-button" style={{ marginTop: '32px' }} onClick={() => setShowLevelHelp(false)}>我瞭解了</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default Profile;
