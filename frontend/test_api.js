import axiosClient from './src/api/axiosClient.js';
import venuesApi from './src/api/venues.js';

async function test() {
    try {
        const data = await venuesApi.getVenues();
        console.log(JSON.stringify(data, null, 2));
    } catch(e) {
        console.error(e);
    }
}
test();
