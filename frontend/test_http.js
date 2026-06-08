const http = require('http');

http.get('http://127.0.0.1:8000/api/v1/venues/', (resp) => {
  let data = '';
  resp.on('data', (chunk) => {
    data += chunk;
  });
  resp.on('end', () => {
    console.log(data.substring(0, 500));
  });
}).on("error", (err) => {
  console.log("Error: " + err.message);
});
