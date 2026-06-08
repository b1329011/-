import axiosClient from './axiosClient';

const venuesApi = {
  getVenues: async () => {
    try {
      const response = await axiosClient.get('/venues/');
      return response;
    } catch (error) {
      console.error('取得場館列表失敗:', error);
      throw error;
    }
  },
  getCourts: async () => {
    try {
      const response = await axiosClient.get('/courts/');
      return response;
    } catch (error) {
      console.error('取得球場列表失敗:', error);
      throw error;
    }
  }
};

export default venuesApi;
