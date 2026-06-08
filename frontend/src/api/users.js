import axiosClient from './axiosClient';

const usersApi = {
  /**
   * 取得個人資料與信譽積分
   * @returns {Promise}
   */
  getUserProfile: () => {
    return axiosClient.get('/users/profile');
  },

  /**
   * 更新個人資料 (建立個人檔案)
   * @param {Object} data - { name, phone, birthday, gender, bio, avatar, levels, line_id, instagram }
   * @returns {Promise}
   */
  updateUserProfile: (data) => {
    return axiosClient.put('/users/profile', data);
  }
};

export default usersApi;
