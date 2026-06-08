import axiosClient from './axiosClient';

const reportsApi = {
  /**
   * 提交檢舉
   * @param {Object} data - { game_id, reported_user_id, reason, detail }
   * @returns {Promise}
   */
  submitReport: (data) => {
    return axiosClient.post('/reports', data);
  }
};

export default reportsApi;
