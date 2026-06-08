import axiosClient from './axiosClient';

const gamesApi = {
  /**
   * 取得球局列表
   * @param {Object} params - Query參數 { region, sport_type, level }
   * @returns {Promise}
   */
  getGames: (params) => {
    return axiosClient.get('/games/', { params: { ...params, _t: Date.now() } });
  },

  /**
   * 取得個人歷史球局
   * @returns {Promise}
   */
  getHistory: () => {
    return axiosClient.get('/games/history/');
  },

  /**
   * 取得單一球局詳細資料
   * @param {number|string} gameId
   * @returns {Promise}
   */
  getGameById: (gameId) => {
    return axiosClient.get(`/games/${gameId}/`);
  },

  /**
   * 主揪發起球局（開房）
   * @param {Object} data - { sport_id, venue_id, most_players, target_level, booking_date, time_slot, duration, is_free, total_price, gender_limit, description }
   * @returns {Promise}
   */
  createGame: (data) => {
    return axiosClient.post('/games/', data);
  },

  /**
   * 報名參加/排候補
   * @param {number|string} gameId 
   * @returns {Promise}
   */
  joinGame: (gameId, data) => {
    return axiosClient.post(`/games/${gameId}/join/`, data);
  },

  /**
   * 取消報名/退出球局
   * @param {number|string} gameId 
   * @returns {Promise}
   */
  cancelGame: (gameId) => {
    return axiosClient.delete(`/games/${gameId}/cancel/`);
  },

  /**
   * 主揪回報場地狀態
   * @param {number|string} gameId 
   * @param {Object} data - { status, note }
   * @returns {Promise}
   */
  updateVenueStatus: (gameId, data) => {
    return axiosClient.patch(`/games/${gameId}/venue-status/`, data);
  },

  /**
   * 取得球局佈告欄歷史紀錄
   * @param {number|string} gameId 
   * @returns {Promise}
   */
  getAnnouncements: (gameId) => {
    return axiosClient.get(`/games/${gameId}/announcements/`);
  },

  /**
   * 主揪發佈新公告
   * @param {number|string} gameId 
   * @param {Object} data - { text }
   * @returns {Promise}
   */
  createAnnouncement: (gameId, data) => {
    return axiosClient.post(`/games/${gameId}/announcements/`, data);
  },

  /**
   * 取得參與名單與候補名單
   * @param {number|string} gameId 
   * @returns {Promise}
   */
  getParticipants: (gameId) => {
    return axiosClient.get(`/games/${gameId}/participants/`);
  },

  /**
   * 主揪取消(刪除)球局
   * @param {number|string} gameId 
   * @returns {Promise}
   */
  deleteGame: (gameId) => {
    return axiosClient.delete(`/games/${gameId}/`);
  }
};

export default gamesApi;
