import axiosClient from './axiosClient';

const notificationsApi = {
  /**
   * 取得通知列表
   * @returns {Promise}
   */
  getNotifications: () => {
    return axiosClient.get('/notifications');
  },

  /**
   * 標記通知為已讀
   * @param {number|string} notificationId 
   * @returns {Promise}
   */
  markAsRead: (notificationId) => {
    return axiosClient.patch(`/notifications/${notificationId}/read`);
  }
};

export default notificationsApi;
