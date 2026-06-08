import axiosClient from './axiosClient';

const adminApi = {
  /**
   * 使用者發送回饋
   * @param {Object} data - { type, content }
   * @returns {Promise}
   */
  submitFeedback: (data) => {
    return axiosClient.post('/feedback', data);
  },

  /**
   * 管理員取得回饋清單 (限 Admin)
   * @param {Object} params - { is_handled }
   * @returns {Promise}
   */
  getFeedbacks: (params) => {
    return axiosClient.get('/admin/feedbacks', { params });
  },

  /**
   * 標記回饋已完成 (結案/忽略)
   * @param {number|string} feedbackId 
   * @param {Object} data - { is_handled }
   * @returns {Promise}
   */
  handleFeedback: (feedbackId, data) => {
    return axiosClient.put(`/admin/feedbacks/${feedbackId}/handle`, data);
  },

  /**
   * 場地管理與刪除
   * @param {number|string} venueId 
   * @returns {Promise}
   */
  deleteVenue: (venueId) => {
    return axiosClient.delete(`/admin/venues/${venueId}`);
  },

  /**
   * 管理員發佈系統公告
   * @param {Object} data 
   * @returns {Promise}
   */
  createSystemAnnouncement: (data) => {
    return axiosClient.post('/admin/announcements', data);
  },

  /**
   * 取得公告 (公開)
   * @returns {Promise}
   */
  getSystemAnnouncements: () => {
    return axiosClient.get('/announcements');
  },

  /**
   * 管理員數據分析 (Dashboard)
   * @returns {Promise}
   */
  getAdminAnalytics: () => {
    return axiosClient.get('/admin/analytics');
  },

  /**
   * 調整房間狀態 (Demo 工具)
   * @param {number|string} gameId 
   * @param {Object} data 
   * @returns {Promise}
   */
  updateDemoGameStatus: (gameId, data) => {
    return axiosClient.patch(`/admin/demo/games/${gameId}/status`, data);
  },

  /**
   * 模擬氣象適合度 (Demo 工具)
   * @param {Object} data 
   * @returns {Promise}
   */
  updateDemoWeather: (data) => {
    return axiosClient.patch(`/admin/demo/weather`, data);
  }
};

export default adminApi;
