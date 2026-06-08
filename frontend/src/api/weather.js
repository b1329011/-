import axiosClient from './axiosClient';

const weatherApi = {
  /**
   * 取得大廳即時天氣與 AQI
   * @returns {Promise}
   */
  getWeatherAqi: () => {
    return axiosClient.get('/weather/aqi');
  }
};

export default weatherApi;
